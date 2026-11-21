"""Grading — v1 grades the ARTIFACT only, exactly.

The clean, defensible, fully-automated measurement is exact match on the committed
held-out value. It works because the item is built so the incumbent frame is
*structurally incapable* of producing that value (it is under-determined under a scalar
potential): a model that states the number must hold the reframe, and no genus-level
slogan earns credit.

What v1 does NOT do, on purpose (see format_sensitivity/progress.md — do not grade with
keyword matching and pretend it is rubric grading):

  * Score the *principle* ("full credit needs the oriented-area statement too"). That is
    a rubric-judge job; here we record whether the value is right and leave principle
    scoring to a validated judge.
  * Count epicycles from prose. `epicycles` is declared on the environment for a future
    rubric/judge pass; a regex count would be exactly the fragile keyword grader we were
    warned off.

So `classify_*` returns a coarse, honest label based on the value and on a few *specific*
falsifiable claims (not generic keyword soup), and flags anything it could not parse for a
human/judge rather than guessing.
"""

import re
from dataclasses import dataclass
from fractions import Fraction

from src.sci_twist.environment import TransferEnvironment

# Phrases by which a model concedes it cannot predict the held-out value — i.e. it is stuck
# in the incumbent frame, under which the value genuinely is a free parameter.
_UNDERDETERMINED = re.compile(
    r"under-?determined|cannot be (?:determined|predicted|known)|can'?t be (?:determined|predicted)"
    r"|not (?:determined|predictable|fixed)|need(?:s)? to (?:be )?(?:measure|run)|must be measured"
    r"|no way to (?:know|predict)|impossible to predict|unconstrained",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Grade:
    label: str
    committed_value: Fraction | None
    forced_value: Fraction
    correct_value: bool
    note: str = ""


def extract_committed_value(text: str, held_label: str) -> Fraction | None:
    """Best-effort parse of the model's committed held-out value.

    Deliberately conservative: prefers a value adjacent to the held-out pair's name
    (e.g. 'T(C,E) = +1'); falls back to a final 'answer/value = <n>'. Returns None when
    nothing is confidently parseable, so the caller flags it for review rather than
    scoring a guess.
    """
    text = text.replace("−", "-")  # unicode minus -> ascii, models emit both
    num = r"[+-]?\d+(?:\.\d+)?(?:\s*/\s*\d+)?"

    def to_frac(s: str) -> Fraction:
        return Fraction(s.replace(" ", ""))

    # Prefer a number on the same line as the held-out pair, taking the LAST number on that
    # line so an intermediate expression ("T(C,E) = k_C - k_E = +1") resolves to its result.
    m = re.match(r"T\((\w+)\s*,\s*(\w+)\)", held_label)
    candidates: list[str] = []
    if m:
        a, b = m.group(1), m.group(2)
        label_pat = re.compile(rf"T\(\s*{a}\s*,\s*{b}\s*\)", re.IGNORECASE)
        for mo in label_pat.finditer(text):
            line = text[mo.end():].split("\n", 1)[0]
            nums = re.findall(num, line)
            if nums:
                candidates.append(nums[-1])
    if not candidates:
        fallback = re.compile(rf"(?:answer|value|result|prediction)\s*(?:=|is|:)\s*({num})", re.IGNORECASE)
        candidates = fallback.findall(text)
    if not candidates:
        return None
    try:
        return to_frac(candidates[-1])  # last mention = the model's final commitment
    except (ValueError, ZeroDivisionError):
        return None


def _asserts_reframe_structure(text: str) -> bool:
    """Does the response make the specific (here FALSE) claims of the reframe — that a scalar
    account is impossible / that a cycle yields net gain? On the negative control these are
    falsifiable and wrong (loops verifiably vanish), so they mark over-reach."""
    pat = re.compile(
        r"net gain|cycle[s]? (?:gain|accumulat|net)|no scalar|not a scalar|cannot be a scalar"
        r"|impossible for (?:any )?potential|second quantity|two quantities|hidden variable",
        re.IGNORECASE,
    )
    return bool(pat.search(text))


def classify_transformative(env: TransferEnvironment, text: str) -> Grade:
    held = env.label(env.held_out)
    value = extract_committed_value(text, held)
    forced = env.forced_value

    if value is not None:
        correct = value == forced
        return Grade(
            label="SPECIES" if correct else "WRONG_VALUE",
            committed_value=value,
            forced_value=forced,
            correct_value=correct,
            note="" if correct else "committed a value, but not the forced one (incumbent-frame fit)",
        )
    if _UNDERDETERMINED.search(text):
        return Grade("STUCK_IN_M", None, forced, False,
                     "declares the value under-determined — the incumbent-frame outcome")
    return Grade("NO_COMMIT", None, forced, False, "no parseable committed value; flag for review")


def classify_negative_control(env: TransferEnvironment, text: str) -> Grade:
    held = env.label(env.held_out)
    value = extract_committed_value(text, held)
    forced = env.forced_value
    overreach = _asserts_reframe_structure(text)

    if overreach:
        return Grade("OVERREACH", value, forced, value == forced if value is not None else False,
                     "asserts impossibility/cycle-gain, which is false here — the reframe misfired")
    if value is not None:
        correct = value == forced
        return Grade("DEFENDS_M" if correct else "WRONG_VALUE", value, forced, correct,
                     "" if correct else "defends M but with the wrong number")
    return Grade("NO_COMMIT", None, forced, False, "no parseable committed value; flag for review")


def grade(env: TransferEnvironment, text: str) -> Grade:
    if env.kind == "transformative":
        return classify_transformative(env, text)
    return classify_negative_control(env, text)
