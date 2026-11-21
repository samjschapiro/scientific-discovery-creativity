"""Transfer environments — the property->relation move class (the Assay House family).

An environment presents a body of pairwise measurements `T(X,Y)` and an incumbent
account of them. The incumbent reads each bath as carrying a single scalar `avidity`,
so transfer is a potential difference `T(X,Y) = k_X - k_Y`. The reframe reads each
bath as carrying *two* quantities, so transfer is an oriented area
`T(X,Y) = x1_X x2_Y - x2_X x1_Y` — an antisymmetric matrix of rank 2.

The whole measurement is the asymmetry between them:

  * The incumbent (scalar potential) CANNOT produce a cycle with net gain, because
    differences `k_X - k_Y` sum to zero around any loop. So on a transformative
    instance no potential reproduces the table, and the held-out entry is
    UNDER-DETERMINED under the incumbent — it can only be fit, never predicted.

  * The reframe (rank 2) forces every 4x4 sub-Pfaffian to vanish, which OVER-
    determines the held-out entry: several disjoint quadruples each pin it to the
    same value, and they agree *before* the tenth measurement is made.

This module carries the exact-arithmetic proof of both facts. `validate()` fails
loudly unless the instance really has this structure — a mis-built item (where the
incumbent could predict the answer, or the reframe does not force it) is not a
research instrument, it is a bug, and it must crash at construction, not at analysis.

The forced held-out value is the **artifact**: grading is exact match to it, so a
verbal reframe with the wrong number earns nothing and a correct number cannot be
reached from the incumbent frame. See docs/memos/grading_frame_replacement.md.

A NEGATIVE CONTROL is the structural mirror image: a genuine potential, where the
incumbent IS correct, loops vanish, and the tempting rank-2 reframe adds nothing. Its
validator asserts the opposite invariant (a potential *does* exist).
"""

import re
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations

# A pair is a tuple of entity indices (i, j) with i < j. `given` and `held_out` are
# keyed this way; the antisymmetric value for (j, i) is the negation.
Pair = tuple[int, int]


def _canonical(i: int, j: int) -> tuple[Pair, int]:
    """Return the i<j key for the pair and the sign to apply to its stored value."""
    if i == j:
        raise ValueError(f"FATAL: a pair needs two distinct entities, got ({i}, {j})")
    return ((i, j), 1) if i < j else ((j, i), -1)


def transfer(values: dict[Pair, Fraction], i: int, j: int) -> Fraction:
    """T(i, j), enforcing antisymmetry from the i<j storage. Raises if unknown."""
    key, sign = _canonical(i, j)
    if key not in values:
        raise KeyError(f"FATAL: T{key} is not known")
    return sign * values[key]


def pfaffian4(values: dict[Pair, Fraction], quad: tuple[int, int, int, int]) -> Fraction:
    """The 4x4 sub-Pfaffian on ordered indices (a<b<c<d).

    For a rank-<=2 antisymmetric matrix this vanishes. It is the single algebraic
    fact the whole reframe rests on:

        Pf = T(a,b) T(c,d) - T(a,c) T(b,d) + T(a,d) T(b,c)
    """
    a, b, c, d = quad
    return (
        transfer(values, a, b) * transfer(values, c, d)
        - transfer(values, a, c) * transfer(values, b, d)
        + transfer(values, a, d) * transfer(values, b, c)
    )


def solve_pair_from_pfaffian(
    values: dict[Pair, Fraction], quad: tuple[int, int, int, int], unknown: Pair
) -> Fraction:
    """Solve Pf(quad) = 0 for the one unknown transfer in `quad`.

    The Pfaffian is linear in any single entry, so evaluating it with the unknown set
    to 0 and to 1 recovers the line `coeff * x + const` and hence its root. This is
    how the reframe predicts the held-out value from the others.
    """
    trial = dict(values)
    key, sign = _canonical(*unknown)

    trial[key] = Fraction(0)
    const = pfaffian4(trial, quad)
    trial[key] = Fraction(1)
    coeff = pfaffian4(trial, quad) - const

    if coeff == 0:
        raise ValueError(
            f"FATAL: quad {quad} does not constrain {key}; cannot solve (coeff = 0)."
        )
    # Pf = coeff * stored + const = 0  ->  stored = -const/coeff, then de-sign it.
    return sign * (-const / coeff)


def find_potential(
    n: int, values: dict[Pair, Fraction]
) -> tuple[dict[int, Fraction] | None, tuple[Pair, Fraction, Fraction] | None]:
    """Try to assign each entity a scalar k with T(i,j) = k_i - k_j on every known edge.

    Returns (potential, None) if a consistent assignment exists, or
    (None, (edge, expected, actual)) with the first edge that contradicts one.

    This is the incumbent's whole claim. On a transformative instance it fails; on a
    negative control it succeeds.
    """
    if n == 0:
        return {}, None
    known = sorted(values)
    adj: dict[int, list[int]] = {i: [] for i in range(n)}
    for (i, j) in known:
        adj[i].append(j)
        adj[j].append(i)

    potential: dict[int, Fraction] = {}
    for start in range(n):
        if start in potential:
            continue
        potential[start] = Fraction(0)
        stack = [start]
        while stack:
            i = stack.pop()
            for j in adj[i]:
                expected = potential[i] - transfer(values, i, j)  # k_j = k_i - T(i,j)
                if j in potential:
                    if potential[j] != expected:
                        key, _ = _canonical(i, j)
                        return None, (key, expected, potential[j])
                else:
                    potential[j] = expected
                    stack.append(j)
    return potential, None


def loop_sum(values: dict[Pair, Fraction], cycle: list[int]) -> Fraction:
    """Net transfer around a closed walk. Zero for any potential; nonzero exposes one."""
    total = Fraction(0)
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        total += transfer(values, a, b)
    return total


@dataclass(frozen=True)
class TransferEnvironment:
    name: str
    kind: str                       # "transformative" | "negative_control"
    entities: list[str]             # display labels, e.g. ["A", "B", "C", "D", "E"]
    given: dict[Pair, Fraction]     # measured transfers, keyed i<j
    held_out: Pair                  # the pair withheld; its value is the artifact
    forced_value: Fraction          # what the correct frame forces the held-out pair to be

    # Narrative components (rendered into the prompt by prompts.py).
    setting: str                    # S — the assay house and its measurement convention
    observations: str               # the two facts that sit awkwardly with the incumbent
    incumbent_account: str          # M — avidity, with its correction-term epicycles

    incumbent: str                  # one-line statement of M's frame
    reframe: str                    # one-line statement of R's frame
    epicycles: list[str]            # the free parameters M must posit; countable
    forbidden: list[str] = field(default_factory=list)   # referent-probe leak guard
    witness_cycle: list[int] = field(default_factory=list)  # a loop proving M impossible
    ground_truth_note: str = ""

    # ---- derived ----

    def n(self) -> int:
        return len(self.entities)

    def label(self, pair: Pair) -> str:
        i, j = pair
        return f"T({self.entities[i]},{self.entities[j]})"

    def all_values(self) -> dict[Pair, Fraction]:
        """Given entries plus the held-out entry at its forced value — the full table."""
        return {**self.given, self.held_out: self.forced_value}

    def forcing_quads(self) -> list[tuple[int, int, int, int]]:
        """Quadruples that contain the held-out pair and otherwise use only given values."""
        u, v = self.held_out
        out = []
        others = [k for k in range(self.n()) if k not in (u, v)]
        for extra in combinations(others, 2):
            quad = tuple(sorted((u, v, *extra)))
            # every pair in the quad except held_out must be given
            pairs = [tuple(sorted(p)) for p in combinations(quad, 2)]
            if all(p in self.given for p in pairs if p != self.held_out):
                out.append(quad)
        return out

    # ---- validation: the item is a bug unless this structure really holds ----

    def validate(self) -> None:
        for attr in ("setting", "observations", "incumbent_account"):
            if not getattr(self, attr).strip():
                raise ValueError(f"FATAL: '{self.name}' has an empty {attr}")

        if self.held_out in self.given:
            raise ValueError(f"FATAL: '{self.name}' held-out pair {self.held_out} is also given")

        if self.kind == "transformative":
            self._validate_transformative()
        elif self.kind == "negative_control":
            self._validate_negative_control()
        else:
            raise ValueError(f"FATAL: '{self.name}' unknown kind '{self.kind}'")

        self._check_no_leak()

    def _validate_transformative(self) -> None:
        # (1) The incumbent is impossible: no scalar potential fits the given table.
        potential, conflict = find_potential(self.n(), self.given)
        if potential is not None:
            raise ValueError(
                f"FATAL: '{self.name}' claims to be transformative, but a scalar potential "
                f"DOES fit its data ({potential}). The incumbent could predict the answer, so "
                f"there is nothing to overturn. This is not a frame-replacement item."
            )
        # ...and a concrete cycle witnesses it, for the prompt and for the reader.
        if self.witness_cycle:
            gain = loop_sum(self.given, self.witness_cycle)
            if gain == 0:
                raise ValueError(
                    f"FATAL: '{self.name}' witness_cycle {self.witness_cycle} has zero net gain; "
                    f"it does not witness the impossibility of a potential."
                )
            if not self.epicycles:
                raise ValueError(
                    f"FATAL: '{self.name}' declares no epicycles; the epicycle cheat is then "
                    f"unscoreable and a patched-M answer is indistinguishable from a jump."
                )

        # (2) The reframe reproduces the given data: every fully-known quad has Pf = 0.
        for quad in combinations(range(self.n()), 4):
            pairs = [tuple(sorted(p)) for p in combinations(quad, 2)]
            if self.held_out in pairs:
                continue
            pf = pfaffian4(self.given, quad)
            if pf != 0:
                raise ValueError(
                    f"FATAL: '{self.name}' given data is not rank-2: Pf{quad} = {pf} != 0. "
                    f"The reframe does not even fit the observations."
                )

        # (3) The reframe FORCES the artifact: every forcing quad agrees on forced_value.
        quads = self.forcing_quads()
        if len(quads) < 2:
            raise ValueError(
                f"FATAL: '{self.name}' has {len(quads)} forcing quad(s); need >=2 so the "
                f"held-out value is over-determined, not merely determined."
            )
        for quad in quads:
            got = solve_pair_from_pfaffian(self.given, quad, self.held_out)
            if got != self.forced_value:
                raise ValueError(
                    f"FATAL: '{self.name}' quad {quad} forces {self.label(self.held_out)} = "
                    f"{got}, but forced_value is {self.forced_value}. The item is inconsistent."
                )

    def _validate_negative_control(self) -> None:
        # Mirror image: a potential DOES exist, and it predicts the held-out value.
        potential, conflict = find_potential(self.n(), self.given)
        if potential is None:
            raise ValueError(
                f"FATAL: '{self.name}' is a negative control but no scalar potential fits its "
                f"data (conflict {conflict}). A negative control must have a *correct* incumbent."
            )
        u, v = self.held_out
        predicted = potential[u] - potential[v]
        if predicted != self.forced_value:
            raise ValueError(
                f"FATAL: '{self.name}' potential predicts {self.label(self.held_out)} = "
                f"{predicted}, but forced_value is {self.forced_value}."
            )

    def _check_no_leak(self) -> None:
        text = f"{self.setting}\n{self.observations}\n{self.incumbent_account}".lower()
        leaked = [t for t in self.forbidden if re.search(rf"\b{re.escape(t.lower())}\b", text)]
        if leaked:
            raise ValueError(
                f"FATAL: '{self.name}' leaks referent term(s) {leaked} into the prompt. The "
                f"surface must cue the wrong branch, not name the reframe."
            )
