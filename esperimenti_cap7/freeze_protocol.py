#!/usr/bin/env python3
"""Congela dataset, memoria, ordine e configurazione dell'ablation del Capitolo 7."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
DATASET = ROOT / "dataset_cap7"
SOURCE_MEMORY = ROOT / "scenario_c" / "memory" / "deepseek-v4-flash.json"
PROTOCOL = HERE / "protocol.json"
SCHEDULE = HERE / "schedule.csv"
MODEL_KEY = "deepseek-v4-flash"
MAX_OUTPUT_TOKENS = 64000

PAIR_ORDER = [
    ("L01", ("C0", "Cmem")),
    ("L02", ("Cmem", "C0")),
    ("L03", ("C0", "Cmem")),
    ("L04", ("Cmem", "C0")),
    ("L05", ("C0", "Cmem")),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def empty_memory(timestamp: str) -> dict:
    return {
        "schema_version": 1,
        "model": MODEL_KEY,
        "created_at_utc": timestamp,
        "updated_at_utc": timestamp,
        "episodic": [],
        "semantic": [],
    }


def validate_inputs() -> None:
    records = [
        json.loads(line)
        for line in (DATASET / "problems.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expected = {f"L{i:02d}" for i in range(1, 6)}
    if {row["id"] for row in records} != expected:
        raise AssertionError("Il dataset non contiene esattamente L01–L05")
    if {row.get("dataset_version") for row in records} != {"definitivo_v2"}:
        raise AssertionError("Il dataset attivo non è la versione definitiva v2")
    ground_truth = json.loads((DATASET / "ground_truth.json").read_text(encoding="utf-8"))
    if {row["id"] for row in ground_truth} != expected:
        raise AssertionError("Gli ID della ground truth non coincidono con i prompt")
    memory = json.loads(SOURCE_MEMORY.read_text(encoding="utf-8"))
    if memory.get("model") != MODEL_KEY:
        raise AssertionError("Lo snapshot appartiene a un modello diverso")
    if len(memory.get("episodic", [])) != 5 or len(memory.get("semantic", [])) != 5:
        raise AssertionError("Sono attese cinque voci episodiche e cinque semantiche")


def artifact_hashes() -> dict[str, str]:
    paths = [
        HERE / "freeze_protocol.py",
        HERE / "run_ablation.py",
        HERE / "check_setup.py",
        HERE / "cap7_aliases.py",
        HERE / "system_prompt_cap7.txt",
        ROOT / "esperimenti_cap5" / "scenario_c_core.py",
        ROOT / "esperimenti_cap5" / "system_prompt_repair_c.txt",
        ROOT / "esperimenti_cap5" / "models.json",
        DATASET / "problems.jsonl",
        DATASET / "ground_truth.json",
        DATASET / "build_dataset_cap7.py",
        DATASET / "verify_with_gurobi.py",
        DATASET / "audit_target_patterns.py",
        DATASET / "solutions_summary.csv",
        DATASET / "verification_report.json",
        DATASET / "target_pattern_audit.json",
        SOURCE_MEMORY,
    ]
    paths.extend(sorted((DATASET / "prompts").glob("L[0-9][0-9].md")))
    return {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def main() -> None:
    validate_inputs()
    if PROTOCOL.exists() or SCHEDULE.exists():
        raise FileExistsError("Il protocollo del Capitolo 7 è già congelato e non può essere sovrascritto")

    timestamp = datetime.now(timezone.utc).isoformat()
    conditions = HERE / "conditions"
    cmem_memory = conditions / "Cmem" / "memory" / f"{MODEL_KEY}.json"
    c0_memory = conditions / "C0" / "memory" / f"{MODEL_KEY}.json"
    cmem_memory.parent.mkdir(parents=True, exist_ok=False)
    c0_memory.parent.mkdir(parents=True, exist_ok=False)
    shutil.copy2(SOURCE_MEMORY, cmem_memory)
    c0_memory.write_text(
        json.dumps(empty_memory(timestamp), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    rows = []
    global_order = 0
    for pair_sequence, (problem_id, order) in enumerate(PAIR_ORDER, start=1):
        for within_pair, condition in enumerate(order, start=1):
            global_order += 1
            rows.append(
                {
                    "global_order": global_order,
                    "pair_sequence": pair_sequence,
                    "within_pair": within_pair,
                    "problem_id": problem_id,
                    "condition": condition,
                    "model": MODEL_KEY,
                    "status": "PENDING",
                }
            )

    with SCHEDULE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    protocol = {
        "schema_version": 1,
        "chapter": 7,
        "experiment": "paired_memory_ablation",
        "dataset_version": "definitivo_v2",
        "frozen_at_utc": timestamp,
        "model": MODEL_KEY,
        "model_configuration": {
            "reasoning_effort": "high",
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "gateway": "OpenRouter",
            "required_upstream_provider": "deepseek",
            "fallbacks": False,
        },
        "problem_ids": [row[0] for row in PAIR_ORDER],
        "executions": 10,
        "replicates_per_condition_problem": 1,
        "order": rows,
        "conditions": {
            "Cmem": "snapshot congelato con cinque episodi e cinque principi semantici",
            "C0": "memoria vuota e congelata",
        },
        "memory_updates_during_test": False,
        "same_components_except_memory": True,
        "preliminary_calibration": {
            "excluded_from_results": True,
            "reason": (
                "il primo insieme di cinque istanze ha prodotto un effetto soffitto: entrambe "
                "le condizioni hanno risolto tutti i problemi e non si sono verificate "
                "correzioni umane. Prima del congelamento del protocollo definitivo sono "
                "quindi aumentate dimensione e densità relazionale delle istanze"
            ),
            "archive": "archivio_cap7/calibrazione_v1_20260826",
            "used_in_main_analysis": False,
        },
        "memory_snapshot_source": str(SOURCE_MEMORY.relative_to(ROOT)),
        "memory_sha256": {
            "Cmem": sha256(cmem_memory),
            "C0": sha256(c0_memory),
        },
        "gates": {
            "traceability_repairs": 1,
            "self_repairs": 3,
            "solver_timeout_seconds": 300,
            "relative_gap_tolerance": 0.001,
            "assurance_review_after_repair_on_high_difficulty": True,
        },
        "artifact_sha256": artifact_hashes(),
    }
    PROTOCOL.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(PROTOCOL)
    print(SCHEDULE)
    print(f"Cmem: {cmem_memory}")
    print(f"C0: {c0_memory}")


if __name__ == "__main__":
    main()
