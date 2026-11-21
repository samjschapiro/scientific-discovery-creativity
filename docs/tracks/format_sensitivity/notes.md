# format_sensitivity — notes

## Why the two controls are not optional

A drop in jump-rate under fragmentation is **uninterpretable on its own**.

- **Comprehension probe.** If the model recalls 18/18 facts from the F3 bundle and still
  doesn't jump, its representation is intact and fragmentation broke the *leap*. That is the
  doc's claim, and a real finding. If it recalls 12/18, fragmentation broke *reading*, and the
  abduction result is downstream of a comprehension failure. These look identical in the
  jump-rate column and mean opposite things.
- **Referent probe.** Two hypotheses predict the same format effect for opposite reasons.
  *Retrieval*: models solve #1/#2 by recognizing the real-world referent from surface features,
  and fragmenting the surface degrades recognition — the jump was never abductive. *Abduction*:
  models reconstruct the frame from the anomalies, and fragmenting degrades the working
  representation. They are separated by whether the referent gets named, and by whether
  jump-rate tracks naming-rate across conditions.

  Grok's existing transcripts name their referents unprompted ("genet", "suborder
  Ceratioidei"), which is at least suggestive of the retrieval hypothesis. The clean way to
  break the tie is a retrieval-resistant environment with no referent to name — see
  `docs/memos/retrieval_resistant_environments.md`. Parked for now.

## Probes are run per (format, sample), not per cell

A probe asks about the *stimulus*, not about the framing. Running it once per framing would
issue two byte-identical API calls. `build_tasks()` deduplicates this deliberately — if you
later add a framing-dependent probe, that assumption breaks.

## Scoring: do not let one judge call score both axes

Two independent axes:

- **Axis 1 (genus):** `JUMP` / `JUMP-HEDGED` / `EPICYCLE` / `MISS` — did it commit to the reframe?
- **Axis 2 (species):** did it state a consequence that follows *only* from the reframe? For
  the Hillside: *the absence of seed is not a gap in the record — it is predicted, because
  propagation is vegetative.*

The gap between the two curves **is** the "slop transformation" failure mode, quantified.
That is the headline plot. A single judge call will smear the two together, because the whole
point is that they dissociate — a model can score `JUMP` on Axis 1 with a fluent verbal
reframe and fail Axis 2 entirely.

Also log: epicycle count (newly posited mechanisms), and `referent_named` as a bool covariate.

## Known weakness of Environments #1 and #2

Neither has a **forced numerical artifact**. Axis 2 does what it can without one. Both also
instantiate the *same* conceptual move (re-individuation: the individuals you counted are
parts of one individual), and both have real-world answer keys. So the 7/9 result is closer
to one data point than two.

## Providers

`thinking`/`effort` map differently per provider, which is why they are validated per provider
rather than globally:

- **anthropic:** `thinking={"type": ...}`, `output_config={"effort": ...}`. Five effort levels.
- **openrouter:** `reasoning={"effort": ...}`, or `reasoning={"enabled": false}` when
  `thinking: disabled`. Only three effort levels — `xhigh`/`max` are rejected at config time
  rather than silently downgraded.

OpenRouter can return HTTP 200 with an `error` object in the body, and can return a null
`content` alongside a populated `reasoning` field. Both are raised, not recorded as empty
responses. Cost accounting requires `"usage": {"include": true}` on the request; if OpenRouter
returns no `cost` field, the provider raises rather than running untracked.

Model IDs are pinned in config. `google/gemini-3.1-pro-preview` is a *preview* ID and can be
withdrawn mid-experiment; `google/gemini-3.5-flash` is the stable fallback but a different tier.

## Thinking and effort are experimental variables

`thinking` and `effort` are required config fields with no defaults, on purpose. Omitting
`thinking` on Opus 4.8 silently runs the model *without* thinking — which is a completely
different experiment from `adaptive`. Do not let that happen by accident.

Sampling parameters (`temperature`, `top_p`, `top_k`) are rejected by Opus 4.8 and are not
plumbed anywhere. Variation across samples comes from the model, not from a sampler knob.

## Failure behavior

`run_experiment.py` lets an API exception propagate and kill the run, leaving a partial
`responses.jsonl`. This is deliberate — a run that silently drops 3% of cells produces a
plot nobody can trust. Re-run with `--overwrite`.
