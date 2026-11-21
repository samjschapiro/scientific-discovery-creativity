"""How do disruption, F/E/G, gap-opening and atom-based combinatorial measures relate?

Reads measures.parquet from build_measures and writes to output_dir:

  spearman.csv            Spearman matrix (within-year percentile ranks = year-controlled)
  partial_spearman.csv    the same after regressing out covariates (citations, references, #concepts)
  figures/<run>_spearman_heatmap.png (track figures folder) both matrices side by side
  kedrick_auc.csv         AUC of each measure: gap-openers vs each other class (bootstrap 95% CI)
  crosstab_*.csv          dominant F/E/G role x CD / DSI tertiles: the empirical "Figure 1" overlaps
  analysis_n.txt          sample sizes at each filter

Analysis set: papers with Fang F/E/G (i.e. >=5 citations in 5 years, which also keeps CD away from
its small-n noise floor) and non-null CD.

    uv run python src/shaky_foundations/scripts/analyze_relationships.py configs/shaky_foundations/analyze_relationships.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

import matplotlib
import numpy as np
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "measures_path", "measures", "covariates", "bootstrap_n", "seed"]
LABELS = {"cd": "CD₅ disruption", "fang_f": "Foundation", "fang_e": "Extension", "fang_g": "Generalization",
          "dsi": "Atom DSI", "pm_distance": "Problem–mechanism dist.", "novel_pair_frac": "Novel concept pairs",
          "pmi_p10": "Pair PMI p10 (low=atypical)", "log_citers5": "log citations (5y)",
          "log_refs": "log references", "n_unique_concepts": "# distinct concepts"}


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not Path(config["measures_path"]).exists():
        raise FileNotFoundError(f"FATAL: {config['measures_path']} not found; run build_measures first")


def year_percentiles(df: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    """Percentile rank within publication year (average ties): Spearman with year held fixed."""
    return df.with_columns([
        ((pl.col(c).rank("average").over("year") - 0.5) / pl.col(c).count().over("year")).alias(c)
        for c in cols
    ])


def residualize(ranks: np.ndarray, covs: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(covs)), covs])
    beta, *_ = np.linalg.lstsq(x, ranks, rcond=None)
    return ranks - x @ beta


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(random positive > random negative), ties count half (Mann-Whitney U / n1 n2)."""
    allv = np.concatenate([pos, neg])
    r = pl.Series(allv).rank("average").to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def heatmap(mats: list[tuple[str, pl.DataFrame]], cols: list[str], path: Path) -> None:
    cmap = LinearSegmentedColormap.from_list("div", ["#256abf", "#f0efec", "#e34948"])
    fig, axes = plt.subplots(1, len(mats), figsize=(7.2 * len(mats), 6.4), facecolor="#fcfcfb")
    for ax, (title, m) in zip(axes, mats):
        v = m.select(cols).to_numpy()
        shown = v.copy()
        np.fill_diagonal(shown, np.nan)  # r = 1 by construction; leave blank so it doesn't dominate
        cmap.set_bad("#fcfcfb")
        ax.imshow(shown, cmap=cmap, vmin=-0.6, vmax=0.6)
        ax.set_xticks(range(len(cols)), [LABELS[c] for c in cols], rotation=50, ha="right", fontsize=8.5)
        ax.set_yticks(range(len(cols)), [LABELS[c] for c in cols], fontsize=8.5)
        for i in range(len(cols)):
            for j in range(len(cols)):
                if i != j:
                    ax.text(j, i, f"{v[i, j]:.2f}", ha="center", va="center", fontsize=7, color="#1a1a19")
        ax.set_title(title, fontsize=10.5, loc="left", color="#1a1a19")
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


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

    raw = pl.read_parquet(config["measures_path"]).with_columns(
        log_citers5=(pl.col("n_i") + pl.col("n_j") + 1).log(), log_refs=(pl.col("n_refs_total") + 1).log())
    measures, covs = config["measures"], config["covariates"]
    cols = measures + covs

    df = raw.filter(pl.col("in_random_sample") & pl.col("fang_f").is_not_null() & pl.col("cd").is_not_null())
    df = df.drop_nulls(cols)
    if args.debug:
        df = df.sample(n=min(5000, len(df)), seed=config["seed"])
    (out / "analysis_n.txt").write_text(
        f"measures.parquet rows: {len(raw)}\n"
        f"random sample with Fang F/E/G and CD, all measures non-null: {len(df)}\n")

    pct = year_percentiles(df, cols)
    ranks = pct.select(cols).to_numpy()
    sp = pl.DataFrame(np.corrcoef(ranks, rowvar=False), schema=cols).insert_column(0, pl.Series("measure", cols))
    sp.write_csv(out / "spearman.csv")

    resid = residualize(pct.select(measures).to_numpy(), pct.select(covs).to_numpy())
    psp = pl.DataFrame(np.corrcoef(resid, rowvar=False), schema=measures).insert_column(0, pl.Series("measure", measures))
    psp.write_csv(out / "partial_spearman.csv")
    heatmap([("Spearman, within-year ranks", sp.filter(pl.col("measure").is_in(measures))),
             ("Partial: citations, references, # concepts removed", psp)], measures, figure_path(out, "spearman_heatmap.png"))

    # Gap-openers vs the other Kedrick classes (all labelled papers, incl. the gap-opener oversample).
    lab = year_percentiles(raw.filter(pl.col("kedrick_class").is_not_null()).drop_nulls(["cd"]), measures)
    rows = []
    for other in ["novel_pair_non_opener", "neither"]:
        for m in measures:
            pos = lab.filter((pl.col("kedrick_class") == "gap_opener") & pl.col(m).is_not_null())[m].to_numpy()
            neg = lab.filter((pl.col("kedrick_class") == other) & pl.col(m).is_not_null())[m].to_numpy()
            boots = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(config["bootstrap_n"])]
            rows.append({"comparison": f"gap_opener vs {other}", "measure": m, "n_gap_openers": len(pos),
                         "n_other": len(neg), "auc": auc(pos, neg),
                         "ci_lo": float(np.quantile(boots, 0.025)), "ci_hi": float(np.quantile(boots, 0.975))})
    pl.DataFrame(rows).write_csv(out / "kedrick_auc.csv")

    # Empirical set overlaps: dominant citation role x tertiles.
    roles = pct.with_columns(
        role=pl.when((df["fang_f"] >= df["fang_e"]) & (df["fang_f"] >= df["fang_g"])).then(pl.lit("Foundation"))
             .when(df["fang_e"] >= df["fang_g"]).then(pl.lit("Extension")).otherwise(pl.lit("Generalization")))
    for m in ["cd", "dsi", "pm_distance", "novel_pair_frac"]:
        t = roles.with_columns(tertile=pl.when(pl.col(m) < 1 / 3).then(pl.lit("low")).when(pl.col(m) < 2 / 3).then(pl.lit("mid")).otherwise(pl.lit("high")))
        t.group_by(["role", "tertile"]).len().pivot(on="tertile", index="role", values="len").select(["role", "low", "mid", "high"]).sort("role") \
         .write_csv(out / f"crosstab_role_x_{m}.csv")

    print(sp.filter(pl.col("measure").is_in(measures)).select(["measure"] + measures))
    print(psp)
    print(pl.read_csv(out / "kedrick_auc.csv"))
    print((out / "analysis_n.txt").read_text())
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
