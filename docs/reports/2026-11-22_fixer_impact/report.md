# Does Fixing a Foundation's Known Limitation Pay Off? A Null Result and a Hypothesis

*Shaky-foundations track, 22 November 2026. Exploratory analysis for the cross-lab project "Alien space of
science meets combinatorial/transformational creativity", prompted by Alejandro Artiles's question of whether
papers that address shaky foundations end up impactful.*

## Abstract

Most influential AI methods have limitations that later papers repeatedly point out, and many later papers
propose fixes. If fixing a foundation's known limitation reliably earned recognition, the limitations we can
already detect would be a direct map of where impactful ideas lie. We test this on 54 highly cited AI papers
from 2010 to 2019 ("foundations") and 82 of their known limitations. We find papers that propose a fix and
compare their citations with other papers citing the same foundation. A Claude-based judge labels fixers with
precision 0.80 and recall 0.92 against hand labels, which makes this possible at scale. **On average, fixing
a known limitation earns nothing.** The 1,336 fixer papers sit 1.0 percentile points *below* other papers
citing the same foundation in the same year (95% CI −3.1 to +1.0). They are indistinguishable from papers that
state the same limitation without fixing it (+0.3, CI −3.3 to +3.9). An exploratory follow-up suggests the
payoff may depend on whether the field agrees on what is wrong: fixers of the third of foundations whose
critiques are most scattered do worst (−5.1 points). This is not statistically reliable (rank correlation
0.27, permutation p = 0.056), so we offer it as a hypothesis for a pre-specified test, not a finding.

## 1. Introduction

**Context.** A recurring idea in the science of science is that progress comes from repairing the weak points
of dominant frameworks. In Kuhn's account, anomalies accumulate against a paradigm until a replacement
absorbs them (Kuhn, 1962). In our earlier work on this track, we showed that the critiques later papers raise
against a foundation can be recovered from LLM-extracted "idea atoms" in the Lacuna corpus. For foundations
with at least 20 attributed critics, the limitation we expected appears among the top three critique groups
for 64% of foundations (progress notes, 2026-11-21). That gives us a map of known weak points. The natural
next question, raised by Alejandro, is whether this map has predictive power for impact: **do papers that
address a foundation's known limitation end up more cited?**

**What we already knew.** Papers that merely *critique* a foundation are barely more cited than matched
papers (about +3 percentile points of total citations; no difference in disruption). Most of their raw
advantage is selection: citing famous work goes with being in popular areas (progress notes, 2026-11-21). But
critiquing is not fixing. Testing fixers had been blocked on labelling: a fix often does not blame the
foundation in its text. We had hand-judged only 146 critics of two foundations (Transformer and VGG).

**What we did.** For each known limitation, we rank every later paper citing the foundation by how closely the
problem it says it tackles matches that limitation. The top 30 per limitation go to a judge. The judge is 16
Claude subagents running inside the analysis session, with no external API. It decides whether each paper
proposes its own fix, applies an existing one, only states the problem, or addresses something unrelated. We
then compare citation percentiles within foundation and year.

**Contributions.**

- **Fixers can be labelled at scale.** The Claude judge agrees with hand labels on 85 blind validation items:
  precision 0.80 and recall 0.92 for "proposes a fix" (Section 2).
- **Fixing does not pay on average (null result).** Fixers are not more cited than other citers of the same
  foundation (−1.0 [−3.1, +1.0]). Nor are they more cited than papers that state the same limitation without
  fixing it (+0.3 [−3.3, +3.9]). The intervals rule out an average advantage larger than about 4 percentile
  points (Section 3, Figure 1).
- **A hypothesis, not a finding.** The payoff may depend on whether critics agree on the problem. Fixers of
  foundations with the most scattered critiques do worst, but the rank correlation is 0.27 with permutation
  p = 0.056 across 51 foundations. The pattern is a step at the low end, not a steady dose-response (Section
  4, Figure 2).

**Why it matters.** For the project's idea-generation goal, the null result is useful. Pointing a generator
at a foundation's known limitation and asking for a fix is not, by itself, a recipe for impact. The fix
literature is large, mostly incremental, and on average unremarkable. If anything distinguishes the fixes
that matter, it lies elsewhere. Candidates are whether the field already agrees the problem is central
(Section 4), and how far the fix departs from the foundation's frame, which this analysis does not measure.

## 2. Finding fixers

### 2.1 Foundations and limitations

We use the gold set of foundation limitations (`configs/shaky_foundations/gold_limitations.yaml`). It covers
62 foundations from the 500 most-cited 2010–2019 papers in Lacuna, each with one or two limitations phrased
the way a citing paper would state them, for example "self-attention has quadratic time and memory cost in
sequence length". Excluding reviews and position papers leaves **54 foundations and 82 limitations**. The gold
set was written by Claude from background knowledge before looking at pipeline output for the test
foundations. The team has not yet reviewed it.

### 2.2 Candidates

For each limitation we take every paper citing the foundation from the year after its publication through
2022. Stopping at 2022 leaves at least three years of citations before the 2025 counts. Lacuna gives each
paper LLM-extracted atoms. We use the atoms describing what the paper sets out to solve: types *problem* and
*limitation* in the *problems and motivation* lens.

Each citer is scored by the highest cosine similarity between the limitation text and any of these atoms,
using bge-large-en-v1.5 embeddings. A cheap concept-centroid score first shortlists the 3,000 closest atoms;
those are then re-scored with their real embeddings. The centroid score alone produces large ties: 28 GAN
citers shared one concept.

Unlike our critique attribution, this does not require the paper to blame the foundation, so fixes that
simply state the problem are reachable. The top 30 papers per limitation (2,460) plus 69 extra validation
items give **2,529 candidates**. A typical limitation has about 1,050 citers with problem atoms, so the top 30
are papers framed around that limitation.

### 2.3 The judge

Each candidate is shown to the judge as: the foundation's title, the limitation, the citing paper's title and
year, its two problem atoms closest to the limitation, and up to four of its method atoms. The judge assigns
one of four labels:

| label | meaning |
|---|---|
| fix | proposes its own new method that at least partially addresses this limitation |
| applies_fix | addresses the limitation only by using an existing, named fix |
| mentions | states the limitation, but its contribution does not address it (analysis, benchmark, survey, application, or a fix for something else) |
| unrelated | its problems have nothing to do with this limitation |

The judges were 16 Claude subagents, each labelling about 159 items from text alone, with no web search and
no code-assigned labels. The prompt is in `fixer_candidates_v1/judge_prompt.md`. Labels: fix 1,414, mentions
498, unrelated 546, applies_fix 71.

### 2.4 Validation

We mixed in the 85 hand-judged critics of the Transformer (quadratic cost) and VGG (vanishing gradients;
parameter count) that fall in the candidate window. The judges did not know which items these were.

| hand label \ judge | fix | applies_fix | mentions | unrelated |
|---|---|---|---|---|
| fix (53) | 49 | 3 | 1 | 0 |
| not fix (32) | 12 | 2 | 16 | 2 |

**Precision is 0.80 and recall 0.92** for "fix". The judge is lenient: 12 of the 32 papers judged as non-fixes
by hand were called fixes. This is consistent with the prompt's rule that partial and domain-specific fixes
count. The hand labels were also made by Claude, in an earlier session from a different view of each paper,
so this measures consistency, not agreement with human experts. Validation covers only two foundations.

Random examples of each label are in Appendix B. One labelling problem occurred and was caught. Several
subagents saved a helper script under the same name in a shared folder and briefly read another batch. Each
noticed through the ID check and relabelled. All 2,529 candidates have exactly one label, and in 30 randomly
sampled labels the stated reason matches the paper.

## 3. Fixing does not pay on average

**Outcome.** A paper's citation percentile within its publication year, among all Lacuna papers with atoms
published that year. We use total OpenAlex citations through 2025 (main outcome) and in-corpus Lacuna
citations (secondary). Within-year percentiles remove the advantage older papers have from more time to
accumulate citations.

**Comparisons.** Two baselines, from loosest to strictest:

1. *Premium over same-foundation citers.* Each paper's percentile minus the mean percentile of all papers
   citing the same foundation in the same year. This removes "this is a popular area".
2. *Fix vs mentions.* Among candidates, all of which state the limitation, we regress percentile on a fix
   indicator with foundation and year indicators and log reference count. This compares fixers with papers
   equally focused on the same problem.

Confidence intervals come from 1,000 bootstrap resamples of whole foundations. Each paper counts once per
foundation, with its most fix-like label.

![Citation premium by label](../../../data/shaky_foundations/figures/fixer_impact_v2_premium_by_label.png)

*Figure 1. Fixers are not more cited than other papers citing the same foundation. The x-axis shows each
group's mean citation percentile minus that of all papers citing the same foundation in the same year, with
95% CIs from a bootstrap over 54 foundations. Total OpenAlex citations through 2025.*

| | total citations | Lacuna citations |
|---|---|---|
| fixers: premium over same-foundation citers (n = 1,336) | −1.0 [−3.1, +1.0] | −0.6 [−2.8, +1.5] |
| fix vs mentions, with foundation and year controls (n = 1,800) | +0.3 [−3.3, +3.9] | +1.4 [−2.3, +4.8] |
| share in their year's top 1%: fix / mentions / unrelated | 5.2% / 8.0% / 6.0% | |
| share in their year's top 10%: fix / mentions / unrelated | 24% / 28% / 24% | 30% / 30% / 27% |

Fixers are an ordinary sample of the papers around a foundation. All candidate groups sit at about the 63rd to
66th percentile, above the median paper, because they cite famous work. Within that, proposing a fix adds
nothing. In the tail, papers that only state the limitation have *more* top-1% hits than fixers, and these
include surveys and benchmarks, which are heavily cited. The result does not depend on the baseline: both
comparisons and both citation sources agree.

**Is this a power problem?** No. With 1,336 fixers across 54 foundations, the intervals exclude an average
advantage larger than about 4 percentile points against either baseline. Any average effect of fixing is
small.

## 4. Exploratory: does it matter whether the field agrees on the problem?

*This analysis was chosen after seeing the main result and is reported as a hypothesis.*

**Idea.** A fix should matter more when the community already agrees the limitation is *the* problem with a
foundation. Linear attention for the Transformer's quadratic cost is the clean example. It should matter less
when critiques scatter across many minor complaints.

**Shakiness measure.** We define a foundation's *shakiness* as the chance that two different randomly chosen
critics raise the same problem. "Same problem" means the same concept in Lacuna's 2,000-concept layer. The
critics are the papers whose critique atoms we attributed to the foundation in the scale-up. The estimate is
Σ m_k(m_k − 1) / (N(N − 1)), where m_k is the number of critics raising concept k and N the number of critics.
This is Simpson's (1949) index in its unbiased form.

We previously used the largest concept's share among 20 randomly subsampled critics, i.e. rarefaction
(Hurlbert, 1971), to avoid small-sample bias. The new measure needs neither subsampling nor a 20-critic
cutoff. It ranks foundations almost identically (Spearman 0.98 where both exist) and shows no dependence on
the number of critics (ρ = 0.07 with log N). It also scores 458 of the top 500 foundations, against 190 under
the old cutoff. We require at least 5 critics, which leaves 51 of the 54 gold foundations.

![Fixer premium vs shakiness](../../../data/shaky_foundations/figures/fixer_impact_v2_dose.png)

*Figure 2. Fixers of foundations with scattered critiques do worse, but the evidence is weak. Each dot is a
foundation: its fixers' mean citation premium over same-foundation citers (y) against its shakiness rank (x).
Dot size is the number of fixers. Black bars show the mean of each third of foundations. Rank correlation 0.27
[−0.00, 0.50], permutation p = 0.056.*

| shakiness measure, minimum critics | foundations | shakier minus less shaky (median split) | Spearman ρ | permutation p |
|---|---|---|---|---|
| agreement, ≥ 5 | 51 | +4.1 [+0.4, +8.0] | 0.27 [−0.00, 0.50] | 0.056 |
| agreement, ≥ 10 | 44 | +3.7 [−0.5, +7.9] | 0.25 [−0.02, 0.51] | 0.096 |
| agreement, ≥ 20 | 32 | +3.5 [−2.0, +8.8] | 0.37 [0.00, 0.62] | 0.040 |
| rarefied top share, ≥ 20 | 32 | +5.0 [+0.0, +10.8] | 0.39 [0.03, 0.66] | 0.031 |

Total citations. Lacuna citations give the same pattern (ρ 0.26 at ≥ 5 critics, 0.43 at ≥ 20).

**Reading.** Every specification points the same way, but none is strong. The best p-value is 0.03, after
trying four specifications. Two further observations argue for caution:

- **It is a step, not a slope.** By thirds of shakiness, fixer premiums are −5.1, +1.6 and −0.2. The least
  shaky third does worse; beyond that, more agreement among critics adds nothing.
- **A few foundations carry much of it.** AdamW (−24) is at the scattered end and FGSM adversarial examples
  (+19) in the middle. Dropping both lowers ρ from 0.27 to 0.23.

The least shaky third includes VGG, BatchNorm, Adam, AdamW, word2vec, DenseNet, DQN and saliency maps. These
are general-purpose tools that attracted many small, incremental fixes. Their negative premiums may reflect
crowded, low-stakes fix literatures rather than a lack of community agreement. The two explanations predict
the same thing here; distinguishing them needs a different measurement (Section 6).

## 5. Limitations

- **"Fix" is broad.** It includes partial and domain-specific fixes; 56% of candidates were labelled fixes.
  Frame-changing fixes such as ResNet or Wasserstein GAN are a handful among 1,336, so the average describes
  the typical fix, not the transformative one. The null result does not show that *important* fixes go
  unrewarded.
- **Candidates are not all fixers.** We judge only the 30 papers per limitation whose stated problem is
  closest to it. Fixers that frame their problem differently are missed. The comparison with same-foundation
  citers therefore includes some unlabelled fixers, which would bias it toward zero if fixing paid.
- **Hindsight.** Limitations come from the gold set, written with knowledge of what later happened. A
  genuinely predictive test would identify the limitation from critiques published up to a cutoff year and
  follow fixes after it.
- **Validation is narrow.** 85 items, two foundations, with reference labels also produced by Claude.
  Precision may differ for foundations far from the Transformer and VGG.
- **Shakiness and the tested limitation can differ.** Shakiness describes how concentrated *all* critiques of
  a foundation are, but fixers were labelled against the gold limitation, which is not always the most
  criticised one.
- **Citations are a narrow measure of impact.** We did not test disruption, adoption of the fix, or whether a
  fix became a foundation itself.

## 6. Next steps

1. **Pre-specified test of the agreement hypothesis.** Measure, for each limitation, its own share of a
   foundation's critiques up to a cutoff year T. Then test whether that share predicts the premium of fixes
   published after T. Fix the specification, the threshold (p < 0.001) and the sample before looking.
2. **Scale.** Extend from the 54 gold foundations to the top critique groups of the top-500 foundations,
   about 450 with at least 5 critics. That is roughly 3–4× this labelling effort, and it would settle the
   hypothesis either way.
3. **Separate incremental from frame-changing fixes,** with a second judging pass or with citation-based
   disruption as the outcome, and ask whether *those* are rewarded.

## 7. Related work

Our critique and fix framing follows Kuhn's (1962) account of anomalies and paradigm change. Citation-based
measures of whether a paper consolidates or disrupts its field (Funk & Owen-Smith, 2017; Wu, Wang & Evans,
2019) and Fang & Evans's foundation/extension/generalization roles (2025) measure a paper's structural
position, not whether it repairs a specific weakness. We previously found critics unremarkable on those
measures. Measuring concentration with Simpson's index rather than rarefied counts follows standard practice
in ecology (Simpson, 1949; Hurlbert, 1971). To our knowledge, linking LLM-extracted limitations of specific
foundations to the impact of the papers that fix them is new. We have not done a systematic literature
search.

## Reproduction

```bash
bash scripts/shaky_foundations/fixer_candidates.sh   # candidates + 16 batches + judge prompt (~20 min, MPS)
# label batches/batch_NN.jsonl -> labels/batch_NN.jsonl (16 Claude subagents, prompt in judge_prompt.md)
bash scripts/shaky_foundations/fixer_impact.sh       # validation, impact, dose analysis, figures
```

Outputs: `data/shaky_foundations/fixer_candidates_v1/` (candidates, batches, labels) and
`data/shaky_foundations/fixer_impact_v2/` (`summary.txt`, `results.csv`, `per_foundation.csv`,
`examples.csv`). Figures are in `data/shaky_foundations/figures/fixer_impact_v2_*`. Upstream inputs: Lacuna
v2 package, the gold set, and the scale-up critique attributions
(`scale_foundations_v2/hits.parquet`).

## References

<!-- AI-GENERATED REFERENCES (VERIFY) -->
- Fang, H. & Evans, J. (2025). Generalization in science. Per-paper F/E/G indices on Zenodo,
  doi:10.5281/zenodo.23817258.
- Funk, R. J. & Owen-Smith, J. (2017). A dynamic network measure of technological change. *Management
  Science*, 63(3), 791–817.
- Hurlbert, S. H. (1971). The nonconcept of species diversity: a critique and alternative parameters.
  *Ecology*, 52(4), 577–586.
- Kuhn, T. S. (1962). *The Structure of Scientific Revolutions*. University of Chicago Press.
- Simpson, E. H. (1949). Measurement of diversity. *Nature*, 163, 688.
- Wu, L., Wang, D. & Evans, J. A. (2019). Large teams develop and small teams disrupt science and technology.
  *Nature*, 566, 378–382.
<!-- END AI-GENERATED REFERENCES -->

## Appendix A. Notes on what was hard

- **Recall of fixes.** Our critique attribution assigns a citing paper's complaint to the reference it best
  matches. It misses most famous fixes, because a fix states the problem but rarely blames the foundation by
  name. Dropping attribution and matching the stated problem directly to the limitation is what made fixers
  findable.
- **Ties from the centroid shortcut.** Scoring atoms by their concept centroid is cheap, but whole concepts
  tie, so the top 30 would have been an arbitrary sample of one concept. Re-scoring a shortlist with real
  embeddings was necessary.
- **Rarefaction was overkill.** Subsampling to 20 critics fixed a real but small bias (raw top share vs log N:
  ρ = −0.11) at the cost of 60% of foundations. The pairwise agreement estimate avoids both problems.
- **Parallel subagents need unique scratch file names.** Otherwise they overwrite each other's helpers. Here
  the per-batch ID check caught it.

## Appendix B. Random examples of judge labels

Eight random candidates of each label (seed 0), not chosen for quality. From `fixer_impact_v2/examples.csv`.

| label | foundation | citing paper (year) | judge's reason |
|---|---|---|---|
| fix | CBAM | Multiscale Hybrid Convolutional Deep Neural Networks with Channel Attention (2022) | lightweight multiscale channel attention reduces overhead |
| fix | FGSM adversarial examples | Ensemble Adversarial Training: Attacks and Defenses (2018) | ensemble adversarial training counters single-step gradient masking |
| fix | GANs | Prb-GAN: A Probabilistic Framework for GAN Modelling (2021) | Bayesian discriminator ensemble stabilizes training and diversity |
| fix | NAS with RL | EENA: Efficient Evolution of Neural Architecture (2019) | efficient evolutionary NAS with network morphisms cuts search cost |
| fix | AdaIN style transfer | In the Light of Feature Distributions: Moment Matching for Neural Style Transfer (2021) | higher-order moment matching beyond mean and variance |
| fix | Normalizing flows | Rectangular Flows for Manifold Learning (2021) | stochastic estimators make injective flow Jacobian terms tractable |
| fix | ConvLSTM | Convolutional Transformer based Dual Discriminator GAN (2021) | dual discriminators keep predicted frames sharp |
| fix | AdaIN style transfer | CartoonRenderer (2020) | learned adaptive blending of statistics instead of direct AdaIN swap |
| mentions | AdamW | On the Algorithmic Stability and Generalization of Adaptive Optimization (2022) | theoretical stability analysis of adaptive optimizers; no new fix |
| mentions | TCN evaluation | Markov Decision Process for Video Generation (2019) | long-term video generation, not TCN receptive field |
| mentions | AdaIN style transfer | A Style-Aware Content Loss for Real-Time HD Style Transfer (2018) | style-aware content loss; does not address mean-variance statistic matching |
| mentions | ELU | Stochastic Selection of Activation Layers for CNNs (2020) | activation-selection ensembles; does not resolve ELU inconsistency |
| mentions | TD3 | Regularized Softmax Deep Multi-Agent Q-Learning (2021) | notes clipped double estimation fails; targets overestimation, not underestimation |
| mentions | CAM | Beyond Semantic to Instance Segmentation (2021) | states CAM sparsity; contribution targets instance separation |
| mentions | FGSM adversarial examples | Rethinking the Number of Shots in Robust Model-Agnostic Meta-Learning (2022) | robust meta-learning shot count, not FGSM weakness |
| mentions | CBAM | CPWC: Contextual Point Wise Convolution for Object Recognition (2019) | lightweight context convolution; not attention overhead specifically |

The fix examples show the label's breadth. Most are reasonable partial or domain-specific fixes; one (ConvLSTM
→ dual-discriminator GAN for sharp frames) is debatable. None is a frame-changing fix.
