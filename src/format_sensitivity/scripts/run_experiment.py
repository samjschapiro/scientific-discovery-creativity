"""Generate model responses across format x framing cells for the Hillside environment.

Grading is downstream work — this script only collects raw responses.
"""

import argparse
import json
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.format_sensitivity import stimuli
from src.format_sensitivity.coverage import validate_skin
from src.format_sensitivity.model import PROVIDERS, build_provider
from src.format_sensitivity.skins import REGISTRY, get_skin
from src.utils import init_directory, load_config

REQUIRED_FIELDS = [
    "output_dir",
    "skin",
    "provider",
    "model",
    "max_tokens",
    "thinking",
    "effort",
    "max_workers",
    "seed",
    "formats",
    "framings",
    "probes",
    "n_samples",
]


def validate_config(config: dict) -> None:
    for field in REQUIRED_FIELDS:
        if field not in config:
            raise ValueError(f"FATAL: '{field}' is required in config")

    if config["provider"] not in PROVIDERS:
        raise ValueError(
            f"FATAL: unknown provider '{config['provider']}'. Known: {sorted(PROVIDERS)}"
        )

    if config["skin"] not in REGISTRY:
        raise ValueError(
            f"FATAL: unknown skin '{config['skin']}'. Known: {sorted(REGISTRY)}"
        )

    skin = get_skin(config["skin"])
    unsupported = set(config["formats"]) - set(skin.supported_formats)
    if unsupported:
        raise ValueError(
            f"FATAL: skin '{skin.name}' does not provide formats {sorted(unsupported)}. "
            f"Provides: {list(skin.supported_formats)}"
        )

    unknown_framings = set(config["framings"]) - set(stimuli.FRAMINGS)
    if unknown_framings:
        raise ValueError(f"FATAL: unknown framings {sorted(unknown_framings)}")

    unknown_probes = set(config["probes"]) - set(stimuli.PROBES)
    if unknown_probes:
        raise ValueError(f"FATAL: unknown probes {sorted(unknown_probes)}")


def build_tasks(config: dict) -> list[dict]:
    """One task per API call.

    Main tasks vary over format x framing x sample. Probe tasks vary over
    format x probe x sample only — a probe asks about the stimulus, not about
    the framing, so running it once per framing would duplicate identical calls.
    """
    tasks = []

    for sample in range(config["n_samples"]):
        seed = config["seed"] + sample

        for format_code in config["formats"]:
            for framing in config["framings"]:
                tasks.append(
                    {
                        "kind": "main",
                        "format": format_code,
                        "framing": framing,
                        "probe": None,
                        "sample": sample,
                        "seed": seed,
                        "instruction": stimuli.FRAMINGS[framing],
                    }
                )

            for probe in config["probes"]:
                tasks.append(
                    {
                        "kind": "probe",
                        "format": format_code,
                        "framing": None,
                        "probe": probe,
                        "sample": sample,
                        "seed": seed,
                        "instruction": stimuli.PROBES[probe],
                    }
                )

    return tasks


def run_task(provider, config: dict, task: dict) -> dict:
    prompt = stimuli.build_prompt(
        config["skin"], task["format"], task["instruction"], task["seed"]
    )

    result = provider.complete(
        prompt=prompt,
        model=config["model"],
        max_tokens=config["max_tokens"],
        thinking=config["thinking"],
        effort=config["effort"],
    )

    return {
        **task,
        "skin": config["skin"],
        "provider": provider.name,
        "model_requested": config["model"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "response": result,
    }


def call_log_entry(record: dict) -> dict:
    """One audit line per API call. `generation_id` reconciles against the
    OpenRouter dashboard; `cost_usd` is what OpenRouter billed, not an estimate."""
    response = record["response"]
    return {
        "timestamp": record["timestamp"],
        "provider": record["provider"],
        "model_requested": record["model_requested"],
        "model_returned": response["model_returned"],
        "generation_id": response["generation_id"],
        "cost_usd": response["cost_usd"],
        "usage": response["usage"],
        "kind": record["kind"],
        "format": record["format"],
        "framing": record["framing"],
        "probe": record["probe"],
        "sample": record["sample"],
        "finish_reason": response["finish_reason"],
    }


def main(config_path: str, overwrite: bool = False, debug: bool = False) -> None:
    config = load_config(config_path)
    validate_config(config)

    if debug:
        config["n_samples"] = 1
        config["max_workers"] = 1
        print(f"DEBUG MODE: n_samples=1, max_workers=1, output_dir={config['output_dir']}")

    output_dir = init_directory(config["output_dir"], overwrite=overwrite)
    (output_dir / "results").mkdir()
    (output_dir / "logs").mkdir()
    shutil.copy(config_path, output_dir / "config.yaml")

    # Information must be held constant across a skin's formats. Prove it before spending.
    validate_skin(config["skin"], seed=config["seed"])
    skin = get_skin(config["skin"])
    print(f"Coverage OK: skin '{skin.name}', {len(skin.facts)} slots, "
          f"formats {config['formats']}.")

    tasks = build_tasks(config)
    print(
        f"Skin '{skin.name}': {len(tasks)} calls queued "
        f"to {config['provider']}/{config['model']}."
    )

    provider = build_provider(config["provider"])
    responses_path = output_dir / "results" / "responses.jsonl"
    call_log_path = output_dir / "logs" / "api_calls.jsonl"
    write_lock = threading.Lock()
    completed = 0
    total_cost = 0.0

    with open(responses_path, "w") as out, open(call_log_path, "w") as log, (
        ThreadPoolExecutor(max_workers=config["max_workers"])
    ) as pool:
        futures = {pool.submit(run_task, provider, config, task): task for task in tasks}

        for future in as_completed(futures):
            record = future.result()
            entry = call_log_entry(record)

            with write_lock:
                out.write(json.dumps(record) + "\n")
                out.flush()
                log.write(json.dumps(entry) + "\n")
                log.flush()

                completed += 1
                total_cost += entry["cost_usd"] or 0.0
                cost = f"${entry['cost_usd']:.4f}" if entry["cost_usd"] is not None else "n/a"
                print(
                    f"  [{completed}/{len(tasks)}] {record['kind']:5} "
                    f"{record['format']} "
                    f"{(record['framing'] or record['probe']):14} "
                    f"sample={record['sample']:<3} {cost}"
                )

    summary = {
        "provider": config["provider"],
        "model_requested": config["model"],
        "calls": completed,
        "total_cost_usd": round(total_cost, 6),
        "cost_accounted": provider.name == "openrouter",
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / "results" / "cost_summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\nWrote {completed} responses to {responses_path}")
    print(f"Per-call audit log: {call_log_path}")
    if summary["cost_accounted"]:
        print(f"Total cost: ${total_cost:.4f} over {completed} calls "
              f"(${total_cost / completed:.4f}/call)")
    else:
        print("Cost: not reported by this provider (Anthropic returns no per-call price).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", type=str, help="Path to config file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output directory")
    parser.add_argument("--debug", action="store_true", help="Debug mode: 1 sample, serial")
    args = parser.parse_args()

    main(args.config_path, args.overwrite, args.debug)
