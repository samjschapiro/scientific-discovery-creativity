# shaky_foundations: notes

## Limitation atoms do not point at the papers they criticise

"Limitation" is an atom *type*. The `lens` column records which extraction pass produced the atom,
and it changes what the limitation is about:

| lens | n (best run) | what the limitation is about |
|---|---|---|
| limitations_and_open_questions | 2.46M | the paper's own shortcomings |
| problems_and_motivation | 0.83M | **prior work**, as "existing approaches…", "standard X…" |
| findings / methods | ~5K | the paper's own method |

Only the problems_and_motivation lens carries a critique of other work, and even there it never
names the paper being criticised. Example: *"Many existing approaches to multi-class ranking
simplify the problem by reducing it to a collection of independent binary tasks…"*

So "paper B cites foundation A **while noting its limitations**" is a join the data can't do by
itself. Matching keywords against a foundation's citers gives the wrong results: among ResNet's
citers, "residual" hits compression residuals and video-codec residuals, not critiques of residual
connections. Attribution will need either semantic matching against the foundation's own atoms or
citation-context text.

## Landmark matching is broken for some of the most important papers

From `landmarks.csv` in the audit (2026-11-16):

| paper | OpenAlex cited_by | in-corpus citations | problem |
|---|---|---|---|
| Attention Is All You Need | null | **0** | unmatched to OpenAlex |
| AlexNet (ImageNet Classification…) | 754 | 352 | matched to the wrong record (real count is >100K) |
| GANs | 4,472 | 1,406 | far too low |
| GPT-3 (Few-Shot Learners) | 2,847 | 4,876 | in-corpus count *higher* than OpenAlex's, so the record is split across versions |
| ResNet, Adam, BERT, VAE, Dropout, LSTM | plausible | plausible | ok |

The package README says *"OpenAlex has some bad records (wrong years or DOIs on a few famous
works)"*, and its 100-paper hand audit checked title matches only. The famous papers are exactly the
foundation candidates, so this has to be fixed before ranking anything. Check `top_cited.csv`
against a hand list of foundations.

## Atom coverage

- The share of papers with atoms rises steadily: 16% (2010), 27% (2015), 47% (2020), 56% (2025).
  Normalise any per-year count of critiques by the number of citers that have atoms.
- Some classic foundations have **no atoms**: LSTM, the ImageNet dataset paper, DQN, SSIM. The
  pre-2010 ones are expected. DQN (Nature 2015) suggests that missing full text, not age, is the
  cause.
- Two extraction models (gemini-3-flash, gemini-2.5-flash-lite) produce different mixes of atoms
  and correlate with year. Control for `concept_model`.

## Environment

- DuckDB 2.0 changed its API. A relation from `con.sql(...)` no longer has `fetchone()`; use
  `con.execute(...).fetchall()`. Window `ORDER BY random()` is rejected, so sample with
  `hash(atom_id, seed)` instead.
- Query the parquet files in place through `open_lacuna()` views. Don't load `atoms.parquet`
  (2.4 GB) into memory.

## The reference graph is split across two tables

The package README says `references_openalex` holds "each paper's full OpenAlex reference list,
including works outside Lacuna". In fact it holds **only** the outside works: 0% of its ids are Lacuna
ids (sample of 200K rows). References to Lacuna papers exist only in `citations` (by pid). A paper's
full reference list is the union. My first CD run used only `references_openalex` and got CD = 0
for every paper. `disruption.build_edges` now builds the union in one integer node space. Worth
telling Alejandro so the README gets fixed.

## Kedrick's files have conflicting duplicates

`figure2_real.csv` repeats ~3.2K paperids and `figure4_data_cdtile.csv` ~1.5K, some with conflicting
labels (e.g. W1977289091 is both gap_opener and novel_pair_non_opener). `external.py` sets conflicting
ids to NULL with `kedrick_conflict = true`. Only 2 such ids are in our pool.

## Package v2 (2026-11-18)

- `papers` gains `wid`, `canonical_pid`, `cites_lacuna(_2025)`, `cites_total(_2025)`,
  `cites_total_source`; `cited_by_count` is gone. Use the `_2025` counts (fixed end for every paper).
- 47,480 duplicate entries. `citations` uses canonical pids only, but `references_openalex` still
  carries 1.1M rows under duplicate pids and `atoms` 326K best-run atoms. Filter to
  `pid = canonical_pid` wherever papers are counted (done in disruption, atom_measures, analogy).
- 9,286 duplicates have atoms while their canonical twin has none; those papers drop out of the
  atom measures (not merged; ~0.4%).
- The v2 README now states that `references_openalex` holds only works outside Lacuna (the issue
  noted above is fixed in the docs).

## Figures live in one folder

All figures for this track are written to `data/shaky_foundations/figures/`, named
`<run output dir>_<figure>.png` (e.g. `factors_v2_factors.png`), via
`src/shaky_foundations/figures.py:figure_path`. Never save figures inside a run's output directory.
