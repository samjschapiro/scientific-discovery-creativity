"""Camera-ready figures and landmark factor scores for the creativity-taxonomy report (factors_v3).

Rebuilds the factor-analysis sample exactly as analyze_factors.py does (within-year percentile ranks of the
same measures), checks the correlation matrix against the saved one, then:
  - Figure 1: varimax loadings, factors named by the variation / selection / retention reading
  - Figure 2: every paper's selection (F1) vs variation (F2) percentile, with landmark papers marked
  - landmark_scores.csv: landmark papers' percentiles on each factor and on the input measures
Figures go to the track figures folder (figures.py).

    uv run python src/shaky_foundations/scripts/taxonomy_figures.py configs/shaky_foundations/taxonomy_figures.yaml
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

REQUIRED = ["output_dir", "factors_dir", "measures_path", "extra_measures_paths", "factor_names", "measure_labels",
            "measure_order", "landmarks"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
DIVERGING = ["#2a78d6", "#f0efec", "#d0453a"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for f in ["loadings.csv", "spearman.csv", "config.yaml"]:
        if not (Path(config["factors_dir"]) / f).exists():
            raise FileNotFoundError(f"FATAL: {config['factors_dir']}/{f} missing; run analyze_factors_v3 first")


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
    plt.rcParams.update({"pdf.fonttype": 42, "font.family": "DejaVu Sans"})

    fdir = Path(config["factors_dir"])
    load = pl.read_csv(fdir / "loadings.csv")
    cols = load["measure"].to_list()
    if cols != load_config(fdir / "config.yaml")["measures"]:
        raise ValueError("FATAL: loadings.csv measures differ from the factor run's config")
    rot = load.drop("measure").to_numpy()
    k = rot.shape[1]
    if len(config["factor_names"]) != k:
        raise ValueError(f"FATAL: {k} factors but {len(config['factor_names'])} names")

    # Same sample and transform as analyze_factors.py.
    raw = pl.read_parquet(config["measures_path"]).with_columns(
        log_citers5=(pl.col("n_i") + pl.col("n_j") + 1).log(), log_refs=(pl.col("n_refs_total") + 1).log())
    for extra in config["extra_measures_paths"]:
        raw = raw.join(pl.read_parquet(extra), on="pid", how="left")
    df = raw.filter(pl.col("in_random_sample") & pl.col("fang_f").is_not_null() & pl.col("cd").is_not_null()).drop_nulls(cols)
    df = df.with_columns([((pl.col(c).rank("average").over("year") - 0.5) / pl.col(c).count().over("year")).alias(c + "_pct")
                          for c in cols])
    x = df.select([c + "_pct" for c in cols]).to_numpy()
    corr = np.corrcoef(x, rowvar=False)
    saved = pl.read_csv(fdir / "spearman.csv").drop("measure").to_numpy()
    if not np.allclose(corr, saved, atol=1e-6):
        raise ValueError("FATAL: rebuilt correlation matrix differs from the saved factor run")
    z = (x - x.mean(axis=0)) / x.std(axis=0)
    scores = z @ np.linalg.solve(corr, rot)
    fcols = [f"F{i + 1}" for i in range(k)]
    df = df.with_columns([pl.Series(f, scores[:, i]) for i, f in enumerate(fcols)])
    df = df.with_columns([((pl.col(f).rank("average") - 0.5) / pl.len()).alias(f + "_pct") for f in fcols])

    # Landmarks.
    lm = pl.DataFrame({"title": [l["title"] for l in config["landmarks"]], "label": [l["label"] for l in config["landmarks"]]})
    hits = df.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).join(
        lm.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).drop("title"), on="t", how="inner")
    missing = set(lm["label"]) - set(hits["label"])
    if missing:
        print(f"note: landmarks not in the factor sample (no Fang F/E/G, CD or atoms): {sorted(missing)}")
    land = hits.select(["label", "year"] + [f + "_pct" for f in fcols] + [c + "_pct" for c in cols]).sort("year")
    land.write_csv(out / "landmark_scores.csv")

    # Figure 1: loadings heatmap, measures grouped by the factor they load on.
    order = config["measure_order"]
    idx = [cols.index(m) for m in order]
    L = rot[idx]
    cmap = LinearSegmentedColormap.from_list("div", DIVERGING)
    fig, ax = plt.subplots(figsize=(6.6, 4.3), facecolor="white")
    ax.imshow(L, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    for i in range(L.shape[0]):
        for j in range(k):
            v = L[i, j]
            ax.text(j, i, f"{v:.2f}".replace("-", "−"), ha="center", va="center", fontsize=7.5,
                    color=INK, weight="bold" if abs(v) >= 0.4 else "normal")
    ax.set_xticks(range(k), [n.replace(" | ", "\n") for n in config["factor_names"]], fontsize=7.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(order)), [config["measure_labels"][m] for m in order], fontsize=7.5)
    ax.tick_params(length=0, colors=INK)
    for s in ax.spines.values():
        s.set_visible(False)
    ev = pl.read_csv(fdir / "eigenvalues.csv")["var_explained"].to_list()[:k]
    for j, v in enumerate(ev):
        ax.text(j, len(order) - 0.35, f"{v:.0%} of variance", ha="center", va="top", fontsize=6.5, color=MUTED)
    fig.tight_layout()
    base = figure_path(out, "loadings")
    for ext, dpi in [("pdf", None), ("png", 300)]:
        fig.savefig(base.with_suffix(f".{ext}"), dpi=dpi, facecolor="white")
    plt.close(fig)

    # Figure 2: selection (F1) vs variation (F2) for all papers, landmarks marked.
    fig, ax = plt.subplots(figsize=(5.2, 4.4), facecolor="white")
    hb = ax.hexbin(df["F2_pct"], df["F1_pct"], gridsize=40, cmap=LinearSegmentedColormap.from_list("g", ["#ffffff", "#c9c8c2"]),
                   mincnt=1, linewidths=0)
    ax.scatter(hits["F2_pct"], hits["F1_pct"], s=26, color=DIVERGING[0], edgecolor="white", linewidth=0.8, zorder=3)
    offsets = {l["label"]: l.get("offset", [4, 3]) for l in config["landmarks"]}
    for r in hits.iter_rows(named=True):
        dx, dy = offsets[r["label"]]
        ax.annotate(r["label"], (r["F2_pct"], r["F1_pct"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.5,
                    color=INK, ha="right" if dx < 0 else "left", va="center")
    ax.axhline(0.5, color=GRID, lw=0.8, zorder=1)
    ax.axvline(0.5, color=GRID, lw=0.8, zorder=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.06)
    ax.set_xlabel("Variation (F2): combinatorial novelty at publication, percentile", fontsize=7.5, color=INK)
    ax.set_ylabel("Selection (F1): later uptake of its ideas, percentile", fontsize=7.5, color=INK)
    ax.tick_params(labelsize=7, colors=MUTED, length=0)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(GRID)
    # Quadrant captions sit inside each quadrant, clear of the landmark band at the top.
    for (xq, yq, txt) in [(0.98, 0.56, "novel and selected"), (0.02, 0.56, "selected, not novel"),
                          (0.98, 0.015, "novel, not selected"), (0.02, 0.015, "neither")]:
        ax.text(xq, yq, txt, transform=ax.transAxes, fontsize=6.5, color=MUTED, style="italic",
                ha="right" if xq > 0.5 else "left", va="bottom")
    fig.tight_layout()
    base = figure_path(out, "selection_vs_variation")
    for ext, dpi in [("pdf", None), ("png", 300)]:
        fig.savefig(base.with_suffix(f".{ext}"), dpi=dpi, facecolor="white")
    plt.close(fig)

    quad = df.select(hi1=pl.col("F1_pct") >= 0.5, hi2=pl.col("F2_pct") >= 0.5).group_by("hi1", "hi2").len()
    (out / "summary.txt").write_text(f"papers: {df.height:,}; landmarks found: {hits.height}/{lm.height}\n"
                                     f"F1 x F2 halves: {quad.sort('hi1', 'hi2').rows()}\n"
                                     f"Spearman F1 vs F2 scores: {df.select(pl.corr('F1', 'F2', method='spearman')).item():.3f}\n")
    with pl.Config(tbl_rows=30, tbl_width_chars=200, float_precision=2):
        print((out / "summary.txt").read_text())
        print(land.select(["label", "year"] + [f + "_pct" for f in fcols]))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
