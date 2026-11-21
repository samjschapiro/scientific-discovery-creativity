#!/bin/bash
# Analogical novelty: distance from a paper's problem to the problems its mechanisms served before.
uv run python src/shaky_foundations/scripts/build_analogy.py configs/shaky_foundations/build_analogy.yaml "$@"
