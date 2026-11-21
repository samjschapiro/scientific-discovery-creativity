# Scientific discovery & creativity

Research code for testing whether AI systems can produce transformational (frame-replacing) scientific ideas.
The active track, `shaky_foundations`, maps how scientific-creativity metrics relate across 2M AI papers. It also
identifies the limitations later papers raise against foundational papers, as targets for idea generation.
Background and status: `docs/research_context.md`.

## Setup

```bash
uv sync
cp .env.example .env   # add API keys
```

Data is not in git. The Lacuna package and external datasets are expected under `data/` (see
`docs/tracks/shaky_foundations/progress.md`).

## Main scripts

```bash
bash scripts/shaky_foundations/build_measures.sh       # disruption, F/E/G, atom novelty per paper
bash scripts/shaky_foundations/build_prescience.sh     # prescience and emergence
bash scripts/shaky_foundations/analyze_factors_v3.sh   # factor structure of the metrics
bash scripts/shaky_foundations/pilot_critiques.sh      # attribute critiques to foundations (pilot)
bash scripts/shaky_foundations/evaluate_gold.sh        # score limitation identification on the gold set
```
