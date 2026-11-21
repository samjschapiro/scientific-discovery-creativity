#!/bin/bash
# Camera-ready one-row version of the limitation timelines (Transformer, VGG).
uv run python src/shaky_foundations/scripts/limitation_timelines.py configs/shaky_foundations/limitation_timelines_camera.yaml "$@"
