"""Aggregate the per-call API logs that run_experiment.py writes.

Each run writes `logs/api_calls.jsonl` inside its own output_dir. This walks a
root directory, sums them, and reports cost by model and by run. Anthropic calls
carry a null cost (the API returns no per-call price) and are counted separately
rather than silently treated as free.

    uv run python -m src.format_sensitivity.costs data/format_sensitivity
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_calls(root: Path) -> list[dict]:
    if not root.exists():
        raise FileNotFoundError(f"FATAL: no such directory: {root}")

    calls = []
    for log_path in sorted(root.glob("**/logs/api_calls.jsonl")):
        run = log_path.parent.parent.name
        with open(log_path) as f:
            for line in f:
                calls.append({**json.loads(line), "run": run})
    return calls


def summarize(calls: list[dict]) -> dict:
    by_model = defaultdict(lambda: {"calls": 0, "cost_usd": 0.0, "untracked": 0})
    by_run = defaultdict(lambda: {"calls": 0, "cost_usd": 0.0})

    for call in calls:
        model = call["model_requested"]
        cost = call["cost_usd"]

        by_model[model]["calls"] += 1
        by_run[call["run"]]["calls"] += 1

        if cost is None:
            by_model[model]["untracked"] += 1
        else:
            by_model[model]["cost_usd"] += cost
            by_run[call["run"]]["cost_usd"] += cost

    return {
        "total_calls": len(calls),
        "total_cost_usd": round(sum(c["cost_usd"] or 0.0 for c in calls), 6),
        "untracked_calls": sum(1 for c in calls if c["cost_usd"] is None),
        "by_model": {k: dict(v) for k, v in by_model.items()},
        "by_run": {k: dict(v) for k, v in by_run.items()},
    }


def main(root: str) -> None:
    calls = load_calls(Path(root))
    if not calls:
        print(f"No api_calls.jsonl found under {root}")
        return

    summary = summarize(calls)
    print(f"{summary['total_calls']} calls, ${summary['total_cost_usd']:.4f} tracked")
    if summary["untracked_calls"]:
        print(f"  ({summary['untracked_calls']} calls carry no per-call price)")

    print("\nBy model:")
    for model, stats in sorted(summary["by_model"].items()):
        note = f", {stats['untracked']} untracked" if stats["untracked"] else ""
        print(f"  {model:35} {stats['calls']:4} calls  ${stats['cost_usd']:.4f}{note}")

    print("\nBy run:")
    for run, stats in sorted(summary["by_run"].items()):
        print(f"  {run:45} {stats['calls']:4} calls  ${stats['cost_usd']:.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m src.format_sensitivity.costs <root_dir>")
    main(sys.argv[1])
