"""Build the retrospective idea-generation benchmark and validate its scoring before any LLM call.

Per target (configs/shaky_foundations/ideagen_targets.yaml):
  cards.json         briefing card as of the cutoff year T (all the generator may see)
  pools.parquet      candidate papers after T: true fixes + random distractors (mechanism atoms)
  prior.parquet      mechanism atoms of papers citing the foundation by T (for prior_overlap)
  controls.csv       scoring controls: the reference idea (true fix in plain words; should rank a fix near the
                     top), the limitation restated (naming the problem must not score as solving it), random
                     unrelated mechanisms (should land near chance)
  summary.txt

    uv run python src/shaky_foundations/scripts/ideagen_build.py configs/shaky_foundations/ideagen_build.yaml
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
from src.shaky_foundations.ideagen import atoms_of, build_card, candidate_pool, citers, find_pid, prepare_vectors, score_ideas
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "targets_path", "hits_path", "n_examples", "n_distractors",
            "n_prior_papers", "n_negative", "n_hard", "remove_limitation_direction", "seed", "embedding"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")


def solver_pids(target: dict) -> list[int]:
    src = target.get("solvers_from")
    if not src:
        return []
    for ex in load_config(src["config"])["examples"]:
        if ex["short"] == src["foundation"]:
            for lim in ex["limitations"]:
                if lim["label"] == src["limitation"]:
                    return list(lim.get("solvers", []))
    raise ValueError(f"FATAL: {target['id']}: solvers_from not found: {src}")


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
    emb = config["embedding"]
    rng = np.random.default_rng(config["seed"])

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    targets = load_config(config["targets_path"])["targets"]
    if args.debug:
        targets = targets[:2]
    hits = pl.read_parquet(config["hits_path"])
    centroids = np.load(Path(config["lacuna_dir"]) / "centroids_c200000.npy")

    cards, pools, priors, controls = [], [], [], []
    for t in targets:
        card = build_card(con, t, hits, centroids, emb, config["n_examples"])
        cards.append(card)
        T = t["cutoff_year"]
        solvers = [p for p in solver_pids(t)
                   if con.execute("SELECT year FROM papers WHERE pid = ?", [p]).fetchall()[0][0] > T]
        pool = candidate_pool(con, t, solvers, config["n_distractors"], config["seed"], hits=hits, n_hard=config["n_hard"],
                              centroids=centroids, emb=emb).with_columns(target=pl.lit(t["id"]))
        f_pid, f_year = find_pid(con, t["foundation"])
        pre = citers(con, f_pid, f_year, T)
        pre = rng.choice(pre, size=min(config["n_prior_papers"], len(pre)), replace=False).tolist() if pre else []
        prior = atoms_of(con, pre, ["mechanism"]).with_columns(target=pl.lit(t["id"]))
        prepare_vectors(con, pool, prior, emb)

        # Negative control: mechanism atoms of random papers published by T that do not cite the foundation.
        neg = con.sql(f"""SELECT text FROM atoms a JOIN papers p USING (pid)
                          WHERE a.run_rank = 1 AND a.type = 'mechanism' AND p.year <= {int(T)}
                            AND a.pid NOT IN (SELECT citing_pid FROM citations WHERE cited_pid = {int(f_pid)})
                          ORDER BY hash(a.atom_id, {int(config['seed'])}) LIMIT {int(config['n_negative'])}""").pl()["text"].to_list()
        ideas = [("reference idea", t["reference_idea"]), ("limitation restated", t["limitation"])] + \
                [("random mechanism", x) for x in neg]
        sc = score_ideas([x for _, x in ideas], pool, prior, emb,
                         limitation=t["limitation"] if config["remove_limitation_direction"] else None)
        controls.append(sc.with_columns(target=pl.lit(t["id"]), control=pl.Series([k for k, _ in ideas])))
        pools.append(pool)
        priors.append(prior)
        print(f"{t['id']}: {pool.filter('is_fix')['pid'].n_unique()} fixes, {pool.filter('is_hard')['pid'].n_unique()} hard negatives, "
              f"{pool['pid'].n_unique()} candidates, "
              f"{card['n_critics_by_T']} critics by T")

    (out / "cards.json").write_text(json.dumps(cards, indent=2))
    pl.concat(pools).write_parquet(out / "pools.parquet")
    pl.concat(priors).write_parquet(out / "prior.parquet")
    ctrl = pl.concat(controls)
    ctrl.write_csv(out / "controls.csv")
    agg = (ctrl.group_by("control").agg(n=pl.len(), auc=pl.col("auc").mean(), mean_fix_rank=pl.col("fix_rank").mean(), median_fix_rank=pl.col("fix_rank").median(),
                                        hit1=pl.col("hit1").mean(), hit10=pl.col("hit10").mean(), mrr=pl.col("rr").mean(),
                                        best_fix_sim=pl.col("best_fix_sim").mean())
           .sort("mrr", descending=True))
    summary = f"targets: {len(targets)}\n{agg}\n"
    (out / "summary.txt").write_text(summary)
    with pl.Config(tbl_rows=60, tbl_width_chars=200, float_precision=3, fmt_str_lengths=40):
        print(agg)
        print(ctrl.filter(pl.col("control") != "random mechanism").select("target", "control", "auc", "fix_rank", "n_candidates",
                                                                          "n_fixes", "best_fix_sim", "prior_overlap"))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
