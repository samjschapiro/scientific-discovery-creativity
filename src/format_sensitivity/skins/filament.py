"""Filament skin — a novel-surface re-individuation, non-biological.

Same skeleton as Hillside. Domain moved off ecology entirely: an invented
industrial apparatus (a bench of "pins" in a "bed"), invented units (passes,
spans, shifts), invented medium (the bed's packing). The reframe is mechanical,
not organic: the pins are surfaced loops of one continuous filament threaded
through the bed. "Cut a hundred and new ones appear at the margins" is served by
a filament under tension redistributing when loops are severed, not by growth.

Purpose: Bar 1. The referent probe should name no real phenomenon. This skin is
a candidate, not a guarantee — the probe adjudicates. If models name a real
apparatus, it is retrieval-permeable and gets redrawn.

Provides F0 / F1 / F3 (enough for the F0-vs-F3 first cut and the framing ladder).
F2 / F5 are not written for this skin yet.
"""

from src.format_sensitivity.skins.base import Skin

FACTS = {
    "S1": "A technician counts pins and calls each one a fixture",
    "S2": "Each pin carries its own bead at the tip",
    "S3": "Each pin is seated in the bed at its base",
    "S4": "Each pin goes slack each shift and draws taut again",
    "S5": "The tally is careful and has been kept for years",
    "S6": "Pins across the whole bench draw taut within one pass of one another",
    "S7": "Pins across the whole bench go slack within one pass of one another",
    "S8": "The pins in the far corner receive far less heat and tension than those by the door",
    "S9": "Clip a hundred pins in one place, and within a week new pins surface at the edges of the bed",
    "S10": "The number of new pins is proportional to how many were clipped",
    "S11": "The new pins surface in places distant from the clipping",
    "S12": "Crush the bead on a single pin and, passes later, pins tens of spans away thicken their own beads",
    "S13": "No pin has ever been seen being set",
    "S14": "Samples of the bed's packing turn up nothing unusual",
    "S15": "Standing account: many separate fixtures, coordinated by the bench's supply and by tension-messages through the bed's packing",
    "S16": "Epicycle: a strain message, posited to explain the bead-thickening",
    "S17": "Epicycle: a crowding message, posited to explain the new pins at the edges",
    "S18": "The account has never failed",
}

ANCHORS = {
    "S1": [["pin"], ["fixture"]],
    "S2": [["bead"]],
    "S3": [["base"], ["seat", "seated"]],
    "S4": [["slack"], ["taut"], ["shift"]],
    "S5": [["tally", "count"], ["year"]],
    "S6": [["taut"]],
    "S7": [["slack"]],
    "S8": [["far corner"], ["heat"], ["tension"]],
    "S9": [["hundred"]],
    "S10": [["proportion"]],
    "S11": [["edge", "distant", "displaced"]],
    "S12": [["thicken"]],
    "S13": [["being set", "been set"]],
    "S14": [["packing"], ["nothing unusual"]],
    "S15": [["message"], ["packing", "bed"]],
    "S16": [["strain message"]],
    "S17": [["crowding message"]],
    "S18": [["never failed", "not failed", "contradicted"]],
}

REFRAME = (
    "The pins are not separate fixtures. They are the surfaced loops of one "
    "continuous filament threaded back and forth through the bed; what the "
    "technician counts as fixtures are folds of one thread. Synchrony needs no "
    "message because there is one filament under one tension, and no pin is ever "
    "'set' because there are no separate pins to set."
)

_F0 = """In a testing hall a technician counts pins and calls each one a fixture. Each pin carries its own bead at the tip, is seated in the bed at its base, goes slack each shift, and draws taut again. The tally is careful and has been kept for years.

Several regularities have accumulated. Pins across the whole bench draw taut within one pass of one another and go slack within one pass of one another, though the pins in the far corner receive far less heat and tension than those by the door. Clip a hundred pins in one place and, within a week, new pins surface at the edges of the bed — in number proportional to how many were clipped, and in places distant from the clipping. Crush the bead on a single pin and, passes later, pins tens of spans away thicken their own beads. No pin has ever been seen being set. Samples of the bed's packing turn up nothing unusual.

The hall's standing account is that these are many separate fixtures coordinated by the bench's supply and by tension-messages passing between them through the bed's packing. This explains the synchrony, and where it falls short a further message is proposed: a strain message to explain the bead-thickening, a crowding message to explain the new pins at the edges. Each addition fits. The account has never failed."""

_F1 = """Testing bench. Recorded observations.

| # | Observation |
|---|---|
| 1 | Pins are counted individually. Each counted pin is recorded as one fixture. |
| 2 | Each pin carries its own bead at the tip. |
| 3 | Each pin is seated in the bed at its base. |
| 4 | Each pin goes slack each shift and draws taut again. |
| 5 | The tally has been kept carefully, for years. |
| 6 | Pins across the whole bench draw taut within one pass of one another. |
| 7 | Pins across the whole bench go slack within one pass of one another. |
| 8 | The far corner receives far less heat and tension than the pins by the door. |
| 9 | Where a hundred pins were clipped, new pins surfaced at the edges of the bed within a week. |
| 10 | The number of new pins was proportional to the number clipped. |
| 11 | The new pins surfaced in places distant from the clipping. |
| 12 | Where the bead was crushed on a single pin, pins tens of spans away thickened their own beads within passes. |
| 13 | No pin has ever been seen being set. |
| 14 | Samples of the bed's packing show nothing unusual. |

Standing account. These are many separate fixtures, coordinated by the bench's supply and by tension-messages passing between them through the bed's packing. A strain message accounts for observation 12. A crowding message accounts for observations 9-11. The account has never failed."""

_BUNDLE = [
    (
        "DOCUMENT A — Bench register, cover sheet",
        """Testing bench. Pins counted individually; each pin entered as one fixture. Bead at the tip, proper to each pin. Each pin seated in the bed at its base. Pins go slack each shift and draw taut again. Tally kept, without a gap, for years.

Fixture totals by year: 1240, 1251, 1249, 1263, 1258, 1266, 1271, 1268, 1279, 1274, 1281, 1277.

Marginal note, different hand: No pin has ever been seen being set, in all the years of watching. Recorded here for want of anywhere better to put it.""",
    ),
    (
        "DOCUMENT B — Cycle table, hall appendix",
        """| Year | First taut, by the door | First taut, far corner | First slack, door | First slack, corner |
|---|---|---|---|---|
| 8 | pass 10 | pass 10 | pass 42 | pass 43 |
| 9 | pass 12 | pass 13 | pass 41 | pass 41 |
| 10 | pass 9 | pass 9 | pass 40 | pass 41 |
| 11 | pass 14 | pass 14 | pass 44 | pass 44 |

Footnote: The far corner receives far less heat and far less tension than the pins by the door. The hall has no explanation for the agreement of the pass-counts and has ceased to remark on it.""",
    ),
    (
        "DOCUMENT C — Clipping trial, summary of results",
        """One hundred pins were clipped from the eastern run in Year 4, to establish whether the bench could be thinned by clipping.

It could not. Within one week, ninety-six new pins had surfaced. None arose at the site of the clipping. All surfaced at the edges of the bed, at distances of forty to seventy spans from the clip. The trial was repeated at two hundred pins in Year 9; one hundred and ninety-four new pins surfaced, again at the edges. The response is proportional to the clipping and displaced from it.""",
    ),
    (
        "DOCUMENT D — Note from the bench's fitter",
        """With regard to the nine core samples of the packing: I regret that I can report nothing unusual. No filler out of the ordinary, no fault in the bed I would not expect to find under any bench of this make.

I remain convinced that the packing is nonetheless where the answer lies. If these fixtures are keeping their taut and their slack together across a bench as uneven as your door and your far corner, they must be signalling to one another, and the packing is the only medium available to them. Their bases sit close.

I would add to the picture two further messages, which I think the hall must accept. A strain message, released by a damaged fixture, would explain the bead-thickening you describe in your slip. A crowding message, by which a fixture senses how many of its fellows remain, would explain the new pins at the edges in the clipping trial.

The account is not yet complete but it has not failed us, and I do not see what would replace it.""",
    ),
    (
        "DOCUMENT E — Undated slip, found loose in the register",
        """Bead on the pin by the gangway crushed by a dropped tool. Two passes on — pins thirty and forty spans off have thickened their beads. Measured twice. Not imagination.""",
    ),
]

_COVERAGE = {
    "F0": {s: "narrative" for s in FACTS},
    "F1": {s: "table" for s in FACTS},
    "F3": {
        "S1": "A", "S2": "A", "S3": "A", "S4": "A", "S5": "A", "S13": "A",
        "S6": "B", "S7": "B", "S8": "B",
        "S9": "C", "S10": "C", "S11": "C",
        "S14": "D", "S15": "D", "S16": "D", "S17": "D", "S18": "D",
        "S12": "E",
    },
}

SKIN = Skin(
    name="filament",
    facts=FACTS,
    anchors=ANCHORS,
    single_block_formats={"F0": _F0, "F1": _F1},
    bundle_documents=_BUNDLE,
    coverage=_COVERAGE,
    reframe=REFRAME,
    supported_formats=("F0", "F1", "F3"),
)
