# Session log: shaky_foundations track, 2026-11-16 to 2026-11-21

## Summary

We set up the shaky_foundations track for the cross-lab project "Alien space of science meets
combinatorial/transformational creativity". It covered two strands:
- **Empirical taxonomy of creativity metrics** on Lacuna's 2010–2019 AI papers. Result: a four-factor structure
  read as blind variation / selection / retention, written up as a report.
- **Identifying the limitations later papers raise against foundational papers.** Validated on a gold set: the
  known limitation is in the top 3 groups for 64% of foundations with at least 20 critics.

## Tasks completed

**Setup and data (11-16)**
- Created the track (`src/`, `scripts/`, `configs/`, `docs/tracks/shaky_foundations/`) from the 11/9 framework in
  the project doc.
- Audited the Lacuna v1 package (`audit_corpus`):
  - Limitation atoms critique *prior* work only in the problems_and_motivation lens, and never name the paper.
  - Landmark OpenAlex matches were broken (Attention had no match, AlexNet was on the wrong record).
  - Atom coverage rises 16% → 56%.
- Downloaded and verified the Fang & Evans F/E/G indices and Kedrick et al.'s gap-opener labels (Zenodo).
- Luo & Evans hole-filling labels are not released; drafted a Slack message to Jerry (no Slack connector used).

**Step 1: how the creativity measures relate (11-16)**
- `build_measures`: CD₅, atom DSI, problem–mechanism distance, concept-pair novelty and PMI, Fang F/E/G and
  Kedrick labels for the 2010–19 pool.
- Found that `references_openalex` holds only out-of-corpus references. CD was 0 everywhere until we built the
  union with `citations`. Kedrick's files have conflicting duplicates, which we set to null.
- `analyze_relationships`:
  - CD tracks Generalization (0.36) and not Foundation (−0.16 raw, 0 partial).
  - Atom DSI relates weakly to CD and Generalization.
  - Atom novelty separates gap-openers from "neither" but not from novel-pair non-openers.

**Analogical novelty (11-16)**
- Built a Kombine-style analogy score: distance from a mechanism's prior problems. It failed cue-phrase
  validation (AUC ≈ 0.5), because a mechanism atom's concept encodes the target domain, not the source. Kept as a
  documented negative result.

**Package v2 and the factor structure (11-20/21)**
- Downloaded Alejandro's corrected v2 package from Drive and checked sha256 sums.
- Moved everything to canonical pids: duplicates were filtered in CD edges, pair novelty and analogy homes.
- All v1 results replicate. Added `analyze_factors` (parallel analysis + varimax).

**Shaky foundations: finding limitations (11-21)**
- `pilot_critiques` (17 foundations):
  - Each critique atom is attributed to one of its citer's references by atom similarity.
  - Fixed misattribution by matching only on a reference's own-contribution atoms.
- Embeddings: plain-text bge-large reproduces Lacuna's vectors exactly (r = 1.0 vs `sim_c200000`), giving a
  reusable cache (`embeddings.py`).
- Hand-labelled 204 attributions: about 25% precise; real vectors don't help.
- The patcher-vs-critic split had no signal.
- `scale_foundations` (top 500, 2010–19):
  - Citation-only displacement separates cracks from controls.
  - Critique concentration does not predict displacement.
  - Found a messenger confound (papers that diagnosed a limitation absorb its critiques).
- Sam reframed the goal as *identifying* limitations, not predicting abandonment (saved to memory).
- Gold set (`gold_limitations.yaml`, written blind) and `evaluate_gold`:
  - The known limitation is in the top 3 groups for 48% overall and 64% with at least 20 critics; missed in 9%.
  - Threshold-free retrieval: 0.60 top-1 against 0.02 by chance.
- `limitation_timelines`:
  - Grid figure with two-sentence descriptions.
  - Camera-ready Transformer and VGG figure with several limitations per foundation.
  - Dots for critic papers that also propose fixes (hand-judged, in config).
- Recent foundations: scale-ups for 2020–23, 2023–25 and 2024–25 (2026 citations included), and critique
  profiles for 2024–25 papers.

**Side analyses (11-21)**
- `foundation_status`: own F/E/G inside Lacuna (Spearman 0.64–0.69 vs Fang). 79% / 78% / 65% of the most-cited
  2010s / 2020–23 / 2024–25 papers are foundations; surveys almost never are.
- `critics_disruption`: critics are not more disruptive or more cited than matched non-critics. Generalization
  papers that cite a top foundation are more cited.
- `cite_types`: prototype citation typing from atoms. Only the critique type is meaningful; "uses as a tool" is
  invisible to atoms.

**Prescience and emergence (11-21)**
- `build_prescience`: atom-based versions after Lockhart et al. 2026. Read the full paper: they report no
  prescience–emergence correlation.
- Reproduced their Figure S3: prescience predicts top-cited status, surprise does not.
- `factors_v3`: four factors, read as Selection (F1), Variation (F2), Retention (F3) and Embeddedness (F4).

**Report**
- `docs/reports/2026-11-21_creativity_taxonomy_bvsr/report.md` and `report.html` (self-contained; figures
  embedded by `render_report`). Ordered interpretation first; title per Sam.
- `taxonomy_figures`: named-loadings figure, selection-vs-variation map, landmark factor scores.
- Drafted a Slack reply to Alejandro explaining critique attribution.

## Files created or modified

- `src/shaky_foundations/`: `data.py`, `disruption.py`, `atom_measures.py`, `external.py`, `analogy.py`,
  `critiques.py`, `embeddings.py`, `displacement.py`, `efg.py`, `prescience.py`, `figures.py`.
- `src/shaky_foundations/scripts/` (17 scripts), each with a config in `configs/shaky_foundations/` and a
  wrapper in `scripts/shaky_foundations/`.
- `docs/tracks/shaky_foundations/progress.md` and `notes.md`; the report folder; this log;
  `docs/research_context.md`, `docs/structure.md`, `README.md`, `.gitignore`.
- Data (gitignored): `data/lacuna-recombination-2026-11-06-v{1,2}` (symlinks), `data/fang_2025_efg/`,
  `data/kedrick_2025_gap_openers/`, `data/shaky_foundations/*`. All figures are in
  `data/shaky_foundations/figures/`.

## Key decisions and insights

- **Limitations are identified at the foundation level, not the critique level.** Attribution noise scatters
  while real critiques pile into one concept group.
- **Consequential AI papers were selected, not especially novel.** 5 of 11 landmarks are in the bottom third of
  variation; all 11 are top-quartile on selection.
- **Forward uptake is its own dimension.** Prescience, emergence and adoption are invisible to citation-structure
  metrics.
- **Conventions set by Sam:**
  - All track figures go in one folder.
  - The outcome of interest is limitation identification, not abandonment.
  - No Slack connector for drafts.

## Open questions and next steps

- **LLM verification of critique attributions:** needs Sam's approval for API spend.
- **Gap-closing data** from Luo & Evans, via Jerry.
- **Taxonomy:**
  - Predicted (pre-publication) emergence.
  - A citation-based novelty-at-publication measure (the empty cell in the report's layout).
  - An oblique rotation.
  - Extending to 2020 and 3-year windows.
- **Idea generation (next):** a retrospective benchmark, briefing cards at a cutoff year, three generation
  operators (analogy, blending, axiom revision), and scoring against the fixes that later appeared.
