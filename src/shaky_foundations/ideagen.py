"""Retrospective idea-generation benchmark: briefing cards, ground truth, candidate pools, scoring.

A target is a foundation, its identified limitation and a cutoff year T. The generator sees a briefing card
built only from literature up to and including T. Its ideas are scored by how well they retrieve the fixes
that actually appeared after T from a pool of other papers that cite the foundation after T:

  sim(idea, paper)   max cosine between the idea and the paper's mechanism atoms (bge-large, same space), after
                     projecting the limitation's own direction out of both (restating the problem scores nothing)
  fix_rank           rank of the best true fix among all candidate papers (1 = the closest paper is a fix)
  hit@k, mrr         from fix_rank
  auc                P(a random true fix is closer to the idea than a random non-fix); chance = 0.5 whatever the
                     number of fixes (the main score: fix_rank is easy when a target has many fixes)
  prior_overlap      max cosine to mechanism atoms of papers citing the foundation by T (was the idea already
                     in the literature?)

Candidates = true fixes + hard negatives (post-T papers raising the same limitation, not labelled fixes) + random
post-T citers. Unlabelled fixes among them make scores conservative.
"""

import numpy as np
import polars as pl

from src.shaky_foundations.embeddings import embed_texts, ensure_embedded, load_vectors


def find_pid(con, title: str) -> tuple[int, int]:
    r = con.execute("""SELECT pid, year FROM papers WHERE lower(trim(title)) = lower(trim(?)) AND pid = canonical_pid
                       ORDER BY cites_lacuna_2025 DESC NULLS LAST LIMIT 1""", [title]).fetchall()
    if not r:
        raise ValueError(f"FATAL: paper not found in Lacuna: {title}")
    return int(r[0][0]), int(r[0][1])


def atoms_of(con, pids: list[int], types: list[str]) -> pl.DataFrame:
    con.register("ig_pids", pl.DataFrame({"pid": pids}))
    tl = ", ".join(f"'{t}'" for t in types)
    return con.sql(f"""SELECT a.pid, p.year, p.title, a.atom_id, a.type, a.text, a.c200000 AS cid
                       FROM atoms a JOIN ig_pids USING (pid) JOIN papers p USING (pid)
                       WHERE a.run_rank = 1 AND a.type IN ({tl})""").pl()


def citers(con, foundation: int, y0: int, y1: int) -> list[int]:
    return [r[0] for r in con.execute("""SELECT DISTINCT citing_pid FROM citations
                                         WHERE cited_pid = ? AND citing_year BETWEEN ? AND ?""",
                                      [foundation, y0, y1]).fetchall()]


def rank_by_text(atoms: pl.DataFrame, query_vec: np.ndarray, centroids: np.ndarray) -> pl.DataFrame:
    """Atoms ranked by cosine of their concept centroid (c200000 proxy) to a query vector."""
    a = atoms.drop_nulls("cid")
    sims = centroids[a["cid"].to_numpy()].astype(np.float32) @ query_vec
    return a.with_columns(sim=pl.Series(sims)).sort("sim", descending=True)


def build_card(con, target: dict, hits: pl.DataFrame, centroids: np.ndarray, emb: dict, n_examples: int) -> dict:
    """Everything the generator may see: literature up to and including T only."""
    T = target["cutoff_year"]
    f_pid, f_year = find_pid(con, target["foundation"])
    lim_vec = embed_texts([target["limitation"]], emb["model"], emb["device"])[0]

    f_atoms = atoms_of(con, [f_pid], ["mechanism", "principle"])
    crit = hits.filter((pl.col("foundation") == f_pid) & (pl.col("year") <= T))
    crit_atoms = atoms_of(con, crit["citer"].unique().to_list(), ["limitation"]).join(
        crit.select(pl.col("atom_id")), on="atom_id", how="inner")
    top_crit = rank_by_text(crit_atoms, lim_vec, centroids).unique("pid", keep="first", maintain_order=True).head(n_examples)

    tried_pids = [find_pid(con, t)[0] for t in target["tried_by_T"]]
    pre_citers = citers(con, f_pid, f_year, T)
    tried_atoms = atoms_of(con, tried_pids + pre_citers, ["mechanism"])
    tried = rank_by_text(tried_atoms, lim_vec, centroids)
    named = tried.filter(pl.col("pid").is_in(tried_pids)).unique("pid", keep="first", maintain_order=True)
    others = tried.filter(~pl.col("pid").is_in(tried_pids)).unique("pid", keep="first", maintain_order=True)
    tried = pl.concat([named, others.head(max(n_examples - named.height, 0))])
    return {
        "id": target["id"], "cutoff_year": T,
        "foundation_title": target["foundation"], "foundation_year": f_year,
        "foundation_mechanisms": f_atoms["text"].head(6).to_list(),
        "limitation": target["limitation"],
        "n_critics_by_T": int(crit["citer"].n_unique()),
        "example_critiques": top_crit["text"].to_list(),
        "already_tried": [{"year": r["year"], "text": r["text"]} for r in tried.iter_rows(named=True)],
    }


def candidate_pool(con, target: dict, solver_pids: list[int], n_distractors: int, seed: int,
                   hits: pl.DataFrame | None = None, n_hard: int = 0, centroids: np.ndarray | None = None,
                   emb: dict | None = None) -> pl.DataFrame:
    """Ground-truth fixes (after T) + hard negatives + random distractors.

    Hard negatives: papers after T whose critique of the foundation is closest to the limitation, minus the
    labelled fixes. They name the same problem, so a match must be to the fix, not the topic. For targets
    without hand-labelled solvers they may include unlabelled fixes (conservative)."""
    T = target["cutoff_year"]
    f_pid, _ = find_pid(con, target["foundation"])
    fixes = [find_pid(con, t) for t in target["fixes_after"]]
    bad = [t for t, (p, y) in zip(target["fixes_after"], fixes) if y <= T]
    if bad:
        raise ValueError(f"FATAL: {target['id']}: fixes published by T: {bad}")
    fix_pids = sorted({p for p, _ in fixes} | set(solver_pids))
    hard = []
    if n_hard and hits is not None:
        crit = hits.filter((pl.col("foundation") == f_pid) & (pl.col("year") > T) & ~pl.col("citer").is_in(fix_pids))
        if crit.height:
            lim_vec = embed_texts([target["limitation"]], emb["model"], emb["device"])[0]
            ca = atoms_of(con, crit["citer"].unique().to_list(), ["limitation"]).join(crit.select("atom_id"), on="atom_id")
            hard = rank_by_text(ca, lim_vec, centroids).unique("pid", keep="first", maintain_order=True).head(n_hard)["pid"].to_list()
    post = [p for p in citers(con, f_pid, T + 1, 2025) if p not in set(fix_pids) | set(hard)]
    rng = np.random.default_rng(seed)
    distract = rng.choice(post, size=min(n_distractors, len(post)), replace=False).tolist() if post else []
    a = atoms_of(con, fix_pids + hard + distract, ["mechanism"])
    return a.with_columns(is_fix=pl.col("pid").is_in(fix_pids), is_hard=pl.col("pid").is_in(hard))


def _remove_direction(x: np.ndarray, d: np.ndarray | None) -> np.ndarray:
    """Project unit vector d out of each row and renormalise (d = None: unchanged)."""
    if d is None:
        return x
    r = x - np.outer(x @ d, d)
    return r / np.linalg.norm(r, axis=1, keepdims=True)


def score_ideas(ideas: list[str], pool: pl.DataFrame, prior: pl.DataFrame, emb: dict,
                limitation: str | None = None) -> pl.DataFrame:
    """One row per idea: fix_rank, hit@1/5/10, reciprocal rank, best fix similarity, prior overlap.

    With `limitation`, its embedding direction is projected out of ideas and atoms before comparing, so restating
    the problem earns nothing: fix papers describe their mechanisms in the problem's vocabulary."""
    ids = pool["atom_id"].to_list() + prior["atom_id"].to_list()
    index, vec = load_vectors(emb["cache_dir"], ids)
    d = embed_texts([limitation], emb["model"], emb["device"])[0] if limitation else None
    idea_vec = _remove_direction(embed_texts(ideas, emb["model"], emb["device"]), d)
    pv = _remove_direction(vec[[index[a] for a in pool["atom_id"]]].astype(np.float32), d)
    sims = idea_vec @ pv.T                                   # ideas x pool atoms
    paper = pool["pid"].to_numpy()
    papers, inv = np.unique(paper, return_inverse=True)
    per_paper = np.full((len(ideas), len(papers)), -1.0, dtype=np.float32)
    for j in range(len(papers)):
        per_paper[:, j] = sims[:, inv == j].max(axis=1)
    is_fix = np.array([bool(pool.filter(pl.col("pid") == p)["is_fix"][0]) for p in papers])
    prv = (_remove_direction(vec[[index[a] for a in prior["atom_id"]]].astype(np.float32), d) if prior.height
           else np.zeros((1, idea_vec.shape[1]), np.float32))
    rows = []
    for i, idea in enumerate(ideas):
        order = np.argsort(-per_paper[i])
        rank = int(np.flatnonzero(is_fix[order])[0]) + 1
        r = np.argsort(np.argsort(per_paper[i])) + 1                       # ranks, ascending similarity
        n1, n0 = int(is_fix.sum()), int((~is_fix).sum())
        auc = float((r[is_fix].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))     # P(fix closer than a non-fix); chance 0.5
        rows.append({"idea": idea, "fix_rank": rank, "auc": auc, "n_candidates": len(papers), "n_fixes": n1,
                     "hit1": rank <= 1, "hit5": rank <= 5, "hit10": rank <= 10, "rr": 1.0 / rank,
                     "best_fix_sim": float(per_paper[i][is_fix].max()),
                     "prior_overlap": float((prv @ idea_vec[i]).max())})
    return pl.DataFrame(rows)


def prepare_vectors(con, pool: pl.DataFrame, prior: pl.DataFrame, emb: dict) -> None:
    ensure_embedded(con, pool["atom_id"].to_list() + prior["atom_id"].to_list(), emb["cache_dir"], emb["model"],
                    emb["device"])
