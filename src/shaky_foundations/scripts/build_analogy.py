"""Analogical novelty scores for the build_measures paper pool (see analogy.py for definitions).

Outputs to output_dir:
    config.yaml
    analogy_atoms.parquet   one row per mechanism atom: transfer distance, home size, established
    analogy.parquet         one row per paper: analogy_max, analogy_mean, counts, log_home_size
    summary.txt

    uv run python src/shaky_foundations/scripts/build_analogy.py configs/shaky_foundations/build_analogy.yaml
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.analogy import (VARIANTS, atom_transfer, focal_atoms, mechanism_homes,
                                           mechanism_paper_counts, paper_scores, similarity_matrix)
from src.shaky_foundations.data import open_lacuna
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "measures_path", "layer", "min_home_papers",
            "min_pair_papers", "debug_sample_size", "seed"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not config["layer"].startswith("f"):
        raise ValueError("FATAL: layer must be a frozen (f*) layer; c* layers use hindsight")
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
    layer = config["layer"]

    t = time.time()
    sim = similarity_matrix(str(Path(config["lacuna_dir"]) / f"centroids_{layer}.npy"))
    print(f"similarity matrix {sim.shape}: {time.time() - t:.1f}s")
    t = time.time()
    homes = mechanism_homes(con, layer, int(focal["year"].max()))
    counts = mechanism_paper_counts(con)
    atoms = focal_atoms(con, layer)
    print(f"homes {homes.height:,} (m, p, year) rows, focal atoms {atoms.height:,}: {time.time() - t:.1f}s")
    t = time.time()
    per_atom = atom_transfer(atoms, homes, counts, sim, config["min_home_papers"], config["min_pair_papers"])
    papers = paper_scores(per_atom)
    print(f"transfer: {time.time() - t:.1f}s")

    per_atom.write_parquet(out / "analogy_atoms.parquet")
    papers.write_parquet(out / "analogy.parquet")
    est = per_atom.filter(pl.col("established"))
    summary = (
        f"focal papers: {focal.height:,}; with >=1 scored mechanism: {papers['analogy_nn1_max'].is_not_null().sum():,}\n"
        f"mechanism atoms with a problem in the paper: {per_atom.height:,}; established: {est.height:,} "
        f"({est.height / per_atom.height:.1%})\n"
    )
    for v in VARIANTS:
        x = est[v].drop_nulls()
        summary += (f"{v}: n={x.len():,}, zero={(x == 0).mean():.1%}, p10/median/p90 = "
                    f"{x.quantile(0.1):.3f} / {x.median():.3f} / {x.quantile(0.9):.3f}\n")
    (out / "summary.txt").write_text(summary)
    print(summary + f"done -> {out}")


if __name__ == "__main__":
    main()
