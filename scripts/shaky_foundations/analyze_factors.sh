#!/bin/bash
# Exploratory factor structure of the creativity measures (parallel analysis + varimax).
uv run python src/shaky_foundations/scripts/analyze_factors.py configs/shaky_foundations/analyze_factors.yaml "$@"
