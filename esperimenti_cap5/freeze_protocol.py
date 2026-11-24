#!/usr/bin/env python3
"""Congela protocollo e sequenza dello Scenario B prima della campagna completa."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import random
from datetime import datetime, timezone
from pathlib import Path

import gurobipy as gp
import openai

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEED = 20260810
MODELS = ["gpt-5.6-sol", "claude-sonnet-5", "deepseek-v4-flash"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_schedule() -> list[dict]:
    pilots = [
        {"model": "gpt-5.6-sol", "problem_id": "M01", "replicate": 1},
        {"model": "claude-sonnet-5", "problem_id": "M01", "replicate": 1},
        {"model": "deepseek-v4-flash", "problem_id": "M01", "replicate": 1},
    ]
    all_rows = [
        {"model": model, "problem_id": f"{prefix}{number:02d}", "replicate": replicate}
        for model in MODELS
        for prefix in ("M", "H")
        for number in range(1, 11)
        for replicate in (1, 2, 3)
    ]
    pilot_keys = {(row["model"], row["problem_id"], row["replicate"]) for row in pilots}
    remaining = [
        row for row in all_rows
        if (row["model"], row["problem_id"], row["replicate"]) not in pilot_keys
    ]
    random.Random(SEED).shuffle(remaining)
    schedule = pilots + remaining
    for sequence, row in enumerate(schedule, start=1):
        row["sequence"] = sequence
    return schedule


def main() -> None:
    schedule_path = HERE / "batch_schedule.csv"
    manifest_path = HERE / "protocol_manifest.json"
    if schedule_path.exists() or manifest_path.exists():
        raise FileExistsError("Protocollo già congelato; non sovrascrivere i file esistenti")

    schedule = make_schedule()
    with schedule_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sequence", "model", "problem_id", "replicate"])
        writer.writeheader()
        writer.writerows(schedule)

    hashed_files = [
        HERE / "system_prompt.txt",
        HERE / "models.json",
        HERE / "run_scenario_b.py",
        HERE / "execute_response.py",
        HERE / "validate_candidate.py",
        ROOT / "dataset_cap4" / "ground_truth.json",
        *sorted((ROOT / "dataset_cap4" / "prompts").glob("[MH][0-9][0-9].md")),
    ]
    manifest = {
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": "B",
        "schedule_seed": SEED,
        "n_runs": len(schedule),
        "n_pilots_already_completed": 3,
        "gateway": "OpenRouter",
        "routing": {
            "provider_official_only": True,
            "allow_fallbacks": False,
            "require_parameters": True,
            "reasoning_effort": "high",
        },
        "models": json.loads((HERE / "models.json").read_text(encoding="utf-8")),
        "runtime": {
            "python": platform.python_version(),
            "gurobipy": ".".join(map(str, gp.gurobi.version())),
            "openai_sdk": openai.__version__,
        },
        "sha256": {str(path.relative_to(ROOT)): sha256(path) for path in hashed_files},
        "schedule_sha256": sha256(schedule_path),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Protocollo congelato: {manifest_path}")
    print(f"Sequenza: {schedule_path} ({len(schedule)} run)")


if __name__ == "__main__":
    main()

