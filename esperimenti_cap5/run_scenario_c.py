#!/usr/bin/env python3
"""Avanza la campagna ufficiale dello Scenario C fino al prossimo handoff."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from scenario_c_core import SCENARIO_ROOT, advance_problem, load_json, model_slug, problem_dir


def load_protocol() -> dict:
    path = SCENARIO_ROOT / "protocol.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Protocollo non congelato: eseguire prima freeze_scenario_c.py ({path})"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def schedule_rows() -> list[dict]:
    with (SCENARIO_ROOT / "schedule.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def row_status(row: dict) -> tuple[str, str]:
    run_dir = problem_dir(
        row["model"], int(row["problem_sequence"]), row["problem_id"]
    )
    final = load_json(run_dir / "final.json")
    if final:
        return ("COMPLETED" if final.get("correct") else "COMPLETED_FAILURE", str(run_dir))
    state = load_json(run_dir / "state.json")
    if state:
        return str(state.get("status", "RUNNING")), str(run_dir)
    return "PENDING", str(run_dir)


def print_status(rows: list[dict]) -> None:
    for model in dict.fromkeys(row["model"] for row in rows):
        model_rows = [row for row in rows if row["model"] == model]
        statuses = [row_status(row)[0] for row in model_rows]
        correct = 0
        handoff = 0
        for row in model_rows:
            run_dir = Path(row_status(row)[1])
            final = load_json(run_dir / "final.json", {})
            state = load_json(run_dir / "state.json", {})
            correct += int(bool(final.get("correct")))
            handoff += len(state.get("interventions", []))
            if state.get("status") == "AWAITING_HANDOFF":
                handoff += 1
        completed = sum(value.startswith("COMPLETED") for value in statuses)
        awaiting = sum(value == "AWAITING_HANDOFF" for value in statuses)
        print(
            f"{model}: completati {completed}/20; corretti {correct}; "
            f"in attesa di handoff {awaiting}; interventi registrati {handoff}"
        )


def first_incomplete_model(protocol: dict, rows: list[dict]) -> str | None:
    for model in protocol["model_order"]:
        model_rows = [row for row in rows if row["model"] == model]
        if any(not row_status(row)[0].startswith("COMPLETED") for row in model_rows):
            return model
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="mostra lo stato senza chiamare le API")
    parser.add_argument(
        "--model",
        help="avanza questo modello; deve essere il primo non ancora completato nell'ordine congelato",
    )
    parser.add_argument(
        "--max-problems", type=int, default=20, help="massimo numero di problemi da completare in questa invocazione"
    )
    args = parser.parse_args()

    protocol = load_protocol()
    rows = schedule_rows()
    if args.status:
        print_status(rows)
        return

    expected_model = first_incomplete_model(protocol, rows)
    if expected_model is None:
        print("Scenario C completato per tutti e tre i modelli.")
        return
    model = args.model or expected_model
    if model != expected_model:
        raise RuntimeError(
            f"Per preservare l'ordine congelato bisogna completare prima {expected_model}; richiesto {model}."
        )

    model_rows = [row for row in rows if row["model"] == model]
    advanced = 0
    print(f"Avvio/continuazione di {model} ({len(model_rows)} problemi)")
    for row in model_rows:
        status, _ = row_status(row)
        if status.startswith("COMPLETED"):
            continue
        if advanced >= args.max_problems:
            break
        result = advance_problem(
            model,
            row["problem_id"],
            int(row["problem_sequence"]),
        )
        if result["status"] == "AWAITING_HANDOFF":
            print(f"HANDOFF RICHIESTO: {result['handoff_dir']}")
            print("La campagna è stata sospesa prima del problema successivo.")
            raise SystemExit(4)
        advanced += 1
        final = result.get("final") or {}
        print(
            f"[{row['problem_sequence']}/20] {row['problem_id']}: "
            f"{'CORRETTO' if final.get('correct') else 'NON CORRETTO'}; "
            f"tentativi={final.get('attempt_count')}; handoff={final.get('handoff_count')}"
        )

    print_status(rows)


if __name__ == "__main__":
    main()
