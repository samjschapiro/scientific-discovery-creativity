"""Restrict Haven's 100 to the discoveries a given time-capsule model could not have read.

Writes the eligible sample (and, separately, the excluded set and the ambiguous straddlers)
to output_dir. Downstream item-authoring reads only `eligible.json`.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.time_capsule.population import MODELS, eligible_sample, get_model
from src.utils import init_directory, load_config

REQUIRED_FIELDS = ["output_dir", "model"]


def validate_config(config: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field not in config:
            raise ValueError(f"FATAL: '{field}' is required in config")
    if config["model"] not in MODELS:
        raise ValueError(
            f"FATAL: unknown model '{config['model']}'. Known: {sorted(MODELS)}"
        )


def main(config_path: str, overwrite: bool = False, debug: bool = False) -> None:
    config = load_config(config_path)
    validate_config(config)

    max_gap = config.get("max_gap")  # optional; None = no gap ceiling
    model = get_model(config["model"])

    output_dir = init_directory(config["output_dir"], overwrite=overwrite)
    (output_dir / "results").mkdir()
    shutil.copy(config_path, output_dir / "config.yaml")

    sample = eligible_sample(config["model"], max_gap=max_gap)

    print(f"Model {model.name}: cutoff T_M = {model.cutoff}, {model.params}")
    if model.control_hf_id:
        print(f"  matched-compute control: {model.control_hf_id}")
    else:
        print("  WARNING: no matched-compute control released for this model — a null result "
              "cannot be separated from a capability floor.")
    print(f"  max_gap: {max_gap if max_gap is not None else 'none'}")
    print()
    print(f"Population: Haven's 100. Eligible (year > {model.cutoff}): {sample['n_eligible']}")

    for d in sample["eligible"]:
        print(f"  {d['year_first']:5}  (+{d['gap']:3}y)  {d['title']}")

    if sample["straddlers"]:
        print(f"\nAMBIGUOUS — multi-year span contains the cutoff ({sample['n_straddlers']}):")
        for d in sample["straddlers"]:
            print(f"  {d['years']}  {d['title']}  -- partly inside the model's world; "
                  f"decide by hand before use")

    for name, key in [("eligible", "eligible"), ("excluded", "excluded"),
                      ("straddlers", "straddlers")]:
        (output_dir / "results" / f"{name}.json").write_text(
            json.dumps(sample[key], indent=1)
        )
    (output_dir / "results" / "summary.json").write_text(
        json.dumps({k: v for k, v in sample.items()
                    if k not in ("eligible", "excluded", "straddlers")}, indent=1)
    )

    print(f"\nWrote {sample['n_eligible']} eligible discoveries to "
          f"{output_dir / 'results' / 'eligible.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", type=str)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args.config_path, args.overwrite, args.debug)
