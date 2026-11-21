#!/bin/bash
# Scale-up on the most-cited 2023-2025 foundations (0-2 years of critiques).
uv run python src/shaky_foundations/scripts/scale_foundations.py configs/shaky_foundations/scale_foundations_2023plus.yaml "$@"
