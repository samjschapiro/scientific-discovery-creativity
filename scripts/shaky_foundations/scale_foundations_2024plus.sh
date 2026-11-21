#!/bin/bash
# Scale-up on the most-cited 2024-2025 foundations, critiques through Nov 2026 (2026 partial).
uv run python src/shaky_foundations/scripts/scale_foundations.py configs/shaky_foundations/scale_foundations_2024plus.yaml "$@"
