# Bridging Cognitive Science and the Science of Science: Blind Variation and Selective Retention Explains Scientific Creativity Metrics

*Shaky-foundations track, 21 November 2026. Exploratory analysis for the cross-lab project "Alien space of
science meets combinatorial/transformational creativity" (Paper 1, empirical taxonomy).*

## Summary

We measured ten indicators of scientific creativity and impact for 106,260 AI papers published 2010–2019. They
come from three independent sources: the papers' own content (LLM-extracted idea atoms), their citation
structure, and what later papers did with their ideas. A factor analysis finds four independent dimensions.
Three of them read naturally as the stages of Campbell's (1960) and Simonton's (1999) **blind variation and
selective retention**:

- **Variation (F2):** how unusual a paper's combination of concepts is when it appears.
- **Selection (F1):** whether the field later moves toward that combination: its new concept pairs are
  adopted, its concepts grow, and what was surprising becomes routine (prescience).
- **Retention (F3):** how later work holds on to the paper. At one pole a community builds on it and cites it
  heavily (Foundation); at the other, citers drop its background (disruption) or carry it into unrelated
  contexts (Generalization).

The fourth factor is mostly mechanical (reference-list length). Variation and selection are independent of each
other and of every citation-structure measure, so citation metrics alone (disruption, Foundation /
Extension / Generalization) cannot see two of the three stages. Landmark papers are all high on selection, mostly
high on retention, but split on variation. Many of the most consequential AI papers of the decade (VGG, ResNet,
Faster R-CNN, GCN, GloVe) were *not* unusual combinations when published; the field selected them anyway.

## 1. Interpretation

*The evidence for this reading is in Section 2 (Results); data, measures and method are in Sections 3–5.*

### 1.1 Variation, selection, retention

Campbell (1960) and Simonton (1999) describe creativity as variation followed by selective retention: many
ideas are generated, few are selected, and the selected ones are kept and built upon. The three substantive
factors line up with these stages.

- **Variation (F2)** is the supply of new combinations: unusual concept pairs and semantically spread-out
  content. Most of it goes nowhere. The negative loading of prescience on F2 is the empirical signature of
  *blind* variation: the more new combinations a paper tries, the smaller the share of them that the field
  adopts.
- **Selection (F1)** is the field converging on a paper's content: its new pairs become standard, its concepts
  grow, and what was surprising becomes routine. This is selection of the *idea*, not attention to the
  *paper*. Citations load only .28, so a paper can be on the trajectory the field takes without being the one
  everyone cites.
- **Retention (F3)** is how the selected work is held. At one pole it becomes a community's foundation: heavily
  cited, with citers who also cite each other. At the other, it is retained by displacement: citers drop its
  predecessors (disruption) or carry it into unrelated contexts (Generalization), thinly and widely.

### 1.2 Two axes of measurement

The three factors also differ in what is measured and when. That leaves one cell empty, which we can fill
with a measure that doesn't exist in our set yet:

| | At publication | After publication |
|---|---|---|
| **Content** (atoms) | Variation: what it combines | Selection: whether its ideas become standard |
| **Citations** | *(empty: reference-based novelty, e.g. Uzzi-style atypical journal pairs or Lockhart et al.'s context prescience)* | Retention: how the paper itself is used |

Citation metrics, the main instruments of the science of science, cover only the bottom-right cell. Whether
citation-based novelty at publication forms its own factor, or joins Variation, is a direct test of this
layout.

### 1.3 What this implies for "transformational"

The natural definition of a transformational contribution is **high variation that is then selected**: an
unusual combination the field reorganises around ("novel and selected" in Figure 2, Section 2.3). Because blind variation
mostly fails, that quadrant is the hard one to reach.

The landmarks (Section 2.3) show something more. Every landmark is in the top quartile of selection, and nine of eleven also
of retention (word2vec and VAE are lower, at 0.65 and 0.59). Yet five of eleven sit in the bottom third of
variation: VGG, GloVe, Faster R-CNN, GCN, ResNet. The Transformer, outside
the factor sample, is in the 4th percentile of new concept pairs. Their consequence came from being selected,
not from recombinant surprise. Read this way, transformation in AI over this decade was driven more by
selection than by variation. A simple combination at the right point in the landscape mattered more than an
unusual one.

### 1.4 Relation to the plasticity–stability analogy

At the 11/20 meeting we discussed whether creativity metrics hide a higher-order structure like the plasticity
and stability meta-traits above the Big Five. The factors suggest a process structure instead of two traits:
- Variation resembles plasticity, or exploration.
- Retention's Foundation pole resembles stability, or consolidation.
- Selection is the link between them. It is the step that existing citation metrics miss, and that only
  forward-looking content measures reveal.

### 1.5 Implications for idea generation (objective 2)

If selection, not variation, is what distinguishes consequential work, an AI idea-generation system should not
be optimised for novelty alone. Novelty is cheap and mostly not selected. It should be judged by how likely the
field is to select the idea. Two pieces we already have point that way:
- **Where to aim:** the shaky-foundations pipeline localises foundations whose limitations later papers keep
  raising.
- **How to evaluate:** a retrospective test can score generated ideas by whether their content matches what the
  field later converged on. That is selection measured directly.

## 2. Results

### 2.1 Pairwise structure

Selected Spearman correlations (within-year ranks, n = 106,260):

| Pair | ρ | Reading |
|---|---|---|
| Disruption – Generalization | 0.36 | disruptive papers are often carried into new contexts (partial ρ = 0.29 controlling citations, references, # concepts) |
| Disruption – Foundation | −0.16 | foundations are *not* the disruptive papers (partial 0.00) |
| Disruption – citations | −0.41 | within a cohort, the most-cited papers consolidate |
| Foundation – citations | 0.37 | |
| DSI – new concept pairs | 0.44 | two views of combinatorial novelty |
| Prescience – emergence | 0.14 | distinct, as Lockhart et al. argue |
| Adoption – prescience / emergence | 0.58 / 0.53 | |
| Prescience – new concept pairs | −0.34 | papers with many new pairs see a smaller share of each adopted |
| Prescience – disruption / Foundation / Generalization / citations | −0.08 / 0.07 / −0.01 / 0.01 | prescience is invisible to citation structure |
| Emergence – citations | 0.27 | |

### 2.2 Four factors

Parallel analysis keeps four components (eigenvalues 2.23, 1.77, 1.62, 1.07; the shuffled-data threshold is
≈ 1.01). Together they explain 68% of the variance.

![Varimax-rotated loadings](../../../data/shaky_foundations/figures/taxonomy_figures_v1_loadings.png)

*Figure 1. Varimax-rotated loadings of the ten measures on the four retained factors (bold: |loading| ≥ 0.4).
Measures are grouped by the factor they load on. n = 106,260 AI papers, 2010–2019.*

| Factor | Variance | Defining loadings | Name |
|---|---|---|---|
| F1 | 22% | adoption .90, emergence .74, prescience .64 (citations .28) | **Selection** |
| F2 | 18% | DSI .79, new concept pairs .79, prescience −.53, emergence .35 | **Variation** |
| F3 | 16% | citations .78, Foundation .54 vs disruption −.75, Generalization −.57 | **Retention** |
| F4 | 11% | references .86 vs Foundation −.46, Generalization −.41 | Embeddedness (mechanical) |

Gap-openers differ from ordinary papers ("neither" class) only on Variation: AUC 0.61 [0.55, 0.68].
Against papers that also introduced a new concept pair, no factor separates them; with 100 gap-openers in the
sample, power is low.

### 2.3 Where landmark papers sit

Factor-score percentiles for landmark papers in the sample:

| Paper | Year | Selection (F1) | Variation (F2) | Retention (F3) |
|---|---|---|---|---|
| word2vec | 2013 | 0.94 | 0.83 | 0.65 |
| VAE | 2014 | 1.00 | 0.41 | 0.59 |
| VGG | 2014 | 0.99 | 0.14 | 0.99 |
| seq2seq | 2014 | 0.76 | 0.79 | 1.00 |
| GloVe | 2014 | 0.96 | 0.22 | 0.95 |
| Bahdanau attention | 2015 | 0.97 | 0.70 | 0.97 |
| BatchNorm | 2015 | 0.96 | 0.69 | 0.99 |
| Faster R-CNN | 2015 | 0.99 | 0.22 | 0.99 |
| ResNet | 2016 | 0.99 | 0.33 | 1.00 |
| GCN | 2017 | 0.97 | 0.30 | 0.98 |
| BERT | 2019 | 0.86 | 0.80 | 1.00 |

*Transformer, GANs, Adam, COCO and U-Net have no matched Fang & Evans record and so drop out of the factor
sample. On the measures they do have, the Transformer is in the 4th percentile for new concept pairs and the
95th for prescience.*

![Selection vs variation](../../../data/shaky_foundations/figures/taxonomy_figures_v1_selection_vs_variation.png)

*Figure 2. Every paper's Selection (F1) against Variation (F2) percentile (grey density; the two are
uncorrelated, ρ = −0.003), with landmark papers marked.*

## 3. Data

**Corpus.** Lacuna recombination package v2 (built by Alejandro Hernández Artiles, 2026-11-18):
- 2.23M AI papers, 95.9% matched to OpenAlex;
- a merged in-corpus citation graph (22.6M edges), plus each paper's references outside the corpus (39.9M);
- 17.6M LLM-extracted **idea atoms**: sentence-level claims typed as problem, mechanism, finding, limitation,
  principle, evaluation or dataset, about 15 per paper;
- atoms embedded with BAAI/bge-large-en-v1.5 and clustered into concept layers. Here we use `f20000`, 20,000
  concepts fit on atoms up to 2014 and then frozen, so concept boundaries carry no hindsight.

Version 2 fixes the OpenAlex matching for the most-cited papers. Version 1 had, for example, no citations for
*Attention Is All You Need*. All results here replicate the version-1 results to two decimals.

**Sample.** Canonical (de-duplicated) papers from 2010–2019 that are matched to OpenAlex, have at least one
reference, and have atoms: 189,572 papers. The factor analysis uses the 106,260 with every measure defined. The
binding constraint is the Fang & Evans indices, which require at least 5 citations within 5 years.

**External data.**
- Foundation / Extension / Generalization indices from Fang & Evans (2025): Zenodo 10.5281/zenodo.23817258,
  joined on OpenAlex ID.
- Gap-opener labels from Kedrick et al. (2026): Zenodo 10.5281/zenodo.15694240, joined on MAG/OpenAlex ID;
  151 gap-openers in the sample.

## 4. Measures

All measures enter the analysis as **within-publication-year percentile ranks**, so correlations are Spearman
correlations with year held fixed.

| Measure | Source | Definition |
|---|---|---|
| Disruption (CD₅) | citations | (n_i − n_j)/(n_i + n_j + n_k) over in-corpus citers within 5 years (Funk & Owen-Smith 2017; Wu, Wang & Evans 2019). n_i = citers of the paper but none of its references; n_j = citers of both; n_k = citers of its references only. |
| Foundation share | citations | Fang & Evans: share of 5-year citers that cite more of the paper's other citers than of its references. |
| Generalization share | citations | Fang & Evans: share of 5-year citers that cite neither its references nor its other citers. |
| Citations | citations | log(1 + in-corpus citers within 5 years). |
| References | citations | log(1 + reference count). |
| Divergent semantic integration (DSI) | content | Mean pairwise cosine distance among the paper's atoms, adapting Johnson et al.'s DSI from words to idea atoms. Atom vectors: c200000 concept centroids. |
| New concept pairs (surprise) | content | Share of the paper's concept pairs that no earlier paper contains. |
| Prescience | forward content | Over the paper's never-before-seen pairs: mean log[(co-occurrences in the next 5 years + 1) / (co-occurrences expected from the two concepts' own later popularity + 1)]. A surprising combination becomes routine, beyond its concepts merely growing. After Lockhart et al. (2026). |
| New pairs later adopted | forward content | Share of the paper's new pairs used by at least 3 papers in the next 5 years. |
| Emergence | forward content | Mean log growth of the paper's concepts' share of papers, from the 3 years up to publication to the 5 years after. Realised growth, not Lockhart et al.'s predicted coalescence. |

All forward measures count rates per paper with atoms in each window, so the rising share of papers with atoms
over time (16% in 2010, 56% in 2025) cancels out.

**Validation checks.**
- Our CD agrees with Kedrick et al.'s CD, computed on all of MAG: Spearman 0.60, n = 43,908.
- The new-pair share equals the novelty measure from the main measures pipeline (r = 1.0).
- Prescience pair counts match an independent recount.
- Landmarks score as expected: Attention, GANs, Adam, GCN and ResNet sit in the top 5–12% on prescience and the
  top 1–21% on emergence.
- We reproduce Lockhart et al.'s Figure S3. Papers in the top prescience decile are top-10% cited 17.3% of the
  time, against 7.9% for the top surprise decile and 10% by chance. Surprise alone relates slightly negatively
  to citations (Spearman −0.05); prescience positively (+0.14).

## 5. Method

1. Within-year percentile ranks of the ten measures, then their correlation matrix.
2. **Number of factors:** Horn's parallel analysis, keeping components whose eigenvalue exceeds the 95th
   percentile of eigenvalues from 20 column-shuffled copies of the data.
3. **Rotation:** principal-component factoring with varimax rotation. With about 100K papers this differs little
   from maximum-likelihood factor analysis, and it needs no distributional assumptions.
4. **Factor scores:** regression scores, reported as percentiles across the sample.
5. **Gap-openers:** AUC of each factor score for gap-openers against Kedrick et al.'s other classes, with
   bootstrap 95% CIs.

## 6. Limitations

- **Hindsight.** Selection measures are realised outcomes (5-year windows), not predictions, so they describe
  papers rather than forecast them. A predicted-emergence variant, using only pre-publication concept trends,
  would match Lockhart et al.'s definition.
- **Measure choice shapes the factors.** The two variation measures are both atom-based, and prescience and
  adoption share part of their definition. Varimax forces the factors to be uncorrelated; an oblique rotation
  would show whether selection and retention are related.
- **Atoms are the papers' own vocabulary.** Influential papers help define the concepts their successors use,
  which can inflate their selection scores.
- **Sample.** AI only; papers with at least 5 citations in 5 years (for Fang & Evans) and with atoms, which
  over-represents later and open-access work. CD counts only citers in the corpus.
- **Missing dimension.** Gap closing (Luo & Evans) awaits data. Gap opening rests on only 151 papers.
- **Interpretation.** The variation / selection / retention reading is ours and exploratory. The factor
  structure is the finding; the names are a hypothesis.

## 7. Next steps

1. Add a citation-based novelty-at-publication measure, to fill the empty cell and test the layout.
2. Run an oblique rotation, and test stability across publication-year halves and subfields.
3. Build predicted (pre-publication) versions of selection, to turn the taxonomy into a forecasting tool.
4. Add gap closing when Luo & Evans's labels arrive.
5. Show case studies of papers in each quadrant of Figure 2.

## Reproduction

Each step reads the previous step's outputs. All are in the shaky-foundations track (`docs/tracks/shaky_foundations/`).

```bash
bash scripts/shaky_foundations/build_measures.sh        # CD, atom DSI / novelty, Fang F/E/G, Kedrick labels
bash scripts/shaky_foundations/build_prescience.sh      # prescience, adoption, emergence
bash scripts/shaky_foundations/analyze_factors_v3.sh    # correlations, parallel analysis, varimax loadings
bash scripts/shaky_foundations/taxonomy_figures.sh      # Figures 1-2, landmark factor scores
```

Outputs: `data/shaky_foundations/{measures_v2, prescience_v1, factors_v3, taxonomy_figures_v1}/`; figures in
`data/shaky_foundations/figures/`.

## References

- Boden, M. A. (2004). *The Creative Mind: Myths and Mechanisms*.
- Campbell, D. T. (1960). Blind variation and selective retention in creative thought as in other knowledge
  processes. *Psychological Review* 67, 380–400.
- Fang, H. & Evans, J. (2025). Generalization and the rise of system-level creativity in science.
  arXiv:2510.03240.
- Funk, R. J. & Owen-Smith, J. (2017). A dynamic network measure of technological change. *Management Science*
  63, 791–817.
- Kedrick, K. et al. (2026). Opening knowledge gaps drives scientific progress. arXiv:2509.21899.
- Lockhart, J. W., Sourati, J., Shi, F. & Evans, J. (2026). China leads scientific trends; the West launches
  new ones. arXiv:2603.01117.
- Shi, F. & Evans, J. (2023). Surprising combinations of research contents and contexts are related to impact
  and emerge with scientific outsiders from distant disciplines. *Nature Communications* 14.
- Simonton, D. K. (1999). Creativity as blind variation and selective retention: Is the creative process
  Darwinian? *Psychological Inquiry* 10, 309–328.
- Wu, L., Wang, D. & Evans, J. A. (2019). Large teams develop and small teams disrupt science and technology.
  *Nature* 566, 378–382.
