#!/bin/bash
# Critique profile per recent foundation: critics split into top limitation groups vs everything else.
uv run python src/shaky_foundations/scripts/critique_profiles.py configs/shaky_foundations/critique_profiles.yaml "$@"
