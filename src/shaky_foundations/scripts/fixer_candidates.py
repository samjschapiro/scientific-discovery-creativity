"""Candidate "fixers" of foundation limitations, batched for labelling by Claude subagents.

Do papers that address a foundation's limitation end up more impactful? Step 1: find them. For every gold
foundation (gold_limitations.yaml, not skipped) and each of its gold limitations, every paper citing the
foundation (foundation year + 1 .. citer_year_max) is scored by how close the problem it states is to the
limitation: max cosine between the limitation (bge-large) and the c200000 concept centroid of the citer's
problem / limitation atoms in the problems_and_motivation lens, then the best `shortlist_atoms` of those are
re-scored with their real bge-large vectors (the proxy ties whole concepts). Unlike critique attribution, the citer need not
blame the foundation, so fixes like ResNet or Linformer are reachable. The top_k citers per limitation become
candidates; a judge decides whether each proposes its own fix.

Validation items: hand-judged critics (limitation_timelines_camera_v1/critics.csv, solvers in
limitation_timelines_camera.yaml) on lines that map to a gold limitation are added with their hand label, so the
judge's labels can be scored. The judge does not see which items are validation items.

Outputs: candidates.parquet (all, with val_label), batches/batch_NN.jsonl (what a judge sees), judge_prompt.md,
summary.txt.

    uv run python src/shaky_foundations/scripts/fixer_candidates.py configs/shaky_foundations/fixer_candidates.yaml
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.embeddings import embed_texts, ensure_embedded, load_vectors
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "gold_path", "scored_path", "citer_year_max", "top_k",
            "problem_types", "problem_lens", "shortlist_atoms", "n_batches", "validation", "seed", "embedding"]

JUDGE_PROMPT = """# Task: does this paper propose a fix for the foundation's limitation?

Each line of the batch file is one item: a foundation paper, one known limitation of it, and a later paper that
cites the foundation (title, year, the problems it says it tackles, its own methods). Decide, from this text only,
which label fits the CITING paper best:

- fix          the paper proposes its OWN new method, architecture, objective or algorithm that (at least
               partially) addresses THIS limitation (or this limitation in a successor of the foundation).
- applies_fix  the paper addresses the limitation only by using an existing, named fix from earlier work.
- mentions     the paper states the limitation (or a close problem) but its contribution does not address it:
               an analysis, benchmark, survey, an application, or a fix for a different problem.
- unrelated    the paper's problems have nothing to do with this limitation.

Rules: judge the limitation as stated, not the foundation in general. A partial or domain-specific fix still
counts as fix. Be strict on "own method": a contribution that only measures or documents the problem is
mentions. Do not use outside knowledge about what later became famous; judge the text.

Output: one JSON object per item, one per line, keys "cand_id" (copied exactly), "label" (one of the four) and
"reason" (at most 15 words). Every item must get exactly one line.
"""


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for p in ["gold_path", "scored_path"]:
        if not Path(config[p]).exists():
            raise FileNotFoundError(f"FATAL: {p} not found: {config[p]}")


def gold_lines(config: dict) -> pl.DataFrame:
    """One row per (gold foundation, gold limitation), with the foundation's pid and year."""
    gold = load_config(config["gold_path"])["foundations"]
    rows = [{"title": g["title"], "lim_idx": i, "limitation": lim}
            for g in gold if not g.get("skip") for i, lim in enumerate(g.get("limitations", []))]
    scored = pl.read_csv(config["scored_path"]).select("pid", "title", "year")
    df = pl.DataFrame(rows).with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).join(
        scored.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).drop("title"), on="t", how="left")
    missing = df.filter(pl.col("pid").is_null())["title"].unique().to_list()
    if missing:
        raise ValueError(f"FATAL: gold foundations not in the scored set: {missing}")
    return df.drop("t").rename({"pid": "foundation", "year": "foundation_year"})


def citer_atoms(con, foundation: int, y0: int, y1: int, types: list[str], lens: str) -> pl.DataFrame:
    tl = ", ".join(f"'{t}'" for t in types)
    return con.sql(f"""
        SELECT a.pid AS citer, a.atom_id, a.text, a.c200000 AS cid
        FROM (SELECT DISTINCT citing_pid FROM citations
              WHERE cited_pid = {int(foundation)} AND citing_year BETWEEN {int(y0)} AND {int(y1)}) c
        JOIN atoms a ON a.pid = c.citing_pid
        WHERE a.run_rank = 1 AND a.type IN ({tl}) AND a.lens = '{lens}' AND a.c200000 IS NOT NULL
    """).pl()


def describe(con, pids: list[int]) -> pl.DataFrame:
    """Title, year and up to 4 own-method atoms per paper."""
    con.register("fc_pids", pl.DataFrame({"pid": pids}))
    papers = con.sql("SELECT pid, title, year FROM papers JOIN fc_pids USING (pid)").pl()
    mech = con.sql("""SELECT pid, list(text ORDER BY atom_id)[1:4] AS methods FROM atoms JOIN fc_pids USING (pid)
                      WHERE run_rank = 1 AND type = 'mechanism' GROUP BY pid""").pl()
    return papers.join(mech, on="pid", how="left").rename({"pid": "citer"})


def validation_items(config: dict, lines: pl.DataFrame) -> pl.DataFrame:
    """Hand-judged critics on lines that map to a gold limitation: (foundation title, lim_idx, citer, val_label)."""
    v = config["validation"]
    critics = pl.read_csv(v["critics_path"])
    camera = {e["short"]: e for e in load_config(v["camera_config"])["examples"]}
    rows = []
    for m in v["line_map"]:
        ex = camera[m["short"]]
        lim = next(l for l in ex["limitations"] if l["label"] == m["label"])
        solvers = set(lim["solvers"])
        for c in critics.filter((pl.col("foundation") == m["short"]) & (pl.col("limitation") == m["label"]))["citer"]:
            rows.append({"title": ex["title"], "lim_idx": m["lim_idx"], "citer": int(c),
                         "val_label": "fix" if c in solvers else "not_fix"})
    out = pl.DataFrame(rows).unique(["title", "lim_idx", "citer"])
    # a paper that is a solver on any mapped line of the same gold limitation counts as fix
    return out.group_by("title", "lim_idx", "citer").agg(
        pl.when((pl.col("val_label") == "fix").any()).then(pl.lit("fix")).otherwise(pl.lit("not_fix")).first().alias("val_label"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    validate_config(config)
    if args.debug:
        config["output_dir"] = config["output_dir"].rstrip("/") + "_debug"
    out = init_directory(config["output_dir"], overwrite=args.overwrite)
    shutil.copy(args.config, out / "config.yaml")

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    centroids = np.load(Path(config["lacuna_dir"]) / "centroids_c200000.npy")
    lines = gold_lines(config)
    if args.debug:
        lines = lines.head(3)
    emb = config["embedding"]
    lim_vecs = embed_texts(lines["limitation"].to_list(), emb["model"], emb["device"])

    val = validation_items(config, lines)   # hand-judged citers: their atoms are always re-scored
    cands, stats = [], []
    for i, r in enumerate(lines.iter_rows(named=True)):
        a = citer_atoms(con, r["foundation"], r["foundation_year"] + 1, config["citer_year_max"],
                        config["problem_types"], config["problem_lens"])
        if a.height == 0:
            stats.append({**r, "n_citers_with_problems": 0})
            continue
        a = a.with_columns(proxy=pl.Series(centroids[a["cid"].to_numpy()].astype(np.float32) @ lim_vecs[i]))
        keep = set(val.filter((pl.col("title") == r["title"]) & (pl.col("lim_idx") == r["lim_idx"]))["citer"].to_list())
        a = a.sort("proxy", descending=True).with_row_index("pr").filter(
            (pl.col("pr") < config["shortlist_atoms"]) | pl.col("citer").is_in(keep)).drop("pr")
        ensure_embedded(con, a["atom_id"].to_list(), emb["cache_dir"], emb["model"], emb["device"])
        index, vec = load_vectors(emb["cache_dir"], a["atom_id"].to_list())
        sims = vec[[index[x] for x in a["atom_id"]]].astype(np.float32) @ lim_vecs[i]
        a = a.with_columns(sim=pl.Series(sims)).sort("sim", descending=True)
        per = a.group_by("citer", maintain_order=True).agg(
            pl.col("sim").first().alias("problem_sim"), pl.col("text").head(2).alias("problems"))
        per = per.with_columns(sim_rank=pl.int_range(1, per.height + 1))   # ranks past the shortlist are not exact
        stats.append({**r, "n_citers_with_problems": per.height})
        cands.append(per.with_columns(title=pl.lit(r["title"]), lim_idx=pl.lit(r["lim_idx"]),
                                      foundation=pl.lit(r["foundation"]), limitation=pl.lit(r["limitation"])))
        print(f"  {i + 1}/{lines.height} {r['title'][:50]} [{r['lim_idx']}]: {per.height:,} citers", flush=True)
    allc = pl.concat(cands)

    top = allc.filter(pl.col("sim_rank") <= config["top_k"]).with_columns(source=pl.lit("top_k"))
    val = val.join(allc, on=["title", "lim_idx", "citer"], how="left")
    no_problem = val.filter(pl.col("problem_sim").is_null()).height
    val = val.filter(pl.col("problem_sim").is_not_null())
    sel = pl.concat([top.join(val.select("title", "lim_idx", "citer", "val_label"), on=["title", "lim_idx", "citer"], how="left"),
                     val.join(top.select("title", "lim_idx", "citer"), on=["title", "lim_idx", "citer"], how="anti")
                        .with_columns(source=pl.lit("validation"))], how="diagonal_relaxed")
    desc = describe(con, sel["citer"].unique().to_list())
    sel = sel.drop("title").join(lines.select("foundation", pl.col("title").alias("foundation_title")).unique(),
                                 on="foundation").join(desc, on="citer", how="left")
    rng = np.random.default_rng(config["seed"])
    sel = sel.with_columns(cand_id=pl.Series([f"c{n:05d}" for n in rng.permutation(sel.height)])).sort("cand_id")
    sel.write_parquet(out / "candidates.parquet")

    bdir = out / "batches"
    bdir.mkdir()
    n_b = config["n_batches"]
    for b in range(n_b):
        part = sel.slice(b * -(-sel.height // n_b), -(-sel.height // n_b))
        with open(bdir / f"batch_{b:02d}.jsonl", "w") as f:
            for r in part.iter_rows(named=True):
                f.write(json.dumps({"cand_id": r["cand_id"], "foundation": r["foundation_title"],
                                    "limitation": r["limitation"], "paper_title": r["title"], "paper_year": r["year"],
                                    "problems_it_states": r["problems"], "its_methods": r["methods"] or []}) + "\n")
    (out / "judge_prompt.md").write_text(JUDGE_PROMPT)

    st = pl.DataFrame(stats)
    st.drop("limitation").write_csv(out / "lines.csv")
    summary = [f"gold lines: {lines.height} ({lines['title'].n_unique()} foundations)",
               f"citers with problem atoms per line: median {st['n_citers_with_problems'].median():.0f}",
               f"candidates: {sel.height} (top_k {config['top_k']}: {top.height}; extra validation: "
               f"{sel.filter(pl.col('source') == 'validation').height})",
               f"validation items: {sel['val_label'].is_not_null().sum()} "
               f"(fix {(sel['val_label'] == 'fix').sum()}, not_fix {(sel['val_label'] == 'not_fix').sum()}); "
               f"{no_problem} hand-judged critics dropped (published after citer_year_max or no problem atoms)",
               f"batches: {n_b} x ~{-(-sel.height // n_b)}"]
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
