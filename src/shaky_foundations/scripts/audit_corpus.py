"""Audit the Lacuna package for the things shakiness scoring depends on.

Before scoring any foundation as "shaky" we need to know whether the corpus can see the
foundations at all. This writes, to output_dir:

  - coverage_by_year.csv      papers, OpenAlex match rate, atom coverage per year
  - atom_type_lens.csv        atom counts by (type, lens), best run only
  - landmarks.csv             every pid whose title matches a configured landmark paper, with
                              OpenAlex citation count vs. in-corpus citations. Several rows per
                              landmark = the paper is split across versions; a low or null count
                              on a famous paper = a bad or missing match.
  - top_cited.csv             most-cited papers inside the corpus (the candidate foundation pool)
  - critique_atom_samples.csv sample limitation atoms per lens, to read by hand

    uv run python src/shaky_foundations/scripts/audit_corpus.py configs/shaky_foundations/audit_corpus.yaml
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.shaky_foundations.data import open_lacuna
from src.utils import init_directory, load_config

REQUIRED = ["output_dir", "lacuna_dir", "lacuna_package", "landmark_titles", "top_cited_n",
            "samples_per_lens", "sample_seed"]


def validate_config(config: dict) -> None:
    for key in REQUIRED:
        if key not in config:
            raise ValueError(f"FATAL: '{key}' is required in config")
    if not config["landmark_titles"]:
        raise ValueError("FATAL: 'landmark_titles' must be non-empty")


def coverage_by_year(con, out: Path) -> None:
    con.sql("""
        SELECT year,
               count(*)                                   AS n_papers,
               avg(matched::INT)                          AS frac_matched,
               avg((n_atoms > 0)::INT)                    AS frac_with_atoms,
               avg((n_refs_total IS NULL)::INT)           AS frac_no_refs
        FROM papers WHERE year BETWEEN 1990 AND 2026
        GROUP BY year ORDER BY year
    """).write_csv(str(out / "coverage_by_year.csv"))


def atom_type_lens(con, out: Path) -> None:
    con.sql("""
        SELECT type, lens, count(*) AS n FROM atoms WHERE run_rank = 1
        GROUP BY ALL ORDER BY n DESC
    """).write_csv(str(out / "atom_type_lens.csv"))


def landmarks(con, titles: list[str], out: Path) -> None:
    con.execute("CREATE TEMP TABLE landmark_titles (landmark VARCHAR)")
    con.executemany("INSERT INTO landmark_titles VALUES (?)", [[t] for t in titles])
    con.sql("""
        WITH internal AS (SELECT cited_pid AS pid, count(*) AS n_cited_in_corpus
                          FROM citations GROUP BY cited_pid)
        SELECT l.landmark, p.pid, p.title, p.year, p.venue, p.matched, p.openalex_id,
               p.cites_total_2025, p.cites_lacuna_2025, coalesce(i.n_cited_in_corpus, 0) AS n_cited_in_corpus, p.n_atoms
        FROM landmark_titles l
        LEFT JOIN papers p ON lower(trim(p.title)) = lower(trim(l.landmark)) AND p.pid = p.canonical_pid
        LEFT JOIN internal i USING (pid)
        ORDER BY l.landmark, n_cited_in_corpus DESC
    """).write_csv(str(out / "landmarks.csv"))


def top_cited(con, n: int, out: Path) -> None:
    con.sql(f"""
        SELECT c.cited_pid AS pid, p.title, p.year, p.cites_total_2025,
               count(*) AS n_cited_in_corpus, p.n_atoms
        FROM citations c JOIN papers p ON p.pid = c.cited_pid
        GROUP BY ALL ORDER BY n_cited_in_corpus DESC LIMIT {int(n)}
    """).write_csv(str(out / "top_cited.csv"))


def critique_atom_samples(con, per_lens: int, seed: int, out: Path) -> None:
    # Seeded hash, not random(): DuckDB rejects volatile window ORDER BYs, and this is reproducible.
    con.sql(f"""
        SELECT lens, pid, year, text FROM (
            SELECT lens, pid, year, text,
                   row_number() OVER (PARTITION BY lens ORDER BY hash(atom_id, {int(seed)})) AS r
            FROM atoms WHERE run_rank = 1 AND type = 'limitation'
        ) WHERE r <= {int(per_lens)} ORDER BY lens, r
    """).write_csv(str(out / "critique_atom_samples.csv"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config_path)
    validate_config(config)
    out = init_directory(config["output_dir"], overwrite=args.overwrite)
    shutil.copy(args.config_path, out / "config.yaml")

    con = open_lacuna(config["lacuna_dir"], config["lacuna_package"])
    print("package verified")

    landmarks(con, config["landmark_titles"], out)
    print("landmarks done")
    if args.debug:
        return

    coverage_by_year(con, out)
    print("coverage done")
    top_cited(con, config["top_cited_n"], out)
    print("top cited done")
    atom_type_lens(con, out)
    print("atom type/lens done")
    critique_atom_samples(con, config["samples_per_lens"], config["sample_seed"], out)
    print(f"done -> {out}")


if __name__ == "__main__":
    main()
