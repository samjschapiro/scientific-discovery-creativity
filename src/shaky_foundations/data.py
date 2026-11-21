"""Access to the Lacuna package (lacuna-recombination-2026-11-06-v1).

The package is ~3.2 GB of parquet, so everything goes through DuckDB queries over the files
rather than loading tables into memory. `open_lacuna` refuses to return a connection unless
every file in the package manifest is present with the declared row count — a truncated
download or a different package version should crash here, not skew a shakiness score later.
"""

import json
from pathlib import Path

import duckdb

PARQUET_TABLES = [
    "papers",
    "citations",
    "references_openalex",
    "directions",
    "atoms",
    "concepts_c2000",
    "concepts_c20000",
    "concepts_c200000",
    "concepts_f2800",
    "concepts_f20000",
]


def verify_package(lacuna_dir: Path, expected_name: str) -> dict:
    """Check manifest name and per-table row counts (from parquet metadata, so it is cheap)."""
    if not lacuna_dir.exists():
        raise FileNotFoundError(f"FATAL: Lacuna package not found: {lacuna_dir}")

    manifest = json.loads((lacuna_dir / "manifest.json").read_text())
    if manifest["name"] != expected_name:
        raise ValueError(
            f"FATAL: expected package '{expected_name}', found '{manifest['name']}' in {lacuna_dir}"
        )

    con = duckdb.connect()
    for table in PARQUET_TABLES:
        path = lacuna_dir / f"{table}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"FATAL: missing {path}")
        declared = manifest["files"][f"{table}.parquet"]["rows"]
        actual = con.execute(
            "SELECT num_rows FROM parquet_file_metadata(?)", [str(path)]
        ).fetchall()[0][0]
        if actual != declared:
            raise ValueError(f"FATAL: {table}.parquet has {actual} rows, manifest says {declared}")
    con.close()
    return manifest


def open_lacuna(lacuna_dir: str, expected_name: str) -> duckdb.DuckDBPyConnection:
    """Verify the package, then return a DuckDB connection with one view per table."""
    root = Path(lacuna_dir).resolve()
    verify_package(root, expected_name)

    con = duckdb.connect()
    for table in PARQUET_TABLES:
        con.execute(f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{root / f'{table}.parquet'}')")
    return con
