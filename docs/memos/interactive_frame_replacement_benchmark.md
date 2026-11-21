# Design memo: the discoverable scientific twist (TwistBench → science)

**Status:** design draft, 2026-07-17. Successor to the retired `time_capsule` track
(`docs/tracks/time_capsule/progress.md`) and the parked `format_sensitivity` track. Supersedes
the standalone framing in `docs/memos/retrieval_resistant_environments.md` and
`docs/memos/grading_frame_replacement.md` by folding both into a single instrument.

Working names: **SciTwist** / **TwistBench-S** / *the Anomaly Rooms*. Pick later.

---

## One-sentence thesis

TwistBench measures transformational creativity by asking a model to **write** a literary story
with a plot twist; the scientific version measures it by asking a model to **discover** the twist
already latent in a body of evidence — a real (or realistically-constrained) scientific reframe
that overturns an incumbent account. Generation → discovery; literary → scientific; LLM-judge →
forced artifact wherever the reframe forces a number.

This is the "assess transformational creativity in science" that TwistBench's own Limitations
section names as future work, and it directly attacks the contamination problem that killed the
`time_capsule` track — by item design (retrieval-resistant surfaces + randomized artifacts)
rather than by crippled vintage models.

## Why "discover," not "write"

TwistBench is a *generation* task and its process analysis found the tell: models choose the twist
first, then retrofit the plot. That is fine for authoring fiction but it is the wrong shape for
*science*, where the twist is not yours to invent — the world already fixed it, and the task is to
be *forced* to it by evidence you did not get to choose. The scientific instrument therefore drops
the model into an environment where the incumbent frame is stated and the anomaly is present, and
asks it to reach the reframe. This is **abduction under an incumbent** — a mode the standard
abduction taxonomy (generation vs. selection, cf. the 2604.08016 survey) has no slot for: there is
already a standing (wrong) explanation that must be *displaced*, which is neither inventing a
hypothesis from nothing nor picking from a menu. Naming that mode is a conceptual contribution.

## The anatomy of a scientific-twist environment

The literary structure ports almost line-for-line. This mapping is the design spec:

| TwistBench (literary) | Scientific twist (this instrument) |
|---|---|
| Conceptual space set by the story | Body of observations `O` + an incumbent frame `M` that reads them |
| Implicit assumptions (a1, a2…) inferred from events | Load-bearing commitments of `M` the data is read *through* |
| The twist: one reveal that overturns the assumptions | The reframe `R`: one restructuring that overturns `M`'s commitments |
| **Surprise** — how much must you re-read | How many of `M`'s assumptions `R` overturns; depth of re-reading |
| **Coherence** — nothing retracted, details fit better | `R` re-reads *every* datum in `O` with nothing retracted (indeed fits better) |
| **Realism** gate — no ghosts/dreams/simulation | **Fair play** gate — `R` reinterprets the *given* evidence; no invented unobservable, no discarded data |
| (none — literary twists force no number) | **Forced artifact** — a held-out value only `R` produces; `M` is structurally unable to |

The last row is the science-only asset. A literary twist can only be judged by rubric; a scientific
twist can force an exact number (the `T(C,E)=+1` of the Assay House), which converts "grade the
species not the genus" from an LLM-judge problem into exact match.

## Fair play is the unifying design principle

TwistBench's realism gate generalizes into the single rule that governs every environment:

> **A reframe plays fair iff it (1) re-reads every given observation without retracting any
> [coherence], (2) overturns a load-bearing commitment of the incumbent [surprise], (3) invents no
> unobservable mechanism and discards no datum [realism], and (4) makes a risky new prediction the
> incumbent does not [the forced artifact].**

This is Popper + Kuhn made mechanical, and it names both cheats at once:

- **The epicycle cheat** = the scientific "it was all a dream." It resolves the anomaly by adding a
  free parameter per observation (membrane-contamination correction terms; scale bias) — fitting
  everything, predicting nothing, retracting nothing but explaining nothing. Fails clause (4): it
  cannot produce the held-out artifact. **Countable**: one epicycle per posited free parameter.
- **Breaking the world model** = the over-eager reframe that is surprising and internally neat but
  contradicts a given datum or posits an impossible mechanism. Fails clause (3).

Every environment is built so the incumbent-plus-epicycles fits all *visible* data and predicts
nothing, while the fair reframe over-determines the artifact. That asymmetry **is** the measurement.

## Two sourcing strategies (run both, like TwistBench's LLM pool + human ceiling)

**Strategy A — real reframes, obfuscated (the "reality-based" route).** Take genuine scientific
twists whose structure is an assumption-overturning: neutron ("it's a gamma ray" → "a neutral
massive particle"), dark matter (rotation anomaly → unseen mass), the selection-effect reframes
(a "law" is the edge of the detection window), Semmelweis, H. pylori/ulcers, continental drift,
oxygen vs. phlogiston. Strip the retrieval keys — rename entities, swap surface vocabulary to cue
the *wrong* salient branch, randomize the quantitative instance. Strongest external-validity claim
("the model reached a real paradigm shift it could not retrieve"); guarded by the referent-naming
probe. This is the science analog of TwistBench's 18 expert-human stories: the ceiling and the
reality anchor.

**Strategy B — synthetic but realistic (the "fair play" route).** Invent micro-worlds (Assay House,
The Trough, The Burrow Survey — already drafted in `retrieval_resistant_environments.md`) where the
incumbent is a plausible misreading and the reframe is forced by real mathematical/physical
structure (exterior algebra, bead-conservation across a front, a detection threshold). No referent,
so retrieval-proof by construction; auto-gradeable; randomizable → scalable. The "reality-based"
claim is weaker (they are puzzles), so they are the **core instrument**, with Strategy A as the
transfer test.

## The scientific twist-type taxonomy (= our move classes)

TwistBench clusters literary twists empirically (Fig. 4). The scientific twist types are not
empirical — they are the catalogue of conceptual restructurings, already inventoried:

- re-individuation (N things are one) — *retrieval-prone, verbal-only arm*
- property → relation (a scalar was a projection of a 2-vector) — *Assay House*
- substance → process (the entity is a pattern in a medium) — *The Trough*
- law → artifact-of-the-window (a tight law is the detection boundary) — *The Burrow*
- figure/ground inversion; direction-of-causation flip; continuous → quantized — *not yet built*

**A move class cannot be made novel** — a genuinely new one would itself be a scientific revolution.
What is novel is the *(substrate, move) pairing*, so no lookup maps surface → answer. State this in
the paper as both a limitation and a defense of the design.

## Protocol: interactive discovery (EscapeBench) + scalable generation (MacGyver)

**Interaction loop (from EscapeBench's implicit-goal design).** The model gets a mundane role
("you are the incoming warden; the standing account is avidity `k_X − k_Y`") and a *small*,
symbolically-computed action grammar — never an LLM in the environment:

- `Measure(pair)` — reveal a withheld datum (computed from `R`'s ground truth)
- `Manipulate(param)` — run a counterfactual (pool two baths, double the microphone area)
- `Note(hypothesis)` — free-text, logged, ungraded
- `Commit(frame, value)` — terminal; grades the forced artifact

Feedback comes from `R`'s ground truth, so a model living in `M` keeps getting data that will not
fit. **The anomaly is never announced** — this is the fix for the `format_sensitivity` finding that
stating the puzzle (`P_PUZZLE`) carries the jump. We measure whether the model *notices*.

**Hint escalation = the frame-stickiness dose (from EscapeBench's hints-when-stuck).** After k
confirmatory actions with no challenge to `M`, escalate: (1) "the correction terms keep growing" →
(2) "the residuals are one-sided" → (3) "a scalar potential cannot produce a cycle." **Hints-to-
reframe** is the headline stickiness measure, replacing the discrete framing ladder with a
continuous, noticing-based one.

**Generation pipeline (from MacGyver's 3-iteration refinement + solvable/unsolvable mix).**
1. Pick a move class; instantiate into a randomized synthetic substrate.
2. **Constraint-inject** the incumbent `M` + its epicycle patch so `M` fits all visible data but is
   rank-deficient for the held-out artifact — verify by symbolic solver (this is MacGyver's "add
   properties to veto the obvious solution").
3. **Distractor-inject** surface vocabulary cueing the wrong retrieval branch; verify with the
   referent-naming probe (does a frontier model name a real phenomenon? if yes, resurface).
4. **Auto-validate difficulty**: confirm `M`+epicycles cannot predict the artifact (under-
   determined) and `R` over-determines it (bonus: two independent quadruples give the same value).
5. Randomize the instance → the artifact is not retrievable.

## Metrics (a blend, each earning its place)

| Metric | Source | Measures |
|---|---|---|
| **Species solve rate** (correct frame *and* forced value) | ours | the transformational claim |
| **Surprise / Coherence** on a TwistBench-style rubric | TwistBench | for the verbal arm + real-reframe items where no number is forced |
| **Realism / fair-play gate** (hard gate) | TwistBench | rejects epicycle *and* world-breaking reframes |
| **Diversity across a model's reframes** (embedding dissimilarity) | TwistBench | mode collapse — does the model have one hammer ("it's a selection effect") |
| **Epicycle count** (free params posited, from the log) | ours | the cheat, objective and mechanical |
| **Hints-to-reframe** | EscapeBench | frame stickiness (dose–response) |
| **Action order** (did it `Commit` before gathering discriminating evidence?) | ours + TwistBench process analysis | confirmation vs. letting data force the reframe — the discovery analog of "twist first, plot second" |
| **Discriminating-experiment rate** (did `Manipulate` choices actually separate `M` from `R`?) | ours | abductive competence; impossible in a static prompt |
| **Incumbency delta** (same item with vs. without `M` stated) | ours | does a present wrong frame *suppress* the leap — the project's core claim |
| **Generation − Selection gap** (must produce `R` vs. pick `R` from a menu) | 2604.08016 survey | localizes whether the model can recognize but not generate |

## Failure modes, translated from TwistBench

- **Mode collapse** → the model resolves every environment with the same genus-level reframe ("it's
  emergent," "it's a selection effect"). The diversity metric catches it; the forced artifact denies
  it credit (the genus produces no number). This *is* the genus/species problem relocated.
- **Breaking the world model** → the model proposes an unfair reframe (invents an unobservable, or
  contradicts a given datum). The realism gate rejects it. Note this is symmetric with the epicycle
  cheat: one over-reframes, one under-reframes; both fail fair play, from opposite sides.

## The negative control is non-negotiable (both benchmarks agree)

TwistBench gates on realism; MacGyver ships 22% *unsolvable* items and grades "correctly identifies
unsolvable." We need the analog: items where `M` is actually **correct** and the tempting reframe is
false (residuals two-sided, excavated specimens show the same relation). Credit = *defend* `M` and
produce `M`'s number; reframing is penalized. Without it, "always reframe" scores 100% and we cannot
separate a model that *makes* leaps from one that *always* leaps. Build ≥1 per move class.

## Open problems / risks

- **Interactivity multiplies grader attack surface.** Keep the action grammar tiny and compute every
  environment response symbolically from `R`. No LLM in the loop for the environment itself.
- **Strategy-A obfuscation may not fool frontier models.** The referent-naming probe is the gate; if
  a re-skinned neutron is still recognized, it drops to the verbal arm or is rebuilt.
- **Realism gate for synthetic worlds needs a definition of "impossible."** In a made-up world,
  fair play means the reframe uses only structure derivable from stated rules — operationalize as
  "no free parameter that is not itself forced by an observation."
- **Move-class inventory is incomplete** (missing figure/ground, causation-flip, quantization) and
  each needs a referent-free substrate.

## What to prototype first

1. **Assay House, static, single-shot.** It already forces `T(C,E)=+1`. Wrap it with the incumbency
   pair (with/without `M`) and one negative control. Grade by exact match + epicycle count. No LLM
   judge, no interactivity yet — prove the artifact grading is clean on a move class that forces a
   number.
2. Add the **referent-naming probe** and run the real-reframe (Strategy A) version of one item to
   test whether obfuscation holds against a frontier model.
3. Only then add the **interactive loop + hint ladder** (Assay House → Trough → Burrow) and the
   discriminating-experiment / action-order metrics.
4. Port the TwistBench **judge ensemble + ICC validation** for the verbal arm and the real-reframe
   items where no number is forced.

The parked re-individuation environments (Hillside, Lanterns) are not wasted — they become the
**verbal-only arm**, and the gap between their verbal score and the synthetic items' artifact score
is itself the quantified "slop transformation" result.
