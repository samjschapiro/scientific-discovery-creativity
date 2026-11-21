"""The discovery population (Haven's 100) and the time-capsule model registry.

Sampling frame: Haven's *100 Greatest Science Discoveries of All Time* (2007). Using a
pre-existing, externally-authored canon rather than hand-picking discoveries means the
population is not selected by us to flatter the hypothesis — an important defense when the
claim is "models can/cannot reach transformative discoveries."

For a time-capsule model M with knowledge cutoff T_M, the eligible sample is every discovery
whose year is strictly greater than T_M: the model cannot have read about it.

`year > T_M` is NECESSARY BUT NOT SUFFICIENT. Two further filters matter, and both are
exposed rather than silently applied:

  * **Gap ceiling.** If the discovery is too far past the cutoff, the model lacks the context
    to even parse the question, and a failure says nothing about transformational ability.
    Note the gap that matters is *conceptual distance*, which time only proxies — a fast-moving
    field can put a 5-year gap further away than decades in a slow one.
  * **Straddlers.** Three Haven entries carry two years ("Years of Discovery: 1937 and 1983").
    If the cutoff falls between them the discovery is partly inside the model's world, so
    eligibility is ambiguous. These are flagged, never silently included or dropped.
"""

import json
from dataclasses import dataclass
from pathlib import Path

HAVEN_PATH = Path(__file__).parent / "haven100.json"


@dataclass(frozen=True)
class TimeCapsuleModel:
    name: str
    cutoff: int  # T_M — knowledge cutoff year
    params: str
    hf_id: str | None
    control_hf_id: str | None  # matched-compute modern-text twin, if the authors released one
    note: str


# Cutoffs and IDs are from docs/tracks/time_capsule/progress.md's sources. A model without a
# matched control cannot separate "failed to jump" from "too weak to do anything" — that is
# why talkie-1930 is the primary: it is the only one shipping a compute-matched modern twin.
MODELS = {
    "talkie-1930": TimeCapsuleModel(
        name="talkie-1930",
        cutoff=1930,
        params="13B",
        hf_id="talkie-lm/talkie-1930-13b-it",
        control_hf_id="talkie-lm/talkie-web-13b-base",
        note="260B tokens of pre-1931 text. Largest public vintage model; the only one with a "
             "same-architecture, same-compute modern-web control (talkie-web-13b-base).",
    ),
    "ranke-1913": TimeCapsuleModel(
        name="ranke-1913", cutoff=1913, params="4B", hf_id=None, control_hf_id=None,
        note="Ranke-4B family. Same family at multiple cutoffs turns 'how big a gap can it "
             "bridge' into a dose-response curve against a FIXED discovery target.",
    ),
    "ranke-1929": TimeCapsuleModel(
        name="ranke-1929", cutoff=1929, params="4B", hf_id=None, control_hf_id=None,
        note="Ranke-4B family.",
    ),
    "ranke-1933": TimeCapsuleModel(
        name="ranke-1933", cutoff=1933, params="4B", hf_id=None, control_hf_id=None,
        note="Ranke-4B family.",
    ),
    "ranke-1939": TimeCapsuleModel(
        name="ranke-1939", cutoff=1939, params="4B", hf_id=None, control_hf_id=None,
        note="Ranke-4B family.",
    ),
    "ranke-1946": TimeCapsuleModel(
        name="ranke-1946", cutoff=1946, params="4B", hf_id=None, control_hf_id=None,
        note="Ranke-4B family.",
    ),
    "gpt-1900": TimeCapsuleModel(
        name="gpt-1900", cutoff=1900, params="unknown", hf_id=None, control_hf_id=None,
        note="Machina Mirabilis (Michael Hla). Built to test relativity / quantum reachability.",
    ),
    "timecapsule-1875": TimeCapsuleModel(
        name="timecapsule-1875", cutoff=1875, params="1.2B", hf_id=None, control_hf_id=None,
        note="TimeCapsuleLLM (1800-1875 London). Author reports high hallucination; likely below "
             "the capability floor for this task.",
    ),
}


def load_discoveries() -> list[dict]:
    with open(HAVEN_PATH) as f:
        data = json.load(f)

    discoveries = data["discoveries"]
    if len(discoveries) != 100:
        raise ValueError(f"FATAL: expected 100 discoveries, found {len(discoveries)}")
    return discoveries


def get_model(name: str) -> TimeCapsuleModel:
    if name not in MODELS:
        raise ValueError(f"FATAL: unknown model '{name}'. Known: {sorted(MODELS)}")
    return MODELS[name]


def eligible_sample(model_name: str, max_gap: int | None = None) -> dict:
    """Restrict Haven's 100 to discoveries strictly after the model's cutoff.

    Returns the eligible set, the excluded set, and the straddlers — separately, so a
    downstream script can never silently inherit an ambiguous item.
    """
    model = get_model(model_name)
    T = model.cutoff

    eligible, excluded, straddlers = [], [], []

    for d in load_discoveries():
        first, last = d["year_first"], d["year_last"]
        gap = first - T

        # A multi-year discovery whose span contains the cutoff is partly inside the model's
        # world. Ambiguous by construction — never silently classified.
        if d["multi_year"] and first <= T < last:
            straddlers.append({**d, "gap": gap})
            continue

        if first <= T:
            excluded.append({**d, "gap": gap})
            continue

        if max_gap is not None and gap > max_gap:
            excluded.append({**d, "gap": gap, "excluded_by": "max_gap"})
            continue

        eligible.append({**d, "gap": gap})

    return {
        "model": model.name,
        "cutoff": T,
        "max_gap": max_gap,
        "n_eligible": len(eligible),
        "eligible": eligible,
        "n_excluded": len(excluded),
        "excluded": excluded,
        "n_straddlers": len(straddlers),
        "straddlers": straddlers,
    }
