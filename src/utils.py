"""Cross-track utilities. Stable API — changing signatures breaks multiple tracks."""

import shutil
from pathlib import Path

import yaml


def load_config(config_path: str) -> dict:
    """Load a YAML config. Fails loudly if the file is missing or empty."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"FATAL: config not found: {config_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    if not config:
        raise ValueError(f"FATAL: config is empty: {config_path}")

    return config


def init_directory(output_dir: str, overwrite: bool = False) -> Path:
    """Create output_dir, refusing to clobber an existing run unless overwrite=True."""
    path = Path(output_dir)

    if path.exists():
        if not overwrite:
            raise ValueError(
                f"FATAL: output_dir already exists: {path}. Use --overwrite to replace it."
            )
        shutil.rmtree(path)

    path.mkdir(parents=True)
    return path
