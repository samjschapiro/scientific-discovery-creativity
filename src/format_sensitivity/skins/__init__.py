"""Skin registry. Add a new re-individuation scenario by importing its SKIN here."""

from src.format_sensitivity.skins.filament import SKIN as _filament
from src.format_sensitivity.skins.hillside import SKIN as _hillside

REGISTRY = {skin.name: skin for skin in (_hillside, _filament)}


def get_skin(name: str):
    if name not in REGISTRY:
        raise ValueError(
            f"FATAL: unknown skin '{name}'. Known: {sorted(REGISTRY)}"
        )
    return REGISTRY[name]
