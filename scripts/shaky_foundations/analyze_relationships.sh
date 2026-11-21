#!/bin/bash
# Correlations / AUCs / crosstabs between CD, F/E/G, gap-opening and atom measures.
uv run python src/shaky_foundations/scripts/analyze_relationships.py configs/shaky_foundations/analyze_relationships.yaml "$@"
