#!/usr/bin/env python3
"""Congela prima degli esperimenti ordine, configurazioni e artefatti dello Scenario C."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from scenario_c_core import (
    DATASET_ROOT,
    HERE,
    INITIAL_SYSTEM_PATH,
    REPAIR_SYSTEM_PATH,
    SCENARIO_ROOT,
    empty_memory,
    load_problems,
    memory_path,
    model_slug,
    save_json,
)


SEED = 20260823
MODELS = ["gpt-5.6-sol", "claude-sonnet-5", "deepseek-v4-flash"]

# Una sola sequenza per i tre modelli. Alterna sempre difficoltà media/elevata
# e non colloca consecutivamente le due istanze dello stesso dominio.
PROBLEM_ORDER = [
    "M10", "H03", "M07", "H02", "M01", "H05", "M09", "H08", "M02", "H06",
    "M05", "H07", "M04", "H09", "M06", "H01", "M03", "H04", "M08", "H10",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_order() -> None:
    problems = load_problems()
    if len(PROBLEM_ORDER) != 20 or set(PROBLEM_ORDER) != set(problems):
        raise AssertionError("La sequenza non contiene esattamente i venti problemi del dataset")
    for index, problem_id in enumerate(PROBLEM_ORDER):
        expected = "Media" if index % 2 == 0 else "Elevata"
        actual = problems[problem_id]["difficulty"]
        if actual != expected:
            raise AssertionError(
                f"Posizione {index + 1}: attesa difficoltà {expected}, trovata {actual} ({problem_id})"
            )
        if index:
            previous = problems[PROBLEM_ORDER[index - 1]]
            if previous["pair"] == problems[problem_id]["pair"]:
                raise AssertionError(f"Due istanze dello stesso dominio sono adiacenti: {problem_id}")


def frozen_model_order() -> list[str]:
    order = MODELS.copy()
    random.Random(SEED).shuffle(order)
    return order


def artifact_hashes() -> dict[str, str]:
    paths = [
        HERE / "models.json",
        INITIAL_SYSTEM_PATH,
        REPAIR_SYSTEM_PATH,
        HERE / "scenario_c_core.py",
        HERE / "run_scenario_c.py",
        HERE / "analyze_scenario_c.py",
        HERE / "submit_handoff.py",
        HERE / "submit_direct_expert_code.py",
        HERE / "execute_response.py",
        HERE / "audit_scenario_b.py",
        HERE / "validate_candidate.py",
        HERE / "revalidate_aliases.py",
        DATASET_ROOT / "problems.jsonl",
        DATASET_ROOT / "ground_truth.json",
    ]
    paths.extend(sorted((DATASET_ROOT / "prompts").glob("[MH][0-9][0-9].md")))
    return {str(path.relative_to(HERE.parent)): sha256(path) for path in paths}


def main() -> None:
    validate_order()
    protocol_path = SCENARIO_ROOT / "protocol.json"
    schedule_path = SCENARIO_ROOT / "schedule.csv"
    if protocol_path.exists() or schedule_path.exists():
        raise FileExistsError(
            "Lo Scenario C risulta già congelato. Non sovrascrivere protocollo o sequenza durante la campagna."
        )

    model_order = frozen_model_order()
    SCENARIO_ROOT.mkdir(parents=True, exist_ok=False)
    protocol = {
        "schema_version": 2,
        "scenario": "C",
        "campaign_role": "definitive_strict_gates",
        "supersedes_technical_pilot": str(HERE.parent / "scenario_c"),
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "model_order": model_order,
        "problem_order": PROBLEM_ORDER,
        "number_of_models": 3,
        "problems_per_model": 20,
        "total_hybrid_executions": 60,
        "replicates_per_configuration": 1,
        "same_problem_order_for_all_models": True,
        "memory_policy": {
            "starts_empty": True,
            "separate_for_each_model": True,
            "updated_only_after_verified_expert_correction": True,
            "semantic_retrieval_limit": 8,
            "episodic_retrieval_limit": 2,
        },
        "gates": {
            "automatic_self_repairs_before_handoff": 3,
            "automatic_traceability_repairs_before_handoff": 1,
            "solver_timeout_seconds": 300,
            "relative_gap_tolerance": 0.001,
            "stage_1": {
                "rule": (
                    "ogni risposta iniziale non vuota deve contenere un TRACEABILITY_JSON valido; "
                    "READY richiede liste unresolved e undefined_symbols vuote e almeno quattro "
                    "corrispondenze requisito -> elemento del modello"
                ),
                "automatic_repair": (
                    "una sola rigenerazione completa se la riga è assente, non valida o incompleta"
                ),
                "handoff": (
                    "immediato per NEEDS_EXPERT o dati irrisolti; dopo il solo retry ammesso negli altri casi"
                ),
                "empty_length_exception": (
                    "una risposta completamente vuota troncata per limite di output è classificata allo Stadio 3"
                ),
            },
            "stage_2": {
                "rule": (
                    "revisione umana obbligatoria, prima dell'accettazione, per ogni problema di "
                    "difficoltà elevata risolto dopo almeno una riparazione automatica"
                ),
                "ground_truth_visible_to_expert": False,
                "checklist": [
                    "variabili e domini",
                    "obiettivo e verso",
                    "copertura dei requisiti mediante vincoli",
                    "coefficienti, indici e unità",
                    "vincoli impliciti",
                ],
                "outcomes": {
                    "APPROVE": "revisione senza correzione; non aggiorna la memoria",
                    "CORRECT": "correzione verificata; aggiorna la memoria dopo il successo",
                    "ACCEPT_FAILURE": "chiusura come non corretto",
                },
            },
            "stage_3": "fino a tre self-repair e poi handoff per errori di codice/esecuzione",
            "stage_4": "handoff se la soluzione non supera la validazione indipendente",
        },
        "artifact_sha256": artifact_hashes(),
    }
    save_json(protocol_path, protocol)

    problems = load_problems()
    with schedule_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "global_order", "model_order", "model", "problem_sequence", "problem_id",
                "difficulty", "domain", "model_class", "status",
            ],
        )
        writer.writeheader()
        global_order = 0
        for model_position, model in enumerate(model_order, start=1):
            for problem_sequence, problem_id in enumerate(PROBLEM_ORDER, start=1):
                global_order += 1
                item = problems[problem_id]
                writer.writerow(
                    {
                        "global_order": global_order,
                        "model_order": model_position,
                        "model": model,
                        "problem_sequence": problem_sequence,
                        "problem_id": problem_id,
                        "difficulty": item["difficulty"],
                        "domain": item["domain"],
                        "model_class": item["model_class"],
                        "status": "PENDING",
                    }
                )

    for model in model_order:
        save_json(memory_path(model), empty_memory(model))
    print(f"Protocollo congelato in {protocol_path}")
    print(f"Ordine dei modelli: {' -> '.join(model_order)}")
    print(f"Sequenza: {' -> '.join(PROBLEM_ORDER)}")


if __name__ == "__main__":
    main()
