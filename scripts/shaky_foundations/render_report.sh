#!/bin/bash
# Render a markdown report to a self-contained HTML file (figures embedded). Usage: render_report.sh docs/reports/<dir>/report.md
uv run --with markdown python src/shaky_foundations/scripts/render_report.py "$@"
