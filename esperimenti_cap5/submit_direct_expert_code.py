#!/usr/bin/env python3
"""Applica a un handoff un modello Python/Gurobi fornito direttamente dall'esperto.

Il modello matematico non viene riscritto né rinviato all'LLM. Il programma viene
eseguito nello stesso ambiente isolato usato per gli output automatici; la
soluzione Gurobi in formato ``.sol`` viene poi convertita nel formato interno e
sottoposta alla validazione indipendente dello Stadio 4.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path

from execute_response import parse_solution, static_check
from scenario_c_core import (
    definitive_validation,
    execute_code,
    finalize_problem,
    load_json,
    save_json,
    save_state,
    utc_now,
)


OBJECTIVE_RE = re.compile(r"^# Objective value\s*=\s*(.+?)\s*$")


def parse_gurobi_sol(path: Path) -> dict:
    """Legge il formato testuale ``.sol`` prodotto da Gurobi."""
    objective = None
    variables: dict[str, float] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = OBJECTIVE_RE.match(line)
        if match:
            objective = float(match.group(1))
            continue
        if line.startswith("#"):
            continue
        name, value = line.rsplit(maxsplit=1)
        variables[name] = float(value)
    if objective is None:
        raise ValueError(f"Valore obiettivo non trovato in {path}")
    if not variables:
        raise ValueError(f"Nessuna variabile trovata in {path}")
    return {"status": "OPTIMAL", "objective": objective, "variables": variables}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--minutes", type=float, required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--principle", default="")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    source = args.source.resolve()
    state_path = run_dir / "state.json"
    state = load_json(state_path)
    if state is None:
        raise FileNotFoundError(state_path)
    if state.get("status") != "AWAITING_HANDOFF" or not state.get("pending_handoff"):
        raise RuntimeError("Il problema non è in attesa di handoff")
    if args.minutes <= 0:
        raise ValueError("Il tempo attivo deve essere maggiore di zero")
    if not source.is_file():
        raise FileNotFoundError(source)

    handoff_dir = run_dir / state["pending_handoff"]
    packet = load_json(handoff_dir / "packet.json")
    if "CORRECT" not in set(packet.get("allowed_actions") or ["CORRECT", "ACCEPT_FAILURE"]):
        raise RuntimeError("Questo handoff non ammette una correzione diretta")
    response_path = handoff_dir / "expert_response.json"
    response = load_json(response_path, {})
    if response.get("status") == "SUBMITTED":
        raise RuntimeError("Questo handoff contiene già una risposta dell'esperto")

    code = source.read_text(encoding="utf-8")
    static_check(code)
    source_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()

    attempt_number = len(state.get("attempts", []))
    attempt_dir = run_dir / f"attempt_{attempt_number:02d}"
    if attempt_dir.exists():
        raise FileExistsError(attempt_dir)
    attempt_dir.mkdir(parents=True)
    shutil.copy2(source, attempt_dir / "expert_source.py")
    save_json(
        attempt_dir / "request.json",
        {
            "scenario": "C",
            "problem_id": state["problem_id"],
            "problem_sequence": state["problem_sequence"],
            "attempt_number": attempt_number,
            "attempt_kind": "EXPERT_DIRECT_CODE",
            "source_path": str(source),
            "source_sha256": source_hash,
            "api_call": False,
            "created_at_utc": utc_now(),
        },
    )

    execution = execute_code(code, attempt_dir)
    if execution.get("timed_out"):
        raise RuntimeError("Il modello fornito dall'esperto ha superato il timeout")
    if execution.get("returncode") != 0:
        raise RuntimeError(
            "Il modello fornito dall'esperto non è stato eseguito correttamente: "
            + str(execution.get("stderr") or execution.get("stdout") or "")
        )
    solution_files = sorted(attempt_dir.glob("*.sol"))
    if len(solution_files) == 1:
        candidate = parse_gurobi_sol(solution_files[0])
        candidate_source = solution_files[0].name
    elif not solution_files:
        try:
            candidate = parse_solution(execution.get("stdout") or "")
        except (ValueError, TypeError) as exc:
            raise RuntimeError(
                "Il modello non ha prodotto né un file .sol né una riga SOLUTION_JSON valida"
            ) from exc
        candidate_source = "stdout:SOLUTION_JSON"
    else:
        raise RuntimeError(
            f"Atteso al massimo un file .sol prodotto dal modello, trovati {len(solution_files)}"
        )
    save_json(attempt_dir / "candidate_solution.json", candidate)
    private, public = definitive_validation(state["problem_id"], candidate)
    save_json(attempt_dir / "validation_private.json", private)
    save_json(attempt_dir / "validation_public.json", public)
    evaluation = {
        "success": bool(private["correct"]),
        "repairable": False,
        "stage": 4,
        "failure_class": "corretta" if private["correct"] else "validazione_indipendente_fallita",
        "detail": (
            "Soluzione ammissibile e gap entro tolleranza"
            if private["correct"]
            else "La soluzione fornita dall'esperto non supera la validazione indipendente"
        ),
        "finish_reason": "expert_direct_artifact",
        "source_sha256": source_hash,
        "candidate_source": candidate_source,
    }
    save_json(attempt_dir / "evaluation.json", evaluation)
    if not private["correct"]:
        raise RuntimeError(
            "Il modello è stato eseguito, ma la soluzione non supera la validazione indipendente; "
            f"vedere {attempt_dir / 'validation_public.json'}"
        )

    submitted_at = utc_now()
    instruction = "Eseguire direttamente il modello Python/Gurobi fornito dall'esperto."
    response = {
        "status": "SUBMITTED",
        "action": "CORRECT",
        "correction_mode": "DIRECT_CODE",
        "active_minutes": float(args.minutes),
        "expert_instruction": instruction,
        "correction_summary": args.summary.strip(),
        "semantic_principle": args.principle.strip(),
        "expert_artifact_source": str(source),
        "expert_artifact_sha256": source_hash,
        "submitted_at_utc": submitted_at,
    }
    save_json(response_path, response)
    intervention = {
        "handoff_number": packet["handoff_number"],
        "stage": packet["stage"],
        "failure_class": packet["failure_class"],
        "active_minutes": float(args.minutes),
        "action": "CORRECT",
        "correction_mode": "DIRECT_CODE",
        "expert_instruction": instruction,
        "correction_summary": args.summary.strip(),
        "semantic_principle": args.principle.strip(),
        "expert_artifact_source": str(source),
        "expert_artifact_sha256": source_hash,
        "submitted_at_utc": submitted_at,
        "memory_committed": False,
    }
    state["interventions"].append(intervention)
    attempt_record = {
        "number": attempt_number,
        "kind": "EXPERT_DIRECT_CODE",
        "directory": attempt_dir.name,
        "created_at_utc": submitted_at,
        "evaluation": evaluation,
    }
    state["attempts"].append(attempt_record)
    state["pending_handoff"] = None
    state["auto_repair_count_current_cycle"] = 0
    state["status"] = "RUNNING"
    save_state(run_dir, state)
    final = finalize_problem(run_dir, state, True, attempt_record)
    print(f"Soluzione verificata: obiettivo {private['projected_objective']}")
    print(f"Tempo-uomo registrato: {args.minutes:g} minuti")
    print(f"Handoff chiuso: {handoff_dir}")
    print(f"Risultato finale: {final}")


if __name__ == "__main__":
    main()
