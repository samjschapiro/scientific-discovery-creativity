"""Type each citation of a foundation from the two papers' Lacuna atoms (no citation contexts needed).

For every citation (citing paper c -> foundation f) of the pilot foundations:
  s_mech = max cosine between c's mechanism atoms and f's mechanism/principle atoms
  s_prob = max cosine between c's problem atoms and f's problem atoms
  critique = one of c's critique atoms is attributed to f (pilot_critiques proxy attribution)
Types:
  critique      c raises a limitation of f
  builds on     same kind of method, same problem (s_mech high, s_prob high)
  transfers     same kind of method, different problem (s_mech high, s_prob low)
  alternative   same problem, different method (s_mech low, s_prob high)
  background    neither
  no atoms      c lacks mechanism or problem atoms
Each citation also gets Fang & Evans's structural label (efg.citation_labels), so content types can be
compared with structure: does "transfers" line up with Generalization?

Outputs: config.yaml, citations.parquet, type_by_efg.csv, by_foundation.csv, examples.csv, summary.txt

    uv run python src/shaky_foundations/scripts/cite_types.py configs/shaky_foundations/cite_types.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.critiques import match_foundations
from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.disruption import build_edges
from src.shaky_foundations.efg import citation_labels, compute_efg
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "pilot_config", "critiques_path", "critique_margin",
            "vector_layer", "citer_year_max", "efg_window_years", "high_quantile", "examples_per_type", "seed"]
TYPES = ["critique", "builds on", "transfers", "alternative", "background", "no atoms"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")


def best_sims(citer_atoms: pl.DataFrame, f_cids: np.ndarray, cent: np.ndarray) -> dict[int, tuple[float, str]]:
    """{citer: (max cosine to any of the foundation's atoms, atom_id of the best citer atom)}."""
    if citer_atoms.height == 0 or len(f_cids) == 0:
        return {}
    a = citer_atoms.sort("citer")
    sims = (cent[a["cid"].to_numpy()].astype(np.float32) @ cent[f_cids].astype(np.float32).T).max(axis=1)
    citers = a["citer"].to_numpy()
    starts = np.flatnonzero(np.r_[True, citers[1:] != citers[:-1]])
    seg_max = np.maximum.reduceat(sims, starts)
    ids = a["atom_id"].to_numpy()
    out = {}
    for i, s0 in enumerate(starts):
        s1 = starts[i + 1] if i + 1 < len(starts) else len(sims)
        j = s0 + int(np.argmax(sims[s0:s1]))
        out[int(citers[s0])] = (float(seg_max[i]), ids[j])
    return out


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
    layer, ymax = config["vector_layer"], config["citer_year_max"]

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    fl = load_config(config["pilot_config"])["foundations"]
    foundations = match_foundations(con, fl[:3] if args.debug else fl)
    fpids = foundations["pid"].to_list()

    # Citations + Fang structural label per citation.
    con.register("fnd", foundations.select("pid", "year"))
    con.execute("CREATE OR REPLACE TEMP TABLE focal AS SELECT pid, year FROM fnd")
    build_edges(con)
    compute_efg(con, config["efg_window_years"], ymax)
    citation_labels(con)
    cits = con.sql("SELECT l.f, l.c, l.efg_label, c.citing_year AS year FROM efg_labels l "
                   "JOIN citations c ON c.citing_pid = l.c AND c.cited_pid = l.f").pl().unique(["f", "c"])

    # Atoms: citers' mechanism + problem atoms; foundations' mechanism/principle + problem atoms.
    con.register("cit_c", cits.select(pl.col("c").alias("pid")).unique())
    atoms = con.sql(f"""SELECT a.pid AS citer, a.atom_id, a.type, a.{layer} AS cid FROM atoms a JOIN cit_c USING (pid)
                        WHERE a.run_rank = 1 AND a.{layer} IS NOT NULL AND a.type IN ('mechanism', 'problem')""").pl()
    fatoms = con.sql(f"""SELECT a.pid AS f, a.type, a.{layer} AS cid FROM atoms a JOIN fnd USING (pid)
                         WHERE a.run_rank = 1 AND a.{layer} IS NOT NULL""").pl()
    cent = np.load(Path(config["lacuna_dir"]) / f"centroids_{layer}.npy")

    rows = []
    for f in fpids:
        fa = fatoms.filter(pl.col("f") == f)
        fm = fa.filter(pl.col("type").is_in(["mechanism", "principle"]))["cid"].to_numpy()
        fp = fa.filter(pl.col("type") == "problem")["cid"].to_numpy()
        cf = cits.filter(pl.col("f") == f)
        sub = atoms.filter(pl.col("citer").is_in(cf["c"].implode()))
        sm = best_sims(sub.filter(pl.col("type") == "mechanism"), fm, cent)
        sp = best_sims(sub.filter(pl.col("type") == "problem"), fp, cent)
        for c in cf["c"].to_list():
            m, p = sm.get(c), sp.get(c)
            rows.append({"f": f, "c": c, "s_mech": m[0] if m else None, "s_prob": p[0] if p else None,
                         "mech_atom": m[1] if m else None, "prob_atom": p[1] if p else None})
    sims = pl.DataFrame(rows, schema={"f": pl.Int64, "c": pl.Int64, "s_mech": pl.Float64, "s_prob": pl.Float64,
                                      "mech_atom": pl.Utf8, "prob_atom": pl.Utf8})

    crit = (pl.read_parquet(config["critiques_path"]).filter(pl.col("margin") >= config["critique_margin"])
            .select(pl.col("citer").cast(pl.Int64).alias("c"), pl.col("best_ref").cast(pl.Int64).alias("f"))
            .unique().with_columns(critique=pl.lit(True)))
    # "High" = top (1 - high_quantile) of all scored citations, pooled across foundations: the centroid proxy
    # compresses similarities (median ~0.87), so fixed cosine cut-offs are meaningless.
    mh = float(sims["s_mech"].drop_nulls().quantile(config["high_quantile"]))
    ph = float(sims["s_prob"].drop_nulls().quantile(config["high_quantile"]))
    df = (cits.with_columns(pl.col("f").cast(pl.Int64), pl.col("c").cast(pl.Int64))
          .join(sims, on=["f", "c"], how="left").join(crit, on=["f", "c"], how="left")
          .with_columns(pl.col("critique").fill_null(False))
          .with_columns(cite_type=pl.when(pl.col("critique")).then(pl.lit("critique"))
                        .when(pl.col("s_mech").is_null() | pl.col("s_prob").is_null()).then(pl.lit("no atoms"))
                        .when((pl.col("s_mech") >= mh) & (pl.col("s_prob") >= ph)).then(pl.lit("builds on"))
                        .when(pl.col("s_mech") >= mh).then(pl.lit("transfers"))
                        .when(pl.col("s_prob") >= ph).then(pl.lit("alternative"))
                        .otherwise(pl.lit("background")))
          .join(foundations.select(pl.col("pid").alias("f"), pl.col("title").alias("foundation"), "kind"), on="f"))
    df.write_parquet(out / "citations.parquet")

    typed = df.filter(pl.col("cite_type") != "no atoms")
    tab = (typed.filter(pl.col("efg_label") != "tie").group_by("cite_type", "efg_label").len()
           .pivot(on="efg_label", index="cite_type", values="len").fill_null(0)
           .with_columns(total=pl.sum_horizontal("Foundation", "Extension", "Generalization"))
           .with_columns([(pl.col(c) / pl.col("total")).alias(f"{c}_share") for c in ["Foundation", "Extension", "Generalization"]]))
    tab = tab.sort(pl.col("cite_type").replace_strict({t: i for i, t in enumerate(TYPES)}, default=99))
    tab.write_csv(out / "type_by_efg.csv")
    byf = (df.group_by("foundation", "kind", "cite_type").len()
           .with_columns(share=pl.col("len") / pl.col("len").sum().over("foundation"))
           .pivot(on="cite_type", index=["foundation", "kind"], values="share").fill_null(0))
    byf.write_csv(out / "by_foundation.csv")

    # Examples per type, with the atoms that drove the call, for reading.
    ex = (typed.filter(pl.col("cite_type") != "critique")
          .with_columns(r=pl.int_range(pl.len()).shuffle(seed=config["seed"]).over("cite_type"))
          .filter(pl.col("r") < config["examples_per_type"]))
    con.register("ex_atoms", pl.concat([ex.select(pl.col("mech_atom").alias("atom_id")), ex.select(pl.col("prob_atom").alias("atom_id"))]).drop_nulls().unique())
    texts = dict(con.sql("SELECT atom_id, text FROM atoms JOIN ex_atoms USING (atom_id)").fetchall())
    titles = con.sql("SELECT pid AS c, title AS citer_title FROM papers").pl().with_columns(pl.col("c").cast(pl.Int64))
    ex = (ex.join(titles, on="c", how="left")
          .with_columns(mech_text=pl.col("mech_atom").replace_strict(texts, default=None),
                        prob_text=pl.col("prob_atom").replace_strict(texts, default=None))
          .select("cite_type", "foundation", "citer_title", "efg_label", "s_mech", "s_prob", "mech_text", "prob_text")
          .sort("cite_type"))
    ex.write_csv(out / "examples.csv")

    q = typed.select([pl.col(c).quantile(x).alias(f"{c}_q{int(x * 100)}") for c in ["s_mech", "s_prob"] for x in [0.25, 0.5, 0.75, 0.9]])
    summary = (f"foundations: {len(fpids)}; citations: {df.height:,}; typed (citer has mechanism + problem atoms): {typed.height:,}\n"
               f"thresholds (q{config['high_quantile']}): mech_high {mh:.3f}, prob_high {ph:.3f}\nsimilarity quantiles: {q.to_dicts()[0]}\n"
               f"type shares: {typed['cite_type'].value_counts(normalize=True).sort('proportion', descending=True).rows()}\n")
    (out / "summary.txt").write_text(summary)
    with pl.Config(tbl_rows=30, tbl_width_chars=220, float_precision=3, fmt_str_lengths=40):
        print(summary)
        print(tab)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
