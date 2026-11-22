# 2026-11-22: idea-generation evaluation rethink; do fixes of foundation limitations pay off?

## Summary

The retrospective idea-generation benchmark was judged a no-go because of LLM contamination, and the Alien Space
of Science evaluation protocol was reviewed as the alternative. Then Alejandro's question (do papers addressing
shaky foundations become impactful?) was tested with Claude subagents labelling 2,529 candidate fixers: fixing a
known limitation does not earn citations, and neither does fixing the one critics agree on most.

## Tasks completed

- **Closing tasks for 2026-11-21** (start of session): scrubbed a personal email from pushed settings
  (amended + force-with-lease push, user-approved); docs updated.
- **Idea-generation benchmark scaffold** (`ideagen.py`, `ideagen_build`, 8 targets): briefing cards at cutoff T,
  candidate pools with hard negatives, limitation-direction projection; scoring controls (reference idea AUC 0.92,
  restated limitation 0.61, random 0.47). Generation pilot put on hold (no Anthropic key), then the user judged the
  retrospective approach a no-go: generators have read the post-T fixes.
- **Alien Space of Science (arXiv 2603.01092 v3) evaluation reviewed:** temporal recovery of 2025 atom
  combinations by a non-LLM generator (35.9x chance; 3.24x for novel), blind GPT-5.5 tournament, 10 human raters,
  autoresearch execution judged by a calibrated LLM. Lesson: retrospective tests only for non-LLM generators; LLM
  ideas judged prospectively.
- **Fixer candidates** (`fixer_candidates.py`): 54 gold foundations, 82 limitations; every citer up to 2022 ranked by
  similarity of its stated problem to the limitation (centroid shortlist, real bge-large re-score); top 30 + hand
  validation items = 2,529 candidates in 16 batches.
- **Labelling by 16 in-session Claude subagents** (no API): fix 1,414 / mentions 498 / unrelated 546 / applies 71.
  Precision 0.80, recall 0.92 vs 85 blind hand labels. Agents collided on a shared scratch script name; each caught
  it via the ID check; 30 sampled reasons verified.
- **Impact** (`fixer_impact.py`, v1 then v2): fixers −1.0 [−3.1, +1.0] percentile points vs same-foundation,
  same-year citers; fix vs mentions +0.3 [−3.3, +3.9]; top-1% share lower for fixers than for mentions.
- **Shakiness measure:** replaced rarefied top share (needs >= 20 critics, 190/500 foundations) with pairwise
  agreement (Simpson's index; rho 0.98 with the old score, no N dependence, 458/500 at >= 5 critics). Foundation-level
  dose: rho 0.27, permutation p = 0.056, terciles −5.1 / +1.6 / −0.2.
- **Report:** `docs/reports/2026-11-22_fixer_impact/report.md` + `.html`, following `docs/writing_advice.md`; two figures
  (`fixer_impact_v2_premium_by_label`, `fixer_impact_v2_dose`), random label examples.
- **User's per-limitation measure** (share of the foundation's critics raising that limitation, cosine >= 0.75/0.78/0.80):
  no relation with fixer citations under any outcome (premium, raw, log, percentile, max, top-10%; |rho| <= 0.10,
  78 limitations), but predicts the number of fixes (rho 0.35–0.41, p <= 0.002). Scratch analysis, not yet in the
  report.
- **Power:** headline null is tight (±4 points); per-limitation test detects only rho >= 0.31. Proposed scale-up to
  ~950 pipeline critique groups x top 10 (~9,500 judgments, detects rho >= 0.09).

## Files created / modified

- `src/shaky_foundations/ideagen.py`, `src/shaky_foundations/scripts/ideagen_build.py`, configs `ideagen_build.yaml`,
  `ideagen_targets.yaml`, wrapper `ideagen_build.sh`
- `src/shaky_foundations/embeddings.py` (`embed_texts`)
- `src/shaky_foundations/scripts/fixer_candidates.py`, `fixer_impact.py`; configs `fixer_candidates.yaml`,
  `fixer_impact.yaml`; wrappers `fixer_candidates.sh`, `fixer_impact.sh`
- `docs/reports/2026-11-22_fixer_impact/report.md`, `report.html`
- `docs/tracks/shaky_foundations/progress.md`, `docs/research_context.md`, `README.md`, `docs/structure.md`
- Data (gitignored): `data/shaky_foundations/fixer_candidates_v1/` (incl. `labels/`), `fixer_impact_v1/`, `fixer_impact_v2/`,
  `ideagen_build_v1/`; figures in `data/shaky_foundations/figures/`

## Key decisions and insights

- Contamination rules out scoring LLM-generated ideas against known later fixes; validate generators in atom space
  or judge prospectively.
- Claude subagents are a workable labelling route without an API key (~2,500 judgments in ~6 minutes).
- Rarefaction was overkill; an unbiased pairwise-agreement estimate or a simple fraction avoids the bias without a
  20-critic floor (the bias came from taking a maximum).
- Recognised limitations attract more fixes, but recognition does not make an individual fix more cited.

## Open questions / next steps

- Go-ahead on the fixer scale-up (950 groups x top 10), with a pre-specified analysis.
- Update the report (simple outcomes; per-limitation null + effort finding) — offered.
- Separate frame-changing from incremental fixes.
- Commit decision for the ideagen scaffold (committed in this closing pass as kept infrastructure).
- Still open from before: gap-closing data (Jerry), LLM verification of critique attributions, taxonomy follow-ups.
