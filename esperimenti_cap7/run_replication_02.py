#!/usr/bin/env python3
"""Esegue la seconda replica completa dell'ablation del Capitolo 7."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import run_ablation as primary


HERE = Path(__file__).resolve().parent
REPLICA_ROOT = HERE / "replica_02"
SCHEDULE = REPLICA_ROOT / "schedule.csv"
PROTOCOL = REPLICA_ROOT / "protocol_replica.json"
MODEL_KEY = "deepseek-v4-flash"

# Ordine globale inverso rispetto alla campagna principale. In questo modo,
# per ogni problema, si inverte anche quale condizione viene eseguita per prima.
PAIR_ORDER = [
    ("L05", ("Cmem", "C0")),
    ("L04", ("C0", "Cmem")),
    ("L03", ("Cmem", "C0")),
    ("L02", ("C0", "Cmem")),
    ("L01", ("Cmem", "C0")),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def condition_root(condition: str) -> Path:
    if condition not in {"C0", "Cmem"}:
        raise ValueError(condition)
    return REPLICA_ROOT / "conditions" / condition


def memory_file(condition: str) -> Path:
    return condition_root(condition) / "memory" / f"{MODEL_KEY}.json"


def schedule_rows() -> list[dict]:
    with SCHEDULE.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_run_dir(row: dict) -> Path:
    return primary.core.problem_dir(
        row["model"],
        int(row["pair_sequence"]),
        row["problem_id"],
        condition_root(row["condition"]),
    )


def row_status(row: dict) -> str:
    run_dir = row_run_dir(row)
    final = primary.core.load_json(run_dir / "final.json")
    if final:
        return "COMPLETED" if final.get("correct") else "COMPLETED_FAILURE"
    state = primary.core.load_json(run_dir / "state.json")
    return str((state or {}).get("status", "PENDING"))


def setup() -> None:
    if PROTOCOL.exists() or SCHEDULE.exists():
        raise FileExistsError("La replica 2 è già stata predisposta")
    timestamp = datetime.now(timezone.utc).isoformat()
    primary_protocol = primary.load_protocol()

    for condition in ("C0", "Cmem"):
        destination = memory_file(condition)
        destination.parent.mkdir(parents=True, exist_ok=False)
        shutil.copy2(primary.memory_file(condition), destination)

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
                    "replicate": 2,
                }
            )

    with SCHEDULE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    record = {
        "schema_version": 1,
        "chapter": 7,
        "experiment": "paired_memory_ablation_robustness_replication",
        "replicate": 2,
        "created_at_utc": timestamp,
        "primary_protocol_sha256": sha256(HERE / "protocol.json"),
        "primary_schedule_sha256": sha256(HERE / "schedule.csv"),
        "primary_results_sha256": sha256(HERE / "RISULTATI_DEFINITIVI_CAP7.json"),
        "same_dataset_prompt_model_solver_gates": True,
        "memory_updates_during_test": False,
        "order_reversed_from_primary": True,
        "executions": 10,
        "conditions": primary_protocol["conditions"],
        "memory_sha256": {
            condition: sha256(memory_file(condition))
            for condition in ("C0", "Cmem")
        },
        "order": rows,
    }
    PROTOCOL.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(PROTOCOL)
    print(SCHEDULE)


def configure(condition: str, protocol: dict) -> None:
    # Le funzioni del runner principale risolvono condition_root a runtime.
    # Il monkey-patch sposta soltanto gli artefatti della replica in una cartella
    # separata; configurazione e logica sperimentale restano identici.
    primary.condition_root = condition_root
    primary.memory_file = memory_file
    primary.configure_core(condition, protocol)
    core = primary.core

    base_call = core.call_openrouter
    base_new_state = core.new_state
    base_finalize = core.finalize_problem

    def tagged_call(model_name, system, user_prompt, attempt_dir, metadata):
        metadata = dict(metadata)
        metadata["replicate"] = 2
        return base_call(model_name, system, user_prompt, attempt_dir, metadata)

    def tagged_new_state(model_name, problem, sequence, retrieval):
        state = base_new_state(model_name, problem, sequence, retrieval)
        state["replicate"] = 2
        return state

    def tagged_finalize(run_dir, state, correct, final_attempt, scenario_root):
        result = base_finalize(
            run_dir, state, correct, final_attempt, scenario_root
        )
        result["replicate"] = 2
        core.save_json(run_dir / "final.json", result)
        return result

    core.call_openrouter = tagged_call
    core.new_state = tagged_new_state
    core.finalize_problem = tagged_finalize

    expected = json.loads(PROTOCOL.read_text(encoding="utf-8"))["memory_sha256"][condition]
    actual = sha256(memory_file(condition))
    if actual != expected or actual != protocol["memory_sha256"][condition]:
        raise RuntimeError(f"Lo snapshot {condition} della replica non coincide con il primario")


def print_status(rows: list[dict]) -> None:
    completed = 0
    for row in rows:
        status = row_status(row)
        completed += int(status.startswith("COMPLETED"))
        print(
            f"{int(row['global_order']):02d}/10  {row['problem_id']}  "
            f"{row['condition']:<4}  {status}"
        )
    print(f"Completate: {completed}/10")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--max-runs", type=int, default=10)
    args = parser.parse_args()

    if args.setup:
        setup()
        return
    if not PROTOCOL.exists() or not SCHEDULE.exists():
        raise FileNotFoundError("Eseguire prima --setup")

    primary_protocol = primary.load_protocol()
    rows = schedule_rows()
    if args.status:
        print_status(rows)
        return

    advanced = 0
    for row in rows:
        status = row_status(row)
        if status.startswith("COMPLETED"):
            continue
        if advanced >= args.max_runs:
            break
        condition = row["condition"]
        configure(condition, primary_protocol)
        before = sha256(memory_file(condition))
        result = primary.core.advance_problem(
            row["model"],
            row["problem_id"],
            int(row["pair_sequence"]),
            scenario_root=condition_root(condition),
        )
        after = sha256(memory_file(condition))
        if before != after:
            raise RuntimeError(f"La memoria {condition} è cambiata durante la replica")
        if result["status"] == "AWAITING_HANDOFF":
            print(f"HANDOFF RICHIESTO — {row['problem_id']} {condition} / replica 2")
            print(result["handoff_dir"])
            raise SystemExit(4)
        final = result.get("final") or {}
        print(
            f"[{row['global_order']}/10] {row['problem_id']} {condition}: "
            f"{'CORRETTO' if final.get('correct') else 'NON CORRETTO'}; "
            f"tentativi={final.get('attempt_count')}; "
            f"handoff={final.get('handoff_count')}"
        )
        advanced += 1

    print_status(rows)


if __name__ == "__main__":
    main()
