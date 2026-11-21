"""Pilot: do critique curves rise before known paradigm cracks, and stay flat for controls?

Attributes every citing paper's critique atoms to its references (critiques.py), then for each
pilot foundation:

  foundations.csv          matched foundations (pid, citations, kind, crack, successor)
  attributions.parquet     every critique: best and runner-up reference, similarities, margin
  curves.csv               per foundation-year: citers, citers able to critique, critics, rate,
                           chance rate
  figures/<run>_<method>_curves.png (track figures folder): small multiples of rate vs chance, successor year marked
  same_limitation.csv      per foundation: concentration (share of critics in the top limitation
                           concept, coarse layer) and onset year vs successor year
  top_limitations.csv      per foundation, the most common attributed limitation concepts
                           (distinct citers), with example critiques: the "same limitation" signal
  precision_sample.csv     random attributions per foundation for hand labelling
  summary.txt

Every per-method file is written twice, prefixed proxy_ (centroid proxy, all critiques) and emb_
(real bge-large vectors re-ranking each critique's proxy top-k shortlist; only critiques with a
pilot foundation in the shortlist). Plus:

  label_pool.csv           (critique, foundation) pairs attributed by either method, sampled per
                           foundation, for hand labelling -> precision of both methods on one pool
  emb_patch_scores.csv     per (critic, foundation): similarity of the critic's mechanism to the
                           foundation's; patchers propose a variant of the foundation itself

    uv run python src/shaky_foundations/scripts/pilot_critiques.py configs/shaky_foundations/pilot_critiques.yaml
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

from src.shaky_foundations.critiques import (attribute, foundation_curves, load_inputs, match_foundations,
                                             mechanism_atoms, patch_scores, rescore_with_embeddings,
                                             shortlist_ref_atoms)
from src.shaky_foundations.embeddings import ensure_embedded, load_vectors
from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.figures import figure_path
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "critique_type", "critique_lens", "citer_year_min",
            "citer_year_max", "vector_layer", "ref_exclude_lenses", "ref_atom_types", "margin", "same_limitation_layer", "concentration_layer", "first_year_min_critics", "top_limitations",
            "precision_sample_per_foundation", "label_pool_per_foundation", "embedding", "seed", "foundations"]
INK, MUTED, SURFACE, GRID = "#1a1a19", "#6b6a66", "#fcfcfb", "#e6e5e1"
CRACK, CONTROL = "#256abf", "#8a8984"


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for f in config["foundations"]:
        if f.get("kind") not in {"crack", "control"}:
            raise ValueError(f"FATAL: foundation kind must be crack/control: {f}")
        if f["kind"] == "crack" and not all(k in f for k in ["crack", "successor", "successor_year"]):
            raise ValueError(f"FATAL: crack foundations need crack, successor, successor_year: {f}")


def short(title: str, n: int = 34) -> str:
    return title if len(title) <= n else title[: n - 1].rstrip() + "…"


def plot(curves: pl.DataFrame, foundations: pl.DataFrame, min_able: int, path: Path) -> None:
    order = foundations.sort(["kind", "cites_lacuna_2025"], descending=[False, True])
    n = order.height
    ncol = 4
    nrow = -(-n // ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 2.5 * nrow), sharex=True, sharey=True,
                             facecolor=SURFACE)
    ymax = curves.filter(pl.col("n_able") >= min_able)["rate"].max() * 1.1
    for ax, f in zip(axes.flat, order.iter_rows(named=True)):
        c = curves.filter((pl.col("foundation") == f["pid"]) & (pl.col("n_able") >= min_able)).sort("year")
        color = CRACK if f["kind"] == "crack" else CONTROL
        ax.plot(c["year"], c["chance_rate"], color=MUTED, lw=1.2, ls=":")
        ax.plot(c["year"], c["rate"], color=color, lw=2)
        if f["successor_year"] is not None:
            ax.axvline(f["successor_year"], color=MUTED, lw=1, ls="--")
            ax.text(f["successor_year"] + 0.2, ymax * 0.93, short(f["successor"], 22), fontsize=6.5,
                    color=MUTED, va="top")
        ax.axvline(f["year"], color=GRID, lw=3, zorder=0)
        ax.set_title(short(f["title"]) + ("" if f["kind"] == "crack" else "  (control)"), fontsize=8, loc="left",
                     color=INK)
        ax.set_ylim(0, ymax)
        ax.grid(axis="y", color=GRID, lw=0.7)
        ax.tick_params(labelsize=7, colors=MUTED, length=0)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        for s in ["left", "bottom"]:
            ax.spines[s].set_color(GRID)
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    fig.suptitle("Share of citing papers whose critique atoms are attributed to the foundation "
                 "(solid) vs chance (dotted); grey bar = publication year, dashed = successor",
                 fontsize=9, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def report(tag: str, hits_attr: pl.DataFrame, able_attr: pl.DataFrame, margin: float, foundations: pl.DataFrame,
           inputs: dict, con, config: dict, out: Path, patch: pl.DataFrame | None = None) -> pl.DataFrame:
    """Curves, same-limitation concentration/onset, top limitations and a precision sample for one
    attribution method. Returns the foundation-attributed hits (margin applied)."""
    curves = foundation_curves(foundations, inputs["citers"], able_attr, margin, hits_from=hits_attr)
    curves.write_csv(out / f"{tag}_curves.csv")
    plot(curves, foundations, min_able=30, path=figure_path(out, f"{tag}_curves.png"))

    titles = con.sql("SELECT pid, title FROM papers").pl()
    labels = con.sql(f"SELECT concept_id AS gid, label FROM concepts_{config['same_limitation_layer']}").pl()
    hits = hits_attr.filter(pl.col("margin") >= margin).join(
        foundations.select(pl.col("pid").alias("best_ref"), pl.col("title").alias("foundation")), on="best_ref")
    top = (hits.group_by(["foundation", "gid"]).agg(n_citers=pl.col("citer").n_unique(), examples=pl.col("text").head(3))
           .sort(["foundation", "n_citers"], descending=[False, True])
           .group_by("foundation", maintain_order=True).head(config["top_limitations"])
           .join(labels, on="gid", how="left")
           .with_columns(pl.col("examples").list.eval(pl.element().str.slice(0, 220)).list.join(" || ")))
    top.select(["foundation", "n_citers", "label", "examples"]).write_csv(out / f"{tag}_top_limitations.csv")

    # Concentration ("is it the same limitation?") and onset, at a coarser layer so near-duplicate
    # concepts merge. With patch scores, onset is also computed for non-patching critics only.
    klabels = dict(con.sql(f"SELECT concept_id, label FROM concepts_{config['concentration_layer']}").fetchall())
    g_all = hits.join(inputs["citers"].rename({"foundation": "best_ref"}), on=["citer", "best_ref"])
    if patch is not None:
        g_all = g_all.join(patch.rename({"foundation": "best_ref"}), on=["citer", "best_ref"], how="left") \
            .with_columns(patcher=pl.col("patch_score") >= config["embedding"]["patch_threshold"])
    k_min = config["first_year_min_critics"]

    def onset(df):
        y = df.group_by("year").agg(k=pl.col("citer").n_unique()).sort("year")
        return y.filter(pl.col("k").cum_sum() >= k_min)["year"].min()

    rows = []
    for (ref,), g in g_all.group_by(["best_ref"]):
        f = foundations.filter(pl.col("pid") == ref).row(0, named=True)
        kid, n_top = g.group_by("kid").agg(n=pl.col("citer").n_unique()).sort(["n", "kid"], descending=[True, False]).row(0)
        t = g.filter(pl.col("kid") == kid)
        yrs = t.group_by("year").agg(k=pl.col("citer").n_unique()).sort("year")
        row = {"foundation": f["title"], "kind": f["kind"], "year": f["year"], "n_critics": g["citer"].n_unique(),
               "top_limitation": klabels[kid], "n_top": n_top, "concentration": n_top / g["citer"].n_unique(),
               "onset_year": onset(t), "successor_year": f["successor_year"]}
        if patch is not None:
            row |= {"top_patcher_share": t.unique("citer")["patcher"].mean(),
                    "onset_nonpatchers": onset(t.filter(~pl.col("patcher").fill_null(False))),
                    "onset_patchers": onset(t.filter(pl.col("patcher").fill_null(False)))}
        row["top_by_year"] = " ".join(f"{y}:{k}" for y, k in zip(yrs["year"], yrs["k"]))
        rows.append(row)
    same = pl.DataFrame(rows).sort(["kind", "concentration"], descending=[False, True])
    same.write_csv(out / f"{tag}_same_limitation.csv")

    sample = (hits.with_columns(r=pl.int_range(pl.len()).shuffle(seed=config["seed"]).over("best_ref"))
              .filter(pl.col("r") < config["precision_sample_per_foundation"])
              .join(titles.rename({"pid": "second_ref", "title": "runner_up"}), on="second_ref", how="left")
              .select(["foundation", "runner_up", "s1", "s2", "margin", "text"]).sort("foundation"))
    sample.write_csv(out / f"{tag}_precision_sample.csv")
    with pl.Config(tbl_rows=40, tbl_width_chars=220, fmt_str_lengths=45, float_precision=3):
        print(f"--- {tag}: {hits.height:,} critiques attributed to pilot foundations")
        print(same.drop("top_by_year"))
    return hits


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

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    fl = config["foundations"][:3] if args.debug else config["foundations"]
    foundations = match_foundations(con, fl)
    foundations.write_csv(out / "foundations.csv")
    fpids = foundations["pid"].to_list()

    t = time.time()
    inputs = load_inputs(con, fpids, config)
    print({k: v.height for k, v in inputs.items()}, f"{time.time() - t:.1f}s")
    centroids = np.load(Path(config["lacuna_dir"]) / f"centroids_{config['vector_layer']}.npy")
    attr = attribute(inputs, centroids, emb["shortlist_k"])
    meta = inputs["critiques"].select(["atom_id", "gid", "kid", "text"])
    attr = attr.join(meta, on="atom_id")
    attr.write_parquet(out / "proxy_attributions.parquet")
    proxy_hits = report("proxy", attr, attr, config["margin"], foundations, inputs, con, config, out)

    # Embedding re-score of every critique with a pilot foundation in its proxy shortlist.
    sel = attr.filter(pl.col("shortlist").list.eval(pl.element().is_in(fpids)).list.any())
    ref_atoms = shortlist_ref_atoms(con, sel["shortlist"].explode().unique().to_list(), config["ref_exclude_lenses"],
                                    config["ref_atom_types"])
    t = time.time()
    n_new = ensure_embedded(con, sel["atom_id"].to_list() + ref_atoms["atom_id"].to_list(), emb["cache_dir"],
                            emb["model"], emb["device"])
    print(f"embedded {n_new:,} new atoms: {time.time() - t:.0f}s")
    index, vectors = load_vectors(emb["cache_dir"], sel["atom_id"].to_list() + ref_atoms["atom_id"].to_list())
    eattr = rescore_with_embeddings(sel, ref_atoms, index, vectors).join(meta, on="atom_id")
    eattr.write_parquet(out / "emb_attributions.parquet")

    # Patchers: critics whose own mechanism is a variant of the foundation's mechanism.
    critics = eattr.filter((pl.col("margin") >= emb["margin"]) & pl.col("best_ref").is_in(fpids)) \
        .select("citer", pl.col("best_ref").alias("foundation")).unique()
    mech = mechanism_atoms(con, critics["citer"].unique().to_list() + fpids)
    ensure_embedded(con, mech["atom_id"].to_list(), emb["cache_dir"], emb["model"], emb["device"])
    mi, mv = load_vectors(emb["cache_dir"], mech["atom_id"].to_list())
    patch = patch_scores(critics, mech, mi, mv)
    patch.write_csv(out / "emb_patch_scores.csv")
    emb_hits = report("emb", eattr, attr, emb["margin"], foundations, inputs, con, config, out, patch=patch)

    # Labelling pool: (critique, foundation) pairs attributed by either method.
    key = ["atom_id", "best_ref"]
    pool = (pl.concat([proxy_hits.select(key + ["citer", "foundation", "text"]),
                       emb_hits.select(key + ["citer", "foundation", "text"])]).unique(key)
            .join(proxy_hits.select(key).with_columns(by_proxy=pl.lit(True)), on=key, how="left")
            .join(emb_hits.select(key).with_columns(by_emb=pl.lit(True)), on=key, how="left")
            .with_columns(pl.col("by_proxy").fill_null(False), pl.col("by_emb").fill_null(False))
            .join(con.sql("SELECT pid AS citer, title AS citer_title FROM papers").pl(), on="citer"))
    labelled = (pool.with_columns(r=pl.int_range(pl.len()).shuffle(seed=config["seed"]).over("best_ref"))
                .filter(pl.col("r") < config["label_pool_per_foundation"]).drop("r")
                .sort(["foundation", "atom_id"]).with_row_index("label_id")
                .with_columns(label=pl.lit(None, dtype=pl.Int8), note=pl.lit(None, dtype=pl.Utf8)))
    labelled.write_csv(out / "label_pool.csv")

    summary = (f"foundations: {foundations.height}; citer-foundation pairs: {inputs['citers'].height:,}\n"
               f"critique atoms: {inputs['critiques'].height:,}; proxy-attributable: {attr.height:,}\n"
               f"proxy hits on pilot foundations: {proxy_hits.height:,} (margin {config['margin']})\n"
               f"re-scored with embeddings: {eattr.height:,}; emb hits: {emb_hits.height:,} (margin {emb['margin']})\n"
               f"agreement on best ref among re-scored: {(eattr.join(attr.select('atom_id', pl.col('best_ref').alias('p')), on='atom_id').select((pl.col('best_ref') == pl.col('p')).mean()).item()):.1%}\n"
               f"label pool: {labelled.height} pairs ({labelled['by_proxy'].sum()} by proxy, {labelled['by_emb'].sum()} by emb)\n")
    (out / "summary.txt").write_text(summary)
    print(summary + f"done -> {out}")


if __name__ == "__main__":
    main()
