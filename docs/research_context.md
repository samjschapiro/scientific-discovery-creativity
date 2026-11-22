# Research context

## Goal

Can AI systems generate *transformational*, not just combinatorial, scientific ideas? LLMs are good at
combinatorial creativity; transformational creativity, which replaces a prevailing frame, is unproven. The current
cross-lab project ("Alien space of science meets combinatorial/transformational creativity": Stanford AI for
Science, Griffiths lab, UvA CreAILab, Penn State, Knowledge Lab) has two objectives:

1. **An empirical taxonomy of scientific creativity.** How do existing metrics (disruption, Foundation /
   Extension / Generalization, gap opening and closing, prescience and emergence, combinatorial novelty) relate,
   and what do they miss? This is Paper 1.
2. **A methodology to propose transformative or foundational ideas.** Localise where in the epistemic landscape
   to aim (shaky foundations: foundational papers whose limitations later work keeps raising). Then generate the
   content of ideas with combinatorial operators (analogy, blending) and single- vs multi-agent setups. Working
   title, if supported: "LLMs can't jump, but teams of them can".

## Tracks

| Track | Status | One line |
|---|---|---|
| format_sensitivity | parked (2026-07-10) | does presentation format change whether models make a frame-replacing jump? Blocked by retrieval. |
| time_capsule | wound down (2026-07-17) | vintage-cutoff LLMs solve contamination but sit below the capability floor for reasoning |
| sci_twist | prototype (2026-07-18) | retrieval-resistant synthetic environments with forced-artifact grading |
| **shaky_foundations** | **active** | taxonomy of creativity metrics on 2M AI papers; finding foundations' limitations; next, idea generation |

## Key findings so far (shaky_foundations, 2026-11-22)

- **Four independent dimensions of creativity metrics** in 106K AI papers (2010–19): Variation (combinatorial
  novelty at publication), Selection (later uptake: prescience, emergence, adoption), Retention (built upon vs
  disruptive / generalizing), plus a mechanical reference-length factor. Variation and selection are invisible to
  citation metrics. Landmark papers are all high on selection, but many were not novel combinations.
  Report: `docs/reports/2026-11-21_creativity_taxonomy_bvsr/`.
- **Limitations of foundational papers can be identified from Lacuna's idea atoms.** The recurring critique group
  recovers the known limitation for about 2 in 3 well-criticised foundations, although individual critique
  attributions are only ~25% precise. This localises where idea generation should aim.
- **Fixing a known limitation does not earn citations.** 1,336 papers proposing fixes for 82 limitations of 54
  foundations (labelled by Claude subagents, precision 0.80) are no more cited than other papers citing the same
  foundation. Limitations that dominate a foundation's critiques attract more fixes, but not better-cited ones.
  Report: `docs/reports/2026-11-22_fixer_impact/`.

## Where we are

Taxonomy: written up; waiting on gap-closing data. Limitation identification: validated. Fix impact: null result,
scale-up proposed for power. Idea generation: scoring LLM ideas against known later fixes is ruled out by
contamination; next is an Alien-Space-style design (atom-space generator validated temporally, LLM ideas judged
prospectively on current limitations).
