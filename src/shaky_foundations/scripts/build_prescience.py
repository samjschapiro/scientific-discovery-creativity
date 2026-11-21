"""Prescience and emergence (prescience.py) for the build_measures paper pool.

Outputs: config.yaml, prescience.parquet (pid + measures), summary.txt

    uv run python src/shaky_foundations/scripts/build_prescience.py configs/shaky_foundations/build_prescience.yaml
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.prescience import compute_prescience
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "measures_path", "layer", "future_years", "recent_years",
            "adoption_min", "eps", "debug_sample_size", "seed"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not config["layer"].startswith("f"):
        raise ValueError("FATAL: layer must be a frozen (f*) layer")
    if not Path(config["measures_path"]).exists():
        raise FileNotFoundError(f"FATAL: {config['measures_path']} not found; run build_measures first")


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

    focal = pl.read_parquet(config["measures_path"], columns=["pid", "year"])
    if args.debug:
        focal = focal.sample(n=config["debug_sample_size"], seed=config["seed"])
    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    con.register("focal_df", focal)
    con.execute("CREATE TEMP TABLE focal AS SELECT * FROM focal_df")
    t = time.time()
    compute_prescience(con, config["layer"], config["future_years"], config["recent_years"], config["adoption_min"],
                       config["eps"])
    res = con.sql("SELECT * FROM prescience").pl()
    print(f"computed for {res.height:,} papers: {time.time() - t:.0f}s")
    res.write_parquet(out / "prescience.parquet")
    cols = ["novel_share", "prescience", "novel_pair_adoption", "emergence"]
    desc = res.select([pl.col(c).quantile(q).alias(f"{c}_q{int(q * 100)}") for c in cols for q in [0.1, 0.5, 0.9]])
    summary = (f"papers: {res.height:,}; with a novel pair (prescience defined): {res['prescience'].is_not_null().sum():,}; "
               f"\n{desc.to_dicts()[0]}\n")
    (out / "summary.txt").write_text(summary)
    print(summary + f"done -> {out}")


if __name__ == "__main__":
    main()
