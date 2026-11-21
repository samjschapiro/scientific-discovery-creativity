"""Foundation / Extension / Generalization indices (Fang & Evans 2025), computed inside Lacuna.

For focal paper f and each Lacuna paper c citing it within [year_f, year_f + window] (and <= year_cap):
    upstream   = how many of f's references c also cites   (references = citations + references_openalex)
    downstream = how many of f's other citing papers c also cites (Lacuna citers only)
    Foundation if downstream > upstream; Extension if upstream > downstream; Generalization if both 0;
    a nonzero tie counts 0.5 Foundation + 0.5 Extension (Fang & Evans README).
Indices are shares of f's citing papers. Fang's published values use all of OpenAlex and stop at 2019;
this version extends to recent papers, at the cost of seeing only Lacuna citers downstream.

Needs tables `edges(c, node)` (disruption.build_edges) and `focal(pid, year)` on the connection.
"""


def compute_efg(con, window: int, year_cap: int) -> None:
    """Create table `efg(pid, n_citers, efg_f, efg_e, efg_g)` for every pid in `focal`."""
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE efg_cit AS
        SELECT DISTINCT f.pid AS f, c.citing_pid AS c
        FROM focal f JOIN citations c ON c.cited_pid = f.pid
        WHERE c.citing_year BETWEEN f.year AND least(f.year + {int(window)}, {int(year_cap)})
          AND c.citing_pid <> f.pid
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE efg_down AS
        SELECT a.f, a.c, count(*) AS down
        FROM efg_cit a JOIN citations e ON e.citing_pid = a.c
        JOIN efg_cit b ON b.f = a.f AND b.c = e.cited_pid
        GROUP BY a.f, a.c
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE efg_refs AS
        SELECT DISTINCT f.pid AS f, e.node FROM focal f JOIN edges e ON e.c = f.pid
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE efg_up AS
        SELECT a.f, a.c, count(*) AS up
        FROM efg_cit a JOIN edges e ON e.c = a.c JOIN efg_refs r ON r.f = a.f AND r.node = e.node
        GROUP BY a.f, a.c
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE efg AS
        WITH k AS (
            SELECT a.f, coalesce(d.down, 0) AS down, coalesce(u.up, 0) AS up
            FROM efg_cit a LEFT JOIN efg_down d USING (f, c) LEFT JOIN efg_up u USING (f, c)
        )
        SELECT f AS pid, count(*) AS n_citers,
               avg(CASE WHEN down > up THEN 1.0 WHEN down = up AND down > 0 THEN 0.5 ELSE 0.0 END) AS efg_f,
               avg(CASE WHEN up > down THEN 1.0 WHEN down = up AND down > 0 THEN 0.5 ELSE 0.0 END) AS efg_e,
               avg(CASE WHEN up = 0 AND down = 0 THEN 1.0 ELSE 0.0 END) AS efg_g
        FROM k GROUP BY f
    """)


def citation_labels(con) -> None:
    """After compute_efg: table `efg_labels(f, c, up, down, efg_label)`, one Fang label per citation."""
    con.execute("""
        CREATE OR REPLACE TEMP TABLE efg_labels AS
        SELECT a.f, a.c, coalesce(u.up, 0) AS up, coalesce(d.down, 0) AS down,
               CASE WHEN coalesce(u.up, 0) = 0 AND coalesce(d.down, 0) = 0 THEN 'Generalization'
                    WHEN coalesce(d.down, 0) > coalesce(u.up, 0) THEN 'Foundation'
                    WHEN coalesce(u.up, 0) > coalesce(d.down, 0) THEN 'Extension'
                    ELSE 'tie' END AS efg_label
        FROM efg_cit a LEFT JOIN efg_down d USING (f, c) LEFT JOIN efg_up u USING (f, c)
    """)
