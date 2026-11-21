# Format Sensitivity: Obfuscating Environments #1 and #2

Testing the interpretation offered on 7/9: *"LLMs are capable of transformational creativity if
the problem is presented in an easy-to-parse fashion... context gets muddied and evidence is not
presented or obtained in a linear fashion... the model's representation of the scenario becomes
fragmented, which constrains the abductive leap."*

That is a causal claim about presentation. It is testable by holding content fixed and varying
only the packaging.

## The design constraint that governs everything here

**Every format variant must contain every atomic fact. No additions, no deletions.**

If a fragmented variant quietly drops "no seed has ever been found," we have not measured format
sensitivity — we have measured what happens when you delete the key anomaly. The two are
indistinguishable after the fact. So each environment gets a numbered fact inventory, and each
variant is annotated with a coverage map. Coverage is checkable mechanically before any model
sees a stimulus.

The facts may be *reordered*, *split across documents*, *stated in different registers*, and
*surrounded by irrelevant material*. They may not be removed, and nothing may be added.

---

## Fact inventory — Environment #1 (The Hillside)

| # | Fact |
|---|---|
| F1 | A gardener counts stems and calls each one a plant |
| F2 | Each stem has its own leaves |
| F3 | Each stem has its own roots near the surface |
| F4 | Each stem dies back in winter and regrows |
| F5 | The count is careful and has been kept for years |
| F6 | Stems across the whole hillside flush their leaves within a day of one another |
| F7 | Stems shed within a day of one another |
| F8 | The north face receives far less sun and water than the south face |
| F9 | Cut a hundred stems in one place → within a week new stems appear at the margins |
| F10 | The number of new stems is proportional to how many were cut |
| F11 | The new stems appear in places distant from the cutting |
| F12 | Strip the leaves from a single stem → days later, stems tens of paces away thicken their leaves |
| F13 | No seed of this plant has ever been found |
| F14 | Soil samples turn up nothing unusual |
| F15 | Standing account: many separate plants, coordinated by environment and by chemical signals through the soil |
| F16 | Epicycle: a wounding signal, posited to explain the leaf-thickening |
| F17 | Epicycle: a density signal, posited to explain the regrowth at the margins |
| F18 | The account has never failed |

## Fact inventory — Environment #2 (Lanterns and Clingers)

| # | Fact |
|---|---|
| G1 | Deep-water fishers bring up a large fish, catalogued as the lantern |
| G2 | Every lantern ever landed has been female, without exception, across many decades of records |
| G3 | No male lantern has ever been caught |
| G4 | Attached to most lanterns are one or more small creatures, catalogued separately as clingers |
| G5 | Clingers are universally regarded as parasites |
| G6 | The clinger is never found free-swimming as an adult |
| G7 | Its mouth is fused to the lantern's flank |
| G8 | Dissection shows the two share blood vessels |
| G9 | The attached clinger has no working gut |
| G10 | Its nostrils are enormous relative to its body |
| G11 | Its eyes are large in the young and shrunken in those that have attached |
| G12 | Clingers are found on lanterns and on nothing else |
| G13 | Young free-swimming clingers are occasionally netted; they have a gut |
| G14 | Young free-swimming clingers do not feed |
| G15 | Standing account: the clinger is a parasite exquisitely specialised to this one host |
| G16 | Epicycle: the lost gut is degeneration from parasitic life |
| G17 | Epicycle: the great nostrils are an organ for locating the host |
| G18 | Epicycle: the absence of males is a sampling problem — males presumed small, rare, passing through the nets |

---

## Conditions

Two crossed factors, plus a dilution knob.

**Factor 1 — Presentation.**

| Code | Format | What it varies |
|---|---|---|
| **F0** | Narrative prose (the original) | baseline |
| **F1** | Bare observation table | is the prose helping or hurting? |
| **F2** | Chronological field log | linearity of *discovery*, not of exposition |
| **F3** | Multi-source document bundle | integration across sources |
| **F4** | Diluted log (F2 + irrelevant entries) | signal-to-noise, holding structure fixed |
| **F5** | Confident review article | resistance to an authoritative wrong frame |

**Factor 2 — Prompt framing.**

| Code | Prompt | What it varies |
|---|---|---|
| **P-puzzle** | *"How do you explain what's happening?"* | the original — signals that a puzzle exists |
| **P-mundane** | *"Draft the summary paragraph for the station's annual report."* | no puzzle cue; must notice unprompted |

`P-mundane` is not a minor variant. The original prompt tells the model that an explanation is
wanted, which in context means the standing account is up for revision. Real normal science hands
you no such cue. I expect this to be the single largest effect in the study, larger than any
format manipulation, and it is nearly free to run.

**Dilution.** For F4, irrelevant-entry ratio ∈ {1×, 3×}. Irrelevant entries are plausible,
well-formed, and carry zero bearing on the anomalies (weather, fencing, staff changes, a different
species, instrument recalibration).

Document order within F3 should be **randomized per sample**. Otherwise "bundle" is just "narrative
with headings."

---

## The two controls that make this interpretable

Without these, a drop in jump-rate under fragmentation is uninterpretable.

### Control 1 — Comprehension check

After the model answers, in a fresh context, give it the same stimulus and ask:

> List every observation recorded about the hillside. Do not explain them.

Score recall against the fact inventory.

This separates two very different failure modes. If the model recalls 18/18 facts from the
fragmented bundle but does not jump, its representation is *intact* and the **leap** is what
fragmentation broke — which is the doc's claim, and a real finding. If it recalls 12/18, then
fragmentation broke **reading**, and the abduction result is a downstream artifact of a
comprehension failure. These look identical in the jump-rate column and mean opposite things.

I expect this control to explain a large fraction of whatever effect we find, and I'd rather know.

### Control 2 — Referent-naming probe

After the model answers, ask in a fresh context:

> Does this scenario correspond to any real phenomenon you are aware of? Name it.

Record whether the model names *clonal colonies / rhizomatous growth* (Env #1) or
*anglerfish / sexual parasitism / Ceratioidei* (Env #2).

This is a covariate, not a condition, and it matters because two hypotheses predict the same
format effect for opposite reasons:

- **Hypothesis R (retrieval).** Models solve #1 and #2 by recognizing the real-world referent from
  surface features. Fragmenting the surface degrades recognition. The jump was never abductive.
- **Hypothesis A (abduction).** Models genuinely reconstruct the frame from the anomalies.
  Fragmenting degrades the working representation and constrains the leap.

Both predict "fragmentation hurts." They are separated by whether the referent gets named, and by
whether jump-rate tracks naming-rate across conditions. Grok's existing transcripts name their
referents unprompted ("genet", "suborder Ceratioidei"), which is at least suggestive of R.

*(The retrieval-resistant environments in the sibling memo are the clean way to break this tie —
they have no referent to name. Parked for now, but this is the experiment that will want them.)*

---

## Scoring

Grade every response on two independent axes. **Do not collapse them.** The gap between them is
the "slop transformation" failure mode, quantified.

**Axis 1 — Reframe (the genus).**

| Grade | Criterion |
|---|---|
| `JUMP` | Commits to the reframe as *the* answer |
| `JUMP-HEDGED` | Offers the reframe among several hypotheses, commits to none |
| `EPICYCLE` | Commits to the standing account, supplemented with further posited mechanisms |
| `MISS` | Neither |

**Axis 2 — Consequence (the species).** Does the response state something that follows *only*
from the reframe and not from the standing account? For the Hillside, the strongest available:
*the absence of seed is not a gap in the record — it is predicted, because propagation is
vegetative.* For the Lanterns: *the male-to-female ratio in the catch is not skewed at all once
the clingers are counted as lanterns.*

Note that #1 and #2 have **no forced numerical artifact** — this is their central weakness as
instruments, and Axis 2 is doing what it can without one. A model can score `JUMP` on Axis 1 with
a fluent verbal reframe and still fail Axis 2 entirely. That combination is the result worth
hunting for.

**Also log:** epicycle count (number of newly posited mechanisms), turns-to-jump (multi-turn
conditions), and referent-named (bool).

---

## Pre-registered predictions

Writing these down before running anything, so we cannot retrofit the story.

| Condition | Predicted effect on jump-rate | If violated, what it means |
|---|---|---|
| F1 (table) | ≈ F0, maybe higher | prose was never load-bearing |
| F2 (log) | small drop | discovery-order alone is not the mechanism |
| F3 (bundle) | large drop | integration across sources is the bottleneck |
| F4 (diluted) | large drop, scaling with dilution | attention/salience, not representation |
| F5 (review) | largest drop | authoritative framing suppresses revision |
| P-mundane | very large drop across all formats | models reframe when asked to, not when warranted |

If **F1 ≥ F0** and **F3 ≪ F0**, the doc's linearity claim survives in a sharpened form: it is not
*prose* linearity that matters but whether the anomalies can be **co-located in one representation**.

If **P-mundane ≈ 0 everywhere**, the headline finding is not about format at all. It is that these
models do not *notice* anomalies; they *resolve* anomalies once told one exists. That is a more
interesting paper than the format result, and it directly attacks "LLMs can jump."

---

# Stimuli — Environment #1 (The Hillside)

## F0 — Narrative (baseline, unchanged)

Reproduce verbatim from the project doc. Not restated here.

## F1 — Bare observation table

> **Hillside plot. Recorded observations.**
>
> | # | Observation |
> |---|---|
> | 1 | Stems are counted individually. Each counted stem is recorded as one plant. |
> | 2 | Each stem bears its own leaves. |
> | 3 | Each stem has its own roots, near the surface. |
> | 4 | Each stem dies back in winter and regrows. |
> | 5 | The count has been kept carefully, for years. |
> | 6 | Stems across the whole hillside flush their leaves within a day of one another. |
> | 7 | Stems across the whole hillside shed within a day of one another. |
> | 8 | The north face receives far less sun and water than the south face. |
> | 9 | Where a hundred stems were cut, new stems appeared at the margins within a week. |
> | 10 | The number of new stems was proportional to the number cut. |
> | 11 | The new stems appeared in places distant from the cutting. |
> | 12 | Where the leaves were stripped from a single stem, stems tens of paces away thickened their own leaves within days. |
> | 13 | No seed of this plant has ever been found. |
> | 14 | Soil samples show nothing unusual. |
>
> **Standing account.** These are many separate plants, coordinated by their shared environment and
> by chemical signals passing between them through the soil. A wounding signal accounts for
> observation 12. A density signal accounts for observations 9–11. The account has never failed.

Coverage: F1–F18. ✅

## F2 — Chronological field log

Facts appear in the order a station would have encountered them. Anomalies are never marked as
anomalies. The standing account accretes rather than being stated.

> **REGISTER OF THE HILLSIDE PLOT — kept by successive wardens**
>
> **Year 1, third month.** Census of the hillside begun. Each stem counted as one plant; this is
> the convention adopted and it will be held to. 1,240 plants recorded. Each stem carries its own
> leaves and puts down its own roots, which run near the surface and are easily lifted with a
> trowel.
>
> **Year 1, tenth month.** All stems have died back. Warden notes the plot appears empty. Expect
> regrowth.
>
> **Year 2, fourth month.** Regrowth confirmed; 1,251 plants. Census procedure unchanged and will
> be kept to annually.
>
> **Year 2, fourth month, later.** Curious. The flush was not staggered. Walked the plot on the
> 9th: nothing. Walked it on the 10th: leaves everywhere, north face and south alike. Note that
> the north face lies in shade for most of the day and takes perhaps a third of the rainfall the
> south face does. One would expect it to lag by a week.
>
> **Year 2, tenth month.** The shed was likewise within a day, across the whole hillside.
>
> **Year 3.** No seed has been found. The warden has looked. His predecessor looked. We have
> sieved the leaf litter across four seasons and there is nothing.
>
> **Year 4, second month.** At the direction of the station, a hundred stems were cut from the
> eastern quarter, to test whether the plot would thin.
>
> **Year 4, second month, ninth day.** New stems have appeared. Not where we cut. They have come
> up at the margins of the plot, a good distance off. Counted 96. The proportion is close enough to
> what was taken that the warden remarks on it.
>
> **Year 5.** Soil samples drawn at nine stations and sent for analysis. Returned: nothing unusual.
> No unusual mineral, no unusual organism.
>
> **Year 6, fifth month.** An accident. A stem near the path was stripped of its leaves by a
> passing cart. Four days later the warden noticed that stems well away from the path — thirty
> paces, forty — had thickened their own leaves noticeably. He measured. The effect is real.
>
> **Year 6, seventh month.** Discussed at the station. The consensus is that the plants
> communicate through the soil. A signal passing between the roots would explain the synchrony
> handsomely, and the roots do lie close together.
>
> **Year 7.** Following the events of Year 6, a *wounding signal* is proposed, released by an
> injured plant and read by its neighbours. This accounts for the leaf-thickening.
>
> **Year 7, later.** A *density signal* is proposed, by which the plants sense how many of them
> remain and grow accordingly. This accounts for the margin regrowth of Year 4.
>
> **Year 12.** Twelve years of records. The account has met every observation the plot has produced,
> and no observation has yet contradicted it.

Coverage: F1–F18. ✅ (F1,F2,F3 Yr1 · F4 Yr1–2 · F5 Yr2 · F6,F8 Yr2 · F7 Yr2 · F13 Yr3 · F9,F10,F11
Yr4 · F14 Yr5 · F12 Yr6 · F15 Yr6 · F16,F17 Yr7 · F18 Yr12)

## F3 — Multi-source bundle

Five documents. **No single document contains more than three of the anomalies.** The most
striking anomaly (F12) is on an undated slip. Present in randomized order.

> ### DOCUMENT A — Census ledger, cover sheet
>
> Hillside plot. Stems counted individually; each stem entered as one plant. Roots near surface,
> proper to each stem. Leaves proper to each stem. Stems die back each winter and regrow. Count
> kept annually, without a gap, for twelve years.
>
> Annual totals: 1240, 1251, 1249, 1263, 1258, 1266, 1271, 1268, 1279, 1274, 1281, 1277.
>
> *Marginal note, different hand:* No seed of this plant has ever been found, in twelve years of
> sieving. Recorded here for want of anywhere better to put it.
>
> ---
>
> ### DOCUMENT B — Phenology table, station appendix
>
> | Year | First flush, south face | First flush, north face | First shed, south | First shed, north |
> |---|---|---|---|---|
> | 8 | 4th month, day 10 | 4th month, day 10 | 10th month, day 2 | 10th month, day 3 |
> | 9 | 4th month, day 12 | 4th month, day 13 | 10th month, day 1 | 10th month, day 1 |
> | 10 | 4th month, day 9 | 4th month, day 9 | 9th month, day 30 | 10th month, day 1 |
> | 11 | 4th month, day 14 | 4th month, day 14 | 10th month, day 4 | 10th month, day 4 |
>
> *Footnote:* The north face lies in shade for the greater part of the day and receives roughly a
> third of the rainfall of the south face. The station has no explanation for the agreement of the
> dates and has ceased to remark on it.
>
> ---
>
> ### DOCUMENT C — Coppicing trial, summary of results
>
> One hundred stems were cut from the eastern quarter in the second month of Year 4, to establish
> whether the plot could be thinned by cutting.
>
> It could not. Within one week, ninety-six new stems were counted. None arose at the site of the
> cutting. All arose at the margins of the plot, at distances of forty to seventy paces from the
> cut. The trial was repeated at two hundred stems in Year 9; one hundred and ninety-four new stems
> arose, again at the margins. The response is proportional to the injury and displaced from it.
>
> ---
>
> ### DOCUMENT D — Letter from the station's soil chemist
>
> With regard to the nine samples: I regret that I can report nothing unusual. No mineral out of
> the ordinary, no organism I do not expect to find in any hillside soil of this type.
>
> I remain convinced that the soil is nonetheless where the answer lies. If these plants are
> coordinating their flush and their shed across ground as different as your north and south faces,
> they must be signalling to one another, and the soil is the only medium available to them. Their
> roots lie close.
>
> I would add to the picture two further signals, which I think the station must accept. A
> **wounding signal**, released by an injured plant, would explain the thickening you describe in
> your slip. A **density signal**, by which a plant senses how many of its fellows remain, would
> explain the margin growth in the coppicing trial.
>
> The account is not yet complete but it has not failed us, and I do not see what would replace it.
>
> ---
>
> ### DOCUMENT E — Undated slip, found loose in the ledger
>
> Stem by the path stripped by a cart. Four days on — stems thirty and forty paces off have
> thickened their leaves. Measured twice. Not imagination.

Coverage: F1–F18. ✅ (A: F1–F5, F13 · B: F6, F7, F8 · C: F9, F10, F11 · D: F14, F15, F16, F17, F18 ·
E: F12)

**Note on why this is the strong condition.** In F3 the wrong frame is embedded in the *structure*
of the evidence, not merely asserted in its prose. The ledger's columns presuppose that a stem is a
plant. To reframe, the model must reject the schema of Document A, not just disagree with the
argument of Document D.

## F4 — Diluted log

F2 verbatim, with irrelevant entries interleaved at 1× and 3× the count of substantive entries.
Irrelevant entries must be plausible, well-formed, and inert. Examples:

> **Year 2, sixth month.** The lower fence was carried away in a storm and has been rebuilt in
> chestnut. Cost recorded in the station accounts.
>
> **Year 3, second month.** A badger has taken up residence at the eastern boundary. The warden
> proposes to leave it undisturbed.
>
> **Year 4, eighth month.** The station's rain gauge was found to read 4% low and has been
> recalibrated. Prior figures should be adjusted accordingly.
>
> **Year 5, first month.** Warden Hallett has retired after nineteen years. Warden Pryce succeeds
> him. The census procedure is unchanged.
>
> **Year 6, ninth month.** A stand of birch on the ridge above the plot was thinned for timber. It
> is not thought to bear on the plot, which lies below and to the south.

Generate these programmatically from a fixed pool so dilution is reproducible, and hold the
substantive entries byte-identical to F2.

## F5 — Confident review article

Every anomaly stated, and each immediately dispatched. The standing account is presented as
settled science by a confident insider. Tests whether the model will revise a frame that no one
has invited it to revise.

> ### The Hillside Plant: A Review of Twelve Years' Observation
>
> The hillside plant is now among the better-understood members of the station's flora, and the
> account given here may be regarded as secure.
>
> The plant grows as a stem, bearing its own leaves and putting down its own shallow roots. It dies
> back in winter and regrows in spring. Our census, kept without a gap for twelve years, counts each
> stem as one individual — a convention which has served us well and which the reader may take as
> given.
>
> The plants of the hillside are notable for the precision of their coordination. Flush and shed
> occur across the whole hillside within a single day, notwithstanding that the north face lies in
> shade and receives a third of the rainfall of the south. *This is no longer mysterious.* The
> plants signal to one another through the soil, in which their roots lie densely intermingled;
> chemical communication of this kind is well attested and requires no special pleading here.
>
> Two further signals complete the picture. When the leaves of a single stem were stripped, stems
> tens of paces distant thickened their own leaves within days — the action of a **wounding
> signal**, released by the injured plant and read by its neighbours. And when a hundred stems were
> cut, ninety-six new stems arose at the plot's margins, proportional to the injury and displaced
> from it — the action of a **density signal**, by which each plant senses how many of its fellows
> remain and grows to fill the deficit.
>
> Two minor matters remain outstanding, neither of which troubles the account. Soil analysis has
> returned nothing unusual, which is unsurprising: signalling compounds of this kind are expected at
> concentrations far below what our chemist can detect. And no seed of the plant has ever been
> found, despite twelve years of sieving. Seed of this type is small and easily overlooked, and we
> anticipate its discovery in due course.
>
> The account has met every observation the plot has produced. Nothing has contradicted it.

Coverage: F1–F18. ✅

**Design note.** F5 adds no facts, but it does add *endorsement*. The two dismissals in the final
paragraph — the undetectable signal and the overlooked seed — are epicycles the doc's own taxonomy
predicts a model will produce on its own. Here they are pre-supplied. If a model that jumps under
F0 declines to jump under F5, the finding is that it is not defending a frame of its own; it is
adopting whichever frame the document holds.

---

# Stimuli — Environment #2 (Lanterns and Clingers)

The same ladder applies. F0 and F1 are mechanical; F2 and F5 follow the Hillside templates. F3 is
given in full because it carries the environment's strongest obfuscation.

## F3 — Multi-source bundle

The wrong frame lives in the **accession structure**: lanterns and clingers occupy different
catalogue series, curated by different departments. To reframe, the model must merge two catalogue
entries that the archive's own schema keeps apart.

> ### DOCUMENT A — Catch record summary, deep-water fishery, forty-one seasons
>
> *Species: LANTERN (accession series L-) — a large deep-water fish*
>
> Total landed: 2,314. Sex determined by dissection in all cases where the specimen permitted
> (n = 2,301). **Female: 2,301. Male: 0.**
>
> No male lantern has been landed in forty-one seasons of record.
>
> *Standing note, appended by the curator:* The absence of males is a sampling artefact. The male
> is presumed small, rare, and of a size to pass through the nets. The fishery's gear is not
> designed to retain him.
>
> ---
>
> ### DOCUMENT B — Parasite catalogue, invertebrate & ectoparasite department
>
> *Species: CLINGER (accession series P-) — a small animal, a minor fraction of the host's bulk*
>
> Recovered from: LANTERN (series L-), on which most specimens bear one or more. Recovered from no
> other host. Never taken free-swimming as an adult.
>
> Attachment: the mouth is fused to the host's flank. Dissection of the attachment site shows the
> blood vessels of parasite and host to be continuous.
>
> *Curator's note:* The clinger is a parasite of remarkable specificity, its adaptations to the
> parasitic life among the most complete known to this department.
>
> ---
>
> ### DOCUMENT C — Dissection notes, attached specimens (P-series)
>
> Gut: present but non-functional. Reduced to a cord. No specimen has been found with stomach
> contents.
>
> Nostrils: enormous. Out of all proportion to the head. In P-0114 the olfactory apparatus occupies
> a greater volume than the brain.
>
> Eyes: shrunken, in every attached specimen examined.
>
> ---
>
> ### DOCUMENT D — Plankton net records, juvenile survey
>
> Occasional take of small free-swimming animals referable to the clinger (P-series, juvenile).
>
> These possess a complete and apparently functional gut. **No specimen has ever been taken with
> food in it.** None has been observed to feed, in the net or in the tank; those held alive did not
> feed and did not survive.
>
> Eyes large. Nostrils large.
>
> ---
>
> ### DOCUMENT E — Departmental memorandum
>
> On the clinger's degenerate gut: this is straightforwardly the degeneration expected of a
> parasite, which draws nourishment from its host and has no use for a gut of its own.
>
> On the clinger's great nostrils: an organ for locating the host, in a dark ocean where hosts are
> few. The parasite must find its lantern.
>
> Both features are precisely what the parasitic life would produce. The account is settled and the
> department does not propose to revisit it.

Coverage: G1–G18. ✅ (A: G1, G2, G3, G18 · B: G4, G5, G6, G7, G8, G12 · C: G9, G10, G11 ·
D: G13, G14 · E: G15, G16, G17)

**Why this bundle is harder than the Hillside's.** Two of the reframe's load-bearing facts —
*the juvenile has a working gut* (D) and *the juvenile does not feed* (D) — sit in a document about
plankton nets, filed by a different survey, and read as routine. The male-less catch (A) and the
gutless attached specimen (C) never appear on the same page. The reframe requires joining A + C + D
across three curatorial boundaries, against a schema that has already assigned the two animals to
different accession series and different departments.

If a model jumps on F0 and not on F3, **this is the document that will tell us what broke** — check
the comprehension control to see whether it retrieved G13 and G14 at all.

---

## Running it

Full grid: 2 environments × 6 formats × 2 framings × {dilution levels for F4} × N models × K samples,
plus 2 control probes per cell in fresh contexts. Cheap. Randomize document order within F3 per
sample. Keep substantive text byte-identical across F2 and F4.

Suggested first cut before building anything: **Env #2, F0 vs F3, P-puzzle vs P-mundane, one model,
K = 20.** Four cells. If F3×P-mundane does not collapse, the whole hypothesis is in trouble and we
should find that out in an afternoon rather than after building a harness.

## What still needs deciding

- **Grader.** Axis 1 is close to mechanical; Axis 2 needs either a rubric-following LLM judge with
  the reference consequence supplied, or human grading on the first few hundred. Do not let a judge
  grade Axis 1 and Axis 2 in one call — the whole point is that they dissociate, and a single call
  will smear them.
- **F2/F4 substantive-entry parity** must be enforced in code, not by eye.
- **Multi-turn.** The doc's `Multi-turn` and `multi-agent` conditions are orthogonal to this and
  should not be crossed in until the single-turn format effect is characterized.
