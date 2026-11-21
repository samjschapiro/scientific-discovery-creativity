"""Prescience and emergence from Lacuna concept atoms (after Lockhart, Sourati, Shi & Evans 2026).

Lockhart et al.: prescient work surprises at publication but becomes routine later; emergence is being
early in areas that come to coalesce. Here, with concepts in a frozen layer (default f20000, fit on atoms
up to 2014) and all rates taken per paper-with-atoms in each window, so rising atom coverage cancels:

  prior window  all papers published before year t;   future window  t+1 .. t+F
  novel pair    a concept pair of the paper that no earlier paper has (surprising at publication; in a
                20K-concept space PMI cannot express surprise because add-one smoothing makes unseen pairs
                of rare concepts look positively associated)

  novel_share         share of the paper's pairs that are novel
  prescience          mean over the paper's novel pairs of log[(n_ab_future + 1) / (E_ab_future + 1)],
                      E_ab_future = n_a_future * n_b_future / N_future: the new combination is used later
                      more than its concepts' own later popularity predicts (concept growth divided out)
  novel_pair_adoption share of the paper's novel pairs used by >= adoption_min papers in the future window
  emergence           mean over the paper's concepts of log[(rate_future + eps) / (rate_recent + eps)],
                      rate = share of papers using the concept; recent = t-R+1 .. t (realised growth, not
                      Lockhart's predicted coalescence)

Expects table `focal(pid, year)` on the connection; uses canonical Lacuna entries only.
"""


def compute_prescience(con, layer: str, future_years: int, recent_years: int, adoption_min: int,
                       eps: float) -> None:
    """Create table `prescience(pid, n_pairs, n_novel, novel_share, prescience, novel_pair_adoption,
    n_concepts, emergence)` for every pid in `focal`."""
    F, R = int(future_years), int(recent_years)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE pc_all AS
        SELECT DISTINCT pid, year, {layer} AS c FROM atoms
        WHERE run_rank = 1 AND {layer} IS NOT NULL AND pid IN (SELECT pid FROM papers WHERE pid = canonical_pid)
    """)
    con.execute("CREATE OR REPLACE TEMP TABLE n_year AS SELECT year, count(DISTINCT pid) AS n FROM pc_all GROUP BY year")
    con.execute("CREATE OR REPLACE TEMP TABLE c_year AS SELECT year, c, count(*) AS n FROM pc_all GROUP BY ALL")
    con.execute("""
        CREATE OR REPLACE TEMP TABLE p_year AS
        SELECT a.year, a.c AS c1, b.c AS c2, count(*) AS n
        FROM pc_all a JOIN pc_all b ON a.pid = b.pid AND a.c < b.c GROUP BY ALL
    """)
    con.execute("""
        CREATE OR REPLACE TEMP TABLE f_pairs AS
        SELECT f.pid, f.year, a.c AS c1, b.c AS c2
        FROM focal f JOIN pc_all a USING (pid) JOIN pc_all b ON b.pid = a.pid AND a.c < b.c
    """)
    # Window totals per focal year.
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE windows AS
        SELECT fy.year,
               (SELECT coalesce(sum(n), 0) FROM n_year y WHERE y.year < fy.year) AS n_prior,
               (SELECT coalesce(sum(n), 0) FROM n_year y WHERE y.year BETWEEN fy.year + 1 AND fy.year + {F}) AS n_future,
               (SELECT coalesce(sum(n), 0) FROM n_year y WHERE y.year BETWEEN fy.year - {R} + 1 AND fy.year) AS n_recent
        FROM (SELECT DISTINCT year FROM focal) fy
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE f_pair_counts AS
        SELECT fp.pid, fp.year, fp.c1, fp.c2,
               coalesce(sum(py.n) FILTER (WHERE py.year < fp.year), 0) AS ab_prior,
               coalesce(sum(py.n) FILTER (WHERE py.year BETWEEN fp.year + 1 AND fp.year + {F}), 0) AS ab_future
        FROM f_pairs fp LEFT JOIN p_year py ON py.c1 = fp.c1 AND py.c2 = fp.c2
        GROUP BY ALL
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE f_concepts AS
        SELECT DISTINCT f.pid, f.year, a.c FROM focal f JOIN pc_all a USING (pid)
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE f_concept_counts AS
        SELECT fc.pid, fc.year, fc.c,
               coalesce(sum(cy.n) FILTER (WHERE cy.year < fc.year), 0) AS c_prior,
               coalesce(sum(cy.n) FILTER (WHERE cy.year BETWEEN fc.year + 1 AND fc.year + {F}), 0) AS c_future,
               coalesce(sum(cy.n) FILTER (WHERE cy.year BETWEEN fc.year - {R} + 1 AND fc.year), 0) AS c_recent
        FROM f_concepts fc LEFT JOIN c_year cy ON cy.c = fc.c
        GROUP BY ALL
    """)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE prescience AS
        WITH pr AS (
            SELECT p.pid, p.ab_prior, p.ab_future,
                   ln((p.ab_future + 1.0) / (a.c_future * b.c_future / greatest(w.n_future, 1) + 1.0)) AS future_lift
            FROM f_pair_counts p JOIN windows w USING (year)
            JOIN f_concept_counts a ON a.pid = p.pid AND a.c = p.c1
            JOIN f_concept_counts b ON b.pid = p.pid AND b.c = p.c2
        ),
        pairs AS (
            SELECT pid, count(*) AS n_pairs,
                   count(*) FILTER (WHERE ab_prior = 0) AS n_novel,
                   avg((ab_prior = 0)::INT) AS novel_share,
                   avg(future_lift) FILTER (WHERE ab_prior = 0) AS prescience,
                   avg((ab_future >= {int(adoption_min)})::INT) FILTER (WHERE ab_prior = 0) AS novel_pair_adoption
            FROM pr GROUP BY pid
        ),
        conc AS (
            SELECT c.pid, count(*) AS n_concepts,
                   avg(ln((c.c_future / w.n_future + {eps}) / (c.c_recent / w.n_recent + {eps}))) AS emergence
            FROM f_concept_counts c JOIN windows w USING (year) GROUP BY c.pid
        )
        SELECT conc.pid, pairs.n_pairs, pairs.n_novel, pairs.novel_share, pairs.prescience,
               pairs.novel_pair_adoption, conc.n_concepts, conc.emergence
        FROM conc LEFT JOIN pairs USING (pid)
    """)
