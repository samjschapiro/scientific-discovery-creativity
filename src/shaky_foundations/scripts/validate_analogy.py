"""Does the analogy score pick up papers that *say* they borrowed a method from elsewhere?

Cue phrases ("inspired by", "originally developed for", "adapts techniques from", ...) in a paper's
own mechanism/principle/finding atoms mark self-described analogical transfer. Four checks:

  cue_samples.csv      random cue hits per cue, for reading by hand (is the cue itself precise?)
  paper_auc.csv        cue papers vs other papers, AUC of each score on within-year ranks, raw and
                       after regressing out covariates (more atoms = more chances to hit a cue).
                       Discriminant check: analogy should beat DSI / problem-mechanism distance,
                       which measure association, not transfer.
  within_paper.csv     inside papers with both, is a cue-bearing *mechanism atom* scored higher
                       than the paper's other mechanism atoms? (P(cue atom > other), ties half.)
                       Holds every paper-level confound fixed.
  per_cue_auc.csv      paper-level AUC per cue, so one cue cannot carry the result alone.

    uv run python src/shaky_foundations/scripts/validate_analogy.py configs/shaky_foundations/validate_analogy.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.analogy import VARIANTS
from src.shaky_foundations.data import open_lacuna
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "measures_path", "analogy_dir", "cue_atom_types",
            "cues", "scores", "covariates", "precision_sample_per_cue", "bootstrap_n", "seed"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for p in [config["measures_path"], Path(config["analogy_dir"]) / "analogy.parquet"]:
        if not Path(p).exists():
            raise FileNotFoundError(f"FATAL: {p} not found; run build_measures / build_analogy first")


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = pl.Series(np.concatenate([pos, neg])).rank("average").to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def auc_ci(pos, neg, rng, n_boot) -> tuple[float, float, float]:
    boots = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(n_boot)]
    return auc(pos, neg), float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))


def year_pct(df: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    return df.with_columns([((pl.col(c).rank("average").over("year") - 0.5) / pl.col(c).count().over("year")).alias(c)
                            for c in cols])


def residualize(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return y - x @ beta


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
    rng = np.random.default_rng(config["seed"])
    cues, scores, covs = config["cues"], config["scores"], config["covariates"]

    measures = pl.read_parquet(config["measures_path"], columns=["pid", "year", "dsi", "pm_distance",
                                                                  "novel_pair_frac", "n_atoms_used"])
    if args.debug:
        measures = measures.sample(n=5000, seed=config["seed"])
    papers = measures.join(pl.read_parquet(Path(config["analogy_dir"]) / "analogy.parquet"), on="pid", how="inner")

    # Cue flags per atom (only the paper's own contribution atoms).
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    con.register("focal_df", papers.select("pid"))
    types = ", ".join(f"'{t}'" for t in config["cue_atom_types"])
    flags = ", ".join(f"regexp_matches(lower(a.text), '{rx}') AS cue_{name}" for name, rx in cues.items())
    cue_atoms = con.sql(f"""
        SELECT a.pid, a.atom_id, a.type, a.text, {flags}
        FROM atoms a JOIN focal_df USING (pid)
        WHERE a.run_rank = 1 AND a.type IN ({types})
    """).pl()
    cue_cols = [f"cue_{n}" for n in cues]
    cue_atoms = cue_atoms.with_columns(cue_any=pl.any_horizontal(cue_cols))

    # 1. Precision samples for hand reading.
    pl.concat([cue_atoms.filter(pl.col(c)).sample(n=min(config["precision_sample_per_cue"], cue_atoms[c].sum()),
                                                  seed=config["seed"]).select(pl.lit(c).alias("cue"), "pid", "type", "text")
               for c in cue_cols]).write_csv(out / "cue_samples.csv")

    # 2. Paper-level AUC, raw and covariate-adjusted.
    per_paper = cue_atoms.group_by("pid").agg(*[pl.col(c).any() for c in cue_cols + ["cue_any"]])
    df = papers.join(per_paper, on="pid", how="left").with_columns(
        [pl.col(c).fill_null(False) for c in cue_cols + ["cue_any"]])
    rows, lines = [], []
    for s in scores:
        d = year_pct(df.drop_nulls([s] + covs), [s])
        y = d["cue_any"].to_numpy()
        raw = d[s].to_numpy()
        adj = residualize(raw, d.select(covs).to_numpy())
        for kind, v in [("raw", raw), ("adjusted", adj)]:
            a, lo, hi = auc_ci(v[y], v[~y], rng, config["bootstrap_n"])
            rows.append({"score": s, "kind": kind, "n_cue": int(y.sum()), "n_other": int((~y).sum()),
                         "auc": a, "ci_lo": lo, "ci_hi": hi})
    paper_auc = pl.DataFrame(rows)
    paper_auc.write_csv(out / "paper_auc.csv")

    # 3. Within-paper: cue-bearing mechanism atoms vs the same paper's other mechanism atoms.
    atoms = pl.read_parquet(Path(config["analogy_dir"]) / "analogy_atoms.parquet").join(
        cue_atoms.filter(pl.col("type") == "mechanism").select(["atom_id", "cue_any"] + cue_cols),
        on="atom_id", how="left").with_columns(pl.col("cue_any").fill_null(False))
    wrows = []
    for v in VARIANTS:
        a = atoms.drop_nulls(v)
        both = a.group_by("pid").agg(pl.col("cue_any").any().alias("has"), (~pl.col("cue_any")).any().alias("has_not")) \
                .filter(pl.col("has") & pl.col("has_not"))["pid"]
        a = a.filter(pl.col("pid").is_in(both.implode()))
        # Per paper: P(cue atom > non-cue atom), ties half; then average over papers.
        per = []
        for (_,), g in a.group_by(["pid"]):
            c, o = g.filter(pl.col("cue_any"))[v].to_numpy(), g.filter(~pl.col("cue_any"))[v].to_numpy()
            per.append(((c[:, None] > o[None, :]).mean() + 0.5 * (c[:, None] == o[None, :]).mean()))
        per = np.array(per)
        boots = [rng.choice(per, len(per)).mean() for _ in range(config["bootstrap_n"])]
        wrows.append({"variant": v, "n_papers": len(per), "p_cue_higher": float(per.mean()),
                      "ci_lo": float(np.quantile(boots, 0.025)), "ci_hi": float(np.quantile(boots, 0.975))})
    pl.DataFrame(wrows).write_csv(out / "within_paper.csv")

    # 4. Per-cue paper-level AUC (adjusted) for every score.
    crows = []
    for s in scores:
        d = year_pct(df.drop_nulls([s] + covs), [s])
        adj = residualize(d[s].to_numpy(), d.select(covs).to_numpy())
        neg = adj[~d["cue_any"].to_numpy()]
        for c in cue_cols:
            pos = adj[d[c].to_numpy()]
            if len(pos) >= 30:
                crows.append({"score": s, "cue": c, "n_cue": len(pos), "auc_adjusted": auc(pos, neg)})
    pl.DataFrame(crows).write_csv(out / "per_cue_auc.csv")

    n_cue = int(df["cue_any"].sum())
    (out / "summary.txt").write_text(
        f"papers: {df.height:,}; with any cue: {n_cue:,} ({n_cue / df.height:.1%})\n"
        + "\n".join(f"  {c}: {int(df[c].sum()):,}" for c in cue_cols) + "\n")
    with pl.Config(tbl_rows=60, tbl_width_chars=200):
        print((out / "summary.txt").read_text())
        print(paper_auc)
        print(pl.read_csv(out / "within_paper.csv"))
        print(pl.DataFrame(crows).filter(pl.col("score").is_in(["analogy_nnk_max", "analogy_wmean_max", "dsi"]))
              .pivot(on="score", index="cue", values="auc_adjusted"))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
