# Session log — 2026-07-10 to 2026-07-15

Cross-track chronological record of the "Can LLMs Jump?" / transformational-creativity work.
Per-track detail lives in `docs/tracks/*/progress.md`; this file is the narrative of what was
tried, what was decided, and — most importantly — **what was rejected and why**, so the dead ends
are not re-walked.

Overall arc: four framework attempts were tried and abandoned before the project settled on
**time-capsule LLMs**. The through-line of every rejection was the same: an item-level attempt to
control retrieval and grade a verbal reframe, which is structurally impossible. Time capsules move
retrieval control to the training data and supply a real, uncontaminated answer key.

---

## Phase 0 — Orientation (2026-07-10)

- Read the project doc "The Scientific Transformational Thinking Test (LLMs *Can* Jump)."
- Core question: what bottlenecks stop LLMs from breakthrough discovery; can they perform
  *transformational creativity* (replace a prevailing frame, not patch it).
- Key prior finding in the doc (7/9): Grok and Gemini make the jump on Environments #1 (Hillside)
  and #2 (Lanterns) when the problem is presented linearly. Doc's interpretation: fragmentation
  constrains the leap.
- My immediate pushback, recorded then and vindicated later: both environments are the *same* move
  (re-individuation), both have real referents (Pando, anglerfish), and Grok *names* them — so 7/9
  may be retrieval, not abduction. This framed everything that followed.

## Phase 1 — TRACK: retrieval-resistant environments (rejected as a standalone)

- Drafted `docs/memos/retrieval_resistant_environments.md`: three novel move classes
  (property->relation "Assay House", substance->process "Trough", law->artifact "Burrow"), each
  forcing a derivable number, plus a negative control.
- Verified the forced numbers by computation (Assay House rank-2 -> T(C,E)=+1 over-determined three
  ways; Trough shock speed -0.5; Burrow one-sided residuals).
- **Parked** by the PI in favor of the format-sensitivity experiment.

## Phase 2 — TRACK: format_sensitivity (built, run, ultimately a dead end)

- Memo `docs/memos/format_sensitivity_stimuli.md` + full track under `src/format_sensitivity/`.
- Design: hold information constant across format variants (F0 narrative .. F5 review), vary only
  packaging; an 18-fact skeleton + a coverage gate that fails loudly on any dropped fact. The gate
  caught a real deletion in my first Lanterns draft (dropped the size dimorphism).
- Providers: Anthropic native SDK + OpenRouter (Grok, Gemini) with per-call cost logging.
- **Findings from the Grok smoke tests (n small, not conclusive):**
  - The pre-registered "fragmentation kills the jump" story did not hold cleanly. Only the
    *conjunction* of fragmentation (F3) and no-puzzle-cue (P_SUMMARIZE) produced an epicycle.
  - The reframe appeared in Grok's hidden reasoning trace but was dropped from the summary
    deliverable — i.e. the task framing measured *compliance*, not whether the model *found* the
    reframe. Led to the framing ladder (P_PUZZLE / P_REVIEW / P_ASSESS / P_SUMMARIZE).
  - Keyword grading false-negatived on "single **coordinated** organism" — proof that Axis-1
    grading cannot be lexical.
  - Referent probe: Grok named Pando unprompted -> the F0 success is at least partly retrieval.
- **Why rejected:** the retrieval problem (Bar 1/Bar 2) is unsolvable at the item level.
  Re-individuation is the *most* retrieval-prone move class; novel surfaces either name a real
  phenomenon (Hillside -> Pando) or read as physically artificial off biology (the "Filament" skin).
  PARKED, not deleted — harness, coverage gate, framing ladder, cost plumbing all work. Total spend
  on this track ~$0.55 OpenRouter.

## Phase 3 — Lit review (deep-research workflow)

- Ran the deep-research harness: 24 sources, 114 claims, 25 adversarially verified (22 confirmed,
  3 killed). Report at `docs/reports/2026-07-10_scientific_qa_abduction_landscape/report.md`.
- **Headline:** no existing benchmark combines (a) a given wrong frame to overturn, (b) retrieval-
  resistance by construction, (c) grading a derivable artifact, (d) frame-replacement rather than
  answer-selection. Nearest neighbors touch one axis each: GPQA (b), InAbHyD (toward c), alphaNLI (the
  explanatory-hypothesis format). Confirms the project's whitespace is real.
- Verification corrected a plausible claim I'd have trusted (OlympiadBench does NOT grade process).
- Pulled 5 lead papers into `literature/` (extracted PDF->markdown, sourced arXiv IDs, not guessed):
  shojaee_2025_llmsrbench, liu_2025_hypobench, chen_2025_hypospace, he_2025_gear,
  abe_2026_syllogistic_abduction. LLM-SRBench confirmed as the nearest competitor (blocks
  memorization by transforming known equations; grades a derivable artifact) — but no incumbent
  frame, so axes (b)+(c) only.

## Phase 4 — Grading-frame-replacement brainstorm (proposed, rejected)

- Memo `docs/memos/grading_frame_replacement.md`: the pivot "stop grading the verbal reframe, grade
  a derivable artifact only the correct frame can produce," eight mechanisms, incumbency-delta and
  negative-control designs.
- **Rejected by the PI** ("bad idea, rethink from scratch"). In hindsight it was still an
  apparatus-level fix.

## Phase 5 — Two from-scratch rethinks (both set aside)

- I named the six assumptions every attempt had shared (static item, given frame, single-shot,
  answer key, toy scenario, product grading) and offered directions that break different ones.
- The PI proposed **time-capsule LLMs**. I initially raised the capability-floor objection (a
  from-scratch 1875 model is too weak to reason, so a null is uninterpretable). Then briefly pivoted
  to an insight-science reframe, which the PI declined.

## Phase 6 — TRACK: time_capsule (current direction) (2026-07-12 to 07-15)

Context doc "Time-Capsule LLMs as a Test of Transformational Ability" resolved my capability-floor
objection: **Talkie-1930** (13B, 260B tokens pre-1931) ships a matched-compute modern-text twin,
`talkie-web-13b-base`. A deficit in the 1930 model but not the twin is attributable to
transformational ability, not size. That control is the whole reason the approach is viable.

### Paper (Overleaf repo `papers/6a4d58554b54a99f193a4a31`)

- Cloned; was a bare "Can LLMs Jump?" skeleton.
- Added the **official** ICLR 2026 style files (from ICLR/Master-Template, not reconstructed).
- Added the **Environment Examples** figure (`figures/environments.png`, Hillside + Lanterns) with a
  caption color-coded to match the figure blocks: M in `CBD5ED`, anomalous findings A in `EDECCB`
  (macros `\hlM`/`\hlA` in `imports/macros.tex`).
- Added the Lakatos epigraph above the Introduction (fixed the key: `lakatos1978methodology`, not
  `lakatos`).
- Reorganized into `sections/` (numbered `00_`..`06_`), `imports/`, `styles/`, `figures/`.
- **Two build fixes made along the way, both were pre-existing breakage:** the PI's `definition`
  environment was undefined (added `amsthm` + `\newtheorem`); BibTeX does not honor `\input@path`
  so `\bibliographystyle` needs an explicit `styles/` path (found by an end-to-end citation test,
  not assumed).
- Workflow note: the PI edits the same Overleaf `main` branch live; several pushes collided and were
  rebased. **Pull before editing when the PI is active.** Nothing of theirs was overwritten.

### Population and sample (`src/time_capsule/`)

- Haven's *100 Greatest Science Discoveries* extracted and **verified** from the archive.org OCR
  (not remembered): 100 titles, 100 year-markers, 0 misalignments, years monotonic. Handled 3 OCR
  traps (plural "Years of Discovery" headers; `Fluman`->Human, `me2`->mc2; 260 B.C. as -260).
  `src/time_capsule/haven100.json`.
- `population.py` + `build_sample.py`: eligible = discoveries with `year > T_M`, with straddler and
  gap-ceiling handling exposed (never silently applied). Talkie-1930 -> **26 eligible**.
- Cross-model table built: neutron is post-cutoff for 5 models (dose-response on gap); Ranke-1929
  (4B) and Talkie-1930 (13B) share an identical 26-item eligible set (a clean scale control).

### Environment formalism (`environment.py`)

- `E = (S, M, A)` = description / prevailing explanation / anomalous evidence. Companion `AnswerKey`
  `= (D, core_commitment, epicycles, criteria)`. `render()` emits S, A, M (anomalies before the
  account, as in Hillside) + the fixed prompt "How do you explain what's happening?"
- House format enforced mechanically: 3 paragraphs, 170-280 words (Hillside 216, Lanterns 231),
  closing on "The account has never failed." Leakage check voids any item whose prompt names D or
  uses anachronistic terms.
- Design rule adopted from the neutron: **A must carry the quantitative contradiction** (the
  proton-vs-nitrogen energy disagreement), or the model can rationally keep M.
- Epicycles are **documented, not invented**: the Joliot-Curies actually made the gamma-ray epicycle
  and missed the neutron; Fermi's 1938 Nobel was for the transuranic epicycle in fission.
- Three environments authored to the house format: **neutron** (STRONG, +2y), **fission**
  (neutron-blocked for 1930), **endosymbiosis** (re-individuation; later found to use anachronistic
  molecular evidence).

### Castability screen (2026-07-15) — `src/time_capsule/classification.py`

Screened the eligible-26 for talkie-1930 against four filters (incumbent frame; anomaly statable
pre-1930; not prerequisite-blocked; small *effective* gap). **26 -> 4 STRONG + 6 MARGINAL + 16 NO.**

- STRONG: Neutron, Dark Matter, The Big Bang, Jumpin' Genes.
- Three findings that change the design:
  1. **Effective anomaly year != Haven year.** Dark Matter's anomaly is Zwicky 1933 (+3y), not
     Haven's 1970; the Big Bang's is Hubble 1929 (-1y), not 1948. Sizing by Haven's date mis-selects.
  2. **Negative effective gap = endorsement test, not generation test** (Big Bang/Lemaitre,
     Fusion/Eddington, Drift/Wegener — the reframe was already a minority view by 1930). Different
     experiment; must not be pooled with generation items.
  3. **Anachronistic-A + co-selection.** Endosymbiosis's evidence is post-1953 molecular biology, so
     it is uncastable for 1930 but castable for a ~1960 cutoff. Item and model must be chosen
     together — the real argument for the Ranke multi-cutoff family beyond dose-response.
- Consequence for the built environments: neutron is correctly homed; fission belongs to a post-1932
  cutoff (Ranke-1929); endosymbiosis needs a ~1960 model or a much weaker pre-molecular A.

## State at end of session

- **No time-capsule model has been run yet.** All work to date is population, formalism, and item
  screening.
- Paper: ICLR-formatted, organized, figure + epigraph in, builds clean. Synced to Overleaf.
- Open next steps: build the 4 STRONG items to the neutron's standard (Dark Matter first — clean,
  quantitative, +3y); contamination-check Talkie-1930 against the targets (TypewriterLM History-Event
  benchmark); write the partial-progress scoring rubric; decide whether to run generation and
  endorsement items as separate conditions.

## Spend

- OpenRouter (format_sensitivity Grok smoke tests): ~$0.55 total. Key had ~$86 of its $250 cap
  remaining as of 2026-07-10. No Anthropic-side per-call cost is logged (API returns none).
