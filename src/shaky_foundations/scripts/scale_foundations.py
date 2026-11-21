"""Shakiness and displacement for the top-N cited foundations: are shakier foundations dropped later?

Outputs to output_dir:
  foundations_scored.csv   per foundation: critics, conc_all / conc_early (rarefied concentration),
                           top limitation, retention (citation-only displacement), pilot kind
  hits.parquet             every critique attributed to a candidate foundation (margin applied)
  community_shares.csv     per foundation-year share of its early neighbourhood that cites it
  relation.csv             Spearman of shakiness vs retention, raw and partial (year, log citations)
  figures/<run>_shaky_vs_retention.png (track figures folder)
  summary.txt

    uv run python src/shaky_foundations/scripts/scale_foundations.py configs/shaky_foundations/scale_foundations.yaml
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

import matplotlib
import numpy as np
import polars as pl

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.critiques import attribute, load_inputs, rarefied_concentration
from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.displacement import community_shares, retention
from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "foundation_year_min", "foundation_year_max",
            "n_foundations", "pilot_config", "critique_type", "critique_lens", "citer_year_min", "citer_year_max",
            "vector_layer", "ref_exclude_lenses", "ref_atom_types", "margin", "same_limitation_layer", "concentration_layer",
            "rarefy_n", "rarefy_reps", "early_window_years", "early_years", "top_k_partners", "min_partners",
            "min_community", "tail_years", "messenger_atom_types", "seed"]
INK, MUTED, SURFACE, GRID = "#1a1a19", "#6b6a66", "#fcfcfb", "#e6e5e1"


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")


def spearman_partial(df: pl.DataFrame, x: str, y: str, covs: list[str]) -> tuple[float, float, int]:
    d = df.drop_nulls([x, y] + covs)
    r = {c: d[c].rank("average").to_numpy() for c in [x, y] + covs}
    raw = float(np.corrcoef(r[x], r[y])[0, 1])
    z = np.column_stack([np.ones(d.height)] + [r[c] for c in covs])
    res = {k: r[k] - z @ np.linalg.lstsq(z, r[k], rcond=None)[0] for k in [x, y]}
    return raw, float(np.corrcoef(res[x], res[y])[0, 1]), d.height


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

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    n = 40 if args.debug else config["n_foundations"]
    fnd = con.sql(f"""
        SELECT pid, title, year, cites_lacuna_2025 FROM papers
        WHERE pid = canonical_pid AND n_atoms > 0
          AND year BETWEEN {int(config['foundation_year_min'])} AND {int(config['foundation_year_max'])}
        ORDER BY cites_lacuna_2025 DESC NULLS LAST LIMIT {int(n)}
    """).pl()
    pilot = load_config(config["pilot_config"])["foundations"]
    kinds = pl.DataFrame({"t": [f["title"].lower().strip() for f in pilot], "kind": [f["kind"] for f in pilot]})
    fnd = fnd.with_columns(t=pl.col("title").str.to_lowercase().str.strip_chars()).join(kinds, on="t", how="left").drop("t")

    t = time.time()
    inputs = load_inputs(con, fnd["pid"].to_list(), config)
    print({k: v.height for k, v in inputs.items()}, f"{time.time() - t:.1f}s")
    centroids = np.load(Path(config["lacuna_dir"]) / f"centroids_{config['vector_layer']}.npy")
    t = time.time()
    attr = attribute(inputs, centroids).join(inputs["critiques"].select(["atom_id", "gid", "kid", "text"]), on="atom_id")
    print(f"attributed {attr.height:,} critiques: {time.time() - t:.0f}s")

    hits = (attr.filter(pl.col("margin") >= config["margin"]).rename({"best_ref": "foundation"})
            .join(inputs["citers"], on=["citer", "foundation"])
            .join(fnd.select(pl.col("pid").alias("foundation"), pl.col("year").alias("fyear")), on="foundation"))
    hits.select(["atom_id", "citer", "foundation", "year", "gid", "kid", "margin", "text"]).write_parquet(out / "hits.parquet")
    klabels = dict(con.sql(f"SELECT concept_id, label FROM concepts_{config['concentration_layer']}").fetchall())
    # Messenger flag: if the foundation's own atoms already sit in its top limitation concept, it is
    # the paper that *diagnosed* the limitation (e.g. "Deeper Insights into GCNs" on over-smoothing),
    # not the foundation that has it. Reviews/surveys summarise limitations and are flagged too.
    con.register("fnd_pids", fnd.select("pid"))
    # Only the foundation's claims count (mechanism/principle/finding), not its self-admitted
    # limitations: a foundation naming its own limitation is not a messenger.
    mtypes = ", ".join(f"'{t}'" for t in config["messenger_atom_types"])
    own = con.sql(f"""SELECT pid, {config['concentration_layer']} AS kid FROM atoms
                      WHERE run_rank = 1 AND type IN ({mtypes}) AND pid IN (SELECT pid FROM fnd_pids)""").pl()
    rows = []
    for (f,), g in hits.group_by(["foundation"]):
        early = g.filter(pl.col("year") <= pl.col("fyear") + config["early_window_years"])
        kid, n_top = g.group_by("kid").agg(n=pl.col("citer").n_unique()).sort(["n", "kid"], descending=[True, False]).row(0)
        rows.append({"pid": f, "n_critics": g["citer"].n_unique(), "n_critics_early": early["citer"].n_unique(),
                     "conc_all": rarefied_concentration(g["kid"].to_numpy(), g["citer"].to_numpy(), config["rarefy_n"], config["rarefy_reps"], rng),
                     "conc_early": rarefied_concentration(early["kid"].to_numpy(), early["citer"].to_numpy(), config["rarefy_n"], config["rarefy_reps"], rng),
                     "top_limitation": klabels[kid], "top_share_raw": n_top / g["citer"].n_unique(),
                     "own_atoms_in_top": own.filter((pl.col("pid") == f) & (pl.col("kid") == kid)).height})
    shaky = pl.DataFrame(rows).with_columns(pl.col("conc_all", "conc_early").fill_nan(None))  # too few critics -> null

    t = time.time()
    shares = community_shares(con, fnd, config["early_years"], config["top_k_partners"], config["min_partners"],
                              config["citer_year_max"])
    shares.write_csv(out / "community_shares.csv")
    ret = retention(shares, config["min_community"], config["tail_years"], config["citer_year_max"])
    print(f"displacement: {time.time() - t:.0f}s")

    able = attr.select("citer").unique().with_columns(able=pl.lit(True))
    rate = (inputs["citers"].join(able, on="citer", how="left").group_by("foundation")
            .agg(n_citers=pl.len(), n_able=pl.col("able").sum()))
    scored = (fnd.join(shaky, on="pid", how="left").join(ret.rename({"foundation": "pid"}), on="pid", how="left")
              .join(rate.rename({"foundation": "pid"}), on="pid", how="left")
              .with_columns(critic_rate=pl.col("n_critics") / pl.col("n_able"),
                            log_cites=(pl.col("cites_lacuna_2025") + 1).log(),
                            is_review=pl.col("title").str.contains(r"(?i)\b(survey|review|overview|tutorial|primer)\b"))
              .with_columns(messenger=(pl.col("own_atoms_in_top") > 0) | pl.col("is_review"))
              .sort("conc_all", descending=True, nulls_last=True))
    scored.write_csv(out / "foundations_scored.csv")

    rel = []
    for subset, df in [("all", scored), ("non_messenger", scored.filter(~pl.col("messenger")))]:
        for x in ["conc_all", "conc_early", "critic_rate"]:
            raw, part, nn = spearman_partial(df, x, "retention", ["year", "log_cites"])
            rel.append({"subset": subset, "shakiness": x, "vs": "retention", "spearman": raw,
                        "partial_year_logcites": part, "n": nn})
    relation = pl.DataFrame(rel)
    relation.write_csv(out / "relation.csv")

    d = scored.filter(~pl.col("messenger")).drop_nulls(["conc_all", "retention"])
    fig, ax = plt.subplots(figsize=(7.5, 5.5), facecolor=SURFACE)
    ax.scatter(d["conc_all"], d["retention"], s=14, color="#9fb8d9", edgecolor=SURFACE, linewidth=0.6, zorder=2)
    for kind, color in [("crack", "#256abf"), ("control", "#e34948")]:
        k = d.filter(pl.col("kind") == kind)
        ax.scatter(k["conc_all"], k["retention"], s=46, color=color, edgecolor=SURFACE, linewidth=1.5, zorder=3,
                   label=f"pilot {kind}")
        for r in k.iter_rows(named=True):
            ax.annotate(r["title"][:22], (r["conc_all"], r["retention"]), fontsize=6.5, color=INK,
                        xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel(f"shakiness: concentration on one limitation (rarefied to {config['rarefy_n']} critics)", color=INK)
    ax.set_ylabel("retention: neighbourhood still citing it, 2024–25 vs peak", color=INK)
    ax.set_title(f"Top {fnd.height} cited AI foundations (2010–2019), messengers and reviews removed", loc="left",
                 fontsize=11, color=INK)
    ax.grid(color=GRID, lw=0.7)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figure_path(out, "shaky_vs_retention.png"), dpi=160, facecolor=SURFACE)
    plt.close(fig)

    summary = (f"foundations: {fnd.height}; with >= {config['rarefy_n']} critics: {scored['conc_all'].is_not_null().sum()} "
               f"(early window: {scored['conc_early'].is_not_null().sum()}); with retention: {scored['retention'].is_not_null().sum()}\n")
    (out / "summary.txt").write_text(summary)
    with pl.Config(tbl_rows=40, tbl_width_chars=220, fmt_str_lengths=48, float_precision=3):
        print(summary)
        print(relation)
        print(scored.group_by("messenger").agg(pl.len(), pl.col("conc_all").median()))
        print(scored.filter(~pl.col("messenger")).select(["title", "year", "kind", "n_critics", "conc_all", "conc_early",
                                                          "retention", "top_limitation"]).head(30))
        print(scored.filter(pl.col("kind").is_not_null()).select(["title", "kind", "messenger", "conc_all", "conc_early", "retention"]))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
