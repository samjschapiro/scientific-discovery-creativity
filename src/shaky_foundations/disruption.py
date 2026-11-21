"""CD disruption index (Funk & Owen-Smith 2017; Wu, Wang & Evans 2019), computed inside Lacuna.

For focal paper f with reference set R_f, look at every Lacuna paper published within the window
[year_f, year_f + window] that cites f or cites something in R_f:

    n_i  cites f, cites nothing in R_f
    n_j  cites f and at least one paper in R_f
    n_k  cites something in R_f but not f

    CD = (n_i - n_j) / (n_i + n_j + n_k)        (null when the denominator is 0; never filled)

THE REFERENCE GRAPH IS SPLIT ACROSS TWO TABLES (found 2026-11-16, not stated in the package README):
`references_openalex` holds only references to works OUTSIDE Lacuna (0% of its ids are Lacuna
ids), and references to Lacuna papers exist only as `citations` edges keyed by pid. A paper's full
reference list is the union. We put both into one integer node space:

    Lacuna paper  -> its pid (positive)
    outside work  -> -(numeric part of its W id) (negative)

Citing papers are limited to Lacuna, since only Lacuna papers have reference lists here.
`citations` already merges paper versions, so a citation of f is just an edge to f's pid.
Package v2 flags 47,480 duplicate Lacuna entries; `citations` uses only canonical pids, but
`references_openalex` also lists the duplicates' references, which would count the same paper
twice as a citer of an outside work. Edges therefore keep canonical pids only (needs v2).

Expects a table `focal(pid, year)` on the connection.
"""


def build_edges(con) -> None:
    """Create table `edges(c, node)`: Lacuna paper c references node (unified integer key)."""
    con.execute("""
        CREATE OR REPLACE TEMP TABLE edges AS
        SELECT citing_pid AS c, cited_pid::BIGINT AS node FROM citations
        UNION ALL
        SELECT pid AS c, -(substr(openalex_id, 2)::BIGINT) AS node FROM references_openalex
        WHERE pid IN (SELECT pid FROM papers WHERE pid = canonical_pid)
    """)
    bad = con.execute("SELECT count(*) FROM references_openalex WHERE openalex_id NOT LIKE 'W%'").fetchall()[0][0]
    if bad:
        raise ValueError(f"FATAL: {bad} references_openalex ids are not W-ids; node encoding would break")


def compute_cd(con, window: int) -> None:
    """Create table `cd(pid, n_i, n_j, n_k, cd)` for every pid in `focal`. Needs `edges`."""
    con.execute("CREATE OR REPLACE TEMP TABLE pyear AS SELECT pid, year FROM papers")
    con.execute("""
        CREATE OR REPLACE TEMP TABLE focal_refs AS
        SELECT DISTINCT f.pid, f.year, e.node FROM focal f JOIN edges e ON e.c = f.pid
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE citers_f AS
        SELECT DISTINCT f.pid AS f, e.c
        FROM focal f JOIN edges e ON e.node = f.pid JOIN pyear y ON y.pid = e.c
        WHERE e.c <> f.pid AND y.year BETWEEN f.year AND f.year + {int(window)}
    """)
    # Papers citing any of f's references within the window. This is the expensive join.
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE citers_r AS
        SELECT DISTINCT fr.pid AS f, e.c
        FROM focal_refs fr JOIN edges e ON e.node = fr.node JOIN pyear y ON y.pid = e.c
        WHERE e.c <> fr.pid AND y.year BETWEEN fr.year AND fr.year + {int(window)}
    """)

    con.execute("""
        CREATE OR REPLACE TEMP TABLE cd AS
        WITH cf AS (SELECT f, c, 1 AS in_f FROM citers_f),
             cr AS (SELECT f, c, 1 AS in_r FROM citers_r),
             u  AS (SELECT coalesce(cf.f, cr.f) AS f, coalesce(in_f, 0) AS in_f, coalesce(in_r, 0) AS in_r
                    FROM cf FULL OUTER JOIN cr ON cf.f = cr.f AND cf.c = cr.c),
             counts AS (SELECT f AS pid,
                               sum((in_f = 1 AND in_r = 0)::INT) AS n_i,
                               sum((in_f = 1 AND in_r = 1)::INT) AS n_j,
                               sum((in_f = 0 AND in_r = 1)::INT) AS n_k
                        FROM u GROUP BY f)
        SELECT focal.pid,
               coalesce(n_i, 0) AS n_i, coalesce(n_j, 0) AS n_j, coalesce(n_k, 0) AS n_k,
               CASE WHEN coalesce(n_i + n_j + n_k, 0) = 0 THEN NULL
                    ELSE (n_i - n_j) / (n_i + n_j + n_k) END AS cd
        FROM focal LEFT JOIN counts USING (pid)
    """)
