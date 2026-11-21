# Track: format_sensitivity

## What this track is testing

The 7/9/2026 result (Grok and Gemini both make the transformative jump on Environments #1
and #2) came with an interpretation: *models can jump when the problem is presented in a
unified, linear way; real discovery arrives fragmented, and fragmentation constrains the
abductive leap.*

That is a causal claim about presentation. This track tests it by holding the information
content exactly constant and varying only the packaging.

Design memo: [`docs/memos/format_sensitivity_stimuli.md`](../../memos/format_sensitivity_stimuli.md).

## The constraint that governs the code

**Every format variant contains every atomic fact.** Facts may be reordered, split across
documents, restated, and buried in noise. They may not be added or removed. If a fragmented
variant quietly drops "no seed has ever been found," we are measuring fact-deletion and
calling it format sensitivity — and the two are indistinguishable after the fact.

This is enforced, not assumed. `src/format_sensitivity/coverage.py` runs before any model
sees a stimulus and hard-fails the run on a gap. It checks two things: that every fact has a
declared location in every format, and that every fact's lexical anchors appear in the
rendered text. The anchor check is a *necessary* condition only — it catches deletions, it
does not prove a fact is stated in the intended sense.

Writing the Lanterns bundle by hand, the first draft silently dropped two facts (the lantern
is *large*, the clinger *small* — i.e. the sexual dimorphism). That is exactly the failure
mode the check exists for.

## Status: PARKED (2026-07-10)

Parked in favor of a literature-review pivot — establish what scientific-Q&A and
abductive-reasoning datasets already exist before designing another instrument. Not
abandoned; the harness, the coverage gate, the framing ladder, and the provider/cost
plumbing all work and are worth resuming from.

**Why parked, specifically:** the retrieval-resistance problem (Bar 1) proved harder than the
harness. Re-individuation is the most retrieval-prone move class in the catalogue — "N tokens
are one entity" is itself a cached schema — so novel surfaces kept threatening to either name a
real phenomenon (Hillside → Pando) or, when pushed off biology (the Filament skin), read as
physically artificial at the regeneration slot. The open question that stalled it: whether a
re-individuation scenario clearing Bar 1 cleanly exists at all, or whether the move class has to
change. The lit review is partly an attempt to answer that from prior art.

What runs and is verified: 18-slot skeleton + skin registry (`hillside`, `filament`), coverage
gate (slot-completeness + declared-coverage + lexical anchors, all fail-loud), the four-rung
framing ladder, two providers (anthropic native SDK, openrouter HTTP) with per-call cost logging.
Smoke-tested against `x-ai/grok-4.5`; n=1 signals only, written up below. Total spent ~$0.55.

---

## Providers and cost accounting

Two providers, same `complete()` signature, same record shape:

| `provider` | Used for | Env var | Per-call cost |
|---|---|---|---|
| `anthropic` | Claude, via the native SDK | `ANTHROPIC_API_KEY` | not returned by the API — logged as `null` |
| `openrouter` | Grok, Gemini, anything else | `OPENROUTER_API_KEY` | returned and logged |

Claude is **not** routed through OpenRouter even though OpenRouter would serve it. Putting one
arm of the experiment behind an extra hop that normalizes reasoning parameters differently is
not worth the convenience.

Every run writes `logs/api_calls.jsonl` — one line per API call, carrying the OpenRouter
`generation_id` (reconcilable against their dashboard), the billed `cost_usd`, token counts
including reasoning tokens, and which cell the call belonged to. `results/cost_summary.json`
holds the run total. The OpenRouter provider **hard-fails if OpenRouter returns no cost field**,
rather than running untracked.

Across runs:

```bash
uv run python -m src.format_sensitivity.costs data/format_sensitivity
```

Anthropic calls are counted but reported as untracked, not as free.

## Status

**2026-07-10 — Scaffolded. Smoke-tested against Grok. Full runs not yet done.**

Implemented for Environment #1 (Hillside):

| Code | Format | Status |
|---|---|---|
| F0 | Narrative (the original, verbatim) | ✅ |
| F1 | Bare observation table | ✅ |
| F2 | Chronological field log | ✅ |
| F3 | Multi-source bundle (document order randomized per sample) | ✅ |
| F4 | Diluted log (F2 + irrelevant entries at 1x / 3x) | ❌ not built — needs a noise pool |
| F5 | Confident review article | ✅ |

Framings: `P_PUZZLE` (the original: *"How do you explain what's happening?"*) and
`P_MUNDANE` (*"Draft the summary paragraph for the station's annual report."*).

Controls, both run in fresh contexts: `comprehension` (recall all 18 facts) and `referent`
(does this correspond to a real phenomenon you know?).

Environment #2 (Lanterns) is drafted in the memo but not yet in code.

### Smoke test: `x-ai/grok-4.5`, n = 1, $0.11

Eight calls (`--debug`), purely to verify the harness end to end. **n = 1 per cell. This is not
evidence.** It is recorded because the pattern is not the one that was pre-registered, and it
should not be quietly forgotten once the real run happens.

| | `P_PUZZLE` | `P_MUNDANE` |
|---|---|---|
| **F0** (narrative) | JUMP | JUMP |
| **F3** (bundle) | JUMP | **EPICYCLE** |

Only the *conjunction* of fragmentation and no puzzle-cue failed. Either factor alone left the
jump intact — including `F0 x P_MUNDANE`, where Grok volunteered the clonal-organism reframe
in an annual-report summary nobody asked to have reframed. That contradicts the pre-registered
prediction that `P_MUNDANE` collapses everywhere.

The `F3 x P_MUNDANE` failure is a textbook epicycle, and worth quoting in full because it is the
behavior the whole benchmark is built to catch:

> "Routine soil chemistry and microbiology detect nothing out of the ordinary, yet the soil
> remains the sole continuous medium available for coordination. Provisional wounding and density
> signals transmitted among the dense near-surface roots therefore continue to furnish the only
> coherent working account. (The account is not yet complete.)"

It restates every anomaly accurately, notes the soil is clean, and keeps the signals anyway.

**Both controls fired, and they point in opposite directions.**

- *Comprehension:* Grok recalled the facts from the F3 bundle fine — it even transcribed the
  twelve-year census series and the phenology dates verbatim. The representation was intact. So
  the `F3 x P_MUNDANE` failure is not a reading failure.
- *Referent:* on F0 it named **Pando** unprompted, plus *Populus tremuloides*, "ramets", "genet".
  That is retrieval, not abduction. Whatever the F0 cells are measuring, recognition of a known
  phenomenon is doing part of the work.

Read together, the interaction is the finding worth chasing: fragmenting the evidence did not stop
the model from *reconstructing* the frame — it stopped the model from *volunteering* it. The
puzzle-cue is what carries F3. Which means the doc's framing ("fragmentation constrains the
abductive leap") may be measuring something closer to "fragmentation raises the threshold at which
a model bothers to revise."

Do not build on any of this until the K=20 run is in.

### The framing ladder (supersedes the P_PUZZLE / P_MUNDANE binary)

`P_MUNDANE` ("draft the summary paragraph") was a **demand characteristic**, not a no-cue
condition. Summarizing means faithfully restating the record, and the record's account is the
epicycle account — so a model that complies produces an epicycle whether or not it noticed
anything. The condition confounded *task demand* with *absence of a puzzle cue*.

The evidence for this is in the reasoning trace. Under `F3 x P_MUNDANE`, Grok reached the
reframe while thinking — *"These observations together indicate that the stems, though counted
individually, function as a single coordinated organism"* — drafted a paragraph ending on it,
then emitted a final answer that dropped it and re-endorsed the wounding and density signals.
The trace narrates the discard approvingly: *"leaves the deeper mechanistic question open as
the chemist himself did."* It did not fail to notice. It noticed and deferred.

So the fix is not "tell it to think" — it already thought, at 1,399 reasoning tokens. The fix
is to vary **what counts as the deliverable**. Framings are now a four-rung ladder in how much
the task licenses revision:

| Rung | Framing | Revision is... |
|---|---|---|
| 1 | `P_PUZZLE` — *"How do you explain what's happening?"* | the deliverable |
| 2 | `P_REVIEW` — *"You are the incoming warden. Review the record and write your assessment."* | licensed by the role |
| 3 | `P_ASSESS` — *"Think it through, then draft the summary paragraph."* | deliberation licensed, deliverable unchanged |
| 4 | `P_SUMMARIZE` — *"Draft the summary paragraph."* | off-task |

`P_SUMMARIZE` is retained as the **floor and the demand-characteristic control**, not deleted.
Its suppression effect is the measurement. Wording below rung 1 deliberately avoids
"what's going on" / "what's happening" — those presuppose that something *is* going on and
smuggle the puzzle cue back in.

The quantity of interest is **the rung at which a model stops volunteering the reframe.**

### Ladder smoke test: `x-ai/grok-4.5`, n = 1, $0.22

| | P_PUZZLE | P_REVIEW | P_ASSESS | P_SUMMARIZE |
|---|---|---|---|---|
| **F0** | JUMP | JUMP | JUMP | EPICYCLE |
| **F3** | JUMP | JUMP | EPICYCLE | EPICYCLE |

Fragmentation appears to shift the threshold by exactly one rung — which is the ordinal form of
"fragmentation raises the threshold at which a model bothers to revise," and a much more
tractable claim than "fragmentation constrains the abductive leap."

**But n = 1 is noise, and here is the proof.** `F0 x P_SUMMARIZE` and the earlier
`F0 x P_MUNDANE` are byte-identical prompts (verified). One returned JUMP, the other EPICYCLE.
Same model, same effort, same stimulus. Every cell in the table above could move. This is why
K = 20.

Three observations that survive regardless of the n=1 noise, because they are about *kind*
rather than *rate*:

1. **`F3 x P_ASSESS` is a textbook "grade the species, not the genus."** The answer calls the
   plot *"a single signalling collective"* — which sounds like the reframe — and then keeps the
   soil as the signalling medium. The genus is right, the species is the standing account. Its
   trace, meanwhile, ends on *"a clonal organism that maintains collective behavior through
   underground communication."* Trace has the species; answer has only the genus.
2. **`F3 x P_SUMMARIZE` invented a third epicycle.** Not content with the wounding and density
   signals, it posits *"a phenological synchronising signal that overrides local climate
   differences."* The epicycle-count metric would score this 3.
3. **Trace-vs-answer suppression is a measurable dependent variable**, and we already log the
   reasoning field. Define `suppression = P(reframe in trace) - P(reframe in answer)`. It is
   the genus/species gap relocated to the boundary between thinking and deliverable, and on
   present evidence it is where the action is.

### Grading warning

**Do not grade Axis 1 with keyword matching.** A keyword screen for the reframe on
`F3 x P_MUNDANE` returned a false negative: it looked for `"single organism"` and the model had
written `"single coordinated organism"`. The single most important cell in the first run was
mis-scored by the obvious method. Grade with a rubric-following judge, or by hand, and validate
the judge against hand labels before trusting it.

## The first cut

`configs/format_sensitivity/hillside_first_cut.yaml` — F0 vs F3, both framings, K=20, one
model. Four cells. Run it before building anything else:

```bash
bash scripts/format_sensitivity/run_hillside.sh
```

If `F3 x P_MUNDANE` does not collapse, the fragmentation hypothesis is in trouble and we
want to know that in an afternoon rather than after building a grader.

## Pre-registered predictions

Written down before running anything, so we cannot retrofit the story afterward.

| Condition | Predicted effect on jump-rate | If violated, what it means |
|---|---|---|
| F1 (table) | ≈ F0, maybe higher | prose was never load-bearing |
| F2 (log) | small drop | discovery-order alone is not the mechanism |
| F3 (bundle) | large drop | integration across sources is the bottleneck |
| F5 (review) | largest drop | authoritative framing suppresses revision |
| P_MUNDANE | very large drop across all formats | models reframe when asked to, not when warranted |

If **F1 ≥ F0** and **F3 ≪ F0**, the linearity claim survives in a sharpened form: it is not
*prose* linearity that matters but whether the anomalies can be co-located in one
representation.

If **P_MUNDANE ≈ 0 everywhere**, the headline finding is not about format at all. It is that
these models do not *notice* anomalies; they *resolve* anomalies once told one exists. That
is a more interesting result than the format effect, and it attacks "LLMs can jump" directly.

## Next

1. Run the first cut. Read the transcripts before writing a grader.
2. Build the grader (see Open questions — do not let one call score both axes).
3. Add Lanterns F0/F3 — its bundle is the stronger obfuscation, since the wrong frame is
   embedded in the archive's accession structure, not merely asserted in its prose.
4. Build F4's noise pool if the F3 result implicates attention rather than integration.
