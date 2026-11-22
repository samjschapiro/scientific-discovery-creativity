# Project structure

```
.
├── README.md, CLAUDE.md, AGENTS.md, GEMINI.md   # entry points; CLAUDE.md -> docs/repo_usage.md
├── pyproject.toml                                # uv-managed dependencies
├── src/
│   ├── utils.py                                  # load_config, init_directory (cross-track)
│   ├── format_sensitivity/  time_capsule/  sci_twist/   # earlier tracks
│   └── shaky_foundations/
│       ├── data.py              # open/verify the Lacuna package (DuckDB views)
│       ├── disruption.py        # CD index over the in-corpus + external reference graph
│       ├── atom_measures.py     # atom DSI, problem-mechanism distance, pair novelty/PMI
│       ├── external.py          # Fang & Evans F/E/G, Kedrick gap-opener views
│       ├── efg.py               # F/E/G computed inside Lacuna (per paper and per citation)
│       ├── prescience.py        # prescience, novel-pair adoption, emergence
│       ├── critiques.py         # critique-to-reference attribution, embedding re-score, patch scores
│       ├── embeddings.py        # bge-large atom-vector cache
│       ├── displacement.py      # citation-only displacement (retention of a foundation's neighbourhood)
│       ├── analogy.py           # analogical-novelty score (negative result)
│       ├── ideagen.py           # idea-generation benchmark: briefing cards, candidate pools, scoring
│       ├── figures.py           # figure_path: every figure -> data/shaky_foundations/figures/
│       └── scripts/             # one entry point per analysis (each takes a config)
├── configs/<track>/             # YAML configs (output_dir, parameters); gold_limitations.yaml = gold set
├── scripts/<track>/             # bash wrappers: bash scripts/<track>/<name>.sh [--overwrite] [--debug]
├── data/                        # gitignored: Lacuna symlinks, external datasets, all outputs
│   └── shaky_foundations/
│       ├── fixer_candidates_v1/ # candidates, batches/, labels/ (Claude subagent judgments), judge_prompt.md
│       ├── figures/             # ALL figures for the track, named <run>_<figure>.png/pdf
│       └── <run>_vN/            # one folder per run (config.yaml + outputs)
├── docs/
│   ├── repo_usage.md            # conventions (single source of truth)
│   ├── research_context.md      # bird's-eye status
│   ├── structure.md             # this file
│   ├── closing_tasks.md
│   ├── tracks/<track>/progress.md, notes.md
│   ├── reports/<date>_<name>/report.md (+ report.html)
│   ├── memos/                   # design memos (earlier tracks)
│   └── logs/<date>/<HHMM>_<topic>.md
├── literature/  resources/  papers/  scratch/   # DVC / external / Overleaf / temporary (contents gitignored)
```
