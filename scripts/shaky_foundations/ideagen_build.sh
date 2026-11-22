#!/bin/bash
# Build the retrospective idea-generation benchmark (cards, ground truth, pools) and validate scoring.
uv run python src/shaky_foundations/scripts/ideagen_build.py configs/shaky_foundations/ideagen_build.yaml "$@"
