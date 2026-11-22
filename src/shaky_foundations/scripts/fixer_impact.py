"""Do papers that fix a foundation's limitation end up more impactful? Step 2, after the subagent labels.

Inputs: fixer_candidates run (candidates.parquet) + labels/*.jsonl written by the judges (cand_id, label, reason).

Unit = (foundation, citing paper); a paper judged `fix` on any of the foundation's gold limitations is a fixer.
Outcomes: within-year percentile (0-100) of total OpenAlex citations through 2025 and of Lacuna citations, among
all canonical Lacuna papers with atoms published that year.

  judge_validation   judge labels vs hand labels on the validation items (fix vs not)
  vs_citers          each candidate minus the mean of ALL papers citing the same foundation in the same year
                     (premium over the foundation's typical citer), by label
  fix_vs_mentions    within candidates (all state the limitation): fix vs mentions, OLS with foundation and year
                     dummies and log references; CI from a bootstrap over foundations
  top10              share in the top 10% of their year, by label
  dose               does the fix premium grow with the foundation's shakiness? Shakiness = agreement: the chance
                     that two distinct random critics of the foundation raise the same c2000 concept,
                     sum m_k(m_k - 1) / (N(N - 1)) (Simpson's index; unbiased at any N, so no rarefaction and
                     only a floor of min_critics). Median split (cluster bootstrap) and Spearman across foundations
                     (bootstrap CI, permutation p). The rarefied conc_all (>= 20 critics) is reported for comparison.

Outputs: labelled.parquet, results.csv, per_foundation.csv, examples.csv (random fix / mentions labels),
summary.txt; figures in data/shaky_foundations/figures/<run>_*.

    uv run python src/shaky_foundations/scripts/fixer_impact.py configs/shaky_foundations/fixer_impact.yaml
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
from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "candidates_dir", "scored_path", "hits_path", "year_min",
            "year_max", "min_critics", "bootstrap_n", "n_permutations", "seed"]
LABELS = ["fix", "applies_fix", "mentions", "unrelated"]
OUTCOMES = {"citations_total": "pct_total", "citations_lacuna": "pct_lacuna"}


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")


def load_labels(cdir: Path, cands: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for p in sorted((cdir / "labels").glob("*.jsonl")):
        for line in p.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    lab = pl.DataFrame(rows).select("cand_id", "label", "reason").unique("cand_id", keep="last")
    bad = lab.filter(~pl.col("label").is_in(LABELS))
    if bad.height:
        raise ValueError(f"FATAL: {bad.height} labels outside {LABELS}: {bad.head(5)}")
    missing = cands.join(lab, on="cand_id", how="anti")
    if missing.height:
        raise ValueError(f"FATAL: {missing.height} candidates have no label (e.g. {missing['cand_id'].head(5).to_list()})")
    return cands.join(lab, on="cand_id")


def percentiles(con, y0: int, y1: int) -> pl.DataFrame:
    return con.sql(f"""
        SELECT pid AS citer, year,
               100 * percent_rank() OVER (PARTITION BY year ORDER BY coalesce(cites_total_2025, 0)) AS pct_total,
               100 * percent_rank() OVER (PARTITION BY year ORDER BY coalesce(cites_lacuna_2025, 0)) AS pct_lacuna,
               ln(1 + coalesce(n_refs_total, 0)) AS log_refs
        FROM papers WHERE pid = canonical_pid AND n_atoms > 0 AND year BETWEEN {y0} AND {y1}
    """).pl()


def citer_baseline(con, foundations: list[int], pct: pl.DataFrame, y0: int, y1: int) -> pl.DataFrame:
    """Mean percentile of all papers citing each foundation, per citing year."""
    con.register("fi_f", pl.DataFrame({"foundation": foundations}))
    edges = con.sql(f"""SELECT DISTINCT c.cited_pid AS foundation, c.citing_pid AS citer FROM citations c
                        JOIN fi_f ON c.cited_pid = fi_f.foundation
                        WHERE c.citing_year BETWEEN {y0} AND {y1}""").pl()
    return edges.join(pct, on="citer").group_by("foundation", "year").agg(
        pl.col("pct_total").mean().alias("base_total"), pl.col("pct_lacuna").mean().alias("base_lacuna"),
        pl.len().alias("n_citers"))


def cluster_boot(df: pl.DataFrame, stat, n: int, rng) -> tuple[float, float, float]:
    groups = df.partition_by("foundation")
    est = stat(df)
    draws = []
    for _ in range(n):
        idx = rng.integers(0, len(groups), len(groups))
        try:
            draws.append(stat(pl.concat([groups[i] for i in idx])))
        except np.linalg.LinAlgError:
            continue
    lo, hi = np.nanpercentile(draws, [2.5, 97.5])
    return est, lo, hi


def agreement(hits_path: str) -> pl.DataFrame:
    """Per foundation: number of distinct critics and the chance two distinct critics share a concept."""
    h = pl.read_parquet(hits_path).select("foundation", "citer", "kid").unique()
    n = h.group_by("foundation").agg(n_critics=pl.col("citer").n_unique())
    pairs = h.group_by("foundation", "kid").agg(m=pl.len()).group_by("foundation").agg(
        s=(pl.col("m") * (pl.col("m") - 1)).sum())
    return n.join(pairs, on="foundation").with_columns(
        agreement=pl.when(pl.col("n_critics") >= 2).then(pl.col("s") / (pl.col("n_critics") * (pl.col("n_critics") - 1)))
    ).drop("s")


def foundation_rho(fm: pl.DataFrame, x: str, y: str, nb: int, nperm: int, rng) -> tuple[float, float, float, float]:
    """Spearman across foundations, bootstrap CI over foundations, two-sided permutation p."""
    rx = fm[x].rank().to_numpy()
    ry = fm[y].rank().to_numpy()
    rho = float(np.corrcoef(rx, ry)[0, 1])
    boots = []
    for _ in range(nb):
        i = rng.integers(0, len(rx), len(rx))
        boots.append(pl.DataFrame({"a": fm[x].to_numpy()[i], "b": fm[y].to_numpy()[i]})
                     .select(pl.corr("a", "b", method="spearman")).item())
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(nperm)])
    p = float((np.sum(np.abs(perm) >= abs(rho)) + 1) / (nperm + 1))
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return rho, float(lo), float(hi), p


def figures(out: Path, config: dict, paper: pl.DataFrame, per_f: pl.DataFrame, results: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    ink, muted, accent = "#1a1a19", "#8a8984", "#2a78d6"

    # Figure 1: premium over same-foundation citers, by label
    r = pl.DataFrame(results).filter((pl.col("analysis") == "vs_citers") & (pl.col("outcome") == "citations_total"))
    names = {"fix": "proposes a fix", "applies_fix": "applies an existing fix", "mentions": "states the limitation only",
             "unrelated": "unrelated problem"}
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    for i, row in enumerate(r.iter_rows(named=True)):
        c = accent if row["group"] == "fix" else muted
        ax.plot([row["lo"], row["hi"]], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(row["estimate"], i, "o", color=c, ms=8, mec="white", mew=1.5)
    ax.set_yticks(range(r.height), [f"{names[g]} (n={n:,})" for g, n in zip(r["group"], r["n"])])
    ax.axvline(0, color=ink, lw=0.8)
    ax.set_xlabel("citation premium (percentile points vs\nsame-foundation, same-year citers)")
    ax.invert_yaxis()
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(figure_path(config["output_dir"], f"premium_by_label.{ext}"), dpi=200)
    plt.close(fig)

    # Figure 2: fixer premium vs shakiness, per foundation
    d = per_f.filter(pl.col("n_critics") >= min(config["min_critics"]))
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    d = d.with_columns(x=100 * (pl.col("agreement").rank() - 0.5) / d.height)   # shakiness rank, percentile
    sizes = 12 + 2.5 * d["n_fix"].to_numpy()
    ax.scatter(d["x"], d["prem_total"], s=sizes, color=accent, alpha=0.55, edgecolor="white", lw=0.8)
    for lo_, hi_ in [(0, 100 / 3), (100 / 3, 200 / 3), (200 / 3, 100)]:
        m = d.filter((pl.col("x") >= lo_) & (pl.col("x") < hi_))["prem_total"].mean()
        ax.plot([lo_ + 2, hi_ - 2], [m, m], color=ink, lw=2.2)
        ax.annotate(f"{m:+.1f}", ((lo_ + hi_) / 2, m), xytext=(0, 5), textcoords="offset points", ha="center",
                    fontsize=9, color=ink, fontweight="bold")
    rho = next(r_ for r_ in results if r_["analysis"] == f"dose_rho_agreement_min{min(config['min_critics'])}"
               and r_["outcome"] == "citations_total")
    ax.text(0.02, 0.97, f"Spearman {rho['estimate']:.2f} [{rho['lo']:.2f}, {rho['hi']:.2f}], permutation p = {rho['p']:.3f}\n"
            f"{d.height} foundations; dot size = number of fixers; bars = tercile means",
            transform=ax.transAxes, va="top", fontsize=8.5, color=muted)
    ax.axhline(0, color=muted, lw=0.8, ls="--")
    short = {"Attention is All you Need": "Transformer", "Generative Adversarial Nets": "GANs",
             "Very Deep Convolutional Networks for Large-Scale Image Recognition": "VGG",
             "Fixing Weight Decay Regularization in Adam": "AdamW",
             "Explaining and Harnessing Adversarial Examples": "FGSM",
             "LINE: Large-scale Information Network Embedding": "LINE",
             "Sequence to Sequence Learning with Neural Networks": "seq2seq",
             }
    for row in d.iter_rows(named=True):
        if row["title"] in short:
            ax.annotate(short[row["title"]], (row["x"], row["prem_total"]), xytext=(5, 3),
                        textcoords="offset points", fontsize=8.5, color=ink)
    ax.set_xlabel("shakiness rank (percentile; shakiness = chance two critics raise the same problem)")
    ax.set_ylabel("fixers' citation premium (percentile points)")
    fig.tight_layout()
    for ext in ["png", "pdf"]:
        fig.savefig(figure_path(config["output_dir"], f"dose.{ext}"), dpi=200)
    plt.close(fig)


def ols_fix_effect(df: pl.DataFrame, y: str) -> float:
    """Coefficient on fix (vs mentions) with foundation and year dummies and log references."""
    d = df.to_dummies(["foundation", "year"], drop_first=True)
    xcols = ["is_fix", "log_refs"] + [c for c in d.columns if c.startswith("foundation_") or c.startswith("year_")]
    X = np.column_stack([np.ones(d.height)] + [d[c].cast(pl.Float64).to_numpy() for c in xcols])
    beta = np.linalg.lstsq(X, d[y].to_numpy(), rcond=None)[0]
    return float(beta[1])


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
    rng = np.random.default_rng(config["seed"])
    nb = 50 if args.debug else config["bootstrap_n"]

    cdir = Path(config["candidates_dir"])
    cands = load_labels(cdir, pl.read_parquet(cdir / "candidates.parquet"))
    summary, results = [], []

    # judge vs hand labels
    v = cands.filter(pl.col("val_label").is_not_null()).with_columns(judge_fix=pl.col("label") == "fix",
                                                                     hand_fix=pl.col("val_label") == "fix")
    tp = (v["judge_fix"] & v["hand_fix"]).sum()
    prec = tp / max(v["judge_fix"].sum(), 1)
    rec = tp / max(v["hand_fix"].sum(), 1)
    agree = (v["judge_fix"] == v["hand_fix"]).mean()
    summary.append(f"judge vs hand labels ({v.height} items, {v['hand_fix'].sum()} hand fixes): "
                   f"precision {prec:.2f}, recall {rec:.2f}, agreement {agree:.2f}")
    results.append({"analysis": "judge_validation", "group": "fix", "outcome": "", "n": v.height,
                    "estimate": float(agree), "lo": float(prec), "hi": float(rec)})
    summary.append("  confusion (hand x judge): " + ", ".join(
        f"{h}->{j}: {n}" for h, j, n in v.group_by("val_label", "label").len().sort("val_label", "label").iter_rows()))

    # paper level: top_k candidates only (validation extras are not a ranked sample)
    c = cands.filter(pl.col("source") == "top_k")
    order = {l: i for i, l in enumerate(LABELS)}
    paper = (c.with_columns(r=pl.col("label").replace_strict(order, return_dtype=pl.Int8))
              .group_by("foundation", "citer").agg(pl.col("r").min())
              .with_columns(label=pl.col("r").replace_strict({i: l for l, i in order.items()}, return_dtype=pl.String))
              .drop("r"))
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    pct = percentiles(con, config["year_min"], config["year_max"])
    paper = paper.join(pct, on="citer", how="inner")
    base = citer_baseline(con, paper["foundation"].unique().to_list(), pct, config["year_min"], config["year_max"])
    paper = paper.join(base, on=["foundation", "year"], how="left").with_columns(
        prem_total=pl.col("pct_total") - pl.col("base_total"), prem_lacuna=pl.col("pct_lacuna") - pl.col("base_lacuna"),
        is_fix=(pl.col("label") == "fix").cast(pl.Int8))
    scored = pl.read_csv(config["scored_path"]).select(pl.col("pid").alias("foundation"), "conc_all", "title")
    paper = paper.join(scored, on="foundation", how="left").join(agreement(config["hits_path"]), on="foundation", how="left")
    paper.write_parquet(out / "labelled.parquet")

    counts = paper.group_by("label").len().sort("label")
    summary.append("papers by label: " + ", ".join(f"{r['label']} {r['len']}" for r in counts.iter_rows(named=True))
                   + f" ({paper['foundation'].n_unique()} foundations)")

    for oname, col in OUTCOMES.items():
        prem = "prem_" + col.split("_")[1]
        summary.append(f"\n[{oname}] within-year percentile")
        for lab in LABELS:
            g = paper.filter(pl.col("label") == lab)
            if g.height < 5:
                continue
            est, lo, hi = cluster_boot(g, lambda d: d[prem].mean(), nb, rng)
            top = g.select((pl.col(col) >= 90).mean()).item()
            summary.append(f"  {lab:12s} n={g.height:4d}  pct {g[col].mean():5.1f}  premium over same-foundation "
                           f"citers {est:+5.1f} [{lo:+.1f}, {hi:+.1f}]  top-10% {top:.0%}")
            results.append({"analysis": "vs_citers", "group": lab, "outcome": oname, "n": g.height,
                            "estimate": est, "lo": lo, "hi": hi})
            results.append({"analysis": "top10", "group": lab, "outcome": oname, "n": g.height,
                            "estimate": top, "lo": None, "hi": None})
        fm = paper.filter(pl.col("label").is_in(["fix", "mentions"]))
        est, lo, hi = cluster_boot(fm, lambda d: ols_fix_effect(d, col), nb, rng)
        summary.append(f"  fix vs mentions (foundation + year FE, log refs): {est:+.1f} [{lo:+.1f}, {hi:+.1f}] "
                       f"(n={fm.height})")
        results.append({"analysis": "fix_vs_mentions", "group": "fix", "outcome": oname, "n": fm.height,
                        "estimate": est, "lo": lo, "hi": hi})
        for measure, floor in [("agreement", m) for m in config["min_critics"]] + [("conc_all", 20)]:
            fx = paper.filter((pl.col("label") == "fix") & (pl.col("n_critics") >= floor) & pl.col(measure).is_not_null())
            fm_ = fx.group_by("foundation").agg(pl.col(measure).first(), pl.col(prem).mean())
            med = fm_[measure].median()
            fx = fx.with_columns(shaky=pl.col(measure) >= med)
            diff = lambda d: d.filter(pl.col("shaky"))[prem].mean() - d.filter(~pl.col("shaky"))[prem].mean()
            est, lo, hi = cluster_boot(fx, diff, nb, rng)
            rho, rlo, rhi, p = foundation_rho(fm_, measure, prem, nb, config["n_permutations"], rng)
            summary.append(f"  dose [{measure}, >= {floor} critics]: {fm_.height} foundations, {fx.height} fixers; "
                           f"shakier minus less shaky {est:+.1f} [{lo:+.1f}, {hi:+.1f}]; "
                           f"Spearman {rho:.2f} [{rlo:.2f}, {rhi:.2f}], permutation p = {p:.3f}")
            results.append({"analysis": f"dose_diff_{measure}_min{floor}", "group": "fix", "outcome": oname,
                            "n": fm_.height, "estimate": est, "lo": lo, "hi": hi})
            results.append({"analysis": f"dose_rho_{measure}_min{floor}", "group": "fix", "outcome": oname,
                            "n": fm_.height, "estimate": rho, "lo": rlo, "hi": rhi, "p": p})

    per_f = (paper.filter(pl.col("label") == "fix").group_by("foundation")
             .agg(pl.col("title").first(), pl.col("agreement").first(), pl.col("n_critics").first(),
                  pl.col("conc_all").first(), n_fix=pl.len(), prem_total=pl.col("prem_total").mean(),
                  prem_lacuna=pl.col("prem_lacuna").mean()).sort("agreement", descending=True))
    per_f.write_csv(out / "per_foundation.csv")
    ex = (cands.filter(pl.col("source") == "top_k").filter(pl.col("label").is_in(["fix", "mentions"]))
          .sample(fraction=1.0, shuffle=True, seed=config["seed"]).group_by("label", maintain_order=True).head(8)
          .select("label", "foundation_title", "limitation", "title", "year", "reason"))
    ex.write_csv(out / "examples.csv")
    figures(out, config, paper, per_f, results)

    pl.DataFrame(results).write_csv(out / "results.csv")
    (out / "summary.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
