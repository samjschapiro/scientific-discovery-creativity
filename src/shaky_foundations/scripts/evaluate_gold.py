"""Can we identify the limitations later papers raise against a foundation? Scored against a gold set.

For each gold foundation, its attributed critiques (scale_foundations hits.parquet) are grouped by
concept (group_layer, c20000) and ranked by distinct critics. Each gold limitation is embedded
(bge-large, plain text, same space as the concept centroids) and compared with the centroids of
the foundation's top groups.

Two scores:
  hit@k        a gold limitation matches one of the top-k groups (cosine >= threshold). The
               threshold is chosen on the calibration split (pilot cracks, judged by hand earlier)
               and applied unchanged to the test split.
  retrieval    threshold-free: for foundation g, rank every foundation's gold limitations by their
               best similarity to g's top-k groups. Is g's own gold ranked first (top-1) / where
               (MRR)? Guards against groups that look like "a limitation" in general.

Outputs: config.yaml, per_foundation.csv (gold, top groups, sims, ranks), review.csv (top groups
with example critiques, for checking matches by hand), scores.csv, summary.txt

    uv run python src/shaky_foundations/scripts/evaluate_gold.py configs/shaky_foundations/evaluate_gold.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "gold_path", "hits_path", "scored_path", "group_layer",
            "top_k", "k_values", "threshold_grid", "model", "device", "examples_per_group"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for p in ["gold_path", "hits_path", "scored_path"]:
        if not Path(config[p]).exists():
            raise FileNotFoundError(f"FATAL: {config[p]} not found")


# Hand verdicts from the pilot (progress.md, 2026-11-21): known limitation within the top 3?
# Adam is excluded (group label matched but its sampled members were generic).
CALIBRATION_VERDICTS = {
    "Attention is All you Need": True, "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift": True,
    "Generative Adversarial Nets": True, "GloVe: Global Vectors for Word Representation": True,
    "Semi-Supervised Classification with Graph Convolutional Networks": True, "Auto-Encoding Variational Bayes": True,
    "Very Deep Convolutional Networks for Large-Scale Image Recognition": True, "Sequence to Sequence Learning with Neural Networks": True,
    "Distributed Representations of Words and Phrases and their Compositionality": True,
    "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks": False,
    "Playing Atari with Deep Reinforcement Learning": False,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config_path)
    validate_config(config)
    out = init_directory(config["output_dir"] + ("_debug" if args.debug else ""), overwrite=args.overwrite)
    shutil.copy(args.config_path, out / "config.yaml")
    K = config["top_k"]

    gold = pl.DataFrame([{**g, "limitations": g.get("limitations", []), "seen": g.get("seen", False),
                          "skip": g.get("skip"), "confidence": g.get("confidence")}
                         for g in load_config(config["gold_path"])["foundations"]])
    scored = pl.read_csv(config["scored_path"]).select("pid", "title", "n_critics")
    gold = gold.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).join(
        scored.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).drop("title"), on="t", how="left")
    missing = gold.filter(pl.col("pid").is_null() & pl.col("skip").is_null())
    if missing.height:
        raise ValueError(f"FATAL: gold foundations not in the scored set: {missing['title'].to_list()}")
    evald = gold.filter(pl.col("skip").is_null())

    hits = pl.read_parquet(config["hits_path"])
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    labels = dict(con.sql(f"SELECT concept_id, label FROM concepts_{config['group_layer']}").fetchall())
    cent = np.load(Path(config["lacuna_dir"]) / f"centroids_{config['group_layer']}.npy").astype(np.float32)

    # Top-K groups per foundation (distinct critics), with example critiques.
    groups = {}
    review = []
    for pid in evald["pid"].to_list():
        h = hits.filter(pl.col("foundation") == pid)
        g = (h.group_by("gid").agg(n=pl.col("citer").n_unique(), ex=pl.col("text").head(config["examples_per_group"]))
             .sort(["n", "gid"], descending=[True, False]).head(K))
        groups[pid] = g
        for rank, (gid, n, ex) in enumerate(g.iter_rows(), 1):
            review.append({"pid": pid, "rank": rank, "n_critics": n, "group_label": labels[gid],
                           "examples": " || ".join(e[:200] for e in ex)})

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(config["model"], device=config["device"])
    gl = evald.select("pid", "limitations").explode("limitations")
    gvec = model.encode(gl["limitations"].to_list(), normalize_embeddings=True).astype(np.float32)
    gl = gl.with_row_index("i")

    # sims[pid_g][pid_f] = best similarity between any of f's gold limitations and g's top-k groups, per k
    pids = evald["pid"].to_list()
    best_rank_sim = {}   # (pid) -> list over gold limitations of array over group ranks
    for pid in pids:
        g = groups[pid]
        gv = cent[g["gid"].to_numpy()] if g.height else np.empty((0, cent.shape[1]), dtype=np.float32)
        own = gl.filter(pl.col("pid") == pid)
        best_rank_sim[pid] = gvec[own["i"].to_numpy()] @ gv.T  # [n_gold, n_groups]

    def hit_at(pid, k, th):
        s = best_rank_sim[pid][:, :k]
        return bool(s.size and (s >= th).any())

    # Threshold from the calibration split: best agreement with the hand verdicts at k = 3.
    cal = evald.filter(pl.col("split") == "calibration")
    cal_pids = {r["pid"]: CALIBRATION_VERDICTS[r["title"]] for r in cal.iter_rows(named=True) if r["title"] in CALIBRATION_VERDICTS}
    agree = {th: np.mean([hit_at(p, 3, th) == v for p, v in cal_pids.items()]) for th in config["threshold_grid"]}
    th = max(agree, key=lambda t: (agree[t], t))  # ties -> stricter threshold

    # Retrieval: foundation g's top-k groups vs every foundation's gold limitations.
    def retrieval(pool, k):
        rr, top1 = [], []
        for g in pool:
            gg = groups[g]
            if gg.height == 0:
                rr.append(0.0); top1.append(False); continue
            gv = cent[gg["gid"].to_numpy()[:k]]
            scores = {f: float((gvec[gl.filter(pl.col("pid") == f)["i"].to_numpy()] @ gv.T).max()) for f in pool}
            rank = 1 + sum(v > scores[g] for v in scores.values())
            rr.append(1 / rank); top1.append(rank == 1)
        return float(np.mean(top1)), float(np.mean(rr))

    rows, per = [], []
    for split in ["calibration", "test"]:
        for subset in (["all", "unseen"] if split == "test" else ["all"]):
            pool_df = evald.filter((pl.col("split") == split) & ((pl.lit(subset == "all")) | ~pl.col("seen")))
            pool = pool_df["pid"].to_list()
            row = {"split": split, "subset": subset, "n": len(pool), "threshold": th}
            for k in config["k_values"]:
                row[f"hit@{k}"] = float(np.mean([hit_at(p, k, th) for p in pool]))
                row[f"retrieval_top1@{k}"], row[f"retrieval_mrr@{k}"] = retrieval(pool, k)
            rows.append(row)
    scores = pl.DataFrame(rows)
    scores.write_csv(out / "scores.csv")

    for r in evald.iter_rows(named=True):
        s = best_rank_sim[r["pid"]]
        first = next((k for k in range(1, s.shape[1] + 1) if (s[:, :k] >= th).any()), None) if s.size else None
        per.append({"split": r["split"], "title": r["title"], "seen": r["seen"], "confidence": r["confidence"],
                    "n_critics": r["n_critics"], "first_hit_rank": first,
                    "best_sim_top3": float(s[:, :3].max()) if s.size else None,
                    "gold": " | ".join(r["limitations"]),
                    "top_groups": " || ".join(f"{n}: {labels[gid][:60]}" for gid, n, _ in groups[r["pid"]].iter_rows())})
    pl.DataFrame(per).write_csv(out / "per_foundation.csv")
    pl.DataFrame(review).join(evald.select("pid", "title", "split"), on="pid").write_csv(out / "review.csv")

    summary = (f"gold foundations: {gold.height} ({gold['skip'].is_not_null().sum()} skipped); evaluated: {evald.height}\n"
               f"threshold {th} chosen on calibration (agreement with hand verdicts at k=3: {agree[th]:.2f}; grid: "
               + ", ".join(f"{t}:{a:.2f}" for t, a in agree.items()) + ")\n")
    (out / "summary.txt").write_text(summary)
    with pl.Config(tbl_rows=60, tbl_width_chars=240, fmt_str_lengths=70, float_precision=2):
        print(summary)
        print(scores)
        print(pl.DataFrame(per).select("split", "title", "seen", "n_critics", "first_hit_rank", "best_sim_top3"))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
