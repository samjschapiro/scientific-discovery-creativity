"""Combinatorial-creativity measures from Lacuna idea atoms (best extraction run only).

dsi
    Divergent semantic integration over atoms: the mean pairwise cosine distance among all of a
    paper's atoms. This adapts Johnson et al.'s DSI, where the units are words of a story.
pm_distance
    Mean cosine distance between each problem atom and each mechanism atom: how far the method is
    from the problem it is applied to.
novel_pair_frac, pmi_p10, pmi_median
    Concept-pair novelty in the frozen layer (default f20000). For each pair of distinct concepts
    in the paper, count co-occurrences among papers from strictly earlier years. PMI uses add-one
    smoothing. novel_pair_frac is the share of pairs never seen before. pmi_p10 is the 10th
    percentile pair PMI (Uzzi-style tail atypicality: lower = more atypical).

EMBEDDING PROXY: the package has no per-atom vectors, so each atom is represented by the centroid
of its concept in `vector_layer` (c200000 by default, ~62 atoms per concept). Two atoms in the same
concept therefore have distance 0. Swap in the real bge-large atom vectors when they arrive.
"""

import numpy as np
import polars as pl


def _mean_pairwise_distance(v: np.ndarray) -> float:
    sims = v @ v.T
    iu = np.triu_indices(len(v), k=1)
    return float(np.mean(1.0 - sims[iu]))


def embedding_measures(con, centroids_path: str, vector_layer: str) -> pl.DataFrame:
    """DSI and problem-mechanism distance for every pid in `focal`."""
    atoms = con.sql(f"""
        SELECT a.pid, a.type, a.{vector_layer} AS cid
        FROM atoms a JOIN focal USING (pid)
        WHERE a.run_rank = 1 AND a.{vector_layer} IS NOT NULL
        ORDER BY a.pid
    """).pl()
    centroids = np.load(centroids_path)  # float16, unit-normalised rows

    rows = []
    for (pid,), g in atoms.group_by(["pid"], maintain_order=True):
        v = centroids[g["cid"].to_numpy()].astype(np.float32)
        types = g["type"].to_numpy()
        dsi = _mean_pairwise_distance(v) if len(v) >= 2 else None
        prob, mech = v[types == "problem"], v[types == "mechanism"]
        pm = float(np.mean(1.0 - prob @ mech.T)) if len(prob) and len(mech) else None
        rows.append({"pid": pid, "n_atoms_used": len(v), "dsi": dsi, "pm_distance": pm,
                     "n_unique_concepts": int(np.unique(g["cid"].to_numpy()).size)})
    return pl.DataFrame(rows, schema={"pid": pl.Int32, "n_atoms_used": pl.Int64, "dsi": pl.Float64,
                                      "pm_distance": pl.Float64, "n_unique_concepts": pl.Int64})


def pair_novelty(con, novelty_layer: str, max_year: int) -> None:
    """Create table `novelty(pid, n_pairs, novel_pair_frac, pmi_p10, pmi_median)` for `focal`."""
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE pc AS
        SELECT DISTINCT pid, year, {novelty_layer} AS c FROM atoms
        WHERE run_rank = 1 AND {novelty_layer} IS NOT NULL AND year <= {int(max_year)}
          AND pid IN (SELECT pid FROM papers WHERE pid = canonical_pid)  -- v2: duplicate entries would double-count pairs
    """)
    # Counts by year; earlier-year totals are summed per focal year below.
    con.execute("CREATE OR REPLACE TEMP TABLE papers_year AS SELECT year, count(DISTINCT pid) AS n FROM pc GROUP BY year")
    con.execute("CREATE OR REPLACE TEMP TABLE concept_year AS SELECT year, c, count(*) AS n FROM pc GROUP BY ALL")
    con.execute("""
        CREATE OR REPLACE TEMP TABLE pair_year AS
        SELECT a.year, a.c AS c1, b.c AS c2, count(*) AS n
        FROM pc a JOIN pc b ON a.pid = b.pid AND a.c < b.c GROUP BY ALL
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE focal_pairs AS
        SELECT f.pid, f.year, a.c AS c1, b.c AS c2
        FROM focal f JOIN pc a USING (pid) JOIN pc b ON b.pid = a.pid AND a.c < b.c
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE novelty AS
        WITH n_prior AS (SELECT fy.year, sum(py.n) AS n
                         FROM (SELECT DISTINCT year FROM focal) fy JOIN papers_year py ON py.year < fy.year
                         GROUP BY fy.year),
             ab AS (SELECT fp.pid, fp.year, fp.c1, fp.c2, coalesce(sum(py.n), 0) AS n_ab
                    FROM focal_pairs fp LEFT JOIN pair_year py
                      ON py.c1 = fp.c1 AND py.c2 = fp.c2 AND py.year < fp.year
                    GROUP BY ALL),
             a AS (SELECT ab.*, coalesce(sum(cy.n), 0) AS n_a FROM ab LEFT JOIN concept_year cy
                     ON cy.c = ab.c1 AND cy.year < ab.year GROUP BY ALL),
             b AS (SELECT a.*, coalesce(sum(cy.n), 0) AS n_b FROM a LEFT JOIN concept_year cy
                     ON cy.c = a.c2 AND cy.year < a.year GROUP BY ALL),
             pmi AS (SELECT b.pid, b.n_ab,
                            ln((b.n_ab + 1) * (np.n + 1) / ((b.n_a + 1) * (b.n_b + 1))) AS pmi
                     FROM b JOIN n_prior np USING (year))
        SELECT pid, count(*) AS n_pairs,
               avg((n_ab = 0)::INT) AS novel_pair_frac,
               quantile_cont(pmi, 0.10) AS pmi_p10,
               median(pmi) AS pmi_median
        FROM pmi GROUP BY pid
    """)
