# Track: shaky_foundations

Part of the cross-lab project *Alien space of science meets combinatorial/transformational
creativity* (Stanford AI for Science, Griffiths lab, UvA CreAILab, Penn State, Knowledge Lab).
Living project doc:
<https://docs.google.com/document/d/1s64rva7wDepT0Xz01pkAO__S6bNhcT73ZLPUD0Hvmdw/edit>.

## What this track is testing

The earlier tracks here asked whether a model can *find* a frame-replacing answer that already
exists. This one moves upstream: **where in science is a frame ready to be replaced?**

**Shaky foundation** (11/9/26 framing): a foundational paper that one or more later papers cite
while noting a limitation of it. Shakiness is graded, not yes/no: the more papers that raise the
*same* limitation, the shakier the foundation. Shaky foundations are the targets for transformational
idea generation. Combinatorial operators (analogy, blending) then do the generating, aimed at those
targets.

- **Identifying shaky foundations is the main contribution.** Nobody in science of science seems to
  have done it systematically. Once targets are known, generation may not need elaborate graph
  machinery.
- **Time matters.** The data covers roughly 2010–2026, so shakiness can be tracked year by year. A
  foundation can crack and then restabilise (e.g. a transformer critique later absorbed back in). A
  shakiness-over-time curve could be a science-of-science result in its own right.
- **Kuhn framing.** Anomalies pile up before a paradigm shifts. The citation graph is the main input,
  and LLMs read only the high-signal papers to keep token cost down (10/30 meeting with Alejandro).
- **Domain choice.** Stick to AI, where OpenAlex coverage has been checked by James Evans's prior
  work. Akshay flagged that OpenAlex leans toward medical/clinical papers and misses canonical
  psychology papers such as Kahneman & Tversky.
- **Cost.** Atomising 16K papers cost ~$300 with compression. The whole 2M corpus is estimated at
  $50K–$80K. Any new LLM pass has to be filtered to a candidate set first.

## Data

**Current: `lacuna-recombination-2026-11-06-v2`** (built 2026-11-18; fixed OpenAlex joins for landmark papers),
symlinked at `data/lacuna-recombination-2026-11-06-v2` -> `~/Downloads/lacuna_v2_download/`. Use `pid =
canonical_pid` and the `*_2025` citation counts (details in notes.md). v1, described below, is kept only for
comparison.

`lacuna-recombination-2026-11-06-v1` (Alejandro Hernández Artiles, built 2026-11-09), 3.2 GB, in
`~/Downloads/`, symlinked at `data/lacuna-recombination-2026-11-06-v1`. The package's README and
`schema.json` are the reference. Contents:

- 2.23M AI papers (95.4% matched to OpenAlex)
- 21.4M in-corpus citation edges, plus 39.9M full OpenAlex references
- 17.6M Lacuna idea atoms, each typed as problem / mechanism / finding / limitation / principle /
  evaluation / dataset
- k-means concept layers. `f2800` and `f20000` are frozen at 2014, so use those for anything that
  predicts forward in time.

## Current state (2026-11-21): read this first

Detailed dated entries follow below; this is the snapshot.

**Works**
- **Data.** Lacuna v2, with canonical pids, Fang F/E/G and Kedrick gap-openers joined (`build_measures`).
- **Limitation identification** (`pilot_critiques`, `scale_foundations`, `evaluate_gold`).
  - Each critique is attributed to one of its citer's references by atom similarity, then grouped by concept per
    foundation.
  - Per critique it is ~25% precise.
  - Per foundation, the known limitation is in the top 3 groups for 64% of foundations with >= 20 critics (gold
    set of 42).
  - Timelines and camera-ready figures: `limitation_timelines`.
- **Taxonomy.** Four factors on 106K papers (`factors_v3`), read as Selection / Variation / Retention /
  Embeddedness. Report: `docs/reports/2026-11-21_creativity_taxonomy_bvsr/`.
- **Prescience and emergence** (`build_prescience`). Reproduces Lockhart et al. Fig. S3.

**Doesn't work / negative results**
- Atom-based analogy score.
- Critique concentration as a predictor of displacement.
- Patcher vs critic split.
- Citation typing beyond "critique".
- Messenger flag.
- Critics are not more disruptive or more cited than matched non-critics.

**Waiting on**
- Luo & Evans gap-closing labels (Jerry).
- Approval for an LLM verification pass on critique attributions.

**Next**
- **Idea generation.** Retrospective benchmark: briefing cards at a cutoff year, generation operators (analogy,
  blending, axiom revision), single vs multi-agent, scored against the fixes that later appeared.
- **Taxonomy follow-ups.** Predicted emergence, citation-based novelty at publication, oblique rotation, 2020 +
  3-year-window sensitivity.

## Status

**2026-11-16: track created; data audited (no shakiness scoring yet).**

`bash scripts/shaky_foundations/audit_corpus.sh`. It takes about 2 s and writes to
`data/shaky_foundations/audit_corpus/`. It checks the package against its manifest, then reports
coverage by year, the most-cited papers in the corpus, how 12 landmark papers are matched, atom
type × lens counts, and samples of limitation atoms. Findings that change the plan are in
[notes.md](notes.md):

1. **The definition can't be computed directly from this data.** Nothing ties an atom to a cited
   paper, and there are no citation contexts. "Limitation" atoms describe the paper's own
   shortcomings. The exception is the problems_and_motivation lens (~830K atoms), where they
   critique prior work, but only as "existing approaches…" and never naming a reference.
2. **Several landmark foundations are missing or broken.** *Attention Is All You Need* is unmatched
   and has 0 in-corpus citations. AlexNet has 352 (wrong OpenAlex record). GPT-3 and GANs are far
   too low. This is the main example axiom, so "highly cited" can't simply be read off this table.
3. **Atom coverage rises over time,** from 16% of papers in 2010 to 56% in 2025. LSTM, ImageNet
   and DQN have no atoms at all. A rise in shakiness over time will be confounded with coverage
   unless it's normalised.

## Step 1 (decided 2026-11-16): how the creativity measures relate, measured on real data

Before scoring shakiness, estimate how disruption, F/E/G, gap-opening/closing and an atom-based
combinatorial measure relate to each other. This is the empirical version of the doc's Figure 1
(10/30 note). Paper-level join on `openalex_id`, AI papers 2010–2019.

| measure | source | status |
|---|---|---|
| Disruption CD₅ | compute from `references_openalex` + `citations` | runnable |
| Foundation / Extension / Generalization | Fang & Evans, [repo](https://github.com/fhbzc/Generalization-replication), per-paper indices on [Zenodo 10.5281/zenodo.23817258](https://doi.org/10.5281/zenodo.23817258) (`openalex_efg_y5.csv`, 3.7 GB, CC-BY). Only papers with ≥5 citations in 5 years and ≥1 reference, 1945–2019. Definition: per citing paper, e_i = number of the focal paper's other citers it also cites, e_j = number of the focal paper's references it also cites. F if e_i > e_j, E if e_i < e_j, G if both are 0. Indices are shares. | **in `data/fang_2025_efg/`** (md5 verified; also saved as `openalex_efg_y5.parquet`). Joins on `openalex_id` for 333K of the 724K Lacuna papers from 2010–19 (46%; most of the rest fall below the ≥5-citation filter). Publication years agree for 88%. |
| Gap-opening | Kedrick et al., arXiv:2509.21899, data + code on [Zenodo 10.5281/zenodo.15694240](https://doi.org/10.5281/zenodo.15694240) (`gap_openers_open_access.zip`, 3.0 GB, CC-BY). **Built on MAG (1900–2020), not OpenAlex**, Join with `'W' \|\| paperid`. | **in `data/kedrick_2025_gap_openers/`** (md5 verified). Per-paper labels are in `data/figure2_real.csv` (`GapOpenersWithNovelPair` / `NonGapOpenersWithNovelPair` / `NonGapOpenersWithoutNovelPair`); their CD index is in `figure4_data_cdtile.csv`, still zipped. Joins for 247K of the 724K papers from 2010–19 (34%), with 93% year agreement, but **only 562 are gap-openers (~0.2%)**, so statistical power is limited. |
| Gap-closing / hole-filling | Luo & Evans, arXiv:2608.28822 (persistent homology on OpenAlex concept Word2Vec embeddings). **No code or data release** in the arXiv HTML. Dimension 2 was not computed for computer science. Uses legacy OpenAlex concepts. | have to ask Jiajie Luo / James Evans for per-work labels |
| Combinatorial creativity | **from Lacuna atoms, replacing Shi & Evans surprise** (see below) | to build |

Atom-based combinatorial measures:
- **DSI over atoms** (adapting Johnson et al.'s divergent semantic integration): mean pairwise cosine
  distance between a paper's best-run atom embeddings.
- **Problem–mechanism distance:** how far the paper's mechanism atoms are from its problem atoms, i.e.
  a method borrowed from a distant area. This is the closest atom analogue of a surprising
  content × context combination.
- **Concept-pair novelty:** whether, and how atypically, a paper's `f20000` concept pairs appeared in
  earlier years (Uzzi-style z-score against earlier years only).

Embeddings: the package ships only concept centroids, not per-atom vectors. Ask Alejandro for the
per-atom bge-large vectors, which must exist because k-means was fit on them. Fallbacks: use each
atom's `c200000` centroid as a proxy, or re-embed a sample locally.

### 2026-11-16: first relationship results (`relationships_v1`)

Run: `bash scripts/shaky_foundations/build_measures.sh` (~100 s; **every** eligible 2010–19 paper,
192,898), then `bash scripts/shaky_foundations/analyze_relationships.sh`. Analysis set: 108,740 papers
with Fang F/E/G (≥5 citations in 5 years) and CD. Spearman correlations on within-year percentile
ranks. Partial correlations remove log citations, log references and # distinct concepts.
Figure: `data/shaky_foundations/figures/relationships_v1_spearman_heatmap.png`.

1. **Disruption is mostly Generalization, not Foundation.** CD vs G ρ = .37 (partial .30); CD vs F
   ρ = −.16 (partial .01). Of Generalization-dominant papers, 76% fall in the top CD tertile. This
   replicates Fang & Evans's point that disruptive citations look like generalization citations,
   now in AI with an in-corpus CD.
2. **The atom combinatorial measures track disruption and generalization, weakly.** Atom DSI vs CD
   ρ = .20 and vs G .20 (partials .12 and .19), vs Extension −.20. The direction is consistent, the
   size is modest.
3. **The atom measures are partly redundant.** DSI vs problem–mechanism distance ρ = .79 (partly
   built in, since problem×mechanism pairs are a subset of all pairs). Novel concept pairs ρ = .46
   with DSI. Pair-PMI p10 is the weakest and least consistent measure.
4. **Atom novelty agrees with Kedrick's novelty, not with gap-opening.** Gap-openers vs papers with
   no novel pair: novel-pair fraction AUC .61 [.56, .65], DSI .56 [.51, .61]. Novel-pair
   non-openers vs no novel pair: AUC .58. **Gap-openers vs novel-pair non-openers: every measure's
   CI includes .5** (n = 147). So the atom measures pick up Kedrick's *combinatorial* step (a new
   concept pair) but nothing about whether the pair *opens a gap*. Power is the caveat: only 147
   gap-openers.

Caveats: DSI uses c200000 centroids as a stand-in for per-atom vectors. Our CD only counts citers
inside the corpus (Spearman .60 with Kedrick's all-MAG CD, n = 44K). Restricting to papers with
atoms selects toward later, open-access papers.

## Next decisions

- **How a critique gets attributed to a foundation.** Options: (a) semantic match between a citing
  paper's problems-lens limitation atoms and the cited paper's mechanism/principle atoms;
  (b) citation-context sentences from full text (S2ORC/Semantic Scholar have these; Lacuna
  doesn't); (c) an LLM pass over (citing, cited) pairs for a filtered candidate set. (a) is free
  and should be benchmarked against (b)/(c) on a hand-labelled sample.
- **Fixing landmark matching.** Merge version-split records and repair matches for the top-N
  candidates, possibly with a hand-curated list of foundations.
- **Defining "foundational".** Fang & Evans's foundations/extensions/generalizations classifier vs.
  a citation-count threshold.
- Andrew Shen on paperclip and James Zou's agent-native curation API for building custom datasets
  is still open.

## 2026-11-16: analogical novelty v1 fails validation (`analogy_v1`, `analogy_validation_v1`)

Goal: DSI covers associative novelty, so add *analogical* novelty (a mechanism established elsewhere,
applied to a far problem). Score (`analogy.py`): for each mechanism atom, its "home" is the problem
concepts it co-occurred with in earlier papers (frozen f20000); transfer = distance from the paper's
problem to that home. Three variants (nearest home problem; nearest with >=3 co-occurrences;
count-weighted typicality).

Validation: cue phrases in the paper's own mechanism/principle/finding atoms ("originally developed
for", "adapts techniques from", "inspired by", ...); 4.4K of 191K papers (2.3%).

| check | result |
|---|---|
| paper-level AUC, cue vs no cue (adjusted for #atoms, home size) | 0.49–0.51 for every variant: **no signal** |
| same, DSI / problem–mechanism distance | 0.48 / 0.47 (cue papers slightly *less* associative) |
| within paper: cue mechanism atom > other mechanism atoms | 0.53 [0.51, 0.55] (nnk): tiny |
| cleanest cue ("originally developed for") | AUC 0.48, wrong direction |

Why: **a mechanism atom's concept is placed by its target domain, not its source.** "Hopcroft's
strategy, originally developed for finite automata minimization, adapted to color refinement" lands
in "algorithmic efficiency in combinatorial coloring", the same concept as the paper's problem, so
transfer = 0. The atom sentence is written in the language of the application; the source is a
clause. Concept co-occurrence cannot see where a method came from. The atoms' `names` don't fix it:
they are LLM-coined descriptions of the new hybrid (1.33M distinct of 1.56M), not canonical methods.

Cue precision from hand reading (`cue_samples.csv`): originally_for and adapt_from are clean;
inspired_by mostly good (some near-field, e.g. robust PCA -> robust tensor); x_inspired is mostly
the bio-inspired metaheuristics field itself; analogy is often explanatory ("analogous to energy"),
not transfer; from_field is poor (papers *in* physics/biology).

Next (decision pending): the source domain has to be extracted, not inferred from the embedding.

## 2026-11-20 updates (project meeting; Walker Rickord, Harvard AI for Science Lab)

- **Paper plan.** Part 1 estimates how the creativity measures (CD, F/E/G, gap opening, gap closing)
  relate. If results support it, working title *"LLMs can't jump, but teams of them can"*, with
  James Evans's multi-agent suggestion as a stress test of his theory. Work on the 2010–2019 AI atom
  set and the shaky-foundations path before the next meeting.
- **Walker on CD.** Citation measures are low-resolution and blind to field/context: they separate
  broad categories, not close ones. There may be many paths to disruption (gap closing, gap opening,
  foundational, even extension). Paradigms can also die quietly (stop being cited, no paper says so).
- **Exploratory dimension analysis.** Radar plot / embedding space / factor analysis to find
  orthogonal dimensions existing metrics miss. Sam's analogy: plasticity and stability, the two
  meta-traits above the Big Five; a higher-order factor may be missing. Framed as exploratory.
- **Open questions.** (1) Can a paper be both gap closing and gap opening; how do they overlap?
  (2) Is there orthogonal, relevant space the existing metrics miss? (3) How to detect papers citing
  a foundation's limitations when the limitation is buried in a narrow-scope paper?
- **Data fix.** Alejandro sent `lacuna-recombination-2026-11-06-v2` (2026-11-18) with corrected
  OpenAlex joins for the broken landmarks (Attention, AlexNet, GANs, GPT-3).

## 2026-11-21: switched to package v2; results replicate; first factor analysis

**v2** (`data/lacuna-recombination-2026-11-06-v2` -> `~/Downloads/lacuna_v2_download/`, sha256
verified). All 12 landmarks now matched with sensible counts (`audit_corpus_v2/landmarks.csv`):
Attention 51,740 in-corpus citations (v1: 0), AlexNet 35,125 (v1: 352), GANs 22,227 (v1: 1,406),
GPT-3 10,979. Code changes: `cites_total_2025` replaces `cited_by_count`; focal papers and all
history counts (pair novelty, analogy homes, CD edges) use `pid = canonical_pid` only. Configs now
write `*_v2` outputs; v1 outputs are kept for comparison.

**Relationships (`relationships_v2`, n = 106,973) replicate v1 to two decimals:** CD~G 0.36
(partial 0.29), CD~F -0.16 (partial 0.00), CD~DSI 0.20 (0.12), DSI~E -0.20. Gap-openers
(n = 151) still separate from "neither" on novel pairs (AUC 0.61 [0.57, 0.65]) but not from
novel-pair non-openers. The landmark fix touched a few hundred top papers; within-year ranks over
~100K papers barely move.

**Factor analysis (`factors_v2`, Walker's suggestion).** Within-year Spearman matrix of 9 measures
(CD, F share, G share, DSI, problem–mechanism distance, novel pairs, PMI p10, log citations,
log references); parallel analysis keeps 3 components (60% of variance); varimax loadings:

| factor | loads on | reading |
|---|---|---|
| F1 (27%) | DSI .91, P–M dist .87, novel pairs .65, PMI p10 −.39 | **content recombination** (atoms) |
| F2 (21%) | citations .86, Foundation .55 vs CD −.62, Generalization −.49, PMI p10 −.44 | **built-upon vs jumped-from**: impact + Foundation at one pole, disruption + Generalization at the other |
| F3 (13%) | log references .85 vs Generalization −.48, Foundation −.30, CD −.27 | **embeddedness** (long reference lists -> Extension); partly mechanical |

Readings, all exploratory:
- **Content recombination is nearly orthogonal to every citation measure** (CD, F/E/G, impact load
  ≤ .27 on F1). That is a candidate answer to open question 2: the citation metrics miss the
  semantic-recombination dimension, which only shows up in the paper's content.
- **Disruption and impact are opposite ends of one axis** (F2), not separate dimensions. Foundation
  papers sit with impact; Generalization with disruption. This is Walker's "many paths" point in
  data form: CD alone mixes Generalization with low impact.
- The plasticity/stability analogy maps loosely (F1 ~ exploration/recombination, F2's Foundation
  pole ~ consolidation), but F2 is bipolar, so it is not a clean two-meta-trait picture. Needs
  more measures (gap closing, prescience, shakiness) before claiming a higher-order factor.
- Gap-openers score a little higher on F1 vs "neither" (AUC 0.58 [0.53, 0.64]), not on F2 or F3.
- Caveat: F1 is partly built in, since DSI and P–M distance are near-duplicates (ρ = .76).

## 2026-11-21: shaky-foundations pilot, critique attribution (`pilot_critiques_v1`)

`bash scripts/shaky_foundations/pilot_critiques.sh` (~1 min). 12 foundations with a known crack and
successor, plus 5 controls (`configs/shaky_foundations/pilot_critiques.yaml`). LSTM and Dropout
dropped: no atoms.

**Method (`critiques.py`).** Each problems_and_motivation limitation atom in a citing paper is
attributed to whichever of that paper's in-corpus references it matches best (max cosine over the
reference's atoms), if it beats the runner-up by >= 0.02. 176K critique atoms from 104K citers;
33% clear the margin. Vectors are the c200000 centroid proxy.

**Fix that mattered:** a reference is represented only by its own-contribution atoms. Its
problems_and_motivation atoms describe the work it replaced (the Transformer's atoms about RNN
limitations), so with them RNN critiques were attributed to the Transformer. After the fix, my
reading of 10 random attributions each: Attention ~9/10 genuine, BatchNorm ~5/10, GANs ~5-6/10.
The rest are generic critiques that land on the foundation for want of a better match.

**Result 1: the same-limitation signal works.** Share of a foundation's critics whose critique
falls in its top coarse (c2000) concept:

| | concentration | top limitation |
|---|---|---|
| Faster R-CNN | 0.55 | downsampling / small-object information loss |
| Attention | 0.43 | quadratic attention complexity |
| GloVe | 0.30 | (c20000: polysemy / static embeddings) |
| seq2seq | 0.30 | length extrapolation / fixed-size state compression |
| GCN | 0.22 | over-smoothing |
| BatchNorm, VAE, GANs, word2vec, Adam | 0.18–0.20 | batch size; blurry reconstruction; instability / metrics; context; gradient instability |
| DQN, VGG | 0.15 | (few critics; VGG: vanishing gradients at c20000) |
| controls: U-Net, ResNet, COCO, XGBoost, sklearn | 0.19, 0.12, 0.10, 0.07, 0.05 | mostly scattered; U-Net's is real (3D volumetric cost) |

Cracks vs controls AUC ≈ 0.93 (56 of 60 pairs), but 5 hand-picked controls is very thin. U-Net is
arguably not a control (its long-range/3D limitations did drive Transformer U-Nets). The
textbook crack is the top c20000 limitation for most cracks (`top_limitations.csv`).

**Result 2: the overall critique rate does not separate cracks from controls** (0.4–2% of able
citers for both) and does not rise before successors; it is highest right after publication and
noisy (`figures/pilot_critiques_v1_curves.png`). Shakiness is about *which* limitation recurs, not how often a paper is
criticised.

**Result 3: timing is weak.** The top limitation reaches 3 critics 1–2 years before the successor
for 6 cracks (Attention 2018 vs 2020, Faster R-CNN 2017 vs 2019, GloVe, GCN, BatchNorm, Adam), the
same year for 3, after for 3 (GANs, word2vec, DQN). Controls also reach onset, and same-limitation
critiques keep growing after the successor (Attention peaks 2022–23): critiques are voiced largely
by the patch/replacement literature, so they run concurrent with the shift more than ahead of it.

**Limits.** Counts are small (Attention: 82 same-limitation critics among 50K citers): ~40% of
citers have critique atoms, the margin keeps a third, and the centroid proxy makes 40% of
critiques tie exactly with some reference atom. References without atoms can't win, so critiques
of them land elsewhere.

**Next.** (1) Real per-atom embeddings for critiques + candidate references (ties, margin).
(2) ~200 hand-labelled attributions for precision/recall. (3) Separate "critic" from "patcher" to
see whether critiques by non-patching papers lead the shift. (4) Scale to the top ~500 cited
foundations with concentration as the shakiness score; displacement curves as the citation-only
cross-check.

## 2026-11-21 (later): next steps run: embeddings, labels, patchers, scale-up

**Embeddings.** bge-large on plain atom text reproduces the package vectors exactly (r = 1.0000
with `sim_c200000`, 1,000 atoms), so we never need vectors from Alejandro. Cache:
`data/shaky_foundations/atom_vectors/` (~306K atoms, ~270 atoms/s on MPS; `embeddings.py`).
`pilot_critiques_v2` re-ranks each critique's proxy top-5 shortlist with real vectors (35K
critiques with a pilot foundation in the shortlist). Also: reference atoms are now restricted to
what a reference proposes (`ref_atom_types: mechanism, principle, limitation, dataset`).

**Hand labels (`label_pool_labelled.csv`, 204 pairs, labelled by Claude; 1 = critique targets the
foundation's own method or its direct class, generic critiques = 0).**

| | precision |
|---|---|
| proxy (centroid) | 0.24 (29/122) |
| embeddings | 0.25 (33/130) |
| higher margin (0.04–0.08) | no reliable gain for either |
| by foundation | Attention ~0.8; GCN, GloVe, seq2seq 0.4–0.67; GANs, VAE, BatchNorm, VGG 0.2–0.5; Adam, ResNet, Faster R-CNN, word2vec, XGBoost, sklearn ~0 |

**Similarity attribution is ~25% precise and real vectors don't fix it.** It works only where the
foundation's mechanism is distinctive (self-attention, graph convolution, static embeddings,
fixed-vector encoder). Generic critiques ("deep CNNs downsample and lose small objects") land on
whichever famous reference is nearest: Faster R-CNN's top concentration (0.52) was this artifact,
0/17 genuine. Earlier "~9/10 for Attention" came from small samples. The true critiques that do
get through are almost all the textbook limitation, so the pipeline needs a verification step,
not a better similarity: an LLM check of "is this critique about A?" on attributed pairs only.

**Embedding concentration** (`emb_same_limitation.csv`): Attention 0.48, Faster R-CNN 0.34,
GloVe 0.31, BatchNorm 0.30, GCN 0.26 ... controls 0.05–0.18. Crack-vs-control AUC ≈ 0.80
(proxy 0.93), with the precision caveat above.

**Patchers (critic whose mechanism is close to the foundation's; threshold 0.80 ≈ top quarter).**
Patch scores sit in a narrow band (IQR 0.72–0.79); by reading, they separate builds-on from
unrelated but not patches from applies. Non-patcher onset is earlier than patcher onset for some
cracks and later for others: **no usable signal**.

**Scale-up (`scale_foundations_v2`, top 500 cited 2010–2019 foundations, proxy attribution).**
190 have >= 20 critics. Citation-only displacement (`displacement.py`: share of a foundation's
early co-citation neighbourhood that still cites it, 2024–25 vs peak):
- **Displacement alone separates the pilot groups:** controls retain 0.55–0.96 (ResNet 0.92,
  U-Net 0.96, COCO 0.90); cracks mostly 0.17–0.47 (BatchNorm 0.17, seq2seq 0.19, word2vec 0.28,
  VGG 0.32, Adam 0.41, GANs 0.42, GloVe 0.47); AUC ≈ 0.80 by hand count. Attention (0.93), GCN
  (0.91), DQN (0.90) are criticised but not (yet) displaced.
- **Critique concentration does not predict displacement:** Spearman 0.10 (partial on year and
  log citations 0.09, n = 189); early-window concentration 0.21 (0.13, n = 68). Same sign
  throughout: if anything, concentrated critique goes with *being kept* (a foundation under repair).
- **The concentration ranking at scale is not trustworthy yet:** given ~25% precision it mixes real
  cracks with messengers (papers that diagnosed a limitation, e.g. "Deeper Insights into GCNs"
  on over-smoothing), surveys, and field-wide problems ("3D data scarcity" for PointNet++). A
  messenger flag (foundation's own claims in the top limitation concept) also catches Attention,
  GloVe, GCN, BatchNorm, so it cannot separate them; kept as an exploratory column only.

**Where this leaves the approach.**
1. Candidate generation by similarity is fine; precision needs an LLM verifier on attributed
   (critique, foundation) pairs. Pilot scale: ~4K pairs; top-500 scale: tens of thousands. Short
   prompts, so a small model would make this cheap, but it is an API spend to approve first.
2. Two separable signals: *contested* (concentrated critique) and *abandoned* (displacement).
   The pilot suggests they are different things, not one shakiness scale.
3. Re-test concentration -> displacement after verification; the null may be precision noise.

## 2026-11-21: reframe: the target is *identifying limitations*, not predicting abandonment

Sam: foundations are 2010–2019 and abandonment can take >10 years, so displacement within the
window is not the outcome of interest. The question is whether we can identify the limitations
later papers raise against a foundation. Displacement stays a side measure.

**Foundation-level identification (pilot, `*_top_limitations.csv`, my judgment vs the known crack):**

| foundation | known limitation | found (top 3 limitation groups) | verdict |
|---|---|---|---|
| Attention | quadratic cost | #1 quadratic attention complexity (43 critics) | hit@1 |
| BatchNorm | small-batch dependence | #1 batch size sensitivity | hit@1 |
| GANs | training instability | #1 adversarial training instability / vanishing gradients | hit@1 |
| GloVe | static embeddings | #1 polysemy / static (28) | hit@1 |
| GCN | over-smoothing / depth | #1 depth-induced degradation, over-smoothing | hit@1 |
| VAE | blurry samples | #1 high-frequency detail loss | hit@1 |
| VGG | depth / parameter count | #1 vanishing gradients, #2 parameter redundancy | hit@1 |
| seq2seq | fixed-size bottleneck | emb #1 (tied), proxy #2 | hit@1–3 |
| word2vec | context-free embeddings | #3, 2 critics | weak hit@3 |
| Adam | convergence | emb #1 non-convex convergence gap, but labelled members were generic | label right, members unverified |
| Faster R-CNN | anchors / two-stage | small-object resolution loss (real, but from generic CNN critiques); anchor dependency lands on COCO | miss |
| DQN | overestimation | too few critics | no data |

About 9 of 12 known limitations are recovered as a foundation's top limitation, while only ~25%
of individual attributions are right: scattered noise averages out, true critiques pile into one
concept. Caveats: famous papers with famous limitations (the easy case; the atom-extraction LLM
may also phrase critiques in textbook terms); 12 cases judged by me; group labels, not verified
members; no recall estimate.

**To answer it properly:** (1) a gold set of known limitations beyond the famous 12, e.g. 50
foundations sampled from the top 500 with limitations taken from survey papers or the
foundations' own follow-ups; (2) score hit@k of the top limitation groups; (3) LLM-verify group
members (pending approval); (4) estimate recall from citers' critiques that name the foundation's
mechanism.

## 2026-11-21: gold-set evaluation of limitation identification (`evaluate_gold_v1`)

**Gold set** (`configs/shaky_foundations/gold_limitations.yaml`): 50 foundations sampled from the
top-500 scale-up (seed 20261121, pilot excluded) + the 12 pilot cracks as calibration. Known
limitations written by Claude from background knowledge **before** looking at pipeline output
for them; 8 reviews/position/finding papers skipped -> 42 test foundations. 8 of the 42 are marked
`seen` (I had seen their top limitation label in earlier printouts). Needs team review.

**Scoring** (`bash scripts/shaky_foundations/evaluate_gold.sh`): each foundation's attributed
critiques (proxy attribution from `scale_foundations_v2/hits.parquet`) grouped by c20000 concept,
ranked by distinct critics; gold limitations embedded with bge-large and compared with group
centroids. Threshold 0.78 set on the calibration split (agreement 0.91 with my pilot verdicts),
applied unchanged to test. Plus a threshold-free retrieval score: does a foundation's top-k groups
match its *own* gold better than the other 41 foundations' gold?

**Results, test split (42):**

| | all (42) | unseen (34) | >= 20 critics (22) | < 20 critics (20) |
|---|---|---|---|---|
| manual: hit (gold limitation clearly in top 3 groups) | 20 (48%) | 14 (41%) | **14 (64%)** | 6 (30%) |
| manual: partial (related group) | 10 | 9 | 6 | 4 |
| manual: miss | 12 | 11 | **2** | 10 |
| auto hit@5 (cos >= 0.78) | 0.79 | 0.82 | | |
| retrieval top-1 @5 (chance 0.02) | 0.60 | 0.65 | | |
| retrieval MRR @5 | 0.68 | 0.72 | | |

Manual verdicts with notes: `evaluate_gold_v1/manual_judgments.csv`; groups with example critiques:
`review.csv`.

**Readings:**
- **Yes, limitations can be identified, when a foundation has enough critics.** With >= 20 attributed
  critics, the known limitation is clearly among the top 3 groups for 64% and missed for only 9%
  (2/22: Fashion-MNIST, AdamW). Examples: GP scalability for Bayesian optimization, synthetic-to-real
  gap for ShapeNet, discriminative-part bias for CAM, memory bandwidth for the TPU, vocabulary gap
  for BioBERT, task-boundary assumption for EWC, search cost for NAS.
- **Coverage is the binding constraint**, not attribution precision: below 20 critics, half are
  misses, often because every group has 1 critic (OverFeat, ECO, UNet++, TD3).
- **Threshold-free retrieval confirms it isn't generic matching:** a foundation's top groups pick
  out its own gold limitation among 42 foundations 60% of the time (chance 2%).
- **Failure modes:** (1) the top group is the *topic* rather than a limitation (Gumbel-Softmax:
  "non-differentiable discrete selection"); (2) field-wide problems (Hourglass: 3D annotation;
  FedProx: communication cost); (3) the problem the foundation *solved* (ELU: "dying neurons" is
  ReLU's problem); (4) a different real limitation than the gold (MDNet: online drift; MAML:
  cross-domain generalization), so some "partials" are gold-set incompleteness.
- **The automatic matcher is a rough cross-check only**: false positives (Fashion-MNIST, AdamW,
  ECO) and false negatives (LINE, NAS, BigGAN, EWC rank). Hit@k from it should not be quoted alone.
- **Caveats:** gold and match judgments are both mine; famous foundations (top 500 by citations);
  proxy attribution (~25% critique-level precision); no recall estimate.

**Next:** (1) team review of the gold set and `review.csv`; (2) raise coverage: more critique atoms
(other lenses, e.g. limitation atoms that name methods), or LLM extraction from citation contexts for
foundations with few critics; (3) suppress failure modes 1–3 (drop groups whose label matches the
foundation's own topic/contribution; down-weight groups common across many foundations);
(4) LLM verification of group members.

## 2026-11-21: shakiness over time for the identified examples (`limitation_timelines_v1`)

`bash scripts/shaky_foundations/limitation_timelines.sh` -> `data/shaky_foundations/figures/limitation_timelines_v1_timelines.png`: cumulative distinct
citing papers raising the identified limitation vs raising any critique, for 8 gold-set hits
(same-meaning concept groups merged; `groups.csv`). Yearly new critics of the limitation:

- **Burst then plateau:** BioBERT vocabulary gap (5 in 2020, 7 in 2021, then 1–2); TPU memory
  bandwidth (rising 2017–21, none after); GP Bayesian optimization scalability (1–6/yr 2014–21,
  then 1). Looks like a crack that stops being raised (fixed or absorbed: e.g. domain-vocabulary
  models such as PubMedBERT appeared in 2020), which is the "crack then restabilise" pattern in the
  framing. Not tested: could also be attribution drift or fewer critique atoms for these citers.
- **Steady accumulation:** NAS search cost, 1–3 new critics every year 2017–2025.
- **Too thin to read dynamics:** ShapeNet (5), CAM (4), EWC (3), BigGAN (5).
- The identified limitation becomes a smaller share of all critiques over time for most examples;
  the all-critique curves rise steeply in 2023–25, partly from rising atom coverage (raw counts, not
  normalized) and partly from attribution noise (~25% precision).

**Update (same day): multiple limitations per foundation + camera-ready figure.** Timelines now draw
one line per identified limitation (config `limitations: [{label, ranks}]`, up to 3; concept groups
chosen after reading example critiques; `groups.csv` lists them). Camera-ready one-row version
(`bash scripts/shaky_foundations/limitation_timelines_camera.sh`):
`data/shaky_foundations/figures/limitation_timelines_camera_v1_timelines.{pdf,png}`, caption in
`data/shaky_foundations/limitation_timelines_camera_v1/caption.md`. Transformer: quadratic cost 96
critics, position/order 11, sequential decoding 7 (of 218 with any critique). VGG: parameter
redundancy 13, vanishing gradients 12, edge-deployment cost 7 (of 159).

**Update: papers that (partially) fix each limitation.** `limitation_timelines.py` now writes
`critics.csv` (every paper counted on a limitation line, with its own mechanism atom closest to that
limitation, real bge-large vectors). I read all 146 and listed as `solvers` in
`limitation_timelines_camera.yaml` the critics whose own method addresses the limitation (excluding
papers that only apply an existing fix, studies, and other limitations). Camera-ready figure shows them
as per-year dots sized by count, totals in parentheses. Transformer: quadratic cost 55 of 96 critics
propose fixes (Transformer-XL, Informer, Perceiver, S4, Autoformer, LogSparse, ...), mostly 2020–23;
position/order 3 of 11; sequential decoding 2 of 7. VGG: parameter redundancy 10 of 13, edge
deployment 6 of 7, vanishing gradients 4 of 12. Famous fixes that are not themselves attributed critics
(Linformer, Reformer, ResNet, MobileNet) cannot appear: a recall gap of the attribution step, not
evidence they don't exist.

## 2026-11-21: 2020s foundations (`scale_foundations_2020s_v1`)

Same pipeline on the 300 most-cited 2020–2023 foundations (`bash scripts/shaky_foundations/scale_foundations_2020s.sh`).
Fewer years of critiques (median 11 critics vs 16 for 2010–2019; 82/300 with >= 20) but higher atom
coverage. Top limitation groups for the most-cited ones are mostly textbook (my reading, not yet
gold-evaluated): SimCLR batch-size sensitivity (33 critics), NeRF per-scene optimization / rendering
latency, LoRA low-rank expressivity bottleneck, CLIP compositional reasoning failure, latent diffusion and
DDIM sampling latency / discretization error, Segment Anything prompt dependency, ViT quadratic attention
(inherited from the Transformer), GPT-4 context-window limits, Llama 2 hallucination, Gemini benchmark
contamination. Misses: DDPM (5 critics despite ~5K citations), DETR (no slow-convergence group), GPT-3
(diffuse). LLM technical reports collect critiques of LLMs as a class (hallucination, context length), the
field-level failure mode noted before.

## 2026-11-21: 2023–2025 foundations (`scale_foundations_2023plus_v1`)

200 most-cited 2023–2025 foundations (`bash scripts/shaky_foundations/scale_foundations_2023plus.sh`), critiques
through 2025. Median 9 critics; 36/200 with >= 20 (24 of them from 2023; 9 from 2024; 3 from 2025).
- **2023 works for the most-cited:** Segment Anything prompt dependency (18), 3D Gaussian Splatting storage
  overhead (9 + 3), Self-Consistency majority-voting limits (9), LLaVA visual-resolution bottleneck and object
  hallucination, MiniGPT-4 hallucination and frozen-encoder bottleneck.
- **2024–2025 are mostly too early:** top groups are 1–3 critics (DeepSeek-R1 has 18 critics but no group above
  2; Qwen2.5, ControlNet, GPT-4o system card scattered).
- **Two failure modes dominate:** model technical reports (GPT-4, Llama 1–3, Gemini, Qwen) collect critiques of
  LLMs as a class (context length, hallucination, contamination, jailbreaks); and a fix absorbs critiques of
  what it fixed (Mamba's #2 group is "quadratic attention complexity", the Transformer's limitation).

## 2026-11-21: critique profiles for 2024–2025 foundations (`critique_profiles_2024plus_v1`)

`bash scripts/shaky_foundations/scale_foundations_2024plus.sh` (2024–2025 foundations, critiques through
Nov 2026; 37% of them from partial 2026) then `bash scripts/shaky_foundations/critique_profiles.sh` ->
`data/shaky_foundations/figures/critique_profiles_2024plus_v1_profiles.{pdf,png}`: per paper, share of critics
in its top 3 limitation groups (identical labels merged) vs all other groups.
- **Converging already:** Mixtral (sparse-MoE memory overhead 10 of 25 critics, then expert collapse),
  GPT-4o system card (cross-modal safety gap 4/15), MiniGPT-4 (multimodal hallucination, frozen-encoder
  bottleneck), Mamba (14/52 "quadratic attention complexity" = the Transformer's limitation, absorbed by the
  fix: messenger effect).
- **Diffuse:** Llama 3 (top group 6 of 120), Qwen2-VL, Qwen3, Qwen2.5, DINOv2, Grounding DINO: general-purpose
  models and tech reports collect critiques of their whole class.
- **Plausible early directions to watch (2–5 critics each):** RL-trained reasoning models: entropy collapse
  (Qwen3), reward hacking and multi-step degradation (DeepSeekMath), prompt sensitivity (DeepSeek-R1);
  long-context degradation (Qwen3).

## 2026-11-21: are the "most cited" papers foundations? (`foundation_status_v1`)

`bash scripts/shaky_foundations/foundation_status.sh`. Fang & Evans F/E/G recomputed inside Lacuna
(`efg.py`; 5-year window; matches the published indices at Spearman 0.64–0.69 on 2010–2019 papers, since only
Lacuna citers count downstream). "Foundation" = Foundation index above the 90th percentile of a random baseline
of ordinary papers from the same years (~3K per set). Paper kind from title regex (`kinds.csv`; misses some
datasets, e.g. SQuAD counted as method).

| set | foundation (> p90 of baseline) | F-dominant | method/idea | surveys | tech reports | datasets |
|---|---|---|---|---|---|---|
| 2010–2019 top 500 | 79% | 64% | 90% | 10 (0% foundation) | 0 | 31 (90%) |
| 2020–2023 top 300 | 78% | 48% | 89% | 16 (25%) | 4 | 11 (91%) |
| 2024–2025 top 150 | 65% | 42% | 74% | 13 (15%) | 16 (75%) | 6 (100%) |

Baselines: 10% by construction; F-dominant 3–7%. The non-foundations among the most cited are surveys and
heavily used *modules* cited as one component among many (CenterNet, CCNet, Group Normalization, SAGAN,
ECA-Net, Coordinate Attention, Segmenter, SimPO, YOLOv9). Datasets and benchmarks are almost always
foundations in this sense. Recent papers are less often foundations, partly because the 2024–25 list holds more
surveys and tech reports and partly because their indices rest on 1–2 years of citations.

## 2026-11-21: are critics of foundations more disruptive? (`critics_disruption_v1`)

`bash scripts/shaky_foundations/critics_disruption.sh`. Population: 107,966 papers from 2010–2019 with Fang F/E/G
and CD. Among the 24,384 that cite a top-500 foundation and have critique atoms, 2,102 have a critique
attributed to a foundation ("critics"). Within-year CD percentiles; "adj" removes log citations, log references
and # concepts.

| comparison | CD pct difference (points) | adjusted | AUC (adj) |
|---|---|---|---|
| critics vs non-critics | +1.2 | +0.6 [−0.1, 1.3] | 0.51 |
| within Generalization-dominant: critics (171) vs non-critics (1,349) | 0.0 | −2.0 [−4.7, 0.8] | 0.46 |
| Generalization-dominant critics vs all Generalization-dominant | −0.8 | +1.8 [−1.1, 4.9] | 0.47 |

Regression (pool, with covariates): critic +1.0 points [0.4, 1.7]; Generalization +10.7; critic x Generalization
−1.9 [−4.9, 1.1]. Critics are slightly more often Generalization-dominant (8.1% vs 6.1%).
**No: papers that critique foundations are not more disruptive, and Generalization papers that critique are not
more disruptive than other Generalization papers.** Caveats: critic labels are ~25% precise (an effect of a few
points could be diluted to near zero), CD is in-corpus, and the hand-judged *solvers* are too few and too recent
(mostly 2020+) to test, since CD needs 5 years.

**Update: citations as the outcome (`critics_disruption_v2`, outcomes disruption / citations_total /
citations_5y_lacuna; citation outcomes adjusted for log references and # concepts only).**

| comparison | total citations (OpenAlex, 2025): raw / adj [CI] | 5-year Lacuna citations: raw / adj [CI] |
|---|---|---|
| critics vs non-critics | +0.7 / +2.7 [1.4, 3.9] | −0.6 / −0.4 [−1.4, 0.7] |
| within Generalization-dominant: critics vs non-critics | −0.7 / +3.1 [−1.6, 8.0] | −1.8 / −2.0 [−6.9, 2.5] |
| Generalization-dominant critics vs *all* Generalization-dominant | +6.5 / +9.4 [4.5, 13.8] | +15.2 / +10.6 [6.4, 15.6] |

Generalization critics are well above the typical Generalization paper, but so are Generalization papers that
cite a top foundation and have critique atoms without critiquing it: the gap is selection (citing famous
foundations, having full-text atoms), not critiquing. Against the matched comparison, critiquing adds at most
~3 percentile points of total citations overall and nothing distinguishable among Generalization papers.

## 2026-11-21: do Generalization papers citing foundations get cited more? Can atoms type citations?

**Citing a top foundation goes with more citations** (`critics_disruption_v2`, new comparisons): Generalization-
dominant papers that cite a top-500 foundation (2,588) vs those that don't (9,238): total citations +7.7
percentile points after controls [6.4, 8.8], 5-year Lacuna citations +13.9 [12.7, 14.9]; other roles +12.2 and
+18.9. Association only: citing famous foundations also marks papers in popular areas.

**Citation typing from atoms (`cite_types_v1`, prototype, not validated):** for 431K citations of the 17 pilot
foundations, type = critique (attributed) / builds on (citer mechanism and problem both close to the
foundation's) / transfers (mechanism close, problem far) / alternative (problem close, mechanism far) /
background, with "close" = top quarter of pooled similarity (centroid proxy compresses cosines, median ~0.87).
Cross-tab with each citation's Fang structural label: share Generalization = critique 17%, background 7.4%,
transfers 3.8%, alternative 3.1%, builds on 2.1%.
- Reading `examples.csv`: **only the critique type is meaningful.** "Builds on" is mostly not (ResNet <- an
  interpretability paper), "transfers" mixes real transfer (VAE <- encoder-decoder for dynamical systems) with tool
  use (Adam as an optimizer). Generic deep-learning atoms resemble everything.
- **The dominant citation type is missing:** *uses as a tool / component / dataset* (most citations of Adam,
  ResNet, COCO). Atoms describe a paper's own contribution, not what it used, so atoms alone cannot type it.
- The critique-Generalization link (17% vs 2–7%) may be an artifact: a structurally disconnected citer has fewer
  related references competing for its critiques, so attribution to the foundation is easier.
- **Routes that would work:** (1) Semantic Scholar's citation intents and contexts (background / method /
  result-comparison, with the citing sentence), available through its API; (2) an LLM classifying (citing paper's
  atoms + title, foundation summary) into uses-as-tool / extends / transfers / compares / critiques / background,
  on a sample per foundation (~5K pairs for the pilot, cheap with a small model; needs approval).

## 2026-11-21: prescience and emergence (`prescience_v1`, `factors_v3`)

After Lockhart, Sourati, Shi & Evans 2026 (arXiv:2603.01117: prescient work surprises at publication but
becomes routine; emergence = leadership in areas that come to coalesce). Atom versions in `prescience.py`,
frozen f20000 concepts, rates per paper-with-atoms so coverage growth cancels, 5-year future window:
- **prescience**: for the paper's never-before-seen concept pairs, mean log[(later co-occurrences + 1) /
  (expected from the two concepts' later popularity + 1)] (concept growth divided out).
- **novel_pair_adoption**: share of its new pairs used by >= 3 papers in the next 5 years.
- **emergence**: mean log growth of its concepts' share of papers, recent 3 years -> next 5 (realised, not
  Lockhart's predicted coalescence).
PMI-based surprise was dropped: in a 20K-concept space add-one smoothing makes unseen pairs of rare concepts look
positively associated. Checks: novelty share equals build_measures novel_pair_frac (r = 1.0); pair counts match
an independent recount; landmarks score high (Attention, GANs, Adam, GCN, ResNet: prescience top 5–12%,
emergence top 1–21%). `bash scripts/shaky_foundations/build_prescience.sh` (seconds).

**Correlations (within-year ranks, n = 106K):** prescience vs emergence 0.14 (distinct, as Lockhart et al.
argue); both relate to adoption (0.58, 0.53). Prescience is ~uncorrelated with disruption (−0.08), F/G (0.07,
−0.01) and citations (0.01); emergence goes with citations (0.27) and Foundation (0.13). Prescience vs
surprise (novel pair share) −0.34: papers with many new pairs see a smaller share of each adopted.

**Factors (`factors_v3`, parallel analysis keeps 4, 68% of variance):**

| factor | loads on | reading |
|---|---|---|
| F1 (22%) | adoption .90, emergence .74, prescience .64, citations .28 | **forward uptake**: content that becomes mainstream |
| F2 (18%) | DSI .79, novel pairs .79, prescience −.53, emergence .35 | **combinatorial novelty at publication** |
| F3 (16%) | citations .78, Foundation .54 vs CD −.75, Generalization −.57 | **built upon vs jumped from** (as before) |
| F4 (11%) | references .86 vs Foundation −.46, Generalization −.41 | embeddedness |

New: forward uptake (prescience/emergence) is a dimension of its own, separate from both novelty at
publication and every citation-structure measure. Gap-openers stand out only on F2 (AUC 0.61 vs "neither").
Caveats: realised (hindsight) measures, so they are outcomes, not predictors; atom concepts are the paper's own
vocabulary, which famous papers help define.

**Check against Lockhart et al. (read the full arXiv v1 text, 34 pp.; figures not inspected).** They report no
paper-level (or other) correlation between prescience and emergence: analysis is at the country level (shares and
per-paper rates of top-5% papers), and they describe the two as different, in-tension strategies. Their definitions
differ from ours: emergence is *predicted* (keyword areas with exponential frequency growth over the prior 5
years, prevalence, and 3-year embedding convergence; papers scored by distance to those areas); prescience is the
drop in surprisal under a hypergraph-embedding model (Shi & Evans 2023) from publication to 2 years later. The one
reproducible quantitative claim is Fig. S3: prescience predicts top-10%-cited status more than surprise does.
**Reproduced** (n = 186,662, citations = OpenAlex through 2025, within-year): P(top 10% cited) in the top
prescience decile 0.173 (above p95: 0.181) vs 0.079 for the top surprise decile (above p95: 0.074); surprise is
slightly negative (Spearman −0.05), prescience positive (0.14). Novel-pair adoption (0.25) and realised emergence
(0.23) predict citations more strongly. Not reproducible here: their country patterns (Lacuna has no
affiliations). A predicted-emergence variant (pre-publication concept growth + convergence) would match their
emergence definition.

## 2026-11-21: report written: variation / selection / retention

`docs/reports/2026-11-21_creativity_taxonomy_bvsr/report.md`: data, measures (with validation), method, the
four factors read as blind variation (F2), selective retention's selection (F1) and retention (F3) stages
(Campbell 1960; Simonton 1999), landmark factor scores, implications, limitations, reproduction. Figures from
`bash scripts/shaky_foundations/taxonomy_figures.sh` (named loadings; selection vs variation map with landmarks;
`taxonomy_figures_v1/landmark_scores.csv`). Key landmark finding: all 11 landmarks in the factor sample are
top-quartile on selection, 9/11 on retention, but 5/11 are in the bottom third of variation (VGG, GloVe, Faster
R-CNN, GCN, ResNet); the Transformer (no Fang record, so outside the factor sample) is 4th percentile on new
concept pairs and 95th on prescience. Figures stay in the track figures folder (not a report figures/ folder) per
Sam's one-folder rule; data/ is gitignored, so they must be copied if the report is shared through git.
