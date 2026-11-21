"""The Assay House — move class: property -> relation (a scalar was a projection of a 2-vector).

Drafted in docs/memos/retrieval_resistant_environments.md (Environment A). Five standing
dye baths A-E; T(X,Y) is the grams the first bath gains when the two are coupled. The
incumbent reads each bath's `avidity` as one number (a scalar potential); the reframe
reads each bath as a 2-vector, so transfer is the oriented area they span.

The canonical instance below is built from ground-truth 2-vectors and forces T(C,E) = +1
by three independent quadruples. `random_instance()` draws fresh vectors so the forced
number is not retrievable across items (the whole point of a synthetic surface).

The surface vocabulary (baths, membranes, uptake, contamination) cues THERMODYNAMICS —
chemical potential across a membrane — which is the wrong branch. The facts select
exterior algebra. There is no famous "dye-bath anomaly" to recall.
"""

import random
from fractions import Fraction

from src.sci_twist.environment import Pair, TransferEnvironment, transfer

LABELS = ["A", "B", "C", "D", "E"]

# Ground-truth 2-vectors (x1, x2) for the canonical instance. T(i,j) = x1_i x2_j - x2_i x1_j.
# Chosen so the nine given transfers are small integers and T(C,E) = +1.
CANONICAL_VECTORS = {
    "A": (1, 0),
    "B": (3, 2),
    "C": (0, 1),
    "D": (-3, -1),
    "E": (-1, -2),
}

SETTING = """
An assay house maintains five standing dye baths, catalogued A through E. When any two baths
are coupled through a porous membrane and left overnight, dye moves between them. The house
records, for each ordered pair, the grams gained by the first bath; call it T(X,Y). The
measurement is clean and repeatable to within 0.01 g, and two regularities have held for
decades: T(X,Y) = -T(Y,X) exactly, and T(X,X) = 0.
""".strip()

INCUMBENT_ACCOUNT = """
The house's account is that each bath has an intrinsic avidity k — a single number, a property
of the bath — and that transfer is driven by the difference, T(X,Y) = k_X - k_Y. This explains
the antisymmetry immediately and has never been questioned. Where it falls short it is repaired:
no single assignment of avidities reproduces the table, so the house carries a set of pairwise
correction terms, one per pair, attributed to membrane contamination, which restore agreement
exactly. Each addition fits. The account has never failed.
""".strip()

OBSERVATIONS = """
Two facts sit awkwardly with the account. First, no consistent assignment of avidities
reproduces the table without the per-pair correction terms. Second, coupling A to B, then B to
D, then D back to A returns dye to A with a net gain, and the cycle can be run again for the same gain.
""".strip()

EPICYCLES = [
    "A per-pair correction term epsilon(X,Y), attributed to membrane contamination, added to "
    "restore agreement with the avidity model — one free parameter per pair.",
    "A 'contamination memory' or membrane-asymmetry term posited to explain the cyclic net gain "
    "while retaining a scalar avidity.",
]

# Terms that would betray the reframe or name the real structure — voids the item if present.
FORBIDDEN = [
    "oriented area", "exterior algebra", "wedge", "bivector", "2-vector", "two-vector",
    "rank 2", "rank-2", "antisymmetric matrix", "pfaffian", "cross product", "determinant",
    "symplectic", "vector", "curl", "non-conservative",
]

WITNESS_CYCLE = [0, 1, 3]  # A -> B -> D -> A


def _table_from_vectors(vectors: dict[str, tuple[int, int]]) -> dict[Pair, Fraction]:
    """Full antisymmetric transfer table (all i<j pairs) from ground-truth 2-vectors."""
    values: dict[Pair, Fraction] = {}
    for i in range(len(LABELS)):
        for j in range(i + 1, len(LABELS)):
            (x1i, x2i) = vectors[LABELS[i]]
            (x1j, x2j) = vectors[LABELS[j]]
            values[(i, j)] = Fraction(x1i * x2j - x2i * x1j)
    return values


def build(vectors: dict[str, tuple[int, int]] | None = None, held_out: Pair = (2, 4)) -> TransferEnvironment:
    """Assemble (and validate) an Assay House from 2-vectors. Held-out defaults to (C, E)."""
    vectors = vectors or CANONICAL_VECTORS
    full = _table_from_vectors(vectors)
    forced = full[held_out]
    given = {p: v for p, v in full.items() if p != held_out}

    env = TransferEnvironment(
        name="assay_house",
        kind="transformative",
        entities=LABELS,
        given=given,
        held_out=held_out,
        forced_value=forced,
        setting=SETTING,
        observations=OBSERVATIONS,
        incumbent_account=INCUMBENT_ACCOUNT,
        incumbent="avidity is a scalar property of a bath; T(X,Y) = k_X - k_Y",
        reframe="each bath carries two quantities; T(X,Y) is the oriented area x1_X x2_Y - x2_X x1_Y (rank 2)",
        epicycles=EPICYCLES,
        forbidden=FORBIDDEN,
        witness_cycle=WITNESS_CYCLE,
        ground_truth_note=(
            f"ground-truth 2-vectors {vectors}; forced T{held_out} = {forced}; "
            f"cyclic net gain around A-B-D-A."
        ),
    )
    env.validate()
    return env


def random_instance(seed: int, held_out: Pair = (2, 4), lo: int = -4, hi: int = 4) -> TransferEnvironment:
    """A fresh Assay House from random integer 2-vectors, retrying until it is a valid,
    non-degenerate transformative item (no accidental scalar potential; artifact over-determined)."""
    rng = random.Random(seed)
    for _ in range(500):
        vectors = {lab: (rng.randint(lo, hi), rng.randint(lo, hi)) for lab in LABELS}
        try:
            return build(vectors, held_out=held_out)
        except ValueError:
            continue  # degenerate draw (e.g. collinear -> a potential fits); redraw
    raise RuntimeError(f"FATAL: could not draw a valid Assay House in 500 tries (seed={seed})")


# ---- Negative control: a genuine potential. The incumbent is CORRECT; reframing is over-reach.

NEG_POTENTIAL = {"A": 0, "B": 2, "C": 5, "D": 1, "E": 4}

NEG_OBSERVATIONS = """
Two facts have been checked. First, a single assignment of avidities reproduces the entire table
with no correction terms. Second, dye run around any closed loop of couplings — A to B to D to A,
or any other — returns to its origin with no net gain; the books balance exactly every time.
""".strip()

NEG_INCUMBENT_ACCOUNT = """
The house's account is that each bath has an intrinsic avidity k, and transfer is the difference
T(X,Y) = k_X - k_Y. The account reproduces every measured pair exactly, with nothing left over
and no corrections required.
""".strip()


def build_negative_control(potential: dict[str, int] | None = None, held_out: Pair = (2, 4)) -> TransferEnvironment:
    """An Assay House whose transfer really is a potential difference. Defending the incumbent
    (and predicting T(C,E) = k_C - k_E) is correct; positing a hidden second quantity is over-reach."""
    potential = potential or NEG_POTENTIAL
    full: dict[Pair, Fraction] = {}
    for i in range(len(LABELS)):
        for j in range(i + 1, len(LABELS)):
            full[(i, j)] = Fraction(potential[LABELS[i]] - potential[LABELS[j]])
    forced = full[held_out]
    given = {p: v for p, v in full.items() if p != held_out}

    env = TransferEnvironment(
        name="assay_house_control",
        kind="negative_control",
        entities=LABELS,
        given=given,
        held_out=held_out,
        forced_value=forced,
        setting=SETTING,
        observations=NEG_OBSERVATIONS,
        incumbent_account=NEG_INCUMBENT_ACCOUNT,
        incumbent="avidity is a scalar property of a bath; T(X,Y) = k_X - k_Y",
        reframe="(the tempting but FALSE reframe) each bath carries two quantities and cycles gain",
        epicycles=[],
        forbidden=FORBIDDEN,
        ground_truth_note=f"genuine potential {potential}; loops vanish; forced T{held_out} = {forced}.",
    )
    env.validate()
    return env
