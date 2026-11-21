"""Citation-only displacement: is a foundation quietly dropped by its own neighbourhood?

For foundation A published in year y_A:
    early citers   papers citing A in [y_A, y_A + early_years]
    partners       the top_k works most often co-cited with A by its early citers (A excluded)
    community(t)   papers published in year t that cite >= min_partners of A's partners
    share(t)       fraction of community(t) that also cites A

The neighbourhood is fixed from A's early years, so a later drift of the field doesn't redefine it.
retention = mean share over the last `tail_years` / peak share (1 = never dropped). Walker's point:
paradigms can die quietly, with nobody writing a critique.
"""

import polars as pl


def community_shares(con, foundations: pl.DataFrame, early_years: int, top_k: int, min_partners: int,
                     year_max: int) -> pl.DataFrame:
    """Per foundation-year: n_community, n_citing_a, share. Expects views papers, citations."""
    con.register("disp_f", foundations.select(pl.col("pid").alias("a"), pl.col("year").alias("ya")))
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE early AS
        SELECT f.a, c.citing_pid AS e FROM citations c JOIN disp_f f ON c.cited_pid = f.a
        WHERE c.citing_year BETWEEN f.ya AND f.ya + {int(early_years)}
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE partners AS
        SELECT a, p FROM (
            SELECT e.a, c.cited_pid AS p, count(*) AS n,
                   row_number() OVER (PARTITION BY e.a ORDER BY count(*) DESC, c.cited_pid) AS r
            FROM early e JOIN citations c ON c.citing_pid = e.e
            WHERE c.cited_pid <> e.a GROUP BY e.a, c.cited_pid
        ) WHERE r <= {int(top_k)}
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE community AS
        SELECT pt.a, c.citing_pid AS x, any_value(c.citing_year) AS year
        FROM partners pt JOIN citations c ON c.cited_pid = pt.p
        WHERE c.citing_year <= {int(year_max)}
        GROUP BY pt.a, c.citing_pid HAVING count(DISTINCT pt.p) >= {int(min_partners)}
    """)
    return con.sql("""
        SELECT m.a AS foundation, m.year, count(*) AS n_community,
               count(c.citing_pid) AS n_citing_a, count(c.citing_pid) / count(*) AS share
        FROM community m JOIN disp_f f ON f.a = m.a
        LEFT JOIN citations c ON c.citing_pid = m.x AND c.cited_pid = m.a
        WHERE m.year >= f.ya AND m.x <> m.a
        GROUP BY ALL ORDER BY foundation, m.year
    """).pl()


def retention(shares: pl.DataFrame, min_community: int, tail_years: int, year_max: int) -> pl.DataFrame:
    s = shares.filter(pl.col("n_community") >= min_community)
    tail = s.filter(pl.col("year") > year_max - tail_years).group_by("foundation").agg(tail_share=pl.col("share").mean())
    peak = s.group_by("foundation").agg(peak_share=pl.col("share").max(),
                                        peak_year=pl.col("year").sort_by("share").last())
    return peak.join(tail, on="foundation").with_columns(retention=pl.col("tail_share") / pl.col("peak_share"))
