#!/bin/bash
# Pilot: attribute citers' critique atoms to their references; critique curves for known cracks vs controls.
uv run python src/shaky_foundations/scripts/pilot_critiques.py configs/shaky_foundations/pilot_critiques.yaml "$@"
