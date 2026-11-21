"""Analogical novelty from Lacuna atoms: a mechanism carried into a problem area it never served.

DSI already measures associative distance (how far apart a paper's atoms are). Analogy is narrower:
a mechanism that is *established* somewhere is applied to a problem *far from where it was used*.

All concepts are in a frozen layer (default f20000), so nothing uses hindsight.

    home(m, y)    problem concepts h that co-occurred with mechanism concept m in the same paper,
                  in papers published strictly before year y, with paper counts n_h

For a focal paper's mechanism atom m and each of the paper's problem concepts p, three transfer
distances (cosine distance between f20000 centroids):

    nn1     1 - max_h sim(p, h)                     nearest prior problem m was used on
    nnk     same, but only h with n_h >= min_pair_papers (drops one-off co-occurrences)
    wmean   1 - sum_h n_h sim(p, h) / sum_h n_h      how far p is from m's *typical* problem

An atom's transfer is the minimum over the paper's problems (the problem the mechanism most
plausibly serves). Mechanisms used in < min_home_papers earlier papers are new inventions, not
analogies: they are counted but not scored.

Why three variants: f20000 concepts are topical, not role-specific (46% mix problem and mechanism
atoms), so nn1 hits 0 for ~60% of atoms. Which variant carries the analogy signature is decided by
validate_analogy (cue phrases), not assumed here.
"""

import numpy as np
import polars as pl

VARIANTS = ["nn1", "nnk", "wmean"]


def similarity_matrix(centroids_path: str, block: int = 2000) -> np.ndarray:
    """Cosine similarity between all centroids (rows are unit-normalised), stored float16."""
    c = np.load(centroids_path).astype(np.float32)
    norms = np.linalg.norm(c, axis=1)
    if not np.allclose(norms, 1.0, atol=1e-2):
        raise ValueError(f"FATAL: centroids in {centroids_path} are not unit-normalised")
    s = np.empty((len(c), len(c)), dtype=np.float16)
    for i in range(0, len(c), block):
        s[i:i + block] = c[i:i + block] @ c.T
    return s


def mechanism_homes(con, layer: str, max_year: int) -> pl.DataFrame:
    """Papers per (mechanism concept m, problem concept p, year), over every Lacuna paper with atoms
    published before max_year (not just the focal set). Also creates temp table pm_atoms."""
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE pm_atoms AS
        SELECT DISTINCT pid, year, type, {layer} AS c FROM atoms
        WHERE run_rank = 1 AND {layer} IS NOT NULL AND type IN ('problem', 'mechanism')
          AND year < {int(max_year)}
          AND pid IN (SELECT pid FROM papers WHERE pid = canonical_pid)  -- v2: duplicate entries would double-count homes
    """)
    return con.sql("""
        SELECT m.c AS m, p.c AS p, m.year, count(*) AS n
        FROM pm_atoms m JOIN pm_atoms p ON p.pid = m.pid AND p.type = 'problem'
        WHERE m.type = 'mechanism' GROUP BY ALL ORDER BY m
    """).pl()


def mechanism_paper_counts(con) -> pl.DataFrame:
    """Papers per (mechanism concept, year); needs pm_atoms from mechanism_homes."""
    return con.sql("""
        SELECT c AS m, year, count(DISTINCT pid) AS n FROM pm_atoms
        WHERE type = 'mechanism' GROUP BY ALL
    """).pl()


def focal_atoms(con, layer: str) -> pl.DataFrame:
    """Problem and mechanism atoms of the papers in table `focal(pid, year)`."""
    return con.sql(f"""
        SELECT a.pid, f.year, a.atom_id, a.type, a.{layer} AS c
        FROM atoms a JOIN focal f USING (pid)
        WHERE a.run_rank = 1 AND a.{layer} IS NOT NULL AND a.type IN ('problem', 'mechanism')
    """).pl()


def _resolve(need: pl.DataFrame, homes: pl.DataFrame, sim: np.ndarray, min_pair_papers: int) -> pl.DataFrame:
    """Transfer distances for every needed (m, q, year): q is a focal problem concept."""
    hm, hp, hy, hn = (homes[c].to_numpy() for c in ["m", "p", "year", "n"])
    bounds = np.searchsorted(hm, np.arange(sim.shape[0] + 1))  # homes sorted by m
    cols = {k: [] for k in ["m_c", "q", "year", "home_size", *VARIANTS]}
    for (m, y), g in need.group_by(["m_c", "year"]):
        q = g["q"].to_numpy()
        lo, hi = bounds[m], bounds[m + 1]
        mask = hy[lo:hi] < y
        up, inv = np.unique(hp[lo:hi][mask], return_inverse=True)
        cnt = np.bincount(inv, weights=hn[lo:hi][mask]) if up.size else np.empty(0)
        res = {v: np.full(len(q), np.nan) for v in VARIANTS}
        if up.size:
            s = sim[np.ix_(q, up)].astype(np.float32)
            res["nn1"] = 1.0 - s.max(axis=1)
            res["wmean"] = 1.0 - (s @ cnt) / cnt.sum()
            strong = cnt >= min_pair_papers
            if strong.any():
                res["nnk"] = 1.0 - s[:, strong].max(axis=1)
        cols["m_c"].append(np.full(len(q), m)); cols["q"].append(q); cols["year"].append(np.full(len(q), y))
        cols["home_size"].append(np.full(len(q), up.size))
        for v in VARIANTS:
            cols[v].append(res[v])
    # NaN (no qualifying home) -> null, so polars aggregations and counts treat it as missing.
    return pl.DataFrame({k: np.concatenate(v) for k, v in cols.items()}).with_columns(
        pl.col("m_c").cast(pl.Int32), pl.col("q").cast(pl.Int32), pl.col("year").cast(pl.Int32),
        *[pl.col(v).fill_nan(None) for v in VARIANTS])


def atom_transfer(atoms: pl.DataFrame, homes: pl.DataFrame, counts: pl.DataFrame, sim: np.ndarray,
                  min_home_papers: int, min_pair_papers: int) -> pl.DataFrame:
    """One row per focal mechanism atom that has at least one problem atom in its paper.

    Columns: pid, year, atom_id, m, home_papers (earlier papers using m), home_size (distinct problem
    concepts in its home), established, and one transfer column per variant (null if not established)."""
    probs = atoms.filter(pl.col("type") == "problem").group_by("pid").agg(pl.col("c").unique().alias("probs"))
    mechs = (atoms.filter(pl.col("type") == "mechanism").join(probs, on="pid", how="inner")
             .rename({"c": "m_c"}).explode("probs").rename({"probs": "q"}))
    resolved = _resolve(mechs.select(["m_c", "q", "year"]).unique(), homes, sim, min_pair_papers)

    years = sorted(atoms["year"].unique().to_list())
    hp = pl.concat([counts.filter(pl.col("year") < y).group_by("m").agg(pl.col("n").sum().alias("home_papers"))
                    .with_columns(year=pl.lit(y, dtype=pl.Int32)) for y in years]) \
        .rename({"m": "m_c"}).with_columns(pl.col("m_c").cast(pl.Int32))

    per_atom = (mechs.join(resolved, on=["m_c", "q", "year"], how="left")
                .group_by(["pid", "year", "atom_id", "m_c"])
                .agg(*[pl.col(v).min() for v in VARIANTS], pl.col("home_size").first())
                .join(hp, on=["m_c", "year"], how="left")
                .with_columns(pl.col("home_papers").fill_null(0))
                .with_columns(established=pl.col("home_papers") >= min_home_papers))
    return per_atom.with_columns(
        [pl.when(pl.col("established")).then(pl.col(v)).otherwise(None).alias(v) for v in VARIANTS]
    ).rename({"m_c": "m"})


def paper_scores(per_atom: pl.DataFrame) -> pl.DataFrame:
    est = pl.col("established")
    return per_atom.group_by("pid").agg(
        *[pl.col(v).max().alias(f"analogy_{v}_max") for v in VARIANTS],
        *[pl.col(v).mean().alias(f"analogy_{v}_mean") for v in VARIANTS],
        n_mech_scored=pl.len(),
        n_mech_established=est.sum(),
        n_mech_new=(~est).sum(),
        log_home_size=(pl.col("home_size").filter(est) + 1).log().mean(),
    )
