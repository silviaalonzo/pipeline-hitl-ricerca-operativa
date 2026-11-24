#!/usr/bin/env python3
"""Ricostruisce risultati e metriche dello Scenario C dai soli log grezzi."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from scenario_c_core import SCENARIO_ROOT, api_usage_for_attempt, load_json, problem_dir, save_json


DETAIL_PATH = SCENARIO_ROOT / "REGISTRO_SCENARIO_C.csv"
INTERVENTIONS_PATH = SCENARIO_ROOT / "INTERVENTI_ESPERTO.csv"
SUMMARY_PATH = SCENARIO_ROOT / "RISULTATI_PROGRESSIVI_SCENARIO_C.json"
FINAL_SUMMARY_PATH = SCENARIO_ROOT / "RISULTATI_DEFINITIVI_SCENARIO_C.json"


def load_schedule() -> list[dict]:
    with (SCENARIO_ROOT / "schedule.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sum_usage(run_dir: Path, state: dict) -> dict:
    total = defaultdict(float)
    for attempt in state.get("attempts", []):
        usage = api_usage_for_attempt(run_dir / attempt["directory"])
        for key, value in usage.items():
            total[key] += float(value or 0)
    return dict(total)


def detail_rows(schedule: list[dict]) -> list[dict]:
    rows = []
    for scheduled in schedule:
        run_dir = problem_dir(
            scheduled["model"], int(scheduled["problem_sequence"]), scheduled["problem_id"]
        )
        state = load_json(run_dir / "state.json", {})
        final = load_json(run_dir / "final.json", {})
        usage = sum_usage(run_dir, state)
        pending = state.get("status") == "AWAITING_HANDOFF"
        interventions = state.get("interventions", [])
        traceability_repairs = sum(
            1 for item in state.get("attempts", []) if item.get("kind") == "TRACEABILITY_REPAIR"
        )
        code_repairs = sum(
            1 for item in state.get("attempts", []) if item.get("kind") == "AUTO_REPAIR"
        )
        stages = [str(item["stage"]) for item in interventions]
        if pending:
            handoff_dir = run_dir / state["pending_handoff"]
            packet = load_json(handoff_dir / "packet.json", {})
            if packet.get("stage") is not None:
                stages.append(str(packet["stage"]))
        rows.append(
            {
                "global_order": scheduled["global_order"],
                "model_order": scheduled["model_order"],
                "model": scheduled["model"],
                "problem_sequence": scheduled["problem_sequence"],
                "problem_id": scheduled["problem_id"],
                "difficulty": scheduled["difficulty"],
                "domain": scheduled["domain"],
                "model_class": scheduled["model_class"],
                "status": state.get("status", "PENDING"),
                "correct": "" if not final else int(bool(final.get("correct"))),
                "pass": "" if not final else int(bool(final.get("pass"))),
                "attempt_count": len(state.get("attempts", [])),
                "automatic_repair_count": traceability_repairs + code_repairs,
                "traceability_repair_count": traceability_repairs,
                "code_repair_count": code_repairs,
                "handoff_count_completed": len(interventions),
                "assurance_review_count": sum(
                    1 for item in interventions if item.get("handoff_mode") == "ASSURANCE_REVIEW"
                ),
                "corrective_handoff_count": sum(
                    1 for item in interventions if item.get("action") == "CORRECT"
                ),
                "handoff_pending": int(pending),
                "handoff_stages": ";".join(stages),
                "human_minutes": sum(float(item.get("active_minutes", 0)) for item in interventions),
                "assurance_review_minutes": sum(
                    float(item.get("active_minutes", 0))
                    for item in interventions
                    if item.get("action") == "APPROVE"
                ),
                "correction_minutes": sum(
                    float(item.get("active_minutes", 0))
                    for item in interventions
                    if item.get("action") == "CORRECT"
                ),
                "memory_semantic_retrieved": len((state.get("memory_retrieval") or {}).get("semantic", [])),
                "memory_episodic_retrieved": len((state.get("memory_retrieval") or {}).get("episodic", [])),
                "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                "completion_tokens": int(usage.get("completion_tokens", 0)),
                "reasoning_tokens": int(usage.get("reasoning_tokens", 0)),
                "total_tokens": int(usage.get("total_tokens", 0)),
                "api_cost_usd": usage.get("api_cost_usd", 0.0),
                "response_seconds": usage.get("response_seconds", 0.0),
                "run_directory": str(run_dir),
            }
        )
    return rows


def intervention_rows(schedule: list[dict]) -> list[dict]:
    rows = []
    for scheduled in schedule:
        run_dir = problem_dir(
            scheduled["model"], int(scheduled["problem_sequence"]), scheduled["problem_id"]
        )
        state = load_json(run_dir / "state.json", {})
        for item in state.get("interventions", []):
            rows.append(
                {
                    "model": scheduled["model"],
                    "problem_sequence": scheduled["problem_sequence"],
                    "problem_id": scheduled["problem_id"],
                    "handoff_number": item["handoff_number"],
                    "stage": item["stage"],
                    "failure_class": item["failure_class"],
                    "handoff_mode": item.get("handoff_mode", "CORRECTION"),
                    "active_minutes": item["active_minutes"],
                    "action": item["action"],
                    "correction_summary": item["correction_summary"],
                    "semantic_principle": item.get("semantic_principle", ""),
                    "memory_committed": int(bool(item.get("memory_committed"))),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict], interventions: list[dict]) -> dict:
    summary: dict = {"scenario": "C", "models": {}}
    for model in dict.fromkeys(row["model"] for row in rows):
        subset = [row for row in rows if row["model"] == model]
        completed = [row for row in subset if row["correct"] != ""]
        correct = sum(int(row["correct"]) for row in completed)
        human_minutes = sum(float(row["human_minutes"]) for row in subset)
        accuracy = correct / len(completed) if completed else None
        handoffs_by_stage = Counter()
        handoffs_by_action = Counter()
        for item in interventions:
            if item["model"] == model:
                handoffs_by_stage[str(item["stage"])] += 1
                handoffs_by_action[str(item["action"])] += 1
        model_summary = {
            "completed": len(completed),
            "correct": correct,
            "accuracy": accuracy,
            "human_minutes": human_minutes,
            "efficiency_correct_problems_per_human_hour": (
                correct / (human_minutes / 60.0) if human_minutes > 0 else None
            ),
            "automatic_repairs": sum(int(row["automatic_repair_count"]) for row in subset),
            "completed_handoffs": sum(int(row["handoff_count_completed"]) for row in subset),
            "pending_handoffs": sum(int(row["handoff_pending"]) for row in subset),
            "handoffs_by_stage": dict(sorted(handoffs_by_stage.items())),
            "handoffs_by_action": dict(sorted(handoffs_by_action.items())),
            "assurance_review_minutes": sum(
                float(row["assurance_review_minutes"]) for row in subset
            ),
            "correction_minutes": sum(float(row["correction_minutes"]) for row in subset),
            "api_cost_usd": sum(float(row["api_cost_usd"]) for row in subset),
            "response_seconds": sum(float(row["response_seconds"]) for row in subset),
            "total_tokens": sum(int(row["total_tokens"]) for row in subset),
        }
        summary["models"][model] = model_summary
    summary["total"] = {
        "completed": sum(item["completed"] for item in summary["models"].values()),
        "correct": sum(item["correct"] for item in summary["models"].values()),
        "human_minutes": sum(item["human_minutes"] for item in summary["models"].values()),
        "api_cost_usd": sum(item["api_cost_usd"] for item in summary["models"].values()),
    }
    return summary


def main() -> None:
    schedule = load_schedule()
    details = detail_rows(schedule)
    interventions = intervention_rows(schedule)
    write_csv(DETAIL_PATH, details)
    intervention_fields = [
        "model", "problem_sequence", "problem_id", "handoff_number", "stage", "failure_class",
        "handoff_mode", "active_minutes", "action", "correction_summary", "semantic_principle",
        "memory_committed",
    ]
    write_csv(INTERVENTIONS_PATH, interventions, intervention_fields)
    summary = build_summary(details, interventions)
    save_json(SUMMARY_PATH, summary)
    campaign_complete = bool(details) and all(
        row["status"] in {"COMPLETED", "COMPLETED_FAILURE"}
        and not int(row["handoff_pending"])
        for row in details
    )
    if campaign_complete:
        save_json(FINAL_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Registro: {DETAIL_PATH}")
    print(f"Interventi: {INTERVENTIONS_PATH}")
    if campaign_complete:
        print(f"Riepilogo definitivo: {FINAL_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
