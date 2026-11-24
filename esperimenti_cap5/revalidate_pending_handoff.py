#!/usr/bin/env python3
"""Rivalida un falso handoff causato esclusivamente dall'infrastruttura sperimentale."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from scenario_c_core import (
    SCENARIO_ROOT,
    evaluate_response,
    finalize_problem,
    load_json,
    save_json,
    save_state,
    utc_now,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    state = load_json(run_dir / "state.json")
    if not state or state.get("status") != "AWAITING_HANDOFF":
        raise RuntimeError("Il run non è in attesa di handoff")
    handoff_dir = run_dir / state["pending_handoff"]
    response = load_json(handoff_dir / "expert_response.json", {})
    if response.get("status") == "SUBMITTED":
        raise RuntimeError("L'esperto ha già risposto: la rivalidazione tecnica non è più ammessa")

    attempt_record = state["attempts"][-1]
    attempt_dir = run_dir / attempt_record["directory"]
    text = (attempt_dir / "response.txt").read_text(encoding="utf-8")
    raw = load_json(attempt_dir / "response.json")
    old_evaluation = attempt_record["evaluation"]
    new_evaluation = evaluate_response(state["problem_id"], text, raw, attempt_dir)
    if not new_evaluation.get("success"):
        raise RuntimeError(
            "La correzione infrastrutturale non ha eliminato il fallimento; l'handoff resta necessario"
        )

    cancellation = {
        "status": "CANCELLED_INFRASTRUCTURE_FALSE_POSITIVE",
        "cancelled_at_utc": utc_now(),
        "reason": args.reason,
        "old_evaluation": old_evaluation,
        "new_evaluation": new_evaluation,
        "count_as_handoff": False,
        "count_as_human_time": False,
        "count_as_memory_event": False,
    }
    save_json(handoff_dir / "cancellation.json", cancellation)
    response["status"] = "NOT_REQUIRED"
    response["closed_at_utc"] = utc_now()
    save_json(handoff_dir / "expert_response.json", response)

    attempt_record["evaluation"] = new_evaluation
    state["status"] = "RUNNING"
    state["pending_handoff"] = None
    save_state(run_dir, state)
    final = finalize_problem(run_dir, state, True, attempt_record)

    amendment_path = SCENARIO_ROOT / "protocol_amendments.json"
    amendments = load_json(amendment_path, [])
    amendments.append(
        {
            "recorded_at_utc": utc_now(),
            "type": "validator_alias_normalization",
            "reason": args.reason,
            "affected_run": str(run_dir.relative_to(SCENARIO_ROOT)),
            "evaluation_criterion_changed": False,
            "ground_truth_disclosed_to_model_or_expert": False,
            "validator_sha256_after_amendment": {
                "audit_scenario_b.py": hashlib.sha256(
                    (Path(__file__).resolve().parent / "audit_scenario_b.py").read_bytes()
                ).hexdigest(),
                "revalidate_aliases.py": hashlib.sha256(
                    (Path(__file__).resolve().parent / "revalidate_aliases.py").read_bytes()
                ).hexdigest(),
            },
        }
    )
    save_json(amendment_path, amendments)
    print(f"Falso handoff annullato: {handoff_dir}")
    print(f"Problema rivalidato come corretto: {final['problem_id']}")


if __name__ == "__main__":
    main()
