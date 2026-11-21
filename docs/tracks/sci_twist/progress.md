# Track: sci_twist

The discoverable scientific twist — the frontier-model successor to the retired
`time_capsule` track and to **TwistBench** (literary plot twists). Design memo:
[`docs/memos/interactive_frame_replacement_benchmark.md`](../../memos/interactive_frame_replacement_benchmark.md).

Flip TwistBench from *generation* (write a story with a twist) to *discovery* (find the twist
latent in the evidence). Contamination is solved at the **item level**: retrieval-resistant
synthetic surfaces whose answer is a **forced artifact** — a number only the correct reframe
can produce. This is what killed `format_sensitivity` (retrieval) and `time_capsule` (capability
floor), solved by construction.

## Status

**2026-07-18 — v1 prototype built and self-validated (no models run yet).**

The first move class is **property → relation** (a scalar was a projection of a 2-vector), realised
as the **Assay House** (`docs/memos/retrieval_resistant_environments.md`, Env A). The whole point of
starting here: it already **forces an exact number**, so we can prove the artifact grader is clean
before spending on interactivity, obfuscation, or an LLM judge.

### What runs and is verified (keyless)

```bash
bash scripts/sci_twist/selfcheck.sh     # or: python src/sci_twist/scripts/selfcheck.py
```

`selfcheck.py` builds both environments (they self-validate on construction) and grades a battery of
canned responses. Verified end to end under Python 3.12:

- **Exact-arithmetic validation** (`environment.py`, `fractions`, no floats): on the transformative
  instance it *proves* (1) no scalar potential fits the table — first contradiction at edge (D,E),
  and the cycle A→B→D→A has net gain **6 ≠ 0**, which a potential difference cannot; (2) the given
  data is rank-2 (every fully-known Pfaffian vanishes); (3) the reframe **over-determines** the
  held-out entry — three disjoint quads {A,B,C,E}, {A,C,D,E}, {B,C,D,E} each force **T(C,E) = +1**.
  A mis-built item crashes at construction, not at analysis.
- **The negative control** is the structural mirror: a genuine potential, where a scalar assignment
  *does* fit and loops vanish. Its validator asserts the opposite invariant.
- **The grader** (`grading.py`) labelled every fixture: transformative → SPECIES / STUCK_IN_M /
  WRONG_VALUE / NO_COMMIT; control → DEFENDS_M / OVERREACH. Grades the **artifact only** (exact match
  on the committed value); principle-scoring and epicycle-counting are deferred to a rubric judge
  rather than faked with keyword matching (the explicit `format_sensitivity` lesson).

### Prompt variants (the incumbency delta)

Rendered by `prompts.py`, all from one environment:

| Variant | Contains | Isolates |
|---|---|---|
| `WITH_M` | setting + data + observations + the avidity account & its epicycles | frame replacement (a wrong frame is present) |
| `WITHOUT_M` | setting + data + observations, no account | pure abduction (no incumbent) |
| `CONTROL` | the negative-control environment | over-reach (incumbent is correct) |

`species-rate(WITHOUT_M) − species-rate(WITH_M)` is the incumbency delta: how much a *stated* wrong
frame suppresses the leap. The anomaly is never announced in the ask — it lives in the observations,
to be noticed.

## Layout

```
src/sci_twist/
  environment.py              # TransferEnvironment + exact-arithmetic validation (the proof)
  environments/assay_house.py # canonical instance, random_instance(seed), negative control
  grading.py                  # artifact-exact-match grader (v1)
  prompts.py                  # WITH_M / WITHOUT_M / CONTROL renderers
  model.py                    # anthropic + openrouter, this-track-local (no cross-track import)
  scripts/selfcheck.py        # keyless proof (run this)
  scripts/run_assay_house.py  # config-driven live run
configs/sci_twist/assay_house_first_cut.yaml
scripts/sci_twist/{run_assay_house,selfcheck}.sh
```

## Next

1. **Run the first cut live.** `uv sync` + `ANTHROPIC_API_KEY`, then
   `bash scripts/sci_twist/run_assay_house.sh --overwrite`. Read the transcripts before trusting the
   grader; validate the value-extractor against hand labels (the `format_sensitivity` warning).
2. **Referent-naming probe** — after each answer, ask whether the scenario corresponds to a known
   phenomenon. If a model names exterior algebra / a real referent, the surface leaked.
3. **Randomized instances** — flip `seed` to confirm the forced value tracks the instance (retrieval-
   proof) and that species-rate is stable across instances.
4. **Second move class** — port The Trough (substance→process) or The Burrow (law→artifact); each
   forces a number and needs its own negative control.
5. **Interactive loop + hint ladder** (EscapeBench) — only after the static artifact grade is trusted.
6. **Rubric judge** for the principle and epicycle-count, validated against hand labels (TwistBench's
   3-judge + ICC pattern).

## Gotchas

- Repo has a **broken active `.venv`** (`VIRTUAL_ENV` points at a missing interpreter); `uv run`
  fails until you `env -u VIRTUAL_ENV` or re-create it with `uv sync`. System `python3` is 3.9;
  the code needs ≥3.11 (uses `X | None` annotations). Run under `uv --python 3.12` or a synced venv.
- Grading is **artifact-only** in v1 by design. Do not read a SPECIES label as "stated the principle";
  it means "committed the forced number." The principle needs the deferred rubric judge.
