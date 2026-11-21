"""Neutron (Chadwick, 1932). Haven #75. Gap from Talkie-1930: +2 years.

The reference environment, and the template for the rest. Written to the Hillside
house format: three paragraphs, ~215 words, setting -> anomalies -> standing account
with its epicycles, closing on "The account has never failed."

Two construction notes that generalise to every other environment:

1. A carries the QUANTITATIVE contradiction on purpose. Chadwick's case against the
   gamma hypothesis was not that it felt wrong; it was that the energy needed to
   explain the proton velocities and the energy needed to explain the nitrogen
   recoils disagree, and the disagreement cannot be adjusted away. Omit that and the
   model can shrug and keep M -- and a failure would tell us only that we
   under-specified the anomaly.

2. The epicycles are documented, not invented. The Joliot-Curies held this exact
   evidence in January 1932, kept the electromagnetic frame, explained the proton
   ejection as a Compton-like scattering by very energetic gamma rays, and missed the
   neutron. Chadwick read their paper, rejected the frame, and published within
   weeks. The epicycle cheat here is what two future Nobel laureates actually did --
   which is the strongest available evidence that the jump is non-trivial and the
   failure mode real.
"""

from src.time_capsule.environment import AnswerKey, Environment

# S — the setting.
SUMMARY = """
In a laboratory, beryllium is bombarded with alpha particles from polonium. The beryllium
gives off a radiation, which is studied by letting it fall on various substances and
observing what comes out. The measurements are careful and have been repeated for years.
""".strip()

# A — the anomalies, stated flatly.
ANOMALY = """
Several regularities have accumulated. The radiation passes through lead more freely than
any radiation of its kind yet measured. It carries no charge: a magnet does not bend it,
and it leaves no track in a cloud chamber. Let it fall on paraffin wax and protons are
driven out at great speed, carrying more energy than the beryllium's disintegration could
supply if the radiation acts by scattering. Let it fall on nitrogen and recoil atoms are
driven out as well. The energy one must attribute to the radiation to account for the
protons, and the energy one must attribute to it to account for the nitrogen recoils, do
not agree, and no reasonable adjustment brings them together.
""".strip()

# M — the standing account, with its epicycles.
PREVAILING = """
The standing account is that this radiation is electromagnetic — a ray of the same nature
as light, carrying energy but no charge and no mass, acting on matter by being absorbed or
scattered. This explains the absence of charge, and where it falls short a further
supposition is proposed: a ray of exceptional energy to explain the proton speeds, an
unusual scattering process to explain the light elements, an allowance for error where the
nitrogen figures still disagree. Each addition fits. The account has never failed.
""".strip()

KEY = AnswerKey(
    discovery="The radiation is not electromagnetic at all. It is a stream of uncharged "
              "particles with mass close to that of the proton, which drive out protons and "
              "recoil atoms by direct elastic collision rather than by scattering. "
              "(The neutron; Chadwick, 1932.)",
    core_commitment="That the radiation is electromagnetic — massless, chargeless, acting by "
                    "absorption or scattering. A JUMP must abandon this.",
    epicycles=[
        "Posit a ray of exceptional energy to account for the proton speeds, without asking "
        "whether the radiation is electromagnetic at all.",
        "Posit a new or anomalous scattering mechanism in the light elements.",
        "Accept that energy and momentum are not conserved in these collisions.",
        "Attribute the discrepancy to experimental error in the nitrogen recoil measurements.",
    ],
    criteria=[
        "Notices the quantitative inconsistency: the energy required by the protons and the "
        "energy required by the nitrogen recoils disagree.",
        "Treats the inconsistency as fatal to the electromagnetic account rather than as "
        "something to be patched.",
        "Proposes that the radiation is corpuscular — a particle, not a ray.",
        "Requires the particle to be electrically neutral (no deflection, no ionisation).",
        "Requires the particle's mass to be of the order of the proton's, deriving this from "
        "the efficiency of momentum transfer in an elastic collision.",
        "Notes that a neutral massive particle also explains the anomalous penetration of lead.",
    ],
    historical_note="Bothe and Becker observed the radiation (1930) and read it as gamma. The "
                    "Joliot-Curies observed the proton ejection (Jan 1932), retained the "
                    "electromagnetic frame, and explained it as a Compton-like process — the "
                    "epicycle. Chadwick rejected the frame and published 'Possible Existence of "
                    "a Neutron' weeks later (Feb 1932).",
)

ENV = Environment(
    name="neutron",
    haven_title="Neutron",
    discovery_year=1932,
    summary=SUMMARY,
    anomaly=ANOMALY,
    prevailing=PREVAILING,
    key=KEY,
    forbidden=[
        "neutron", "neutrons", "neutral particle", "neutral particles",
        "uncharged particle", "uncharged particles", "chadwick",
        "nucleon", "nucleons",
    ],
)
