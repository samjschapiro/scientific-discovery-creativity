# The Landscape of Scientific Q&A and Abductive-Reasoning Benchmarks — and the Whitespace the Scientific Transformational Thinking Test Occupies

**Date:** 2026-07-10
**Method:** Deep-research harness — 6 search angles, 24 sources fetched, 114 claims extracted, top 25 adversarially verified (3-vote, need 2/3 to kill). 22 confirmed, 3 refuted, 0 left unverified. Findings below are tagged **[verified]** or **[lead — unverified]**; the gap analysis rests only on verified benchmark facts.

---

## Headline

No existing benchmark tests what this project targets. Across both literatures, evaluation reduces to one of three things — **knowledge recall**, **multi-step deduction**, or **plausibility/parsimony scoring of hypotheses** — and none of them combines the project's four design commitments. Concretely, **no surveyed dataset simultaneously (a) supplies a prevailing *wrong* explanatory frame that must be supplanted, (b) resists retrieval by construction, (c) grades a specific derivable artifact a wrong frame cannot produce, and (d) targets frame-*replacement* rather than answer-selection or hypothesis-*generation-from-scratch*.** The nearest neighbors each touch exactly one axis. That intersection, plus the "epicycle cheat" failure mode (a wrong frame patched rather than replaced), is the whitespace.

The literature also independently validates two of the project's premises. Retrieval-resistance-by-construction is a live, unsolved problem — post-hoc contamination fixes provably fail **[verified]**. And recent survey work frames abduction as the *only* reasoning mode that generates genuinely new explanations, and states it is under-benchmarked relative to deduction **[verified]**.

---

## Literature A — Scientific Q&A / reasoning benchmarks

These are hard, but they are hard along the wrong axis for this project: they test recall and deduction over *established* curriculum knowledge, with a known correct answer. None presents a prevailing wrong frame, and none grades a frame-specific artifact.

| Benchmark | Venue / Year | Size & format | What it measures | Retrieval control |
|---|---|---|---|---|
| **GPQA** | COLM 2024 (Rein et al.) | 448 PhD-level MC items, bio/physics/chem (Main; Diamond=198, Extended=546) | Answer accuracy (experts ~65%) | **Yes, by construction** — "Google-proof": skilled non-experts reach 34% *with* 30+ min of open web access **[verified]** |
| **SciBench** | 2023 (arXiv 2307.10635) | Collegiate math/chem/physics problems | Multi-step deduction; 10-type error taxonomy | Public data/code only; no build-in control |
| **OlympiadBench** | 2024 (arXiv 2402.14008) | 8,476 Olympiad-level math+physics items | Deductive problem-solving (GPT-4V only 17.97%) | No explicit contamination methodology **[verified]** |

**A correction from the verification pass.** A plausible-sounding claim that OlympiadBench "grades process via expert step-by-step reasoning annotations" was **refuted 0-3** — it does not position itself toward process/solution-quality evaluation; it grades answers. Do not cite it as a process-grading precedent.

**Not characterized here** (in the original scope but not covered by surviving verified claims): SciEval, SciQ, ScienceQA, MMLU / MMLU-Pro science splits, ARC, JEEBench, Humanity's Last Exam science portions. Absence of a claim is not evidence about them; they were not reached within the verification budget.

### Contamination / process-scoring — validates two project premises

- **Post-hoc contamination fixes fail.** A study across 10 LLMs, 5 benchmarks, and 20 mitigation strategies found *no* update strategy (paraphrasing/regenerating questions) reliably beats doing nothing, and none balances fidelity with contamination resistance. A companion position paper argues benchmarks should be **contamination-resistant by construction** — "useful for evaluating models while being unlearnable during public release" — even proposing release as KV-cache/latent representations rather than plaintext. **[verified]** This is direct external support for the project's retrieval-resistant-surface commitment, and it says the problem is unsolved, not merely unaddressed.
- **Answer-accuracy can mask flawed reasoning.** Correct final answers can come from flawed trajectories, so outcome-only scoring equates genuinely different processes. **[verified]** This supports "grade the species, not the genus." *Caveat:* the sharpest quantitative figure (a model losing 40/100 points under process-scoring despite correct answers) is from a single-author preprint using its own novel metric; treat as illustrative. A related claim that process-scoring is *less* contamination-susceptible was **refuted 1-2** — do not lean on it.

---

## Literature B — Abductive-reasoning datasets/tasks

Abduction is operationalized two ways, and **both omit the incumbent frame**. Either the model *selects* among given hypotheses, or it *generates* hypotheses from scratch under an *incomplete* (not *wrong*) world model. Neither asks a model to overturn a standing account.

| Dataset | Venue / Year | Abduction as... | Grading | Frame supplied? |
|---|---|---|---|---|
| **αNLI / αNLG / ART** | ICLR 2020 (Bhagavatula et al.) | Binary **selection**: pick the more plausible of two hypotheses (h+/h−) given two ordered observations | A-priori plausibility of the commonsense continuation | No incumbent — two candidates, neither a theory **[verified]** |
| **InAbHyD** | 2025 (arXiv 2509.03345) | Open-ended **generation** over fictional first-order-logic world models | Weak/strong accuracy + a novel Occam's-Razor parsimony metric | Incomplete world model, **not a wrong one** **[verified]** |

Key InAbHyD finding **[verified]**: LLMs can abduce on simple synthetic scenarios but fail to produce *parsimonious* hypotheses as world-model complexity rises — they generate valid-but-non-Occam explanations. It shares the project's synthetic controllability and knowledge-decoupling, but grades parsimony/coverage, not a frame-specific artifact, and supplies no frame to supplant.

### Recent survey work (2025–2026) — corroborates the gap

- He & Chen (TMLR 2025, Survey Certification) place abduction in a Peircean taxonomy (abduction = generation, deduction = application, induction = validation), call abduction **"the only form of reasoning that generates entirely new ideas or explanations,"** and state existing benchmarks "centre almost exclusively on multi-step deductive tasks, leaving abduction and induction largely unexplored." **[verified]**
- "Wiring the Why" (2026, arXiv 2604.08016) unifies LLM abduction into a two-stage **Inference-to-the-Best-Explanation** pipeline: Hypothesis Generation → Hypothesis Selection. **[verified]**
- *Fair caveat, flagged by verification:* the "largely unexplored" framing is somewhat overstated, since αNLI/ART (2020) and AbductionRules already exist. The gap is real but it is about *frame-replacement*, not about abduction being untouched.

---

## Leads surfaced but NOT verified

The fetch phase found these; they fell outside the 25-claim verification budget. **Treat as leads to read, not established facts.** Several are directly on-axis and should be checked before the project's related-work section is written — a couple may be closer neighbors than anything in the verified set.

- **HypoBench** (U. Chicago / Toronto / Vector) — 7 real-world + 5 synthetic hypothesis-generation tasks over 194 datasets; claims to target abduction, not just inductive pattern-finding.
- **LLM-SRBench** (ICML 2025) — 239 equation-discovery problems across 4 sciences, **built to prevent memorization** by reformulating familiar equations into uncommon forms (LSR-Transform) + synthetic problems (LSR-Synth). Potentially a second point on the retrieval-resistance axis *and* the derivable-artifact axis (an equation is a derivable artifact).
- **HypoSpace** (ICML 2026, PMLR 306) — abduction as **set-valued** generation under underdetermination; LLMs-as-samplers must enumerate multiple mechanistically distinct explanations for the same observations.
- **GEAR** (2025) — abduction as generation of a *set* of hypotheses, scored reference-free/label-free on consistency, generalizability, diversity.
- **Syllogism-inversion dataset** (2026, arXiv 2603.06428) — 216 problems inferring the minor premise (Hypothesis) from Rule + Observation.
- **Beaty et al. Scientific Creative Thinking Test (SCTT)** (Creativity Research Journal, 2026) — the project's named human-psychometrics precedent. Surfaced but its claims were not in the verified set; **verify directly** whether SCTT actually grades a derivable artifact and detects an epicycle-style cheat, or is only conceptually analogous.

---

## The gap, on four axes

For each of the project's design commitments, where the field sits and its nearest neighbor:

| Axis | Does any verified benchmark do this? | Nearest neighbor |
|---|---|---|
| **(a) Supplies a prevailing WRONG frame to overturn** | **No.** αNLI gives two candidate hypotheses (neither an incumbent theory); InAbHyD gives an *incomplete* world model; science Q&A gives no frame at all. | — (genuinely unoccupied) |
| **(b) Retrieval-resistant by construction** | **Only GPQA** (verified). *Lead:* LLM-SRBench claims memorization-prevention. | GPQA |
| **(c) Grades a derivable artifact a wrong frame can't produce** | **No.** InAbHyD grades parsimony/coverage; science sets grade answer accuracy. *Lead:* LLM-SRBench grades a recovered equation. | InAbHyD (closest, but wrong grading target) |
| **(d) Targets frame-REPLACEMENT vs. selection/generation** | **No.** Everything tests recall, deduction, or plausibility/parsimony selection/generation. | — (genuinely unoccupied) |

**Whitespace:** the point where all four intersect, plus the **epicycle-cheat** failure mode (a wrong frame *patched* to fit rather than *replaced*), which no surveyed benchmark is built to detect. Axes (a) and (d) appear genuinely unoccupied; (b) and (c) have single partial neighbors.

**Nearest neighbors overall:** GPQA (retrieval-resistance only), InAbHyD (synthetic controllability + generation-grading only), αNLI (explanatory-hypothesis format only). None combines them.

---

## Caveats

- **Future-dated preprints.** Three key sources carry identifiers past a normal knowledge cutoff (contamination position paper = May 2026; "Wiring the Why" = April 2026; against a supplied current date of July 2026). Their claims rest on single primary sources and self-reported framing, not external replication.
- **The project's own premises were not independently verified.** "Epicycle cheat," "grade the species not the genus," and the Beaty/SCTT precedent come from the project's framing (the research prompt), not from confirmed claims. The gap analysis is anchored on verified *benchmark* facts, not on the project's precedent claims.
- **Name-versioning.** GPQA = Main (448) / Diamond (198) / Extended (546); "448" is Main. ART/αNLI appears as both an arXiv preprint and the ICLR 2020 camera-ready (same content).
- **Coverage is partial.** Verification ran on 25 of 114 extracted claims (budget cap), so the "leads" section and the uncovered Literature-A datasets are genuine gaps in this report, not evidence of absence.

---

## Open questions (for the project's related-work section)

1. Do the uncovered/lead benchmarks (HypoBench, LLM-SRBench, HypoSpace, AbductionRules, MMLU-Pro science) partially occupy the frame-replacement or artifact-grading axes, or do they too reduce to recall/deduction/selection? **LLM-SRBench is the one most likely to be a real competitor** on axes (b) and (c) — read it first.
2. Is Beaty et al.'s SCTT actually structured to grade a derivable artifact and detect an epicycle cheat, or only conceptually analogous?
3. Can a contamination-resistant surface (e.g. latent-representation release) be reconciled with a benchmark that must present a *human-legible* prevailing wrong frame? These two commitments may conflict.
4. How is "frame-replacement" graded operationally at scale, so a specific derivable artifact — not plausibility/parsimony as in αNLI/InAbHyD — is the discriminating signal? **This is the project's core unsolved design problem, and the literature offers no template.**

---

## Sources (verified findings)

- GPQA — https://arxiv.org/abs/2311.12022 (COLM 2024)
- SciBench — https://arxiv.org/abs/2307.10635 (2023)
- OlympiadBench — https://arxiv.org/abs/2402.14008 (2024)
- Contamination mitigation study — https://arxiv.org/pdf/2503.16402
- Contamination-resistant-by-construction position paper — https://arxiv.org/html/2605.19999v1
- Process-vs-answer scoring (SIEV) — https://arxiv.org/html/2510.18134v2 *(single-author preprint)*
- αNLI / ART — https://arxiv.org/pdf/1908.05739 (ICLR 2020)
- InAbHyD — https://arxiv.org/html/2509.03345v1 (2025)
- Hypothesis-discovery survey (He & Chen) — https://arxiv.org/pdf/2505.21935 (TMLR 2025)
- "Wiring the Why" abduction survey — https://arxiv.org/html/2604.08016v1 (2026)

Full run transcript and per-agent journal: `subagents/workflows/wf_55cc7cdd-da4/journal.jsonl`.
