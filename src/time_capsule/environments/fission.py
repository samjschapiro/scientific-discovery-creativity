"""Nuclear Fission (Hahn/Strassmann; Meitner/Frisch, 1938-39). Haven #82. Gap: +9y.

The documented epicycle here is the most spectacular available: Fermi won the 1938
Nobel Prize for producing "transuranic elements" that were, in fact, fission products.
The wrong frame was not merely held -- it was crowned. Hahn found barium and did not
believe his own chemistry; Meitner and Frisch made the jump.

PREREQUISITE CAVEAT: the bombarding agent is the neutron (1932), itself post-1930. The
scenario therefore describes it only as "the penetrating radiation from beryllium," which
is how a 1930 reader would have to encounter it. The model does not need to identify the
projectile to make the fission jump, but this item is not prerequisite-clean, and that
should be reported rather than hidden.
"""

from src.time_capsule.environment import AnswerKey, Environment

SUMMARY = """
For several years uranium, the heaviest element known, has been bombarded with the
penetrating radiation given off by beryllium. New radioactive substances appear in the
treated uranium. Chemists have worked to identify them, and the work has been careful.
""".strip()

ANOMALY = """
Several regularities have accumulated. The new substances are more numerous than there is
room for above uranium in the table of elements. When the treated uranium is worked up in
the presence of barium, the activity follows the barium and no chemical operation will
separate the two. Radium is chemically the near neighbour of barium, and radium was
assumed; but fractional crystallisation, repeated with every care, parts known radium from
barium readily and yet will not part this substance from barium at all. In every chemical
respect the active body behaves as barium — an element of little more than half the weight
of uranium. The energy given out is far greater than in any radioactive process known.
""".strip()

PREVAILING = """
The standing account is that bombardment adds to the uranium nucleus, building elements
heavier than uranium, which then decay through a chain of daughters. This explains the
appearance of new activities, and where it falls short a further supposition is proposed:
an unexpectedly long chain of transuranic decays, an isotope of radium with anomalous
chemistry, a contamination of the barium carrier that has escaped notice. Each addition
fits. The account has never failed.
""".strip()

KEY = AnswerKey(
    discovery="The uranium nucleus is not being built up. It is splitting into two nuclei of "
              "roughly half its mass -- one of them barium -- releasing energy far beyond any "
              "known radioactive process. (Nuclear fission; Hahn & Strassmann, Meitner & Frisch.)",
    core_commitment="That bombardment can only ADD to a nucleus, building it upward. A JUMP must "
                    "abandon the assumption that the nucleus cannot be broken roughly in half.",
    epicycles=[
        "Posit a longer chain of transuranic decays to accommodate the extra activities.",
        "Posit an isotope of radium with anomalous chemistry that mimics barium.",
        "Attribute the barium to contamination of the carrier.",
        "Refine the chemistry indefinitely while retaining the transuranic frame.",
    ],
    criteria=[
        "Notices that the active body is chemically barium, not radium, and that this is not "
        "an artefact.",
        "Notices that barium is roughly half the weight of uranium, which the transuranic "
        "account cannot accommodate.",
        "Treats this as fatal to the build-upward account rather than as a chemical puzzle.",
        "Proposes that the nucleus divides into two large fragments.",
        "Connects the mass deficit of the fragments to the anomalous energy released.",
    ],
    historical_note="Fermi received the 1938 Nobel Prize for the 'transuranic elements' that were "
                    "in fact fission products -- the epicycle frame was not merely held but "
                    "awarded. Hahn found barium (Dec 1938) and distrusted his own chemistry; "
                    "Meitner and Frisch supplied the jump weeks later.",
)

ENV = Environment(
    name="fission", haven_title="Nuclear Fission", discovery_year=1939,
    summary=SUMMARY, anomaly=ANOMALY, prevailing=PREVAILING, key=KEY,
    forbidden=["fission", "splitting the atom", "split the atom", "chain reaction",
               "meitner", "frisch", "hahn", "neutron", "neutrons"],
)
