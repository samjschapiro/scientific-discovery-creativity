"""Attribute critique atoms to the references they criticise.

Lacuna's problems_and_motivation limitation atoms criticise prior work ("existing approaches
suffer from ...") but never name it. We turn attribution into a choice among the citing paper's
own references:

    for critique c in citing paper B, and each in-corpus reference r of B that has atoms:
        s_r = max over r's own-contribution atoms (ref_exclude_lenses dropped) of cos(c, atom)
    c is attributed to argmax_r s_r if (best - runner-up) >= margin and B has >= 2 candidates

The choice is made per citing paper, independent of which foundation we care about, so a critique
in a paper citing both Adam and the Transformer goes to whichever it matches better.

Known blind spot: references without atoms (outside Lacuna, or no full text) can never win, so a
critique of one of them may be misattributed to the nearest reference that has atoms. The margin
guards against this only partly; check it in the precision sample.

Vectors: each atom is represented by its concept centroid in `layer` (c200000 default), the same
proxy as atom_measures.py, until per-atom embeddings exist.
"""

import numpy as np
import polars as pl


def match_foundations(con, foundations: list[dict]) -> pl.DataFrame:
    """Exact (case-insensitive) title match among canonical entries; fails if any is missing or ambiguous."""
    rows = []
    for f in foundations:
        hits = con.execute("""
            SELECT pid, year, cites_lacuna_2025, n_atoms FROM papers
            WHERE lower(trim(title)) = lower(trim(?)) AND pid = canonical_pid
            ORDER BY cites_lacuna_2025 DESC NULLS LAST
        """, [f["title"]]).fetchall()
        if not hits:
            raise ValueError(f"FATAL: foundation not found: {f['title']}")
        if len(hits) > 1 and hits[1][2] and hits[1][2] > 0.1 * (hits[0][2] or 0):
            raise ValueError(f"FATAL: ambiguous title match for {f['title']}: {hits}")
        pid, year, cites, n_atoms = hits[0]
        if not n_atoms:
            raise ValueError(f"FATAL: foundation has no atoms, cannot be attributed: {f['title']}")
        rows.append({"pid": pid, "title": f["title"], "year": year, "cites_lacuna_2025": cites,
                     "kind": f["kind"], "crack": f.get("crack"), "successor": f.get("successor"),
                     "successor_year": f.get("successor_year")})
    return pl.DataFrame(rows)


def load_inputs(con, foundation_pids: list[int], config: dict) -> dict[str, pl.DataFrame]:
    """Citers of the foundations, their critique atoms, their references and those references' atoms."""
    layer, group_layer = config["vector_layer"], config["same_limitation_layer"]
    # A reference is represented by its own contribution only: its problems_and_motivation atoms
    # describe *other* work (e.g. the Transformer's atoms about RNN limitations) and would pull
    # critiques of what it replaced onto it.
    excluded = ", ".join(f"'{lens}'" for lens in config["ref_exclude_lenses"]) or "''"
    # ...and only by what it *proposes*. A paper whose contribution is diagnosing a limitation
    # ("Deeper Insights into GCNs" on over-smoothing) has finding atoms about it and would absorb the
    # critiques aimed at the method it diagnosed.
    types = ", ".join(f"'{t}'" for t in config["ref_atom_types"])
    con.execute("CREATE OR REPLACE TEMP TABLE fpids AS SELECT unnest(?) AS pid", [foundation_pids])
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE pilot_citers AS
        SELECT DISTINCT c.cited_pid AS foundation, c.citing_pid AS citer, c.citing_year AS year
        FROM citations c JOIN fpids f ON f.pid = c.cited_pid
        WHERE c.citing_year BETWEEN {int(config['citer_year_min'])} AND {int(config['citer_year_max'])}
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE critiques AS
        SELECT a.pid AS citer, a.atom_id, a.{layer} AS cid, a.{group_layer} AS gid,
               a.{config["concentration_layer"]} AS kid, a.text
        FROM atoms a JOIN (SELECT DISTINCT citer FROM pilot_citers) s ON s.citer = a.pid
        WHERE a.run_rank = 1 AND a.type = ? AND a.lens = ? AND a.{layer} IS NOT NULL
    """, [config["critique_type"], config["critique_lens"]])
    con.execute("""
        CREATE OR REPLACE TEMP TABLE citer_refs AS
        SELECT DISTINCT c.citing_pid AS citer, c.cited_pid AS ref
        FROM citations c JOIN (SELECT DISTINCT citer FROM critiques) s ON s.citer = c.citing_pid
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE ref_atoms AS
        SELECT DISTINCT a.pid AS ref, a.{layer} AS cid
        FROM atoms a JOIN (SELECT DISTINCT ref FROM citer_refs) r ON r.ref = a.pid
        WHERE a.run_rank = 1 AND a.{layer} IS NOT NULL AND coalesce(a.lens, '') NOT IN ({excluded})
          AND a.type IN ({types})
    """)
    return {
        "citers": con.sql("SELECT * FROM pilot_citers").pl(),
        "critiques": con.sql("SELECT * FROM critiques ORDER BY citer").pl(),
        "citer_refs": con.sql("SELECT * FROM citer_refs WHERE ref IN (SELECT ref FROM ref_atoms) ORDER BY citer, ref").pl(),
        "ref_atoms": con.sql("SELECT * FROM ref_atoms ORDER BY ref").pl(),
    }


def attribute(inputs: dict[str, pl.DataFrame], centroids: np.ndarray, shortlist_k: int = 5) -> pl.DataFrame:
    """One row per critique atom whose citer has >= 2 candidate references:
    citer, atom_id, best_ref, s1, second_ref, s2, n_candidates, shortlist (top-k refs, best first;
    the candidates that rescore_with_embeddings re-ranks)."""
    ra = inputs["ref_atoms"]
    ra_ref, ra_cid = ra["ref"].to_numpy(), ra["cid"].to_numpy()
    uniq_refs, ref_start = np.unique(ra_ref, return_index=True)
    ref_end = np.append(ref_start[1:], len(ra_ref))
    ref_pos = {int(r): i for i, r in enumerate(uniq_refs)}

    refs_by_citer = {int(c): g["ref"].to_numpy() for (c,), g in inputs["citer_refs"].group_by(["citer"])}
    out = {k: [] for k in ["citer", "atom_id", "best_ref", "s1", "second_ref", "s2", "n_candidates", "shortlist"]}
    for (citer,), g in inputs["critiques"].group_by(["citer"], maintain_order=True):
        refs = refs_by_citer.get(int(citer))
        if refs is None or len(refs) < 2:
            continue
        idx = [ref_pos[int(r)] for r in refs]
        cids = np.concatenate([ra_cid[ref_start[i]:ref_end[i]] for i in idx])
        starts = np.cumsum([0] + [ref_end[i] - ref_start[i] for i in idx[:-1]])
        s = centroids[g["cid"].to_numpy()].astype(np.float32) @ centroids[cids].astype(np.float32).T
        per_ref = np.maximum.reduceat(s, starts, axis=1)          # critiques x refs
        order = np.argsort(-per_ref, axis=1, kind="stable")
        top2 = order[:, :2]
        rows = np.arange(len(per_ref))
        out["citer"].extend([citer] * len(per_ref))
        out["atom_id"].extend(g["atom_id"].to_list())
        out["best_ref"].extend(refs[top2[:, 0]].tolist())
        out["s1"].extend(per_ref[rows, top2[:, 0]].tolist())
        out["second_ref"].extend(refs[top2[:, 1]].tolist())
        out["s2"].extend(per_ref[rows, top2[:, 1]].tolist())
        out["n_candidates"].extend([len(refs)] * len(per_ref))
        out["shortlist"].extend(refs[order[:, :shortlist_k]].tolist())
    return pl.DataFrame(out).with_columns(margin=pl.col("s1") - pl.col("s2"))


def foundation_curves(foundations: pl.DataFrame, citers: pl.DataFrame, attributions: pl.DataFrame,
                      margin: float, hits_from: pl.DataFrame | None = None) -> pl.DataFrame:
    """Per foundation-year: citers, citers that could critique (>= 1 critique atom, >= 2 candidates),
    citers attributing >= 1 critique to the foundation, rate, and the chance expectation
    sum_B 1 - (1 - 1/R_B)^k_B (uniform attribution among B's R_B candidates, no margin)."""
    per_citer = attributions.group_by("citer").agg(k=pl.len(), R=pl.col("n_candidates").first())
    # Denominators (who could critique) always come from the full proxy attribution; hits may come
    # from the embedding re-score, which only covers shortlisted critiques.
    hits = (attributions if hits_from is None else hits_from).filter(pl.col("margin") >= margin).select(["citer", "best_ref"]).unique() \
        .rename({"best_ref": "foundation"}).with_columns(hit=pl.lit(True))
    d = (citers.join(per_citer, on="citer", how="left")
         .join(hits, on=["citer", "foundation"], how="left")
         .with_columns(pl.col("hit").fill_null(False), able=pl.col("k").is_not_null(),
                       chance=(1 - (1 - 1 / pl.col("R")) ** pl.col("k")).fill_null(0.0)))
    return (d.group_by(["foundation", "year"]).agg(
                n_citers=pl.len(), n_able=pl.col("able").sum(), n_critics=pl.col("hit").sum(),
                chance_critics=pl.col("chance").sum())
            .with_columns(rate=pl.col("n_critics") / pl.col("n_able"),
                          chance_rate=pl.col("chance_critics") / pl.col("n_able"))
            .join(foundations.select(pl.col("pid").alias("foundation"), "title", "kind"), on="foundation")
            .sort(["foundation", "year"]))


def shortlist_ref_atoms(con, shortlisted_refs: list[int], excluded_lenses: list[str],
                        atom_types: list[str]) -> pl.DataFrame:
    """(ref, atom_id) of the own-contribution atoms of every shortlisted reference."""
    excluded = ", ".join(f"'{lens}'" for lens in excluded_lenses) or "''"
    con.register("sl_refs", pl.DataFrame({"ref": shortlisted_refs}))
    return con.sql(f"""
        SELECT a.pid AS ref, a.atom_id FROM atoms a JOIN sl_refs r ON r.ref = a.pid
        WHERE a.run_rank = 1 AND coalesce(a.lens, '') NOT IN ({excluded})
          AND a.type IN ({", ".join(f"'{t}'" for t in atom_types)})
    """).pl()


def rescore_with_embeddings(selected: pl.DataFrame, ref_atoms: pl.DataFrame, index: dict[str, int],
                            vectors: np.ndarray) -> pl.DataFrame:
    """Re-rank each critique's proxy shortlist with real atom vectors.

    Same rule as `attribute`: s_r = max cosine over r's atoms; best vs runner-up within the shortlist.
    Shortlisting means a reference the proxy ranked outside the top k can never win (recall cost)."""
    rows_by_ref = {int(r): np.array([index[a] for a in g["atom_id"]]) for (r,), g in ref_atoms.group_by(["ref"])}
    out = {k: [] for k in ["citer", "atom_id", "best_ref", "s1", "second_ref", "s2", "n_shortlist"]}
    for citer, atom_id, shortlist in selected.select(["citer", "atom_id", "shortlist"]).iter_rows():
        refs = [r for r in shortlist if r in rows_by_ref]
        if len(refs) < 2:
            continue
        c = vectors[index[atom_id]].astype(np.float32)
        s = np.array([(vectors[rows_by_ref[r]].astype(np.float32) @ c).max() for r in refs])
        o = np.argsort(-s, kind="stable")
        out["citer"].append(citer); out["atom_id"].append(atom_id)
        out["best_ref"].append(refs[o[0]]); out["s1"].append(float(s[o[0]]))
        out["second_ref"].append(refs[o[1]]); out["s2"].append(float(s[o[1]]))
        out["n_shortlist"].append(len(refs))
    return pl.DataFrame(out).with_columns(margin=pl.col("s1") - pl.col("s2"))


def mechanism_atoms(con, pids: list[int]) -> pl.DataFrame:
    con.register("mech_pids", pl.DataFrame({"pid": pids}))
    return con.sql("""
        SELECT a.pid, a.atom_id FROM atoms a JOIN mech_pids USING (pid)
        WHERE a.run_rank = 1 AND a.type = 'mechanism'
    """).pl()


def patch_scores(pairs: pl.DataFrame, mech: pl.DataFrame, index: dict[str, int], vectors: np.ndarray) -> pl.DataFrame:
    """For (citer, foundation) pairs: max cosine between the citer's and the foundation's mechanism
    atoms. High = the citer proposes a variant of the foundation's own mechanism (a patcher)."""
    rows = {int(p): vectors[[index[a] for a in g["atom_id"]]].astype(np.float32) for (p,), g in mech.group_by(["pid"])}
    scores = []
    for citer, foundation in pairs.select(["citer", "foundation"]).iter_rows():
        a, b = rows.get(int(citer)), rows.get(int(foundation))
        scores.append(float((a @ b.T).max()) if a is not None and b is not None else None)
    return pairs.with_columns(patch_score=pl.Series(scores, dtype=pl.Float64))


def rarefied_concentration(kids: np.ndarray, citers: np.ndarray, n: int, reps: int, rng) -> float:
    """Mean share of the top limitation concept among `n` critics drawn without replacement.

    Raw concentration is biased upward for foundations with few critics (5 critics: top share >= 0.2),
    so every foundation is scored at the same number of critics. Each critic counts once per concept."""
    pairs = np.unique(np.column_stack([citers, kids]), axis=0)
    uc = np.unique(pairs[:, 0])
    if len(uc) < n:
        return float("nan")
    by_citer = {c: pairs[pairs[:, 0] == c, 1] for c in uc}
    shares = []
    for _ in range(reps):
        pick = rng.choice(uc, n, replace=False)
        _, counts = np.unique(np.concatenate([by_citer[c] for c in pick]), return_counts=True)
        shares.append(counts.max() / n)
    return float(np.mean(shares))
