#!/bin/bash
# Are the "most cited" papers foundations? F/E/G inside Lacuna vs a baseline, plus paper kind.
uv run python src/shaky_foundations/scripts/foundation_status.py configs/shaky_foundations/foundation_status.yaml "$@"
