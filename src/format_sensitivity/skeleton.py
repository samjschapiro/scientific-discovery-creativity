"""The domain-neutral skeleton shared by every re-individuation scenario.

The fixed structure (agreed with the PI):

  PROLIFERATION  The standing account carries k mechanisms, each introduced to
                 absorb one anomaly, each locally adequate, jointly unfalsified.
                 "The account has never failed" — because it cannot.
  UNIFICATION    A single posit U entails every observation and requires ZERO of
                 the k mechanisms. Not "more elegant" — the mechanisms become
                 unnecessary, because there are no separate individuals to
                 coordinate.
  SIGNATURE      At least one observation is anomalous under the standing account
                 and positively predicted under U (here: an origin artifact that
                 is never found). Without the signature there is no forced answer
                 and the item is not a test.

The re-individuation move: the N counted TOKENs are parts of one extended
individual U. A skin is a lexical filling of these 18 slots in a novel surface.

`SLOTS` is the canonical key set. Every skin must fill exactly these keys — no
more, no fewer — which `coverage.py` enforces.
"""

# Slot -> the role it plays in the structure (domain-neutral).
SLOTS = {
    "S1": "A census individuates TOKENs and calls each one an INDIVIDUAL.",
    "S2": "Each token carries its own local apparatus A.",
    "S3": "Each token has its own local apparatus B, near a boundary.",
    "S4": "Each token ceases and resumes on a cycle.",
    "S5": "The count is careful and has been kept for a long time.",
    "S6": "Tokens across the whole field begin within one TIME-UNIT of one another.",
    "S7": "Tokens across the whole field end within one TIME-UNIT of one another.",
    "S8": "Subregion X receives far less of two resources than subregion Y.",
    "S9": "Remove ~100 tokens in one place; within a short time new tokens appear at the margins.",
    "S10": "The number of new tokens is proportional to how many were removed.",
    "S11": "The new tokens appear in places distant from the removal.",
    "S12": "Damage one token's apparatus A; later, tokens far away strengthen their own A.",
    "S13": "SIGNATURE: no origin artifact of any token has ever been found.",
    "S14": "Samples of the MEDIUM turn up nothing unusual.",
    "S15": "Standing account: many separate individuals, coordinated by environment and by signals through the MEDIUM.",
    "S16": "Epicycle 1: a wounding-type signal, posited to explain S12.",
    "S17": "Epicycle 2: a density-type signal, posited to explain S9-S11.",
    "S18": "The account has never failed.",
}

# Which facts each F3 bundle document should carry, by role. Skins follow this so
# the same anomaly is split across sources the same way in every domain.
BUNDLE_LAYOUT = {
    "A": ["S1", "S2", "S3", "S4", "S5", "S13"],
    "B": ["S6", "S7", "S8"],
    "C": ["S9", "S10", "S11"],
    "D": ["S14", "S15", "S16", "S17", "S18"],
    "E": ["S12"],
}

# All formats any skin may implement, in canonical order. A skin declares the
# subset it actually provides via `supported_formats`.
FORMAT_CODES = ["F0", "F1", "F2", "F3", "F5"]

# --------------------------------------------------------------------------
# Task framings (shared across skins) — a ladder in revision license.
# See docs/tracks/format_sensitivity/progress.md for why P_SUMMARIZE is the
# floor and a control rather than a "no cue" condition.
# --------------------------------------------------------------------------

FRAMINGS = {
    "P_PUZZLE": "How do you explain what's happening?",
    "P_REVIEW": (
        "You are the incoming supervisor. Review the record and write your "
        "assessment for the report."
    ),
    "P_ASSESS": (
        "Think it through, then draft the summary paragraph for the report."
    ),
    "P_SUMMARIZE": "Draft the summary paragraph for the report.",
}

# Control probes, run in fresh contexts. `referent` is the Bar-1 acceptance gate:
# a skin whose referent-naming rate is nonzero is retrieval-permeable and should
# be redrawn, not kept.
PROBES = {
    "comprehension": "List every observation recorded. Do not explain them.",
    "referent": (
        "Does this scenario correspond to any real phenomenon you are aware of? "
        "Name it."
    ),
}
