#!/bin/bash
# Candidate fixers of gold foundation limitations, batched for labelling by Claude subagents.
uv run python src/shaky_foundations/scripts/fixer_candidates.py configs/shaky_foundations/fixer_candidates.yaml "$@"
