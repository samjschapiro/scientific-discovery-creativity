#!/bin/bash
# Do analogy scores pick up papers that say they borrowed a method ("inspired by", "originally developed for")?
uv run python src/shaky_foundations/scripts/validate_analogy.py configs/shaky_foundations/validate_analogy.yaml "$@"
