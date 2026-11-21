#!/bin/bash
# Keyless proof of the instrument: validates both environments and grades canned responses.
uv run python src/sci_twist/scripts/selfcheck.py "$@"
