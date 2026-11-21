"""Discovery environments.

    E = (S, M, A)

      S  description / summary  — the setting, in terms available at year T_M
      M  prevailing explanation — the incumbent frame the model must supplant
      A  anomalous evidence     — the evidence that threatens M

E is the *stimulus*. It never contains the discovery.

HOUSE FORMAT — every environment is modelled on Environment #1 (The Hillside) and
Environment #2 (Lanterns and Clingers). Those set the template and new environments
must not drift from it:

  * Three paragraphs, ~200-240 words total. Hillside is 216, Lanterns 231.
  * Paragraph 1 = S: the setting and the convention by which things are observed.
  * Paragraph 2 = A: "Several regularities have accumulated..." — the anomalies,
    stated flatly as observations, never editorialised as puzzling.
  * Paragraph 3 = M: the standing account, then its epicycles introduced as
    reasonable additions, closing on "Each addition fits. The account has never failed."
  * Plain declarative prose. No period pastiche — the constraint is that no
    post-cutoff *concept* appears, not that the prose sound antique.
  * One prompt, always the same: "How do you explain what's happening?"

Note the render order is S, A, M — the anomalies land before the account that fails
to explain them, exactly as in Hillside. The tuple is a component decomposition,
not a presentation order.

E alone is not gradeable, so each environment carries a companion `AnswerKey`:

    K = (D, core_commitment, epicycles, criteria)

`epicycles` is what makes the failure mode gradeable rather than impressionistic,
and history hands it to us: for a real discovery, the record documents what
competent scientists *actually proposed instead*. Each environment therefore ships
with a **documented human epicycle baseline**, not one we invented.

Grading is defined relative to M and D:

  JUMP      abandons M's core commitment and reaches D
  EPICYCLE  preserves M's core commitment, patched with auxiliary assumptions
  MISS      neither

The leakage check is the load-bearing safety property. If any word of E names D, or
is anachronistic for the model's era, the item is void — the entire reason for a
time-capsule model is that D is unreachable by retrieval.
"""

import re
from dataclasses import dataclass, field

# The single-turn prompt, identical across environments (as in Hillside/Lanterns).
PROMPT = "How do you explain what's happening?"

# Word-count band for S + A + M, anchored on Hillside (216) and Lanterns (231).
MIN_WORDS, MAX_WORDS = 170, 280


@dataclass(frozen=True)
class AnswerKey:
    discovery: str          # D — the target, held out
    core_commitment: str    # the belief M rests on; a JUMP must abandon it
    epicycles: list[str]    # patches that preserve the core commitment
    criteria: list[str]     # partial-credit checkpoints, easiest to hardest
    historical_note: str = ""


@dataclass(frozen=True)
class Environment:
    name: str
    haven_title: str        # must match a title in haven100.json
    discovery_year: int     # T'
    summary: str            # S
    anomaly: str            # A
    prevailing: str         # M
    key: AnswerKey
    # Terms that must NOT appear in S/A/M: they name D, or are anachronistic for a
    # pre-T_M reader. Checked mechanically; a hit voids the item.
    forbidden: list[str] = field(default_factory=list)

    def render(self) -> str:
        """The scenario. S, A, M — never the key."""
        return (
            f"{self.summary.strip()}\n\n"
            f"{self.anomaly.strip()}\n\n"
            f"{self.prevailing.strip()}"
        )

    def render_prompt(self) -> str:
        return f"{self.render()}\n\n{PROMPT}"

    def word_count(self) -> int:
        return len(self.render().split())

    def validate(self) -> None:
        """Fail loudly on an empty component, a missing epicycle set, format drift, or a leak."""
        for label, text in (("S", self.summary), ("A", self.anomaly), ("M", self.prevailing)):
            if not text.strip():
                raise ValueError(f"FATAL: environment '{self.name}' has an empty {label}")

        if not self.key.epicycles:
            raise ValueError(
                f"FATAL: environment '{self.name}' declares no epicycles. Without them the "
                f"epicycle cheat cannot be scored, and the item cannot distinguish a model that "
                f"patched M from one that replaced it."
            )

        n = self.word_count()
        if not (MIN_WORDS <= n <= MAX_WORDS):
            raise ValueError(
                f"FATAL: environment '{self.name}' is {n} words; the house format is "
                f"{MIN_WORDS}-{MAX_WORDS} (Hillside 216, Lanterns 231). Environments must not "
                f"drift in length — scenario length is a confound across items."
            )

        prompt = self.render().lower()
        leaked = [t for t in self.forbidden
                  if re.search(rf"\b{re.escape(t.lower())}\b", prompt)]
        if leaked:
            raise ValueError(
                f"FATAL: environment '{self.name}' leaks {leaked} into the prompt. The item is "
                f"void — a time-capsule model could reach D by reading rather than reasoning."
            )
