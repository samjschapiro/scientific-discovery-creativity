"""Every figure for this track goes in ONE folder: data/shaky_foundations/figures/.

Filenames are prefixed with the run's output-dir name so provenance stays visible, e.g.
figure_path("data/shaky_foundations/factors_v2", "factors.png")
    -> data/shaky_foundations/figures/factors_v2_factors.png
Never save figures inside a run's output directory.
"""

from pathlib import Path

FIGURES_DIR = Path("data/shaky_foundations/figures")


def figure_path(output_dir: str | Path, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR / f"{Path(output_dir).name}_{name}"
