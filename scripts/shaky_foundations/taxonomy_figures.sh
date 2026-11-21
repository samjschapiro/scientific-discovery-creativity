#!/bin/bash
# Camera-ready taxonomy figures (named loadings; selection vs variation map) and landmark factor scores.
uv run python src/shaky_foundations/scripts/taxonomy_figures.py configs/shaky_foundations/taxonomy_figures.yaml "$@"
