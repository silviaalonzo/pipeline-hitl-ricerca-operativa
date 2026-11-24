#!/usr/bin/env python3
"""Annulla un falso handoff della replica 2 dovuto a soli alias equivalenti."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import run_replication_02 as replica


def append_amendment(entry: dict) -> None:
    path = replica.REPLICA_ROOT / "protocol_amendments.json"
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    payload.append(entry)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=("Cmem", "C0"), required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    protocol = replica.primary.load_protocol()
    replica.configure(args.condition, protocol)
    core = replica.primary.core
    row = next(
        item
        for item in replica.schedule_rows()
        if item["condition"] == args.condition and item["problem_id"] == args.problem
    )
    run_dir = replica.row_run_dir(row)
    state = core.load_json(run_dir / "state.json")
    if not state or state.get("status") != "AWAITING_HANDOFF":
        raise RuntimeError("La prova non è in attesa di handoff")

    handoff_dir = run_dir / state["pending_handoff"]
    response_path = handoff_dir / "expert_response.json"
    expert_response = core.load_json(response_path, {})
    if expert_response.get("status") == "SUBMITTED":
        raise RuntimeError("L'esperto ha già risposto: rivalidazione non ammessa")

    attempt_record = state["attempts"][-1]
    attempt_dir = run_dir / attempt_record["directory"]
    old_evaluation = attempt_record["evaluation"]
    text = (attempt_dir / "response.txt").read_text(encoding="utf-8")
    raw = core.load_json(attempt_dir / "response.json")
    new_evaluation = core.evaluate_response(
        state["problem_id"], text, raw, attempt_dir
    )
    if not new_evaluation.get("success"):
        raise RuntimeError(
            "La soluzione resta non corretta dopo la normalizzazione degli alias"
        )

    cancellation = {
        "status": "CANCELLED_INFRASTRUCTURE_FALSE_POSITIVE",
        "cancelled_at_utc": core.utc_now(),
        "reason": args.reason,
        "old_evaluation": old_evaluation,
        "new_evaluation": new_evaluation,
        "count_as_handoff": False,
        "count_as_human_time": False,
        "count_as_memory_event": False,
    }
    core.save_json(handoff_dir / "cancellation.json", cancellation)
    expert_response["status"] = "NOT_REQUIRED"
    expert_response["closed_at_utc"] = cancellation["cancelled_at_utc"]
    core.save_json(response_path, expert_response)

    attempt_record["evaluation"] = new_evaluation
    state["status"] = "RUNNING"
    state["pending_handoff"] = None
    core.save_state(run_dir, state)
    final = core.finalize_problem(
        run_dir,
        state,
        True,
        attempt_record,
        replica.condition_root(args.condition),
    )
    append_amendment(
        {
            "recorded_at_utc": cancellation["cancelled_at_utc"],
            "replicate": 2,
            "condition": args.condition,
            "problem_id": args.problem,
            "reason": args.reason,
            "action": "alias_normalization_and_false_handoff_cancellation",
            "count_as_handoff": False,
            "count_as_human_time": False,
            "run_dir": str(run_dir.relative_to(replica.REPLICA_ROOT)),
        }
    )
    print(f"Falso handoff annullato: {handoff_dir}")
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
