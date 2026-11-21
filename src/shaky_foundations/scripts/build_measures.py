"""Build one paper-level table of creativity measures for a sample of Lacuna AI papers.

Sample: Lacuna papers in [year_min, year_max] that are OpenAlex-matched, have >=1 reference and have
atoms. A seeded random sample of `sample_size`, plus (optionally) every eligible Kedrick gap-opener,
since there are only ~500 of them. `in_random_sample` marks which is which, so analyses can use only
the random sample.

Measures:
    ours      cd (+ n_i, n_j, n_k), dsi, pm_distance, novel_pair_frac, pmi_p10, pmi_median
    external  fang_f/e/g (+ fang_c5), kedrick_class, kedrick_cd (for validating our cd)

Outputs to output_dir: config.yaml, measures.parquet, summary.txt

    uv run python src/shaky_foundations/scripts/build_measures.py configs/shaky_foundations/build_measures.yaml
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.atom_measures import embedding_measures, pair_novelty
from src.shaky_foundations.data import open_lacuna
from src.shaky_foundations.disruption import build_edges, compute_cd
from src.shaky_foundations.external import create_external_views
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "year_min", "year_max", "sample_size",
            "debug_sample_size", "seed", "include_all_gap_openers", "cd_window_years", "vector_layer",
            "novelty_layer", "fang_efg_path", "kedrick_labels_path", "kedrick_cd_path"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if config["vector_layer"] not in {"c2000", "c20000", "c200000", "f2800", "f20000"}:
        raise ValueError(f"FATAL: unknown vector_layer {config['vector_layer']}")
    if not config["novelty_layer"].startswith("f"):
        raise ValueError("FATAL: novelty_layer must be a frozen (f*) layer; c* layers use hindsight")


def select_focal(con, config: dict, n: int) -> None:
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE eligible AS
        SELECT pid, year, openalex_id FROM papers
        WHERE year BETWEEN {int(config['year_min'])} AND {int(config['year_max'])}
          AND matched AND n_refs_total >= 1 AND n_atoms > 0
          AND pid = canonical_pid   -- v2: one entry per work
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE random_part AS
        SELECT pid FROM eligible ORDER BY hash(pid, {int(config['seed'])}) LIMIT {int(n)}
    """)
    extra = ""
    if config["include_all_gap_openers"]:
        extra = """UNION SELECT e.pid FROM eligible e JOIN kedrick k USING (openalex_id)
                   WHERE k.kedrick_class = 'gap_opener'"""
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE focal AS
        SELECT e.pid, e.year, e.openalex_id, (r.pid IS NOT NULL) AS in_random_sample
        FROM (SELECT pid FROM random_part {extra}) s
        JOIN eligible e USING (pid) LEFT JOIN random_part r USING (pid)
    """)


def timed(label, fn, *args):
    t = time.time()
    out = fn(*args)
    print(f"{label}: {time.time() - t:.1f}s")
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

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    create_external_views(con, config["fang_efg_path"], config["kedrick_labels_path"], config["kedrick_cd_path"])

    n = config["debug_sample_size"] if args.debug else config["sample_size"]
    select_focal(con, config, n)
    print(con.sql("SELECT count(*) AS focal, sum(in_random_sample::INT) AS random FROM focal").fetchall())

    timed("edges", build_edges, con)
    timed("cd", compute_cd, con, config["cd_window_years"])
    timed("pair novelty", pair_novelty, con, config["novelty_layer"], config["year_max"])
    centroids = str(Path(config["lacuna_dir"]) / f"centroids_{config['vector_layer']}.npy")
    emb = timed("embedding measures", embedding_measures, con, centroids, config["vector_layer"])
    con.register("emb", emb)

    con.sql("""
        SELECT f.pid, f.year, f.openalex_id, f.in_random_sample, p.title, p.venue, p.n_authors,
               p.cites_total_2025, p.cites_lacuna_2025, p.n_refs_total, p.concept_model,
               cd.n_i, cd.n_j, cd.n_k, cd.cd,
               emb.n_atoms_used, emb.n_unique_concepts, emb.dsi, emb.pm_distance,
               nv.n_pairs, nv.novel_pair_frac, nv.pmi_p10, nv.pmi_median,
               fa.fang_c5, fa.fang_f, fa.fang_e, fa.fang_g,
               k.kedrick_class, k.kedrick_conflict, kc.kedrick_cd
        FROM focal f
        JOIN papers p USING (pid)
        LEFT JOIN cd USING (pid)
        LEFT JOIN emb USING (pid)
        LEFT JOIN novelty nv USING (pid)
        LEFT JOIN fang fa ON fa.openalex_id = f.openalex_id
        LEFT JOIN kedrick k ON k.openalex_id = f.openalex_id
        LEFT JOIN kedrick_cd kc ON kc.openalex_id = f.openalex_id
        ORDER BY f.pid
    """).write_parquet(str(out / "measures.parquet"))

    summary = con.sql(f"""
        SELECT count(*) AS n, count(DISTINCT pid) AS n_distinct_pid,
               count(cd) AS has_cd, count(dsi) AS has_dsi, count(pm_distance) AS has_pm,
               count(novel_pair_frac) AS has_novelty, count(fang_f) AS has_fang,
               count(kedrick_class) AS has_kedrick, sum((kedrick_class = 'gap_opener')::INT) AS gap_openers,
               count(kedrick_cd) AS has_kedrick_cd, avg(n_i + n_j) AS mean_citers5,
               corr(cd, kedrick_cd) AS pearson_cd_vs_kedrick_cd,
               corr(rank_cd, rank_kcd) AS spearman_cd_vs_kedrick_cd
        FROM (SELECT *, rank() OVER (ORDER BY cd) AS rank_cd, rank() OVER (ORDER BY kedrick_cd) AS rank_kcd
              FROM read_parquet('{out / "measures.parquet"}') WHERE cd IS NOT NULL AND kedrick_cd IS NOT NULL
              UNION ALL BY NAME
              SELECT * FROM read_parquet('{out / "measures.parquet"}') WHERE cd IS NULL OR kedrick_cd IS NULL)
    """)
    (out / "summary.txt").write_text(str(summary))
    print(summary.pl().transpose(include_header=True))
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
