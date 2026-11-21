"""Stimulus dispatch across skins.

The fact skeleton and the framing/probe sets live in skeleton.py. Each domain
skin (skins/) fills the skeleton's 18 slots in a novel surface. This module is
the thin layer the orchestration script talks to.

Information must be held constant across formats *within a skin*: every format
variant of a skin contains every fact. Comparisons across skins are comparisons
of surface at fixed structure, not of content.
"""

from src.format_sensitivity.skeleton import FORMAT_CODES, FRAMINGS, PROBES
from src.format_sensitivity.skins import REGISTRY, get_skin

__all__ = [
    "FORMAT_CODES",
    "FRAMINGS",
    "PROBES",
    "REGISTRY",
    "get_skin",
    "render",
    "build_prompt",
]


def render(skin_name: str, format_code: str, seed: int) -> str:
    return get_skin(skin_name).render(format_code, seed)


def build_prompt(skin_name: str, format_code: str, instruction: str, seed: int) -> str:
    return f"{render(skin_name, format_code, seed)}\n\n---\n\n{instruction}"
