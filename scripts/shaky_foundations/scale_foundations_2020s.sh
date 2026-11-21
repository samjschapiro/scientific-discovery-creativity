#!/bin/bash
# Scale-up on the most-cited 2020-2023 foundations (fewer years of critiques, higher atom coverage).
uv run python src/shaky_foundations/scripts/scale_foundations.py configs/shaky_foundations/scale_foundations_2020s.yaml "$@"
