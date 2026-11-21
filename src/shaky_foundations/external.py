"""Paper-level measures released by other groups, joined onto Lacuna by OpenAlex work id.

Fang & Evans (arXiv:2510.03240): F/E/G indices, 5-year window, OpenAlex release 2025-01-29.
    Only papers with >=5 citations in 5 years and >=1 reference; absent otherwise (not zero).
Kedrick et al. (arXiv:2509.21899): gap-opener labels and their own CD, built on MAG.
    MAG paper ids map to OpenAlex ids as 'W' || paperid.
    Their files repeat ~3K paperids (labels) and ~1.5K (CD), sometimes with CONFLICTING values. An
    id whose duplicate rows disagree gets NULL (`kedrick_conflict` = true); identical duplicates
    collapse to one row.
"""

from pathlib import Path


def _require(path: str) -> str:
    if not Path(path).exists():
        raise FileNotFoundError(f"FATAL: external data missing: {path}")
    return path


def create_external_views(con, fang_efg_path: str, kedrick_labels_path: str, kedrick_cd_path: str) -> None:
    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW fang AS
        SELECT id AS openalex_id, citation_count_y5 AS fang_c5, f_y5 AS fang_f, e_y5 AS fang_e, g_y5 AS fang_g
        FROM read_parquet('{_require(fang_efg_path)}')
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE kedrick AS
        WITH raw AS (
            SELECT paperid,
                   CASE WHEN GapOpenersWithNovelPair = 1 THEN 'gap_opener'
                        WHEN NonGapOpenersWithNovelPair = 1 THEN 'novel_pair_non_opener'
                        WHEN NonGapOpenersWithoutNovelPair = 1 THEN 'neither' END AS cls
            FROM read_csv('{_require(kedrick_labels_path)}', header = true))
        SELECT 'W' || paperid AS openalex_id,
               CASE WHEN count(DISTINCT cls) = 1 THEN any_value(cls) END AS kedrick_class,
               count(DISTINCT cls) > 1 AS kedrick_conflict
        FROM raw GROUP BY paperid
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE kedrick_cd AS
        SELECT 'W' || paperid AS openalex_id,
               CASE WHEN count(DISTINCT cd) = 1 THEN any_value(cd) END AS kedrick_cd
        FROM read_csv('{_require(kedrick_cd_path)}', header = true) GROUP BY paperid
    """)
