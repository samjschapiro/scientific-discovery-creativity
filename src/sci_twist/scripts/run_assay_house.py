"""Run the Assay House first cut against a model.

The story, line by line:
  1. Load + validate the config (output_dir required; fail fast).
  2. Build the transformative environment (canonical or a seeded random instance) and,
     if requested, the negative control. Both self-validate on construction.
  3. For each cell (variant x sample), render the prompt, call the model, grade the
     artifact, and log one record.
  4. Write results.jsonl, a summary, and the exact prompts — reproducibility first.

The incumbency delta is the point of running WITH_M and WITHOUT_M together: the gap in
species-rate between them is how much a stated wrong frame suppresses the leap.

The clean automated grade is exact match on the held-out value. Principle-level scoring
and epicycle counting are left to a later rubric-judge pass (see grading.py) — this
script records the raw text so that pass can run downstream without re-querying models.

    uv run python src/sci_twist/scripts/run_assay_house.py configs/sci_twist/assay_house_first_cut.yaml --overwrite
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.utils import init_directory, load_config
from src.sci_twist import model as model_api
from src.sci_twist.environments import assay_house
from src.sci_twist.grading import grade
from src.sci_twist.prompts import render


def _build_environments(config: dict):
    """The transformative item (canonical or seeded-random) plus the optional control."""
    seed = config.get("seed")
    env = assay_house.build() if seed is None else assay_house.random_instance(seed)
    envs = {"WITH_M": env, "WITHOUT_M": env}
    if config.get("include_control", True):
        envs["CONTROL"] = assay_house.build_negative_control()
    return envs


def main(config_path, overwrite=False, debug=False):
    config = load_config(config_path)
    if "output_dir" not in config:
        raise ValueError("FATAL: 'output_dir' is required in config")
    for field in ("provider", "model", "variants"):
        if field not in config:
            raise ValueError(f"FATAL: '{field}' is required in config")

    output_dir = init_directory(config["output_dir"], overwrite=overwrite)
    (output_dir / "prompts").mkdir()
    (output_dir / "logs").mkdir()

    # Reproducibility: keep the exact config used for this run.
    with open(output_dir / "config.yaml", "w") as f:
        import yaml
        yaml.safe_dump(config, f, sort_keys=False)

    envs = _build_environments(config)
    variants = config["variants"]
    samples = 1 if debug else int(config.get("samples", 1))
    max_tokens = int(config.get("max_tokens", 4096))
    thinking = config.get("thinking", "adaptive")
    effort = config.get("effort", "high")

    # Persist the exact prompt for every variant.
    for v in variants:
        (output_dir / "prompts" / f"{v}.txt").write_text(render(envs[v], v))

    records = []
    for v in variants:
        env = envs[v]
        prompt = render(env, v)
        for s in range(samples):
            resp = model_api.complete(
                prompt=prompt, provider=config["provider"], model=config["model"],
                max_tokens=max_tokens, thinking=thinking, effort=effort,
            )
            g = grade(env, resp["text"])
            rec = {
                "variant": v, "sample": s, "env": env.name, "kind": env.kind,
                "provider": config["provider"], "model": config["model"],
                "grade": {**asdict(g), "committed_value": str(g.committed_value),
                          "forced_value": str(g.forced_value)},
                "text": resp["text"], "reasoning": resp.get("reasoning"),
                "cost_usd": resp.get("cost_usd"), "generation_id": resp.get("generation_id"),
            }
            records.append(rec)
            print(f"[{v} s{s}] {env.name}: {g.label} (committed {g.committed_value}, forced {g.forced_value})")

    with open(output_dir / "results.jsonl", "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    # Species-rate per variant — the headline number, and the incumbency delta between variants.
    summary = {}
    for v in variants:
        cell = [r for r in records if r["variant"] == v]
        hits = sum(1 for r in cell if r["grade"]["label"] in ("SPECIES", "DEFENDS_M"))
        summary[v] = {"n": len(cell), "species_or_defend": hits,
                      "rate": hits / len(cell) if cell else None}
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nsummary: {json.dumps(summary)}")
    print(f"wrote {len(records)} records to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", type=str)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true", help="one sample per cell")
    args = parser.parse_args()
    main(args.config_path, args.overwrite, args.debug)
