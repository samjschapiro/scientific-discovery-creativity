#!/bin/bash
# Shakiness over time for identified limitations (cumulative critics raising it vs all critics).
uv run python src/shaky_foundations/scripts/limitation_timelines.py configs/shaky_foundations/limitation_timelines.yaml "$@"
