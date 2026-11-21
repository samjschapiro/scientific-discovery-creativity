"""How many "most cited" papers are actually foundations?

For each candidate list (the scale-up sets) and a random baseline of ordinary papers from the same years,
compute Foundation / Extension / Generalization indices inside Lacuna (efg.py). A paper counts as a
foundation if its Foundation index is above the 90th percentile of its baseline (later work builds on it
as a community far more than usual); "F-dominant" (F is its largest share) is reported too. Each paper is
also typed from its title (survey, technical report, dataset, software, or method/idea).

For 2010–2019 papers our indices are checked against Fang & Evans's published ones (all of OpenAlex).

Outputs: config.yaml, papers.csv, summary.csv, validation.txt

    uv run python src/shaky_foundations/scripts/foundation_status.py configs/shaky_foundations/foundation_status.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.disruption import build_edges
from src.shaky_foundations.efg import compute_efg
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "fang_efg_path", "sets", "window_years", "year_cap",
            "baseline_per_set", "min_citers", "seed", "kinds"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    for name, path in config["sets"].items():
        if not Path(path).exists():
            raise FileNotFoundError(f"FATAL: set '{name}' file not found: {path}")


def kind_of(title: str, kinds: dict) -> str:
    import re
    for name, rx in kinds.items():
        if re.search(rx, title or "", flags=re.IGNORECASE):
            return name
    return "method / idea"


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

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    frames = []
    for name, path in config["sets"].items():
        s = pl.read_csv(path).select(pl.col("pid").cast(pl.Int64), "title", pl.col("year").cast(pl.Int64))
        if args.debug:
            s = s.head(20)
        frames.append(s.with_columns(set=pl.lit(name), group=pl.lit("most cited")))
        y0, y1 = s["year"].min(), s["year"].max()
        n_base = 200 if args.debug else config["baseline_per_set"]
        base = con.sql(f"""
            SELECT pid, title, year FROM papers
            WHERE pid = canonical_pid AND year BETWEEN {int(y0)} AND {int(y1)}
              AND cites_lacuna >= {int(config['min_citers'])}
            ORDER BY hash(pid, {int(config['seed'])}) LIMIT {int(n_base)}
        """).pl().with_columns(pl.col("pid").cast(pl.Int64), pl.col("year").cast(pl.Int64))
        frames.append(base.with_columns(set=pl.lit(name), group=pl.lit("baseline")))
    cand = pl.concat(frames).with_columns(pl.col("pid").cast(pl.Int64), pl.col("year").cast(pl.Int64))
    con.register("cand_df", cand.select("pid", "year").unique())
    con.execute("CREATE OR REPLACE TEMP TABLE focal AS SELECT * FROM cand_df")
    build_edges(con)
    compute_efg(con, config["window_years"], config["year_cap"])
    efg = con.sql("SELECT * FROM efg").pl().with_columns(pl.col("pid").cast(pl.Int64))
    fang = con.sql(f"""SELECT p.pid, f.f_y5 AS fang_f, f.g_y5 AS fang_g FROM papers p
                        JOIN read_parquet('{config['fang_efg_path']}') f ON f.id = p.openalex_id
                        WHERE p.pid IN (SELECT pid FROM cand_df)""").pl().with_columns(pl.col("pid").cast(pl.Int64))

    df = (cand.join(efg, on="pid", how="left").join(fang, on="pid", how="left")
          .filter(pl.col("n_citers") >= config["min_citers"])
          .with_columns(kind=pl.col("title").map_elements(lambda t: kind_of(t, config["kinds"]), return_dtype=pl.Utf8),
                        f_dominant=(pl.col("efg_f") >= pl.col("efg_e")) & (pl.col("efg_f") >= pl.col("efg_g"))))
    p90 = df.filter(pl.col("group") == "baseline").group_by("set").agg(f_p90=pl.col("efg_f").quantile(0.9))
    df = df.join(p90, on="set").with_columns(foundation=pl.col("efg_f") > pl.col("f_p90"))
    df.write_csv(out / "papers.csv")

    v = df.filter(pl.col("fang_f").is_not_null() & (pl.col("group") == "most cited"))
    vb = df.filter(pl.col("fang_f").is_not_null())
    (out / "validation.txt").write_text(
        f"own vs Fang & Evans Foundation index, Spearman: most-cited n={v.height}: "
        f"{v.select(pl.corr('efg_f', 'fang_f', method='spearman')).item():.2f}; all with Fang n={vb.height}: "
        f"{vb.select(pl.corr('efg_f', 'fang_f', method='spearman')).item():.2f}\n"
        f"Generalization index: {vb.select(pl.corr('efg_g', 'fang_g', method='spearman')).item():.2f}\n")

    summary = (df.group_by("set", "group").agg(
                   n=pl.len(), foundation=pl.col("foundation").mean(), f_dominant=pl.col("f_dominant").mean(),
                   median_f=pl.col("efg_f").median(), median_g=pl.col("efg_g").median(),
                   method_idea=(pl.col("kind") == "method / idea").mean())
               .sort("set", "group", descending=[False, True]))
    summary.write_csv(out / "summary.csv")
    kinds = (df.filter(pl.col("group") == "most cited").group_by("set", "kind")
             .agg(n=pl.len(), foundation=pl.col("foundation").mean()).sort("set", "n", descending=[False, True]))
    kinds.write_csv(out / "kinds.csv")
    with pl.Config(tbl_rows=40, tbl_width_chars=200, float_precision=2):
        print((out / "validation.txt").read_text())
        print(summary)
        print(kinds)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
