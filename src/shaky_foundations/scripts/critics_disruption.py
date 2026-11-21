"""Are papers that critique a foundation special? More disruptive than other (Generalization) papers?

Population: 2010–2019 papers with Fang & Evans F/E/G and a CD index (build_measures, random sample).
A paper's role is its dominant Fang share (Foundation / Extension / Generalization, as in
analyze_relationships). Flags:
  cites_foundation  cites at least one top-N foundation (scale_foundations candidate list)
  can_critique      has >= 1 critique atom (limitation atom in the problems_and_motivation lens)
  critic            at least one of its critiques is attributed to a top-N foundation (scale hits)

Main comparison, which holds "cites a famous foundation" and "has critique atoms" fixed:
critics vs non-critics among papers that cite a foundation and can critique; overall, within
Generalization-dominant papers, and within the rest. Disruption = within-year CD percentile, raw and
residualized on log citations (5y), log references and # distinct concepts. Plus all Generalization-
dominant papers as the reference group the question asks about.

Several outcomes (config `outcomes`): disruption (CD) and citation impact, each a within-year percentile,
with its own covariates (citations cannot be a control when they are the outcome).

Outputs: config.yaml, <outcome>_groups.csv, <outcome>_comparisons.csv, <outcome>_regression.csv, summary.txt

    uv run python src/shaky_foundations/scripts/critics_disruption.py configs/shaky_foundations/critics_disruption.yaml
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

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "measures_path", "foundations_path", "hits_path",
            "critique_type", "critique_lens", "outcomes", "bootstrap_n", "seed"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for k in ["measures_path", "foundations_path", "hits_path"]:
        if not Path(config[k]).exists():
            raise FileNotFoundError(f"FATAL: {config[k]} not found")


def year_pct(df: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    return df.with_columns([((pl.col(c).rank("average").over("year") - 0.5) / pl.col(c).count().over("year")).alias(c + "_pct")
                            for c in cols])


def residualize(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(x)), x])
    return y - x @ np.linalg.lstsq(x, y, rcond=None)[0]


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = pl.Series(np.concatenate([pos, neg])).rank("average").to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


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
    covs = sorted({c for o in config["outcomes"].values() for c in o["covariates"]})

    m = (pl.read_parquet(config["measures_path"])
         .filter(pl.col("in_random_sample") & pl.col("fang_f").is_not_null() & pl.col("cd").is_not_null())
         .with_columns(log_citers5=(pl.col("n_i") + pl.col("n_j") + 1).log(), log_refs=(pl.col("n_refs_total") + 1).log())
         .drop_nulls(covs)
         .with_columns(role=pl.when((pl.col("fang_f") >= pl.col("fang_e")) & (pl.col("fang_f") >= pl.col("fang_g")))
                       .then(pl.lit("Foundation")).when(pl.col("fang_e") >= pl.col("fang_g"))
                       .then(pl.lit("Extension")).otherwise(pl.lit("Generalization"))))
    if args.debug:
        m = m.sample(n=8000, seed=config["seed"])

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    fnd = pl.read_csv(config["foundations_path"]).select(pl.col("pid").alias("foundation"))
    con.register("pop", m.select("pid"))
    con.register("fnd", fnd)
    cites = con.sql("SELECT DISTINCT citing_pid AS pid FROM citations c JOIN fnd ON fnd.foundation = c.cited_pid "
                    "WHERE citing_pid IN (SELECT pid FROM pop)").pl().with_columns(cites_foundation=pl.lit(True))
    able = con.sql("SELECT DISTINCT pid FROM atoms WHERE run_rank = 1 AND type = ? AND lens = ? "
                   "AND pid IN (SELECT pid FROM pop)", params=[config["critique_type"], config["critique_lens"]]
                   ).pl().with_columns(can_critique=pl.lit(True))
    critics = (pl.read_parquet(config["hits_path"]).select(pl.col("citer").alias("pid")).unique()
               .with_columns(critic=pl.lit(True)))
    df = (m.join(cites, on="pid", how="left").join(able, on="pid", how="left").join(critics, on="pid", how="left")
          .with_columns([pl.col(c).fill_null(False) for c in ["cites_foundation", "can_critique", "critic"]]))

    is_g = pl.col("role") == "Generalization"
    pool = pl.col("cites_foundation") & pl.col("can_critique")
    all_covs = sorted({c for o in config["outcomes"].values() for c in o["covariates"]})
    outcome_cols = [o["column"] for o in config["outcomes"].values()]
    df = year_pct(df, sorted(set(outcome_cols + all_covs)))
    groups = {
        "all papers": pl.lit(True),
        "all Generalization-dominant": is_g,
        "Generalization-dominant citing a top foundation": is_g & pl.col("cites_foundation"),
        "Generalization-dominant not citing one": is_g & ~pl.col("cites_foundation"),
        "other roles citing a top foundation": ~is_g & pl.col("cites_foundation"),
        "other roles not citing one": ~is_g & ~pl.col("cites_foundation"),
        "cite a foundation + can critique: critics": pool & pl.col("critic"),
        "cite a foundation + can critique: non-critics": pool & ~pl.col("critic"),
        "  Generalization-dominant critics": pool & pl.col("critic") & is_g,
        "  Generalization-dominant non-critics": pool & ~pl.col("critic") & is_g,
        "  other-role critics": pool & pl.col("critic") & ~is_g,
        "  other-role non-critics": pool & ~pl.col("critic") & ~is_g,
    }
    comparisons = {
        "within Generalization-dominant: cites a top foundation vs not": (is_g & pl.col("cites_foundation"), is_g & ~pl.col("cites_foundation")),
        "within other roles: cites a top foundation vs not": (~is_g & pl.col("cites_foundation"), ~is_g & ~pl.col("cites_foundation")),
        "critics vs non-critics (cite a foundation + can critique)": (pool & pl.col("critic"), pool & ~pl.col("critic")),
        "within Generalization-dominant: critics vs non-critics": (pool & pl.col("critic") & is_g, pool & ~pl.col("critic") & is_g),
        "within other roles: critics vs non-critics": (pool & pl.col("critic") & ~is_g, pool & ~pl.col("critic") & ~is_g),
        "Generalization-dominant critics vs all Generalization-dominant": (pool & pl.col("critic") & is_g, is_g),
    }
    printed = []
    for oname, o in config["outcomes"].items():
        col, covs = o["column"], o["covariates"]
        # Within-year percentile of the outcome, raw and with covariates regressed out (whole population).
        d = df.with_columns(y_pct=pl.col(col + "_pct"),
                            y_adj=pl.Series(residualize(df[col + "_pct"].to_numpy(),
                                                        df.select([c + "_pct" for c in covs]).to_numpy())) + 0.5)
        rows = []
        for name, cond in groups.items():
            g = d.filter(cond)
            rows.append({"group": name, "n": g.height, "pct_mean": g["y_pct"].mean(), "adj_mean": g["y_adj"].mean(),
                         f"{col}_median": g[col].median(), "share_generalization": (g["role"] == "Generalization").mean()})
        gtab = pl.DataFrame(rows)
        gtab.write_csv(out / f"{oname}_groups.csv")

        comp_rows = []
        for name, (a_cond, b_cond) in comparisons.items():
            a, b = d.filter(a_cond), d.filter(b_cond)
            res = {"comparison": name, "n_a": a.height, "n_b": b.height}
            for kind in ["pct", "adj"]:
                x, y = a[f"y_{kind}"].to_numpy(), b[f"y_{kind}"].to_numpy()
                diffs = [rng.choice(x, len(x)).mean() - rng.choice(y, len(y)).mean() for _ in range(config["bootstrap_n"])]
                res |= {f"{kind}_diff_points": 100 * (x.mean() - y.mean()),
                        f"{kind}_ci_lo": 100 * float(np.quantile(diffs, 0.025)),
                        f"{kind}_ci_hi": 100 * float(np.quantile(diffs, 0.975)), f"{kind}_auc": auc(x, y)}
            comp_rows.append(res)
        comps = pl.DataFrame(comp_rows)
        comps.write_csv(out / f"{oname}_comparisons.csv")

        # Interaction within the pool: outcome pct ~ critic + G + critic x G + covariates.
        p = d.filter(pool)
        X = np.column_stack([np.ones(p.height), p["critic"].cast(pl.Float64), (p["role"] == "Generalization").cast(pl.Float64),
                             (p["critic"] & (p["role"] == "Generalization")).cast(pl.Float64)]
                            + [p[c + "_pct"].to_numpy() for c in covs])
        names = ["intercept", "critic", "generalization", "critic x generalization"] + [c + "_pct" for c in covs]
        yv = p["y_pct"].to_numpy()
        beta = np.linalg.lstsq(X, yv, rcond=None)[0]
        boots = []
        for _ in range(config["bootstrap_n"]):
            idx = rng.integers(0, len(yv), len(yv))
            boots.append(np.linalg.lstsq(X[idx], yv[idx], rcond=None)[0])
        boots = np.array(boots)
        reg = pl.DataFrame({"term": names, "coef_points": 100 * beta, "ci_lo": 100 * np.quantile(boots, 0.025, axis=0),
                            "ci_hi": 100 * np.quantile(boots, 0.975, axis=0)})
        reg.write_csv(out / f"{oname}_regression.csv")
        printed.append((oname, covs, gtab, comps, reg))

    summary = (f"population (Fang + CD, random sample): {df.height:,}; cite a top foundation: {df['cites_foundation'].sum():,}; "
               f"of those can critique: {df.filter(pool).height:,}; critics: {df.filter(pool & pl.col('critic')).height:,}\n"
               "Outcomes are within-publication-year percentiles; 'adj' regresses out each outcome's covariates.\n"
               "Critics come from similarity attribution (~25% precise per critique), which dilutes any difference.\n")
    (out / "summary.txt").write_text(summary)
    with pl.Config(tbl_rows=30, tbl_width_chars=220, float_precision=3, fmt_str_lengths=60):
        print(summary)
        for oname, covs, gtab, comps, reg in printed:
            print(f"===== outcome: {oname} (adj removes {covs})")
            print(gtab)
            print(comps.select("comparison", "n_a", "n_b", "pct_diff_points", "pct_ci_lo", "pct_ci_hi",
                               "adj_diff_points", "adj_ci_lo", "adj_ci_hi", "adj_auc"))
            print(reg)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
