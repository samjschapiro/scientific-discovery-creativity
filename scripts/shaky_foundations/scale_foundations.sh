#!/bin/bash
# Shakiness (critique concentration) and citation displacement for the top-N cited foundations.
uv run python src/shaky_foundations/scripts/scale_foundations.py configs/shaky_foundations/scale_foundations.yaml "$@"
