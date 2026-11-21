"""Self-check: prove the instrument without any API key.

Runs the exact-arithmetic validation on both environments (transformative + negative
control), prints the forcing-quad witnesses that pin the artifact, renders the three
prompt variants, and grades a battery of canned responses so the grader's behaviour is
visible on every failure mode. This is the "prove the artifact grading is clean" step
from docs/memos/interactive_frame_replacement_benchmark.md — no models, no cost.

    python src/sci_twist/scripts/selfcheck.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.sci_twist.environment import solve_pair_from_pfaffian, loop_sum, find_potential
from src.sci_twist.environments import assay_house
from src.sci_twist.grading import grade
from src.sci_twist.prompts import VARIANTS, render

# Canned responses exercising each failure mode. These are illustrative fixtures, not
# model outputs — they exist so the grader's decisions are visible and testable.
CANNED_TRANSFORMATIVE = {
    "species (reframe + right number)":
        "A scalar avidity cannot produce a cycle with net gain, so the account is the wrong kind "
        "of object. Treating each bath as carrying two quantities whose oriented area gives the "
        "transfer, the table is rank 2 and every 4x4 minor vanishes. Solving, T(C,E) = +1.",
    "genus-only slogan (no number)":
        "The avidity may be relational rather than intrinsic; the system looks non-conservative "
        "and there may be hidden variables at play. More structure is clearly needed here.",
    "epicycle / stuck in M":
        "Refine the correction terms epsilon(X,Y) to absorb the cyclic gain. With one term per "
        "pair the fit is exact, but T(C,E) is then unconstrained and cannot be predicted; the "
        "house would need to measure it.",
    "confident wrong number":
        "Interpolating the avidities gives k_C - k_E, so T(C,E) = +3.",
}

CANNED_CONTROL = {
    "correctly defends M":
        "A single set of avidities reproduces the whole table and every loop balances, so there "
        "is no hidden structure. T(C,E) = k_C - k_E = +1.",
    "over-reaches (false reframe)":
        "This is surely the oriented-area structure again — a second quantity per bath, and the "
        "cycles must gain. No scalar potential can be right. T(C,E) = +1.",
}


def hr(title: str) -> None:
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


def main() -> None:
    hr("BUILD + VALIDATE (fails loudly if the item structure is wrong)")
    env = assay_house.build()                 # validates on construction
    ctrl = assay_house.build_negative_control()
    print(f"transformative : {env.name}   held-out {env.label(env.held_out)}   "
          f"forced = {env.forced_value}")
    print(f"negative ctrl  : {ctrl.name}   held-out {ctrl.label(ctrl.held_out)}   "
          f"forced = {ctrl.forced_value}")

    hr("WHY THE INCUMBENT IS IMPOSSIBLE (transformative)")
    _, conflict = find_potential(env.n(), env.given)
    gain = loop_sum(env.given, env.witness_cycle)
    cyc = " -> ".join(env.entities[i] for i in env.witness_cycle + [env.witness_cycle[0]])
    print(f"no scalar potential fits: first contradiction at edge {conflict[0]} "
          f"(expected {conflict[1]}, got {conflict[2]})")
    print(f"witness cycle {cyc} has net gain {gain} != 0  (a potential difference cannot)")

    hr("WHY THE REFRAME FORCES THE ARTIFACT (over-determined)")
    for quad in env.forcing_quads():
        labels = ",".join(env.entities[i] for i in quad)
        got = solve_pair_from_pfaffian(env.given, quad, env.held_out)
        print(f"quad {{{labels}}}  =>  {env.label(env.held_out)} = {got}")

    hr("PROMPT VARIANTS (rendered)")
    for v in VARIANTS:
        src = ctrl if v == "CONTROL" else env
        text = render(src, v)
        print(f"\n----- {v} ({len(text.split())} words) -----\n{text}")

    hr("GRADER ON CANNED RESPONSES — transformative")
    for name, resp in CANNED_TRANSFORMATIVE.items():
        g = grade(env, resp)
        print(f"  {name:34s} -> {g.label:14s} value={g.committed_value}  {g.note}")

    hr("GRADER ON CANNED RESPONSES — negative control")
    for name, resp in CANNED_CONTROL.items():
        g = grade(ctrl, resp)
        print(f"  {name:34s} -> {g.label:14s} value={g.committed_value}  {g.note}")

    print("\nOK — validation passed and the grader labelled every fixture.")


if __name__ == "__main__":
    main()
