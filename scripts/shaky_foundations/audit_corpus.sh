#!/bin/bash
# Data audit: can the Lacuna corpus see the foundations we want to score?
uv run python src/shaky_foundations/scripts/audit_corpus.py configs/shaky_foundations/audit_corpus.yaml "$@"
