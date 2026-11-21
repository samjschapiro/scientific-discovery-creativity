"""Exploratory: what independent dimensions do the creativity measures span? (Walker / Sam, 11-20)

Correlation matrix of within-year percentile ranks (Spearman with year held fixed), then:

  eigenvalues.csv   eigenvalues of the matrix vs Horn's parallel analysis (95th percentile of
                    eigenvalues from column-shuffled data). Keep components above the null.
  spearman.csv      the correlation matrix (within-year ranks)
  loadings.csv      varimax-rotated principal-component loadings for the retained components
  figures/<run>_factors.png  (track figures folder) scree with the parallel-analysis null + rotated loading heatmap
  gap_opener_auc.csv  do Kedrick gap-openers stand out on any factor? (AUC vs each other class)
  analysis_n.txt

Principal-component factoring (not maximum-likelihood FA): with ~100K papers and a handful of
measures the difference is cosmetic, and PCs need no distributional assumptions.

    uv run python src/shaky_foundations/scripts/analyze_factors.py configs/shaky_foundations/analyze_factors.yaml
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

REQUIRED = ["output_dir", "measures_path", "measures", "parallel_reps", "seed", "bootstrap_n"]
LABELS = {"cd": "CD₅ disruption", "fang_f": "Foundation share", "fang_e": "Extension share",
          "fang_g": "Generalization share", "dsi": "Atom DSI", "pm_distance": "Problem–mechanism dist.",
          "novel_pair_frac": "Novel concept pairs", "pmi_p10": "Pair PMI p10", "log_citers5": "log citations (5y)",
          "log_refs": "log references", "n_unique_concepts": "# distinct concepts",
          "prescience": "Prescience", "novel_pair_adoption": "Novel pairs later adopted", "emergence": "Emergence",
          "novel_share": "Novel pair share"}


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not Path(config["measures_path"]).exists():
        raise FileNotFoundError(f"FATAL: {config['measures_path']} not found; run build_measures first")
    unknown = set(config["measures"]) - set(LABELS)
    if unknown:
        raise ValueError(f"FATAL: no label for measures {unknown}")


def year_pct(df: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    return df.with_columns([((pl.col(c).rank("average").over("year") - 0.5) / pl.col(c).count().over("year")).alias(c)
                            for c in cols])


def varimax(loadings: np.ndarray, iters: int = 100, tol: float = 1e-8) -> np.ndarray:
    p, k = loadings.shape
    r = np.eye(k)
    d = 0.0
    for _ in range(iters):
        lam = loadings @ r
        u, s, vt = np.linalg.svd(loadings.T @ (lam ** 3 - lam @ np.diag((lam ** 2).sum(axis=0)) / p))
        r = u @ vt
        if s.sum() < d * (1 + tol):
            break
        d = s.sum()
    return loadings @ r


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = pl.Series(np.concatenate([pos, neg])).rank("average").to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def plot(eig: np.ndarray, null: np.ndarray, rot: np.ndarray, cols: list[str], path: Path) -> None:
    ink, muted, surface = "#1a1a19", "#6b6a66", "#fcfcfb"
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2), facecolor=surface,
                                 gridspec_kw={"width_ratios": [1, 1.25]})
    x = np.arange(1, len(eig) + 1)
    a1.plot(x, eig, color="#256abf", lw=2, marker="o", ms=8, label="observed")
    a1.plot(x, null, color=muted, lw=2, ls="--", label="parallel-analysis null (95th pct)")
    a1.set_xticks(x)
    a1.set_xlabel("component", color=ink)
    a1.set_ylabel("eigenvalue", color=ink)
    a1.set_title("How many dimensions?", loc="left", fontsize=11, color=ink)
    a1.legend(frameon=False, fontsize=9)
    a1.grid(axis="y", color="#e6e5e1", lw=0.8)
    for s in ["top", "right"]:
        a1.spines[s].set_visible(False)

    cmap = LinearSegmentedColormap.from_list("div", ["#256abf", "#f0efec", "#e34948"])
    a2.imshow(rot, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    a2.set_yticks(range(len(cols)), [LABELS[c] for c in cols], fontsize=9)
    a2.set_xticks(range(rot.shape[1]), [f"F{i + 1}" for i in range(rot.shape[1])], fontsize=9)
    for i in range(rot.shape[0]):
        for j in range(rot.shape[1]):
            a2.text(j, i, f"{rot[i, j]:.2f}", ha="center", va="center", fontsize=8.5, color=ink)
    a2.set_title("Varimax-rotated loadings", loc="left", fontsize=11, color=ink)
    a2.tick_params(length=0)
    for s in a2.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=surface)
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
    cols = config["measures"]

    raw = pl.read_parquet(config["measures_path"]).with_columns(
        log_citers5=(pl.col("n_i") + pl.col("n_j") + 1).log(), log_refs=(pl.col("n_refs_total") + 1).log())
    for extra in config.get("extra_measures_paths", []):   # e.g. prescience.parquet, joined on pid
        raw = raw.join(pl.read_parquet(extra), on="pid", how="left")
    df = raw.filter(pl.col("in_random_sample") & pl.col("fang_f").is_not_null() & pl.col("cd").is_not_null()).drop_nulls(cols)
    if args.debug:
        df = df.sample(n=min(5000, len(df)), seed=config["seed"])
    x = year_pct(df, cols).select(cols).to_numpy()
    corr = np.corrcoef(x, rowvar=False)
    pl.DataFrame(corr, schema=cols).insert_column(0, pl.Series("measure", cols)).write_csv(out / "spearman.csv")
    eigval, eigvec = np.linalg.eigh(corr)
    order = np.argsort(eigval)[::-1]
    eigval, eigvec = eigval[order], eigvec[:, order]

    null = []
    for _ in range(config["parallel_reps"]):
        xs = np.column_stack([rng.permutation(x[:, j]) for j in range(x.shape[1])])
        null.append(np.sort(np.linalg.eigvalsh(np.corrcoef(xs, rowvar=False)))[::-1])
    null95 = np.quantile(np.array(null), 0.95, axis=0)
    k = int(np.argmax(eigval <= null95)) if (eigval <= null95).any() else len(eigval)
    k = max(k, 2)  # always show at least two dimensions
    pl.DataFrame({"component": np.arange(1, len(eigval) + 1), "eigenvalue": eigval, "null95": null95,
                  "var_explained": eigval / eigval.sum(), "retained": np.arange(len(eigval)) < k}) \
        .write_csv(out / "eigenvalues.csv")

    loadings = eigvec[:, :k] * np.sqrt(eigval[:k])
    rot = varimax(loadings)
    rot = rot * np.sign(rot[np.abs(rot).argmax(axis=0), np.arange(k)])  # largest loading positive
    pl.DataFrame(rot, schema=[f"F{i + 1}" for i in range(k)]).insert_column(0, pl.Series("measure", cols)) \
        .write_csv(out / "loadings.csv")
    plot(eigval, null95, rot, cols, figure_path(out, "factors.png"))

    # Factor scores (regression on standardised ranks) for every labelled paper, then gap-opener AUCs.
    weights = np.linalg.solve(corr, rot)
    mu, sd = x.mean(axis=0), x.std(axis=0)
    lab = raw.filter(pl.col("kedrick_class").is_not_null()).drop_nulls(cols)
    lx = year_pct(lab, cols).select(cols).to_numpy()
    scores = ((lx - mu) / sd) @ weights
    cls = lab["kedrick_class"].to_numpy()
    rows = []
    for other in ["novel_pair_non_opener", "neither"]:
        for j in range(k):
            pos, neg = scores[cls == "gap_opener", j], scores[cls == other, j]
            boots = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(config["bootstrap_n"])]
            rows.append({"comparison": f"gap_opener vs {other}", "factor": f"F{j + 1}", "n_gap_openers": len(pos),
                         "n_other": len(neg), "auc": auc(pos, neg), "ci_lo": float(np.quantile(boots, 0.025)),
                         "ci_hi": float(np.quantile(boots, 0.975))})
    pl.DataFrame(rows).write_csv(out / "gap_opener_auc.csv")
    (out / "analysis_n.txt").write_text(f"papers (random sample, Fang + CD, all measures non-null): {len(df)}\n"
                                        f"Kedrick-labelled papers scored: {len(lab)}\nretained factors: {k}\n")

    with pl.Config(tbl_rows=30, tbl_width_chars=160, float_precision=3):
        print(pl.read_csv(out / "eigenvalues.csv"))
        print(pl.read_csv(out / "loadings.csv"))
        print(pl.read_csv(out / "gap_opener_auc.csv"))
    print((out / "analysis_n.txt").read_text() + f"done -> {out}")


if __name__ == "__main__":
    main()
