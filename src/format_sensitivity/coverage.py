"""Fact-coverage validation, per skin.

The experiment rests on information being constant across a skin's formats. If a
variant silently drops a fact, we measure fact-deletion and call it format
sensitivity. So coverage is enforced before any model sees a stimulus.

Three checks, all of which must pass for a skin:

1. Slot completeness — the skin's facts and anchors fill exactly the skeleton's
   slot keys (S1..S18), no more, no fewer.
2. Declared coverage — every slot has a declared location in every format the
   skin provides.
3. Lexical anchors — every slot's anchor groups appear in every rendered format.
   A *necessary* condition, not sufficient: catches deletions, does not prove a
   fact is stated in the intended sense.
"""

from src.format_sensitivity.skeleton import SLOTS
from src.format_sensitivity.skins import REGISTRY, get_skin


def check_slots(skin) -> None:
    slot_keys = set(SLOTS)
    if set(skin.facts) != slot_keys:
        raise ValueError(
            f"FATAL: skin '{skin.name}' facts do not match the skeleton slots. "
            f"Missing: {sorted(slot_keys - set(skin.facts))}. "
            f"Extra: {sorted(set(skin.facts) - slot_keys)}."
        )
    if set(skin.anchors) != slot_keys:
        raise ValueError(
            f"FATAL: skin '{skin.name}' anchors do not match the skeleton slots. "
            f"Missing: {sorted(slot_keys - set(skin.anchors))}. "
            f"Extra: {sorted(set(skin.anchors) - slot_keys)}."
        )


def check_declared_coverage(skin, format_code: str) -> None:
    declared = skin.coverage.get(format_code)
    if declared is None:
        raise ValueError(
            f"FATAL: skin '{skin.name}' has no declared coverage for '{format_code}'"
        )
    missing = sorted(set(SLOTS) - set(declared), key=lambda s: int(s[1:]))
    if missing:
        raise ValueError(
            f"FATAL: skin '{skin.name}' format '{format_code}' declares no "
            f"location for slots: {missing}"
        )


def check_anchors(skin, format_code: str, seed: int) -> None:
    text = skin.render(format_code, seed).lower()
    failures = []
    for slot, groups in skin.anchors.items():
        for group in groups:
            if not any(alt.lower() in text for alt in group):
                failures.append((slot, group))
    if failures:
        detail = "; ".join(f"{slot} needs one of {group}" for slot, group in failures)
        raise ValueError(
            f"FATAL: skin '{skin.name}' format '{format_code}' missing anchors: {detail}"
        )


def validate_skin(skin_name: str, seed: int = 0) -> None:
    skin = get_skin(skin_name)
    check_slots(skin)
    for format_code in skin.supported_formats:
        check_declared_coverage(skin, format_code)
        check_anchors(skin, format_code, seed=seed)


def validate_all(seed: int = 0) -> None:
    for skin_name in REGISTRY:
        validate_skin(skin_name, seed=seed)


if __name__ == "__main__":
    validate_all()
    for name, skin in sorted(REGISTRY.items()):
        print(f"OK: skin '{name}' — {len(skin.facts)} slots, "
              f"formats {list(skin.supported_formats)}")
