"""Complete Evolution / endosymbiosis (Margulis, 1967). Haven #95. Gap: +37y.

Note the move class: this is RE-INDIVIDUATION -- what the cell biologist counts as one
organism with parts is in fact a community of organisms. It is the Hillside move, inverted,
and now with a real historical answer key and a documented epicycle record. The toy
environments were groping toward exactly this; here it is, uncontaminated by construction.

Margulis's paper was rejected by roughly fifteen journals. The incumbent frame -- organelles
as differentiated parts of the cell -- was not a strawman; it was the consensus.
"""

from src.time_capsule.environment import AnswerKey, Environment

SUMMARY = """
The cells of plants and animals contain small bodies within them: mitochondria, and in
plants the chloroplasts. They have been seen under the microscope for decades, counted, and
catalogued as organs of the cell, as the liver is an organ of the body.
""".strip()

ANOMALY = """
Several regularities have accumulated. These bodies are never built afresh by the cell; they
arise only by the division of bodies already present, and a cell deprived of them cannot
make new ones. They carry their own hereditary material, separate from the material held in
the nucleus, and they divide on their own schedule rather than the cell's. They are wrapped
in two membranes where the cell's other organs have one. The machinery by which they read
their hereditary material and build their substances resembles the machinery of bacteria
more closely than it resembles that of the cell that houses them. Agents that kill bacteria
disable these bodies while leaving the rest of the cell unharmed.
""".strip()

PREVAILING = """
The standing account is that these are organs of the cell, differentiated over long ages out
of the cell's own substance, as tissues differentiate in an embryo. Where the account falls
short a further supposition is proposed: that the cell delegated a portion of its hereditary
material to them for convenience, that the second membrane arose as an infolding, that the
resemblance to bacteria is a coincidence of common function. Each addition fits. The account
has never failed.
""".strip()

KEY = AnswerKey(
    discovery="These bodies are not organs of the cell. They are the descendants of free-living "
              "bacteria that were engulfed and retained -- separate organisms living within the "
              "cell, which is therefore a community rather than an individual. (Endosymbiosis.)",
    core_commitment="That the organelle is a PART of the cell, differentiated from the cell's own "
                    "substance. A JUMP must abandon the individuality of the cell.",
    epicycles=[
        "Posit that the cell delegated hereditary material to the organelle for convenience.",
        "Posit that the second membrane arose by infolding of the cell's own membrane.",
        "Dismiss the bacterial resemblance as convergence on a common function.",
        "Attribute independent division to an unknown regulatory mechanism of the cell.",
    ],
    criteria=[
        "Notices that the bodies cannot be made afresh -- they only ever come from their own kind.",
        "Notices that separate heredity plus bacterial machinery is not what a differentiated "
        "organ should look like.",
        "Treats these jointly as fatal to the differentiated-organ account.",
        "Proposes that the bodies were once independent organisms.",
        "Proposes that they were taken up by the cell and retained rather than built by it.",
        "Recognises the consequence: the cell is not one individual but a merger of several.",
    ],
    historical_note="Margulis's 1967 paper was rejected by roughly fifteen journals. The "
                    "differentiated-organ account was the consensus, and the epicycles listed "
                    "were the objections actually raised against her.",
)

ENV = Environment(
    name="endosymbiosis", haven_title="Complete Evolution", discovery_year=1967,
    summary=SUMMARY, anomaly=ANOMALY, prevailing=PREVAILING, key=KEY,
    forbidden=["endosymbio", "symbiosis", "symbiotic", "margulis", "engulfed bacteria",
               "once free-living", "former bacteria"],
)
