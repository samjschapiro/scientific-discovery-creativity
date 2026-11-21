#!/bin/bash
# Score limitation identification against the gold set (calibration = pilot cracks, test = 50 sampled foundations).
uv run python src/shaky_foundations/scripts/evaluate_gold.py configs/shaky_foundations/evaluate_gold.yaml "$@"
