"""Castability screen for the eligible-26 (Haven discoveries after T_M = 1930).

`year > T_M` makes a discovery ELIGIBLE. Being ELIGIBLE does not make it an item. To be
castable as E = (S, M, A) with a scorable epicycle cheat, a discovery must clear four
filters, and most of the 26 fail at least one:

  1. FRAME. Reaching D must require overturning an incumbent explanation M that absorbed
     the anomalies by auxiliary hypotheses. Engineering feats, rediscoveries, and
     framework-definitions have no M and no epicycle cheat.

  2. ANOMALY-IS-PRE-CUTOFF. The evidence A must be STATABLE in pre-T_M vocabulary. Many
     frame-replacements rest on evidence that postdates the cutoff (organelle DNA, X-ray
     structures), so a T_M model cannot even be shown A. This is the filter I under-weighted
     when I first built the endosymbiosis environment.

  3. NOT PREREQUISITE-BLOCKED. D must not presuppose an intermediate discovery D' that is
     ALSO post-T_M. Fission presupposes the neutron (1932); it is unreachable in one step
     for a 1930 model.

  4. EFFECTIVE GAP. The gap that matters is (effective_anomaly_year - T_M), NOT
     (Haven_year - T_M). Haven dates a discovery to its consensus moment; the anomaly that
     forces it is often decades earlier. Dark matter is Haven-dated 1970 but the Coma-cluster
     anomaly is Zwicky 1933 (+3y). Using Haven's year mis-sizes the gap, sometimes badly.

Two cross-cutting flags that are not disqualifying but change what the item MEASURES:

  * `reframe_predates_cutoff`: the reframe was already PROPOSED (as a minority view) by ~T_M
    -- Lemaitre's primeval atom, Eddington's stellar fusion. A T_M model may have read it.
    Such an item tests ENDORSEMENT of a known-but-contested idea, not GENERATION of an
    unknown one. Different experiment.

  * Co-selection: a frame-item blocked or anachronistic for 1930 is often castable for a
    LATER-cutoff model. Endosymbiosis wants ~1960; DNA-structure ~1950; fission ~1935. The
    item and the model should be chosen together, which is the real argument for the Ranke
    multi-cutoff family.

Verdicts (`castable_1930`): STRONG, MARGINAL, NO. History-of-science judgments; `confidence`
is flagged and this file is meant to be revised, not treated as ground truth.
"""

# Each row is my assessment. Fields:
#   move: frame_replacement | incremental | engineering | rediscovery | framework
#   M:    the incumbent frame a JUMP must abandon (None if move != frame_replacement)
#   epicycle: the documented patch that preserved M (None/known)
#   eff_year: when A first became statable (may be < Haven year)
#   blocked_by: post-1930 prerequisite D' that D needs (None if clean)
#   anomaly_pre1930: is A expressible in pre-1930 terms?
#   reframe_predates_cutoff: was the reframe already proposed as a minority view by ~1930?
#   castable_1930 / confidence / note
ROWS = [
    dict(title="Neutron", haven_year=1932, move="frame_replacement",
         M="the radiation is electromagnetic (a gamma ray)",
         epicycle="an unusually energetic gamma ray; abandon energy conservation (Joliot-Curies)",
         eff_year=1932, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=False,
         castable_1930="STRONG", confidence="high",
         note="Reference item. Quantitative anomaly (proton vs nitrogen energies disagree). +2y."),

    dict(title="Cell Structure", haven_year=1933, move="engineering",
         M=None, epicycle=None, eff_year=1933, blocked_by="electron microscope (~1931-33)",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="Observational: mapping ultrastructure via new instruments. No incumbent frame."),

    dict(title="The Function of Genes", haven_year=1934, move="incremental",
         M="genes act by some unspecified holistic mechanism",
         epicycle=None, eff_year=1934, blocked_by=None, anomaly_pre1930=True,
         reframe_predates_cutoff=False, castable_1930="NO", confidence="med",
         note="One-gene-one-enzyme is positive mechanism discovery, not an epicycle-defended frame."),

    dict(title="Ecosystem", haven_year=1935, move="frame_replacement",
         M="a plant community is a superorganism that develops like an individual (Clements)",
         epicycle="treat departures from the climax as arrested development of the superorganism",
         eff_year=1935, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=False,
         castable_1930="MARGINAL", confidence="med",
         note="Real incumbent (Clements superorganism) and a re-individuation move, but the "
              "dispute is conceptual -- no forcing quantitative anomaly A."),

    dict(title="Weak and Strong Force", haven_year=1937, move="frame_replacement",
         M="energy is conserved in beta decay, so the emitted electron should be monoenergetic",
         epicycle="abandon energy conservation in individual decays (Bohr)",
         eff_year=1927, blocked_by="strong-force half needs the neutron (1932)",
         anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="MARGINAL", confidence="med",
         note="The WEAK-force / neutrino sub-item is strong: continuous beta spectrum (Ellis-"
              "Wooster 1927) with Bohr's documented energy-nonconservation epicycle vs Pauli's "
              "neutrino. But Pauli proposed the neutrino in 1930 (at the cutoff), so it tests "
              "endorsement; the strong-force half is neutron-blocked. Split the entry."),

    dict(title="Metabolism", haven_year=1938, move="incremental",
         M="metabolism is a linear chain of degradations", epicycle=None,
         eff_year=1938, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="med",
         note="Krebs cycle: linear->cyclic is a structural insight, not a paradigm with epicycles."),

    dict(title="Coelacanth", haven_year=1938, move="rediscovery",
         M=None, epicycle=None, eff_year=1938, blocked_by=None, anomaly_pre1930=True,
         reframe_predates_cutoff=False, castable_1930="NO", confidence="high",
         note="A fish thought extinct, found alive. No frame to overturn."),

    dict(title="Nuclear Fission", haven_year=1939, move="frame_replacement",
         M="bombardment only ADDS to a nucleus, building transuranic elements",
         epicycle="a longer transuranic decay chain; a radium isotope mimicking barium (Fermi's "
                   "1938 Nobel was for these non-existent transuranics)",
         eff_year=1938, blocked_by="the neutron (1932) is the projectile",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="MARGINAL", confidence="high",
         note="Excellent content, best documented epicycle in science, but the projectile is the "
              "neutron. Prereq-clean only for a post-1932 cutoff model. Built; keep for Ranke-1929+."),

    dict(title="Blood Plasma", haven_year=1940, move="engineering",
         M=None, epicycle=None, eff_year=1940, blocked_by=None, anomaly_pre1930=True,
         reframe_predates_cutoff=False, castable_1930="NO", confidence="high",
         note="Plasma separation / blood banking. Medical engineering, no frame."),

    dict(title="Semiconductor Transistor", haven_year=1947, move="engineering",
         M=None, epicycle=None, eff_year=1947, blocked_by="band theory of solids (1930s)",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high", note="A device. No incumbent frame to overturn."),

    dict(title="The Big Bang", haven_year=1948, move="frame_replacement",
         M="the universe is static and eternal",
         epicycle="the redshift is not real expansion (tired light); continuous creation keeps "
                   "density constant (steady-state, but that is Hoyle 1948, post-cutoff)",
         eff_year=1929, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="STRONG", confidence="med",
         note="The anomaly (Hubble's velocity-distance law) is 1929, PRE-cutoff -- the model has "
              "the data. Reframe = run expansion backward to a hot dense origin. But Lemaitre's "
              "primeval atom (1927/31) predates cutoff, so partly an endorsement test. Effective "
              "gap ~0y despite Haven's 1948."),

    dict(title="Definition of Information", haven_year=1948, move="framework",
         M=None, epicycle=None, eff_year=1948, blocked_by=None, anomaly_pre1930=True,
         reframe_predates_cutoff=False, castable_1930="NO", confidence="high",
         note="Shannon defines a quantity. No anomaly, no incumbent frame."),

    dict(title="Jumpin' Genes", haven_year=1950, move="frame_replacement",
         M="genes are fixed in position on the chromosome",
         epicycle="dismiss the mosaic/unstable phenotypes as anomalies or artifacts (McClintock's "
                   "work was ignored for ~20 years)",
         eff_year=1948, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=False,
         castable_1930="STRONG", confidence="med",
         note="Classical-genetics evidence (unstable, mosaic maize kernels), pre-1930 vocabulary, "
              "clean. Ignored-scientist frame-replacement, parallels endosymbiosis. Anomaly A is "
              "subtle to make forcing, but the frame is real and clean. Nominal +20y."),

    dict(title="Fusion", haven_year=1951, move="frame_replacement",
         M="the sun shines by gravitational contraction (Kelvin-Helmholtz)",
         epicycle="the sun is younger than geology says; an unknown chemical energy source",
         eff_year=1905, blocked_by="detailed p-p / CNO mechanism needs post-1930 nuclear physics",
         anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="MARGINAL", confidence="med",
         note="Anomaly (contraction gives ~20 Myr, radiometric rock ages give billions) is classic "
              "and pre-cutoff. But Eddington argued subatomic stellar energy by 1920, so the "
              "reframe predates the cutoff -- endorsement, not generation. Mechanism is blocked."),

    dict(title="Origins of Life", haven_year=1952, move="incremental",
         M="life requires a vital force (vitalism)", epicycle=None,
         eff_year=1952, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="NO", confidence="med",
         note="Miller-Urey is a positive demonstration; vitalism was already moribund by 1952."),

    dict(title="DNA", haven_year=1953, move="frame_replacement",
         M="proteins carry heredity; DNA is a monotonous tetranucleotide, too simple",
         epicycle="dismiss transformation as protein contamination of the DNA preparation",
         eff_year=1944, blocked_by="Avery (1944), Hershey-Chase (1952), X-ray data all post-1930",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="Great frame (protein->DNA), but every anomaly postdates the cutoff; a 1930 model "
              "does not even know DNA is a candidate. Castable for a ~1943 cutoff model."),

    dict(title="Seafloor Spreading", haven_year=1957, move="frame_replacement",
         M="continents are fixed; ocean basins are permanent",
         epicycle="sunken land bridges explain the matching fossils across oceans",
         eff_year=1915, blocked_by="the spreading MECHANISM needs paleomagnetic striping (1960s)",
         anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="NO", confidence="high",
         note="The beautiful frame (fixed continents, land-bridge epicycle) is Wegener 1915 = "
              "PRE-cutoff (Haven #64, ineligible; the model already knows drift). The eligible "
              "piece is the mechanism, which is striping-blocked. Neither level works for 1930."),

    dict(title="The Nature of the Atmosphere", haven_year=1960, move="frame_replacement",
         M="the atmosphere is deterministic and predictable given enough data",
         epicycle="attribute forecast failure to insufficient data / measurement error",
         eff_year=1890, blocked_by="the discovery context is computer simulation (post-1930)",
         anomaly_pre1930=True, reframe_predates_cutoff=True,
         castable_1930="MARGINAL", confidence="low",
         note="Sensitive dependence was known to Poincare (~1890), so the seed predates cutoff, but "
              "the meteorological reframe is a computer-era result. Abstract anomaly. Gap +30y."),

    dict(title="Quarks", haven_year=1962, move="frame_replacement",
         M="protons and neutrons are elementary and indivisible",
         epicycle="add each new hadron to an ever-growing list of elementary particles",
         eff_year=1961, blocked_by="the particle zoo, mesons, the neutron -- all post-1930",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="Composite-hadron frame, but a 1930 model cannot parse the Eightfold Way. Gap +32y."),

    dict(title="Quasars and Pulsars", haven_year=1963, move="incremental",
         M=None, epicycle=None, eff_year=1963,
         blocked_by="neutron stars (1934), radio astronomy (post-1930)",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="Discovery of new objects. Blocked and +33-37y."),

    dict(title="Complete Evolution", haven_year=1967, move="frame_replacement",
         M="organelles are differentiated organs of the cell",
         epicycle="the cell delegated heredity to them; the second membrane is an infolding; the "
                   "bacterial resemblance is convergence (the objections raised against Margulis)",
         eff_year=1962, blocked_by="the compelling evidence (organelle DNA, ribosome type) is "
                                    "molecular biology, post-1953",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="MARGINAL", confidence="high",
         note="Endosymbiosis: the re-individuation move, with a documented rejection record. But "
              "the forcing evidence is molecular and postdates the cutoff -- my first draft used "
              "anachronistic A. Castable for a ~1960 cutoff model, not 1930."),

    dict(title="Dark Matter", haven_year=1970, move="frame_replacement",
         M="a bound system's gravitating mass is its luminous (visible) matter",
         epicycle="the cluster is not really bound; measurement error; unseen ordinary stars",
         eff_year=1933, blocked_by=None, anomaly_pre1930=True, reframe_predates_cutoff=False,
         castable_1930="STRONG", confidence="high",
         note="Standout. Zwicky's Coma-cluster velocity anomaly is 1933, so effective gap is +3y "
              "even though Haven dates it 1970 (Rubin). Virial theorem + redshifts are pre-cutoff. "
              "Clean, quantitative, small gap. The clearest case that effective_year != Haven_year."),

    dict(title="The Nature of Dinosaurs", haven_year=1976, move="frame_replacement",
         M="dinosaurs were sluggish, cold-blooded reptiles",
         epicycle="read every active-posture fossil as an exceptional case",
         eff_year=1969, blocked_by="the key specimens (Deinonychus, 1969) are post-1930",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="med",
         note="Genuine reframe, but the evidence is post-1930 fossils and qualitative. Gap +46y."),

    dict(title="Planets Exist Around Other Stars", haven_year=1995, move="engineering",
         M=None, epicycle=None, eff_year=1995,
         blocked_by="precision Doppler spectroscopy (post-1930)",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="A detection achievement. Gap +65y, prereq-heavy."),

    dict(title="Accelerating Universe", haven_year=1998, move="frame_replacement",
         M="cosmic expansion is decelerating under gravity (universally assumed)",
         epicycle="attribute the SN dimming to dust or evolution of the standard candle",
         eff_year=1998, blocked_by="Big Bang, Type Ia standard candles, GR cosmology -- all post-1930",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high",
         note="Clean frame in the abstract, but every prerequisite postdates the cutoff. Gap +68y."),

    dict(title="Human Genome", haven_year=2003, move="engineering",
         M=None, epicycle=None, eff_year=2003, blocked_by="molecular biology, sequencing (post-1930)",
         anomaly_pre1930=False, reframe_predates_cutoff=False,
         castable_1930="NO", confidence="high", note="A sequencing project. No frame. Gap +73y."),
]


def by_verdict() -> dict:
    out = {"STRONG": [], "MARGINAL": [], "NO": []}
    for r in ROWS:
        out[r["castable_1930"]].append(r)
    return out


if __name__ == "__main__":
    from src.time_capsule.population import eligible_sample

    elig = {d["title"] for d in eligible_sample("talkie-1930")["eligible"]}
    classified = {r["title"] for r in ROWS}
    missing = elig - classified
    extra = classified - elig
    if missing:
        raise SystemExit(f"FATAL: eligible but unclassified: {sorted(missing)}")
    if extra:
        raise SystemExit(f"FATAL: classified but not eligible: {sorted(extra)}")

    buckets = by_verdict()
    print(f"Eligible-26 castability for talkie-1930 (T_M=1930):\n")
    for verdict in ("STRONG", "MARGINAL", "NO"):
        rows = buckets[verdict]
        print(f"{verdict} ({len(rows)}):")
        for r in rows:
            gap = r["eff_year"] - 1930
            tag = "" if r["eff_year"] == r["haven_year"] else f"  [eff {r['eff_year']}, Haven {r['haven_year']}]"
            print(f"  {r['title']:32} {r['move']:18} eff_gap {gap:+3}y{tag}")
        print()
