#!/usr/bin/env python3
"""Registra in modo strutturato l'intervento umano richiesto dallo Scenario C."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from scenario_c_core import load_json, save_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff-dir", type=Path, required=True)
    parser.add_argument("--minutes", type=float, required=True)
    parser.add_argument("--instruction", default="")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--principle", default="")
    parser.add_argument(
        "--accept-failure",
        action="store_true",
        help="chiude il problema come non corretto senza chiedere una nuova soluzione al modello",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="approva una soluzione dopo la revisione di assicurazione dello Stadio 2",
    )
    args = parser.parse_args()

    handoff_dir = args.handoff_dir.resolve()
    packet_path = handoff_dir / "packet.json"
    response_path = handoff_dir / "expert_response.json"
    if not packet_path.exists() or not response_path.exists():
        raise FileNotFoundError(f"Cartella di handoff non valida: {handoff_dir}")
    current = load_json(response_path, {})
    if current.get("status") == "SUBMITTED":
        raise RuntimeError("Questo handoff contiene già una risposta dell'esperto e non può essere sovrascritto")
    if args.minutes <= 0:
        raise ValueError("Il tempo attivo deve essere maggiore di zero")
    if args.accept_failure and args.approve:
        raise ValueError("--approve e --accept-failure sono mutuamente esclusivi")
    packet = load_json(packet_path, {})
    if args.approve:
        action = "APPROVE"
    elif args.accept_failure:
        action = "ACCEPT_FAILURE"
    else:
        action = "CORRECT"
    allowed_actions = set(packet.get("allowed_actions") or ["CORRECT", "ACCEPT_FAILURE"])
    if action not in allowed_actions:
        raise ValueError(f"L'azione {action} non è ammessa per questo handoff")
    if action == "CORRECT" and not args.instruction.strip():
        raise ValueError("Per correggere il problema è necessaria un'istruzione precisa")

    response = {
        "status": "SUBMITTED",
        "action": action,
        "active_minutes": args.minutes,
        "expert_instruction": args.instruction.strip(),
        "correction_summary": args.summary.strip(),
        "semantic_principle": args.principle.strip(),
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(response_path, response)
    print(f"Intervento registrato in {response_path}")
    print("Rieseguire run_scenario_c.py per applicare la correzione e continuare la sequenza.")


if __name__ == "__main__":
    main()
