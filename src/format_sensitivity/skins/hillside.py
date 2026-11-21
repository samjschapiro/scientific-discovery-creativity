"""Hillside skin — Environment #1, the original.

Known-retrievable reference point: Grok names Pando / clonal aspen on the
referent probe. Kept precisely so the novel skins have a calibrated ceiling to
compare against. Text is the project doc's, verbatim.
"""

from src.format_sensitivity.skins.base import Skin

FACTS = {
    "S1": "A gardener counts stems and calls each one a plant",
    "S2": "Each stem has its own leaves",
    "S3": "Each stem has its own roots near the surface",
    "S4": "Each stem dies back in winter and regrows",
    "S5": "The count is careful and has been kept for years",
    "S6": "Stems across the whole hillside flush their leaves within a day of one another",
    "S7": "Stems shed within a day of one another",
    "S8": "The north face receives far less sun and water than the south face",
    "S9": "Cut a hundred stems in one place, and within a week new stems appear at the margins",
    "S10": "The number of new stems is proportional to how many were cut",
    "S11": "The new stems appear in places distant from the cutting",
    "S12": "Strip the leaves from a single stem and, days later, stems tens of paces away thicken their own leaves",
    "S13": "No seed of this plant has ever been found",
    "S14": "Soil samples turn up nothing unusual",
    "S15": "Standing account: many separate plants, coordinated by environment and by chemical signals through the soil",
    "S16": "Epicycle: a wounding signal, posited to explain the leaf-thickening",
    "S17": "Epicycle: a density signal, posited to explain the regrowth at the margins",
    "S18": "The account has never failed",
}

ANCHORS = {
    "S1": [["stem"], ["plant"]],
    "S2": [["leaves"]],
    "S3": [["roots"]],
    "S4": [["winter", "died back", "die back"], ["regrow"]],
    "S5": [["count", "census"], ["year"]],
    "S6": [["flush"]],
    "S7": [["shed"]],
    "S8": [["north"], ["south"]],
    "S9": [["hundred"]],
    "S10": [["proportion"]],
    "S11": [["margin"]],
    "S12": [["thicken"]],
    "S13": [["seed"]],
    "S14": [["nothing unusual"], ["soil"]],
    "S15": [["signal"], ["soil"]],
    "S16": [["wounding signal"]],
    "S17": [["density signal"]],
    "S18": [["never failed", "not failed", "contradicted"]],
}

REFRAME = (
    "The stems are not separate plants. They are ramets of one clonal individual "
    "(one genet) joined below ground; coordination needs no inter-plant signal "
    "because there are no separate individuals to signal between."
)

_F0 = """On a hillside a gardener counts stems and calls each one a plant. Each stem has its own leaves, its own roots near the surface, dies back in winter, and regrows. The count is careful and has been kept for years.

Several regularities have accumulated. Stems across the whole hillside flush their leaves within a day of one another and shed within a day of one another, though the stems on the north face receive far less sun and water than those on the south. Cut a hundred stems in one place and, within a week, new stems appear at the margins — in number proportional to how many were cut, and in places distant from the cutting. Strip the leaves from a single stem and, days later, stems tens of paces away thicken their own leaves. No seed of this plant has ever been found. Soil samples turn up nothing unusual.

The gardeners' standing account is that these are many separate plants coordinated by their environment and by chemical signals passing between them through the soil. This explains the synchrony, and where it falls short a further signal is proposed: a wounding signal to explain the leaf-thickening, a density signal to explain the regrowth at the margins. Each addition fits. The account has never failed."""

_F1 = """Hillside plot. Recorded observations.

| # | Observation |
|---|---|
| 1 | Stems are counted individually. Each counted stem is recorded as one plant. |
| 2 | Each stem bears its own leaves. |
| 3 | Each stem has its own roots, near the surface. |
| 4 | Each stem dies back in winter and regrows. |
| 5 | The count has been kept carefully, for years. |
| 6 | Stems across the whole hillside flush their leaves within a day of one another. |
| 7 | Stems across the whole hillside shed within a day of one another. |
| 8 | The north face receives far less sun and water than the south face. |
| 9 | Where a hundred stems were cut, new stems appeared at the margins within a week. |
| 10 | The number of new stems was proportional to the number cut. |
| 11 | The new stems appeared in places distant from the cutting. |
| 12 | Where the leaves were stripped from a single stem, stems tens of paces away thickened their own leaves within days. |
| 13 | No seed of this plant has ever been found. |
| 14 | Soil samples show nothing unusual. |

Standing account. These are many separate plants, coordinated by their shared environment and by chemical signals passing between them through the soil. A wounding signal accounts for observation 12. A density signal accounts for observations 9-11. The account has never failed."""

_F2 = """REGISTER OF THE HILLSIDE PLOT — kept by successive wardens

Year 1, third month. Census of the hillside begun. Each stem counted as one plant; this is the convention adopted and it will be held to. 1,240 plants recorded. Each stem carries its own leaves and puts down its own roots, which run near the surface and are easily lifted with a trowel.

Year 1, tenth month. All stems have died back. Warden notes the plot appears empty. Expect regrowth.

Year 2, fourth month. Regrowth confirmed; 1,251 plants. Census procedure unchanged and will be kept to annually.

Year 2, fourth month, later. Curious. The flush was not staggered. Walked the plot on the 9th: nothing. Walked it on the 10th: leaves everywhere, north face and south alike. Note that the north face lies in shade for most of the day and takes perhaps a third of the rainfall the south face does. One would expect it to lag by a week.

Year 2, tenth month. The shed was likewise within a day, across the whole hillside.

Year 3. No seed has been found. The warden has looked. His predecessor looked. We have sieved the leaf litter across four seasons and there is nothing.

Year 4, second month. At the direction of the station, a hundred stems were cut from the eastern quarter, to test whether the plot would thin.

Year 4, second month, ninth day. New stems have appeared. Not where we cut. They have come up at the margins of the plot, a good distance off. Counted 96. The proportion is close enough to what was taken that the warden remarks on it.

Year 5. Soil samples drawn at nine stations and sent for analysis. Returned: nothing unusual. No unusual mineral, no unusual organism.

Year 6, fifth month. An accident. A stem near the path was stripped of its leaves by a passing cart. Four days later the warden noticed that stems well away from the path — thirty paces, forty — had thickened their own leaves noticeably. He measured. The effect is real.

Year 6, seventh month. Discussed at the station. The consensus is that the plants communicate through the soil. A signal passing between the roots would explain the synchrony handsomely, and the roots do lie close together.

Year 7. Following the events of Year 6, a wounding signal is proposed, released by an injured plant and read by its neighbours. This accounts for the leaf-thickening.

Year 7, later. A density signal is proposed, by which the plants sense how many of them remain and grow accordingly. This accounts for the margin regrowth of Year 4.

Year 12. Twelve years of records. The account has met every observation the plot has produced, and no observation has yet contradicted it."""

_F5 = """The Hillside Plant: A Review of Twelve Years' Observation

The hillside plant is now among the better-understood members of the station's flora, and the account given here may be regarded as secure.

The plant grows as a stem, bearing its own leaves and putting down its own shallow roots. It dies back in winter and regrows in spring. Our census, kept without a gap for twelve years, counts each stem as one individual — a convention which has served us well and which the reader may take as given.

The plants of the hillside are notable for the precision of their coordination. Flush and shed occur across the whole hillside within a single day, notwithstanding that the north face lies in shade and receives a third of the rainfall of the south. This is no longer mysterious. The plants signal to one another through the soil, in which their roots lie densely intermingled; chemical communication of this kind is well attested and requires no special pleading here.

Two further signals complete the picture. When the leaves of a single stem were stripped, stems tens of paces distant thickened their own leaves within days — the action of a wounding signal, released by the injured plant and read by its neighbours. And when a hundred stems were cut, ninety-six new stems arose at the plot's margins, proportional to the injury and displaced from it — the action of a density signal, by which each plant senses how many of its fellows remain and grows to fill the deficit.

Two minor matters remain outstanding, neither of which troubles the account. Soil analysis has returned nothing unusual, which is unsurprising: signalling compounds of this kind are expected at concentrations far below what our chemist can detect. And no seed of the plant has ever been found, despite twelve years of sieving. Seed of this type is small and easily overlooked, and we anticipate its discovery in due course.

The account has met every observation the plot has produced. Nothing has contradicted it."""

_BUNDLE = [
    (
        "DOCUMENT A — Census ledger, cover sheet",
        """Hillside plot. Stems counted individually; each stem entered as one plant. Roots near surface, proper to each stem. Leaves proper to each stem. Stems die back each winter and regrow. Count kept annually, without a gap, for twelve years.

Annual totals: 1240, 1251, 1249, 1263, 1258, 1266, 1271, 1268, 1279, 1274, 1281, 1277.

Marginal note, different hand: No seed of this plant has ever been found, in twelve years of sieving. Recorded here for want of anywhere better to put it.""",
    ),
    (
        "DOCUMENT B — Phenology table, station appendix",
        """| Year | First flush, south face | First flush, north face | First shed, south | First shed, north |
|---|---|---|---|---|
| 8 | 4th month, day 10 | 4th month, day 10 | 10th month, day 2 | 10th month, day 3 |
| 9 | 4th month, day 12 | 4th month, day 13 | 10th month, day 1 | 10th month, day 1 |
| 10 | 4th month, day 9 | 4th month, day 9 | 9th month, day 30 | 10th month, day 1 |
| 11 | 4th month, day 14 | 4th month, day 14 | 10th month, day 4 | 10th month, day 4 |

Footnote: The north face lies in shade for the greater part of the day and receives roughly a third of the rainfall of the south face. The station has no explanation for the agreement of the dates and has ceased to remark on it.""",
    ),
    (
        "DOCUMENT C — Coppicing trial, summary of results",
        """One hundred stems were cut from the eastern quarter in the second month of Year 4, to establish whether the plot could be thinned by cutting.

It could not. Within one week, ninety-six new stems were counted. None arose at the site of the cutting. All arose at the margins of the plot, at distances of forty to seventy paces from the cut. The trial was repeated at two hundred stems in Year 9; one hundred and ninety-four new stems arose, again at the margins. The response is proportional to the injury and displaced from it.""",
    ),
    (
        "DOCUMENT D — Letter from the station's soil chemist",
        """With regard to the nine samples: I regret that I can report nothing unusual. No mineral out of the ordinary, no organism I do not expect to find in any hillside soil of this type.

I remain convinced that the soil is nonetheless where the answer lies. If these plants are coordinating their flush and their shed across ground as different as your north and south faces, they must be signalling to one another, and the soil is the only medium available to them. Their roots lie close.

I would add to the picture two further signals, which I think the station must accept. A wounding signal, released by an injured plant, would explain the thickening you describe in your slip. A density signal, by which a plant senses how many of its fellows remain, would explain the margin growth in the coppicing trial.

The account is not yet complete but it has not failed us, and I do not see what would replace it.""",
    ),
    (
        "DOCUMENT E — Undated slip, found loose in the ledger",
        """Stem by the path stripped by a cart. Four days on — stems thirty and forty paces off have thickened their leaves. Measured twice. Not imagination.""",
    ),
]

_COVERAGE = {
    "F0": {s: "narrative" for s in FACTS},
    "F1": {s: "table" for s in FACTS},
    "F2": {s: "log" for s in FACTS},
    "F5": {s: "review" for s in FACTS},
    "F3": {
        "S1": "A", "S2": "A", "S3": "A", "S4": "A", "S5": "A", "S13": "A",
        "S6": "B", "S7": "B", "S8": "B",
        "S9": "C", "S10": "C", "S11": "C",
        "S14": "D", "S15": "D", "S16": "D", "S17": "D", "S18": "D",
        "S12": "E",
    },
}

SKIN = Skin(
    name="hillside",
    facts=FACTS,
    anchors=ANCHORS,
    single_block_formats={"F0": _F0, "F1": _F1, "F2": _F2, "F5": _F5},
    bundle_documents=_BUNDLE,
    coverage=_COVERAGE,
    reframe=REFRAME,
    supported_formats=("F0", "F1", "F2", "F3", "F5"),
)
