#!/bin/bash
# Are papers that critique a top foundation more disruptive (overall and among Generalization papers)?
uv run python src/shaky_foundations/scripts/critics_disruption.py configs/shaky_foundations/critics_disruption.yaml "$@"
