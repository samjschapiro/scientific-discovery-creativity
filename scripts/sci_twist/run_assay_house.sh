#!/bin/bash
# Run the Assay House first cut against a model. Needs `uv sync` and ANTHROPIC_API_KEY.
uv run python src/sci_twist/scripts/run_assay_house.py configs/sci_twist/assay_house_first_cut.yaml "$@"
