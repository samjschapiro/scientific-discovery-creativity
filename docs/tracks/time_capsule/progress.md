# Track: time_capsule

Test transformational ability by giving a **time-capsule LLM** (knowledge cutoff `T_M`) the
anomalous evidence that preceded a real discovery `D` made at `T' > T_M`, and seeing whether it
reaches `D`. Because `D` postdates the model's training data, **retrieval is impossible by
construction** — the problem that killed every previous track (see
`docs/tracks/format_sensitivity/progress.md`) is solved at the data level rather than by item design.

## Status

**2026-07-17 — WOUND DOWN for the transformational-ability question. Capability floor, not a fixable bug.**

Initial runs with **talkie-1930** (the largest and only controlled model in the registry, 13B / 260B
tokens) show it cannot reason or follow the task at all — incoherent, not wrong-but-coherent. This is
the **capability-vs-cutoff confound** this doc flagged from the start (see the Models table and the
TypewriterLM leakage paper) firing at full strength: a null is uninterpretable because *"didn't jump"*
cannot be separated from *"too weak to do anything."*

The conclusion generalizes past talkie to **the whole vintage-model family**: every other model in the
registry (Ranke-4B, gpt-1900, timecapsule-1875 at 1.2B) is *smaller* and weaker. If 13B can't reason,
none can. Contamination-by-construction works, but only in a capability regime where nothing can think —
**the capability floor for frame-replacing reasoning sits far above what any sub-cutoff training corpus
can support.** That is a real methodological finding, recorded here so it is not re-discovered the hard way.

**What is retired:** using vintage LLMs to *test* transformational ability. **What is kept and reused:**
the move-type castability classification (`classification.py`), the externally-authored Haven canon, and
the effective-anomaly-year insight — all feed the frontier redesign.

**Successor:** the contamination problem moves from the *data level* (vintage models) to the *item level*
— retrieval-proof synthetic environments + forced-artifact grading, run on frontier models. See
`docs/memos/interactive_frame_replacement_benchmark.md`.

---

### Original status (superseded)

**2026-07-12 — Population and sample built. No models run yet.**

## Population: Haven's 100

`src/time_capsule/haven100.json` — Kendall Haven, *100 Greatest Science Discoveries of All Time*
(Libraries Unlimited, 2007), all 100 entries with their years.

Using an **externally-authored canon** rather than discoveries we hand-pick is the point: it means
the population was not selected by us to flatter the hypothesis. That matters a lot when the claim
is "models can/cannot reach transformative discoveries."

**Provenance (extracted, not remembered).** Parsed from the
[archive.org OCR full text](https://archive.org/details/100GreatestScienceDiscoveriesOfAllTimeKendallHaven).
Titles from the table of contents (100); years from each chapter's `Year(s) of Discovery` header
(100). Zipped in document order, then verified three ways: 84/100 chapters have their title
physically adjacent to their own year marker, **0 misalignments**, and the resulting years are
**monotonically non-decreasing** (the book is chronological — a strong independent check that the
zip is correct).

Three OCR traps, all handled rather than papered over:
- 3 chapters use a *plural* header (`Years of Discovery: 1937 and 1983`), which a naive regex
  misses. Recovering them mattered: without them the title↔year zip silently misaligns.
- 2 OCR title errors corrected (`Fluman Genome` → Human Genome; `E = me2` → `E = mc2`).
- `Levers and Buoyancy` is 260 B.C.E., encoded as `year_first = -260`.

## Sample: discoveries the model cannot have read

`eligible_sample(model)` keeps every discovery with `year_first > T_M`.

`year > T_M` is **necessary but not sufficient.** Two further filters are exposed, never applied
silently:

- **Gap ceiling (`max_gap`).** Too far past the cutoff and the model cannot even parse the
  question, so a failure is uninformative. Note the gap that matters is *conceptual* distance;
  years are only a proxy, and a fast-moving field can put 5 years further away than decades in a
  slow one.
- **Straddlers.** A multi-year discovery whose span contains the cutoff is *partly inside* the
  model's world. Reported separately and never auto-classified. (Fires for `ranke-1939` and
  `ranke-1946`, both on *Weak and Strong Force* 1937–1983.)

```bash
bash scripts/time_capsule/build_sample.sh --overwrite
```

## Models

| Model | `T_M` | Size | Eligible | ≤10y gap | Matched control? |
|---|---|---|---|---|---|
| **talkie-1930** | 1930 | 13B | 26 | 9 | **YES** — `talkie-web-13b-base` |
| ranke-1913 / 1929 / 1933 / 1939 / 1946 | — | 4B | 38 / 26 / 24 / 18 / 17 | 5 / 8 / 7 / 4 / 7 | no |
| gpt-1900 (Machina Mirabilis) | 1900 | ? | 51 | 9 | no |
| timecapsule-1875 | 1875 | 1.2B | 58 | 2 | no |

**Talkie-1930 is the primary model, and the control is the reason.** `talkie-web-13b-base` is the
same architecture and the same compute trained on modern web text. Without such a twin, a null
result is uninterpretable — "didn't jump" cannot be separated from "too weak to do anything." That
was my central objection to this whole approach, and the Talkie release answers it. Every other
vintage model in the registry lacks a control, which is a real limitation on using them alone.

## Two designs the sample makes available

**1. Dose–response on gap size, fixed target.** For a *fixed* discovery, several models sit at
different distances from it. The neutron (1932) is post-cutoff for five models simultaneously:

| Model | `T_M` | Gap to neutron |
|---|---|---|
| talkie-1930 | 1930 | +2y |
| ranke-1929 | 1929 | +3y |
| ranke-1913 | 1913 | +19y |
| gpt-1900 | 1900 | +32y |
| timecapsule-1875 | 1875 | +57y |

That turns "can it jump" into "**how far** can it jump" — a curve, not a binary. It also gives a
built-in sanity check: performance should *decay* with gap. If it doesn't, something is leaking.

**2. Capability control at near-fixed cutoff.** `ranke-1929` (4B) and `talkie-1930` (13B) have
almost the same cutoff and an identical 26-discovery eligible set — a clean scale comparison
holding the epistemic position fixed.

## The problem I would flag before we author a single item

**Haven's list is "greatest discoveries," not "paradigm shifts."** The project is about
*transformational* creativity — replacing a prevailing frame. Many eligible entries are not that:

- *Coelacanth* (1938) is a **rediscovery** — a fish found alive. There is no frame to overturn.
- *Blood Plasma* (1940), *Semiconductor Transistor* (1947), *Human Genome* (2003) are largely
  **engineering / technical achievements**.
- *Neutron* (1932) **is** a frame replacement — abandon "it's a gamma ray" for "it's a neutral
  massive particle" — which is exactly why the context doc chose it as the worked example.

So the eligible-26 is a *sampling frame*, not the item set. It needs a second pass classifying each
discovery by whether reaching it actually required **frame replacement** vs. an incremental finding
vs. an engineering feat. Otherwise we are measuring "can the model guess a discovery," not "can it
jump" — and the epicycle-cheat failure mode (keep patching the gamma-ray story) only even *exists*
for the frame-replacement subset.

This sub-classification is the natural next step, and it is where the earlier tracks' taxonomy work
(proliferation → unification → signature) actually pays off: it gives us the criterion for deciding
which of the 26 are real test items.

## Castability screen (2026-07-15)

`src/time_capsule/classification.py` screens the eligible-26 for talkie-1930. **Eligible is not
castable.** To be an item, a discovery must clear four filters: (1) there is an incumbent frame M
with an epicycle cheat; (2) the anomaly A is statable in pre-1930 terms; (3) it is not blocked by a
post-1930 prerequisite; (4) the effective gap is small, where effective gap uses the year the
*anomaly* became available, not Haven's consensus date.

**The 26 collapse to 4 strong + 6 marginal + 16 out.**

| Verdict | n | Discoveries |
|---|---|---|
| STRONG | 4 | Neutron, Dark Matter, The Big Bang, Jumpin' Genes |
| MARGINAL | 6 | Nuclear Fission, Weak/Strong Force, Ecosystem, Fusion, Nature of the Atmosphere, Complete Evolution |
| NO | 16 | the rest — engineering (Transistor, Blood Plasma, Human Genome, Planets), rediscovery (Coelacanth), framework (Information), incremental (Metabolism, Function of Genes, Origins of Life, Cell Structure, Quasars/Pulsars), or frame-replacements that are prerequisite-blocked / anachronistic-A for 1930 (DNA, Quarks, Accelerating Universe, Dinosaurs, Seafloor Spreading) |

### Three findings that change the design

1. **Effective anomaly year != Haven year, and it matters enormously.** Dark Matter is Haven-dated
   1970 but the Coma-cluster velocity anomaly is Zwicky **1933** (+3y). The Big Bang is Haven-dated
   1948 but Hubble's expansion law is **1929** (-1y — inside the model's world). Sizing the gap by
   Haven's date would have discarded Dark Matter as a +40y long-shot; it is actually one of the
   nearest and cleanest items.

2. **Negative effective gap = endorsement test, not generation test.** Five items have the anomaly
   (and sometimes the reframe) available *before* 1930: Big Bang, Weak/Strong, Fusion, Atmosphere,
   Seafloor. Where the reframe itself was already proposed as a minority view by the cutoff
   (Lemaitre's primeval atom 1927/31; Eddington's stellar fusion 1920; Wegener's drift 1915), the
   item tests whether the model *endorses a known-but-contested idea*, not whether it *generates an
   unknown one*. Both are interesting, but they are different experiments and must not be pooled.

3. **Anachronistic-A kills endosymbiosis for 1930 — and co-selection rescues it.** The endosymbiosis
   environment I already built rests on organelle DNA and ribosome type: molecular evidence that
   postdates 1953. A 1930 model cannot be shown that A. The fix is not to drop the item but to match
   it to the right cutoff: endosymbiosis wants a ~1960 model, DNA-structure ~1950, fission ~1935
   (post-neutron). **The item and the model should be chosen together** — which is the real argument
   for the Ranke multi-cutoff family, beyond the dose-response curve.

### Consequences for the three environments already built

- **Neutron** — STRONG, clean, +2y. Keep as the reference. Correct for talkie-1930.
- **Fission** — MARGINAL for 1930 (neutron-blocked). Correct as-is for a post-1932 cutoff (Ranke-1929/1933). Re-home it.
- **Endosymbiosis** — anachronistic-A for 1930. Either re-home to a ~1960 cutoff model or rebuild A
  from pre-molecular evidence only (independent division, bacterial size/shape) — which is much weaker.

## Next

1. ~~Classify the eligible 26 by move type.~~ Done — `src/time_capsule/classification.py`.
2. Contamination check — the TypewriterLM paper (arXiv 2606.02991) ships a `History-Event` leakage
   benchmark; verify Talkie-1930 is actually clean on our targets rather than assuming the cutoff held.
3. Author the toy environment `E` for the frame-replacement subset, phrased in pre-`T_M` terms
   (the context doc's neutron prompt is the template).
4. Scoring rubric for partial progress — the context doc explicitly anticipates models getting
   *partway* to `D`.

## Sources

- Context doc: *Time-Capsule LLMs as a Test of Transformational Ability*.
- Talkie-1930: [talkie-lm/talkie](https://github.com/talkie-lm/talkie) · 13B, 260B tokens pre-1931.
- [TimeCapsuleLLM](https://github.com/haykgrigo3/TimeCapsuleLLM) · [awesome-vintage-llms](https://github.com/entanglr/awesome-vintage-llms) (Ranke-4B family).
- TypewriterLM, *Pretraining Language Models on Historical Text* (arXiv 2606.02991) — leakage benchmark; flags the capability-vs-cutoff confound.
