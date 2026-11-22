#!/bin/bash
# Impact of papers judged to fix a foundation's limitation (needs labels from the fixer judges).
uv run python src/shaky_foundations/scripts/fixer_impact.py configs/shaky_foundations/fixer_impact.yaml "$@"
