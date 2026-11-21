# Retrieval-Resistant Environments (draft)

Three new environments for the Scientific Transformational Thinking Test, plus a
negative control. Written against the two design criteria in the project doc:

1. **Retrieval-resistant surface** — prompt vocabulary cues a different (salient) branch of
   the space than the one the facts select. No textbook signature fact present.
2. **Grade the species, not the genus** — the required response is a derivable artifact
   (a number, a formula, a forced prediction) that only the correct frame produces.

## Why these three

Environments #1 (Hillside) and #2 (Lanterns) instantiate the **same** conceptual move:
*re-individuation* — the individuals you counted are parts of one individual. They also both
have real-world answer keys (clonal colonies; ceratioid anglerfish), and Grok's transcripts
name them ("genet/ramet", "suborder Ceratioidei"). Its answers read like successful retrieval,
not successful abduction.

So the 7/9 result ("LLMs can jump") is weaker than it looks on two counts: one move class,
both with referents. The environments below vary the move class and remove the referent.

| Env | Move class | Standing account | Reframe |
|---|---|---|---|
| #1 Hillside | re-individuation | many plants + signals | one organism |
| #2 Lanterns | re-individuation | host + parasite | one mating pair |
| **A. Assay House** | property → relation | scalar potential per bath | each bath carries *two* quantities |
| **B. The Trough** | substance → process | the knot is a corpuscle | the knot is a pattern |
| **C. The Burrow Survey** | law → artifact of the window | conservation law | detection boundary |
| **D. Control** | *none — no jump* | trade-off is real | (reframe is wrong) |

Every environment below is built so that the epicycle account **fits all given data and
predicts nothing**, while the reframe **forces an exact number**. That asymmetry is the whole
measurement.

---

## Environment A — The Assay House

*Move class: a property of an object turns out to be a relation between objects — and the
scalar you assigned turns out to have been a projection of a 2-vector.*

### Scenario

An assay house maintains five standing dye baths, catalogued **A** through **E**. When any two
baths are coupled through a porous membrane and left overnight, dye moves between them. The
house records, for each ordered pair, the grams gained by the first bath. Call it `T(X,Y)`.

The measurement is clean and repeatable to within 0.01 g. Two regularities have held for
decades:

- `T(X,Y) = -T(Y,X)` exactly. Whatever one bath gains, the other loses.
- `T(X,X) = 0`.

The house's account is that each bath has an intrinsic **avidity** `k` — a single number, a
property of the bath — and that transfer is driven by the difference: `T(X,Y) = k_X - k_Y`.
This explains antisymmetry immediately. It has never been questioned.

Nine of the ten pairs have been measured:

```
T(A,B) = +2      T(B,C) = +3      T(C,D) = +3
T(A,C) = +1      T(B,D) = +3      T(D,E) = +5
T(A,D) = -1      T(B,E) = -4
T(A,E) = -2
```

The tenth pair, `T(C,E)`, has never been run.

Two facts sit awkwardly with the standing account. First, no consistent assignment of avidities
reproduces the table; the house has for some years carried a set of **pairwise correction terms**
`ε(X,Y)`, attributed to membrane contamination, one per pair, which restores agreement exactly.
Second, coupling A to B, then B to D, then D to A, returns dye to A with a net gain of 6 g per
cycle, and the cycle can be run again.

### Prompt

> The assay house wishes to know, before running it, what `T(C,E)` will be. Give the value and
> the principle that fixes it.

### Bad response (the epicycle cheat)

Refine the avidity model. Attribute the cyclic gain to membrane asymmetry or contamination
memory; add or re-fit the correction terms `ε(X,Y)`. Every observation is absorbed — there is
one free parameter per pair, so the fit is perfect and empty. **`T(C,E)` is unconstrained.**
The model cannot answer the question that was asked.

Log each posited correction term as an epicycle. They are literally countable here.

### Good response (transformative restructuring)

A cycle with net gain is impossible for *any* quantity of the form `k_X - k_Y`, since such
differences sum to zero around any loop. No amount of correction repairs this; the standing
account is not underfit, it is **the wrong kind of object**. Avidity is not a scalar property of
a bath.

The reframe: each bath carries **two** independent quantities, `(x₁, x₂)`, and transfer is the
oriented area they span:

```
T(X,Y) = x₁y₂ − x₂y₁
```

This is antisymmetric (recovering the observed regularity for free), admits cycles (recovering
the anomaly), and — crucially — is *rank 2*. The 5×5 table of transfers is an antisymmetric
matrix of rank 2, so every 4×4 Pfaffian vanishes:

```
T(A,B)·T(C,E) − T(A,C)·T(B,E) + T(A,E)·T(B,C) = 0
```

Substituting: `2·T(C,E) + 4 − 6 = 0`, so **`T(C,E) = +1`**.

The value is over-determined — two other quadruples give the same answer:

```
{A,C,D,E}:  (1)(5) − (−1)·T(C,E) + (−2)(3) = 0   →  T(C,E) = 1
{B,C,D,E}:  (3)(5) − (3)·T(C,E) + (−4)(3) = 0   →  T(C,E) = 1
```

and the nine given values already satisfy the two relations that do not involve `T(C,E)`, so the
frame is testable *before* the tenth measurement is made.

### Grading

- **Species (full credit):** states `T(C,E) = +1` *and* the rank-2 / oriented-area principle.
- **Partial:** identifies that a scalar potential is impossible because of the cycle, but cannot
  produce a value.
- **Genus only (no credit):** "avidity may be relational rather than intrinsic," "the system is
  non-conservative," "there may be hidden variables." All true, all compatible with the wrong
  species, none of them yield 1.

### Retrieval resistance

The vocabulary (baths, membranes, uptake, contamination) cues **thermodynamics** — chemical
potential, activity coefficients, transport across a membrane. That is the salient branch and it
is exactly the wrong one; the facts select **exterior algebra**. There is no famous "dye bath
anomaly" to recall. The withheld retrieval key is any statement that a bath is characterized by
more than one number.

The move class does have historical cousins (non-conservative fields, Condorcet cycles,
intransitive dice), but no lookup carries a model from this surface to `+1`. It must rederive.

### Follow-up probe (multi-turn condition)

If the house pools the entire contents of bath A and bath B into one vessel, what is `T(A+B, C)`?
The reframe forces **+4** (`T(A,C) + T(B,C)`, by bilinearity and extensivity). The avidity model
predicts a mass-weighted average of `k_A` and `k_B`, hence a value strictly between `+1` and `+3`.
The two frames are discriminated by a single measurement.

---

## Environment B — The Trough

*Move class: an entity turns out to be a process — a pattern in a medium, not a thing moving
through it.*

### Scenario

A long trough is filled with identical beads, each occupying one place in a line of places. The
line advances by a rule confirmed in every observation ever made: **a bead steps forward exactly
one place when the place ahead of it is vacant, and otherwise does not move.** No bead ever moves
backwards. No bead is ever created or destroyed.

Along the trough there travels a sharp, visible boundary the surveyors call **the knot**: behind
it the beads are sparse, ahead of it they are crowded. The knot has been catalogued for years as
a distinct entity with its own position, its own velocity, and its own mass.

Measurements, all stable:

- **Behind the knot** (sparse region): 2 beads per 5 places. Each bead advances one place per tick.
- **Ahead of the knot** (crowded region): 4 beads per 5 places. Each bead advances one place per
  four ticks.
- The knot travels at a **constant** rate.
- A bead marked with paint never travels with the knot. It is overtaken from behind, crawls
  through the crowded region, and emerges ahead. The knot retains none of its beads.
- Two knots that meet merge into a single knot.

The standing account is that the knot is a corpuscle propagating along the trough. Where the
account falls short, further properties are supplied: a *coupling* to explain why the knot's speed
matches no bead's speed, an *accretion* term to explain why its mass grows, a *negative mobility*
to explain the direction it travels. Each addition fits.

### Prompt

> How fast does the knot travel, and in which direction? Give a number, in places per tick, and
> derive it.

### Bad response (the epicycle cheat)

Retain the corpuscle. Assign it a drift velocity somewhere between the two bead speeds (0.25 and
1.0 places per tick, forward), attribute the discrepancy to coupling with the medium, and explain
the mass growth by accretion at the leading face. Every observation is absorbed. No number is
derived — the velocity is fitted, not predicted.

### Good response (transformative restructuring)

The knot is not a thing. It is the **boundary between two densities**, and it has no bead
membership at all — which is why marked beads pass through it. Its speed is fixed by bead
conservation across the boundary, not by any property of a bead.

Let `u` be the knot's velocity. In the knot's own frame, beads must enter from behind at the same
rate they leave ahead:

```
ρ_behind · (v_behind − u) = ρ_ahead · (v_ahead − u)
0.4 · (1 − u)             = 0.8 · (0.25 − u)
0.4 − 0.4u                = 0.2 − 0.8u
0.4u                      = −0.2
u                         = −0.5
```

**The knot travels backwards at one place every two ticks** — opposite in sign to every bead that
composes it, and equal in magnitude to no bead's speed. Nothing in the trough moves backwards; the
knot does.

Two further forced consequences:

- The knot **absorbs beads at `(ρ_ahead − ρ_behind)·|u| = 0.2` beads per tick** — one bead every
  five ticks. What the corpuscle account calls accretion is just the boundary sweeping backwards
  through a sparse region and leaving a crowded one.
- Merging is not a collision. Two boundaries between the same pair of densities cannot pass through
  one another, because there is nothing to pass.

### Grading

- **Species (full credit):** **−0.5 places per tick**, derived by conservation across the front.
- **Partial:** identifies the knot as a density pattern but does not produce `−0.5`, or produces a
  forward velocity.
- **Genus only (no credit):** "this is emergent collective behavior," "the knot is a wave, not a
  particle," "the pattern is not the substrate." **Expect models to produce this fluently.** That
  is the point of the item: the genus here is cheap and almost certainly retrievable, so the item's
  entire discriminating power sits in the number. A model that says "it's a wave" and then predicts
  the knot drifts forward has retained the corpuscle underneath.

### Retrieval resistance

Weakest of the three, and worth being honest about it: the underlying structure is a deterministic
exclusion process, and a model may recognize the local rule. The surface is chosen so the salient
branch is **collective behavior / emergence**, which delivers the genus and stops there. The
mitigation is not obfuscation but the forced number, which no amount of pattern-matching supplies.

If we want to harden it: state the rule only through observations of individual beads, never as a
rule, and force the model to induce it first.

---

## Environment C — The Burrow Survey

*Move class: a tight empirical law turns out to be the edge of the observable window, not a
mechanism.*

### Scenario

A field station surveys a burrowing animal. Surveys are acoustic: an observer listens at a fixed
station for a fixed period and records every animal heard calling. Two facts about the calls are
established. A heavier animal's call is louder, and the area over which a call can be heard grows
in proportion to the animal's mass. Animals differ greatly in how often they call.

Across two decades, every recorded specimen has satisfied a strikingly tight relation between body
mass `m` (grams) and call rate `c` (calls per minute):

| specimen | m (g) | c (calls/min) | m·c |
|---|---|---|---|
| 1 | 0.20 | 60.3 | 12.06 |
| 2 | 0.55 | 22.4 | 12.32 |
| 3 | 1.30 | 9.37 | 12.18 |
| 4 | 2.90 | 4.29 | 12.44 |
| 5 | 6.10 | 1.98 | 12.08 |
| 6 | 11.4 | 1.12 | 12.77 |
| 7 | 18.0 | 0.679 | 12.22 |
| 8 | 29.5 | 0.425 | 12.54 |

Mass spans more than two orders of magnitude. The product does not.

The station's account is the **Law of Vital Economy**: an animal's energy budget forces
`m · c = 12`, a conserved quantity. Where the account falls short, it is repaired — the residual
scatter is attributed to measurement error in the mass, and the fact that the residuals run a
little high is attributed to a small positive bias in the field scales.

### Prompt

> The station has acquired microphones with twice the audible area. Before the new survey season
> begins, predict what it will find. Be specific.

### Bad response (the epicycle cheat)

Retain the conservation law. Predict that the new microphones will detect the same relation
`m·c = 12` and, being more sensitive, will measure it *more tightly*. Refine the scale-bias
correction to absorb the one-sided residuals. Every observation is absorbed; the prediction is
that nothing changes.

### Good response (transformative restructuring)

`m · c = 12` is not a law. It is the **detection boundary**.

An animal is recorded only if it is heard. The chance of hearing it grows with the audible area
(∝ `m`), with how often it calls (∝ `c`), and with how long the observer listens (∝ `t`). So
detectability is governed by `m · c · t`, and the survey records exactly those animals for which
`m · c · t` exceeds the station's threshold. With the historical listening period, that threshold
sits at `m · c = 12`.

There is no conservation of anything. Animals with `m·c < 12` exist and have never been heard.
The animals piled up just above 12 are not obeying a law; they are lying against a wall.

The tell is already in the data the station has: **the residuals are one-sided.** Every product
lies between 12.00 and 12.77, and not one lies below 12.00. A conserved quantity measured with
error must scatter *both ways*. A boundary can only be exceeded in one direction. The station read
this as a positive bias in its scales; it is the signature of the whole account being wrong.

Forced predictions, each of which the conservation account contradicts:

1. **Doubling the audible area halves the constant.** The new survey will find animals down to
   `m · c ≈ 6`, and the apparent law will re-form at **6**, not tighten at 12.
2. **Doubling the listening period does the same.** The "constant of nature" depends on how long
   the observer sat there — which is an absurd property for a metabolic law and a necessary one for
   a detection threshold. Forced value: **6**.
3. **Specimens obtained by excavation show no relation at all** between `m` and `c`, because
   excavation does not filter on audibility.
4. The newly detected animals will fill in *below* the old line, and the residuals of the new
   sample will again be one-sided, now against 6.

### Grading

- **Species (full credit):** states the constant scales as `1/effort`, gives **6**, and cites the
  one-sidedness of the existing residuals as the evidence that killed the law.
- **Partial:** identifies a selection effect but predicts the law persists at 12, or gives no value.
- **Genus only (no credit):** "this could be a selection effect," "we only observe what we can
  detect," "correlation is not causation." Compatible with both frames; forces nothing.

### Retrieval resistance

The vocabulary (body mass, call rate, energy budget, metabolic trade-off) cues **allometric scaling
laws** — Kleiber, mass–rate trade-offs, life-history theory. That is the salient branch and it is
wrong. The facts select the geometry of a detection threshold.

The retrieval key is deliberately withheld: the scenario never says "detection threshold," never
says "we only record what we hear," and never states that detectability is a function of `m·c`. It
supplies the two ingredients separately — audible area grows with mass; call rate varies — and the
model must combine them. Presenting the product column is a concession; it makes the one-sidedness
findable without naming it.

---

## Environment D — The Negative Control

**This is the most important item in the set, and the current design has nothing like it.**

A benchmark composed entirely of scenarios whose standing account is wrong cannot distinguish a
model that *makes* transformational leaps from a model that *always* leaps. "Reframe everything"
scores 100%. Whatever we report about Grok and Gemini on #1 and #2 is, right now, confounded with
this.

The control is cheap because it can reuse a surface exactly. Take Environment C's field station,
its vocabulary, its table, and its stated law — and change the ground truth:

- Residuals are **two-sided**: products scatter symmetrically above and below 12.
- Excavated specimens (no acoustic filtering) show **the same relation**.
- Doubling the audible area finds more animals, all of which **still satisfy `m·c ≈ 12`**.

Now the trade-off is real, and the tempting reframe is false. The correct response is to *defend
the standing account* and to say what would have falsified it — the one-sided residuals and the
excavation discrepancy that are conspicuously absent.

A model that reframes here is not creative. It is uncalibrated. The pairing of C and D turns a
generation task into a discrimination task, and the difference in behavior across the pair is a far
better estimate of transformational competence than performance on C alone.

Build at least one control per move class.

---

## Ablations worth running

- **Referent-naming probe.** After a model answers, ask: "does this scenario correspond to any
  phenomenon you know?" If it names one, its answer was retrieval. Score #1 and #2 this way
  retroactively — the existing Grok transcripts name theirs unprompted.
- **Surface swap.** Instantiate one move class in two unrelated substrates. If a model solves one
  and not the other, structure was not what it used.
- **Genus/species gap.** Score every response twice — once for the verbal reframe, once for the
  artifact. The gap between the two curves *is* the "slop transformation" failure mode, quantified.
  This is the headline plot.
- **Epicycle count.** Environments A and B admit a literal count of the free parameters a model
  posits. That is the epicycle-cheat metric, and it is objective.

## Open problems

- **Env B's genus is retrievable.** Accept it and lean on the number, or rebuild the substrate.
- **Move-class inventory is incomplete.** We have re-individuation, property→relation,
  substance→process, law→artifact. Missing at least: figure/ground inversion, direction-of-causation
  flip, and discreteness (continuous → quantized). Each needs a substrate with no referent.
- **Can a move class be novel at all?** Probably not — the move classes *are* the taxonomy of
  scientific revolutions, and any genuinely new one would be a research contribution in itself. What
  we can make novel is the (substrate, move) *pairing*, so that no lookup maps surface to answer.
  Worth stating explicitly in the paper; it is a limitation and also a defense of the design.
