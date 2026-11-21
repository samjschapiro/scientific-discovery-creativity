# Brainstorm: how to actually grade frame replacement

## Why the current framework stalled

The Hillside/Lanterns framework grades a **verbal reframe** ("the stems are one organism")
under a **task framing** ("explain / summarize"). Three limitations are coupled, and none is
fixable by better skinning:

1. **Species-vs-genus is ungradeable in prose.** Grok wrote "a single signalling collective"
   (right genus) while keeping soil as the medium (wrong species). A verbal answer cannot be
   made to distinguish these; a keyword grader false-negatived on "single *coordinated*
   organism." The doc's own "grade the species" rule has no verbal implementation.
2. **Retrieval leakage.** Re-individuation answers ("N tokens are one entity") are cached
   schemas. Novel surfaces block naming the *instance* (Pando) but not retrieving the *move*.
3. **Demand characteristics.** Whether the model *volunteers* the reframe is set by the task
   framing, not by whether it *found* it (the P_SUMMARIZE result). We were measuring compliance.

The lit review (`docs/reports/2026-07-10_scientific_qa_abduction_landscape/`) confirms this is
structural, not local: **no existing benchmark grades a frame-specific derivable artifact**;
αNLI grades plausibility, InAbHyD grades parsimony, science Q&A grades answer accuracy. And
LLM-SRBench shows the fix works at scale — grade a **derivable artifact** (an equation) and
block memorization by **transforming** known forms.

## The pivot

**Stop grading the reframe. Grade a derivable artifact only the correct frame can produce.**

A verbal reframe can be faked with a slogan; a *number* cannot. If the item is built so the
standing account is structurally incapable of producing the artifact — it is underdetermined,
or has the wrong functional form — then a model that produces the artifact must hold the
correct frame, and no genus-level acknowledgment earns credit. This simultaneously kills all
three limitations: species-vs-genus becomes exact-match, retrieval dies because the artifact
depends on this item's randomized data, and demand characteristics vanish because the task is
"compute X," not "reframe if you feel like it."

The cost: **re-individuation mostly does not force an artifact** (that is why it stalled). The
move classes that do are property→relation, constraint/detection-boundary, and
substance→process — the ones already sketched in
`docs/memos/retrieval_resistant_environments.md`. The pivot is as much *which move classes we
use* as *how we grade*.

---

## Eight mechanisms for grading frame replacement

Each is rated on: can the wrong frame fake it, does it detect the epicycle cheat, is it
retrieval-resistant, and can it be graded without an LLM judge.

### 1. Forced held-out prediction (the strongest primitive)

Observations O are consistent with both the wrong frame W and the right frame R. The task asks
for a specific value of an **unseen manipulation M**. W and R give *different* answers to M — or
W gives "underdetermined" while R over-determines it. Grade = exact/symbolic match to R's value.

- *Assay House pattern:* the rank-2 structure forces the unmeasured tenth transfer to +1; the
  scalar-potential (epicycle) account has one free parameter per pair and **cannot** predict it.
- **Fake-proof:** W literally cannot compute M's value. A slogan earns nothing.
- **Epicycle detection:** "I'd need to measure it" or a wrong number *is* the epicycle response;
  R's frame over-determines M, so uncertainty = W.
- **Retrieval-resistant:** the value derives from this item's randomized data; "+1" is not
  retrievable, it must be rederived.
- **Auto-gradeable:** yes, exact match.

### 2. Counterfactual battery

One held-out prediction can be a fluke. Ask a *battery* of counterfactuals where W and R
diverge; require ≥k of n consistent with R. The **pattern** of hits localizes whether the model
has R's machinery or only R's slogan — the genus-only model passes the easy probes and fails the
ones needing the actual mechanism.

- Robust against luck; turns a binary into a graded score.
- The failure pattern is itself diagnostic data (which consequences does the genus not cover?).

### 3. Executable model, graded by simulation

Ask for a **model** (a short program / set of equations / parameterization), not prose. Run it
against held-out manipulations. Grade = predictive accuracy on held-out data.

- **Epicycle cheat becomes objective and countable:** W's program needs O(n) parameters (one per
  observation); R's needs O(1). Count them. This is the epicycle metric made mechanical.
- No LLM judge, no keyword fragility — the grader is an interpreter.
- This is LLM-SRBench's machinery (symbolic accuracy by simulation) *plus* a given wrong frame to
  overturn — i.e. exactly axes (a)+(d) added to LLM-SRBench's (b)+(c).

### 4. Description-length / compression score

Frame replacement = a shorter description that reproduces all observations. Score the model's
account by the parameters+rules needed to regenerate O. W-with-epicycles has description length
growing with observations; R is flat. Grade = does the account reach R's compression.

- Ties directly to the proliferation→unification structure: epicycles *are* added length.
- Generalizes InAbHyD's Occam metric from generation-from-scratch to the given-wrong-frame case.
- Risk: needs a formal description language; fiddly to operationalize fairly.

### 5. Design-the-discriminating-experiment

Don't ask for an explanation. Ask for **the single experiment that would distinguish the standing
account from any alternative.** A model in W proposes experiments W already accommodates; a model
holding R names the experiment where W and R diverge. Grade = does the proposed experiment
actually discriminate (checkable by simulation).

- Sidesteps retrieval entirely: naming Pando does not help you design the crucial assay.
- Distinguishes the epicycle *mindset* (proposes confirmatory tests) from the replacement mindset
  (proposes discriminating tests).

### 6. Perturbation-consistency ("does it stick")

Multi-turn. After the model answers, feed a new observation that is anomalous under W and
predicted under R. A model genuinely holding R says "expected." A genus-only model expresses
surprise or **patches** (an epicycle, in real time). Grade = the response to the diagnostic
observation.

- The most direct operationalization of "grade the species": the follow-up is chosen so only R
  predicts it, and the epicycle cheat is caught in the act.

### 7. Falsification round-trip

Give the model both W and R and ask it to state **R's riskiest prediction** — the observation
that would kill R. Then check that prediction against held-out data. Tests whether the model
grasps R as a falsifiable structure with commitments, not as a slogan.

### 8. Representational probe (research direction, open-weight only)

Rather than grading output, probe whether the model's internal state shifted toward R (the doc's
mech-interp angle). Too heavy for a benchmark, but the way to ask whether a "jump" is a
representational event or a decoding one. Park for a separate track.

---

## Synthesized item template

Combine 1 + 2 + 3 into one item type:

1. Present O (consistent with W and R), the standing account W with its epicycles, and the one
   anomaly W patches.
2. Ask for a **derivable artifact** about a held-out manipulation M (a number, or an executable
   model that predicts M).
3. Build the item so **W is structurally incapable** of producing M's value (underdetermined, or
   wrong functional form) and **R over-determines** it.
4. Grade automatically: exact/symbolic match, or held-out predictive accuracy by simulation.
5. Log the **epicycle count** (mechanisms posited) and whether the model answered
   "underdetermined" (= stuck in W).
6. Randomize the instance data per item → retrieval-proof by construction.

Nothing verbal is graded. A model earns the item only by producing what only R can produce.

---

## Two experimental contrasts that isolate *frame replacement* specifically

The artifact-grading above measures abduction-to-artifact. To isolate the thing that makes this
project distinct from αNLI/InAbHyD — that an incumbent wrong frame must be *overturned* — run
these contrasts on top:

- **The incumbency delta.** Give two copies of the same item, one **with** the standing account
  stated, one **without** (pure abduction, no incumbent). Frame-replacement difficulty =
  score(without W) − score(with W). A large positive delta is direct evidence that the presence
  of a plausible wrong frame *suppresses* the leap — the project's core claim, measured. This is
  cheap and no existing benchmark reports it.
- **The negative control (non-negotiable).** Items where W is actually **correct** and the
  tempting reframe is false. Grade = does the model defend W and produce *W's* number. Without
  this, "always produce a clever number / always reframe" scores well, and we cannot separate a
  model that *makes* leaps from one that *always* leaps. Build ≥1 per move class.

---

## What to prototype first

1. Take the **Assay House** environment (already forces +1) and wrap it in the synthesized
   template: add the incumbency-delta pair and one negative-control variant.
2. Grade by exact match + epicycle count. No LLM judge yet — prove the artifact grading is clean
   on a move class that already forces a number.
3. Only then port the harder move classes (Trough, Burrow) and consider the executable-model
   grader for items whose artifact is a model rather than a scalar.
4. Read `literature/shojaee_2025_llmsrbench/` for the simulation-grading and memorization-
   transform machinery before building the executable-model grader — it is the same problem
   solved, minus the incumbent frame.

The re-individuation environments (Hillside, Lanterns) are not wasted: they become the
**verbal-only** arm of an ablation showing that verbal grading and artifact grading diverge —
which is itself the quantified "slop transformation" result.
