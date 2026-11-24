#!/usr/bin/env python3
"""Audit indipendente e riproducibile delle 180 esecuzioni dello Scenario B.

L'audit non modifica le risposte, il codice o le validazioni già esistenti. Parte
dai file grezzi, ricostruisce il candidato stampato dal codice, applica soltanto
la normalizzazione documentata dei nomi delle variabili e verifica ogni vettore
di decisione sia con il validatore algebrico sia con un modello Gurobi in cui le
variabili vengono fissate ai valori prodotti dall'LLM.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from execute_response import extract_code, parse_solution, static_check
from revalidate_aliases import remap_candidate
from validate_candidate import (
    canonicalize_variable_name,
    validate,
    variable_signature,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNS = HERE / "runs" / "B"
GROUND_TRUTH = ROOT / "dataset_cap4" / "ground_truth.json"
FINAL_RESULTS = HERE / "RISULTATI_DEFINITIVI_SCENARIO_B.csv"


def is_formulation_auxiliary(problem_id: str, variable_name: str) -> bool:
    """Variabili che possono essere completate senza cambiare la decisione operativa.

    In H04 le variabili y indicano soltanto se un tipo di veicolo viene attivato
    su una rotta. Il vincolo x <= M y, insieme a sum(y) <= 2, è già sufficiente
    a imporre il limite sui tipi effettivamente usati; richiedere anche y <= x
    seleziona una rappresentazione canonica, ma non cambia né l'allocazione x né
    l'obiettivo. Per questo la verifica definitiva fissa x e lascia a Gurobi il
    completamento delle sole y di H04.
    """
    if problem_id == "H04" and variable_name.startswith("y_"):
        return True
    if problem_id == "H06" and variable_name.startswith(("C_", "o_")):
        # I completamenti C sono determinati dai tempi di inizio S e dalle durate;
        # le binarie o codificano soltanto l'ordine già implicito negli stessi S.
        # Una formulazione equivalente può quindi ometterle senza cambiare le
        # decisioni operative, il ritardo o il valore dell'obiettivo.
        return True
    return False


def is_candidate_auxiliary(problem_id: str, variable_name: str) -> bool:
    """Variabili derivate aggiunte dal candidato ma assenti dalla ground truth."""
    canonical = canonicalize_variable_name(variable_name)
    if problem_id == "H02" and canonical in {"I_A_0", "I_B_0", "I_C_0"}:
        # Le scorte iniziali sono dati fissati dal testo. Alcune formulazioni le
        # rappresentano come variabili vincolate al valore noto; non sono
        # decisioni operative e possono essere escluse dalla proiezione.
        return True
    if problem_id == "M06" and canonical in {"C_A", "C_B", "Load_A", "Load_B"}:
        # Carichi delle macchine, determinati interamente dalle assegnazioni x.
        return True
    return False


def expected_value_map(record: dict, candidate: dict) -> tuple[dict[str, float], list[str], list[str]]:
    """Replica il matching del validatore e restituisce i valori nei nomi attesi."""
    specs = {item["name"]: item for item in record["variables"]}
    expected = set(specs)
    signatures: dict[tuple[str, tuple[str, ...]], list[str]] = defaultdict(list)
    for name in expected:
        signatures[variable_signature(name)].append(name)

    mapped: dict[str, float] = {}
    unknown: list[str] = []
    duplicates: list[str] = []
    for raw_name, raw_value in (candidate.get("variables") or {}).items():
        canonical = canonicalize_variable_name(raw_name)
        target = raw_name if raw_name in expected else canonical
        if target not in expected:
            matches = signatures.get(variable_signature(canonical), [])
            if len(matches) == 1:
                target = matches[0]
            else:
                unknown.append(raw_name)
                continue
        if target in mapped:
            duplicates.append(target)
            continue
        mapped[target] = float(raw_value)
    values = {name: mapped.get(name, 0.0) for name in expected}
    return values, unknown, duplicates


def build_ground_truth_model(record: dict, fixed_values: dict[str, float] | None = None) -> gp.Model:
    model = gp.Model(f"audit_{record['id']}")
    model.Params.OutputFlag = 0
    kinds = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
    variables = {}
    for spec in record["variables"]:
        ub = GRB.INFINITY if spec["ub"] is None else float(spec["ub"])
        variables[spec["name"]] = model.addVar(
            lb=float(spec["lb"]), ub=ub, vtype=kinds[spec["vartype"]], name=spec["name"]
        )
    model.update()
    objective = gp.quicksum(
        float(coef) * variables[name]
        for name, coef in record["objective"]["coefficients"].items()
    )
    sense = GRB.MINIMIZE if record["objective"]["sense"] == "min" else GRB.MAXIMIZE
    model.setObjective(objective, sense)
    for constraint in record["constraints"]:
        lhs = gp.quicksum(
            float(coef) * variables[name] for name, coef in constraint["coeffs"].items()
        )
        rhs = float(constraint["rhs"])
        if constraint["sense"] == "<=":
            model.addConstr(lhs <= rhs, name=constraint["name"])
        elif constraint["sense"] == ">=":
            model.addConstr(lhs >= rhs, name=constraint["name"])
        else:
            model.addConstr(lhs == rhs, name=constraint["name"])
    if fixed_values is not None:
        for name, value in fixed_values.items():
            model.addConstr(variables[name] == float(value), name=f"audit_fix_{name}")
    return model


def certify_ground_truth(records: dict[str, dict]) -> dict[str, float]:
    objectives = {}
    for problem_id, record in records.items():
        model = build_ground_truth_model(record)
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            raise AssertionError(f"Ground truth {problem_id}: status Gurobi {model.Status}")
        expected = float(record["solution"]["objective"])
        if not math.isclose(model.ObjVal, expected, abs_tol=1e-6):
            raise AssertionError(
                f"Ground truth {problem_id}: Gurobi={model.ObjVal}, file={expected}"
            )
        objectives[problem_id] = model.ObjVal
    return objectives


def audit_candidate(record: dict, candidate: dict) -> tuple[dict, dict, dict]:
    remapped, aliases = remap_candidate(record["id"], candidate)
    algebraic = validate(record, remapped)
    values, unknown, duplicates = expected_value_map(record, remapped)
    model = build_ground_truth_model(record, values)
    model.optimize()
    gurobi_feasible = model.Status == GRB.OPTIMAL
    gurobi_objective = model.ObjVal if gurobi_feasible else None
    if gurobi_feasible != bool(algebraic["feasible"]):
        raise AssertionError(f"{record['id']}: disaccordo tra validatore e Gurobi")
    if gurobi_feasible and not math.isclose(
        float(gurobi_objective), float(algebraic["recomputed_objective"]), abs_tol=1e-6
    ):
        raise AssertionError(f"{record['id']}: obiettivo diverso tra validatore e Gurobi")

    # Verifica indipendente dalla specifica formulazione: le decisioni operative
    # prodotte dall'LLM vengono fissate, mentre le sole variabili ausiliarie
    # esplicitamente documentate possono essere completate dal solver.
    operational_values = {
        name: value
        for name, value in values.items()
        if not is_formulation_auxiliary(record["id"], name)
    }
    projected_model = build_ground_truth_model(record, operational_values)
    projected_model.optimize()
    projected_feasible = projected_model.Status == GRB.OPTIMAL
    projected_objective = projected_model.ObjVal if projected_feasible else None
    optimum = float(record["solution"]["objective"])
    declared = candidate.get("objective")
    try:
        declared_matches = declared is not None and math.isclose(float(declared), optimum, abs_tol=1e-6)
    except (TypeError, ValueError):
        declared_matches = False
    projected_correct = (
        candidate.get("status") == "OPTIMAL"
        and projected_feasible
        and projected_objective is not None
        and math.isclose(float(projected_objective), optimum, abs_tol=1e-6)
        and declared_matches
    )
    ignored_candidate_auxiliaries = sorted(
        name for name in unknown if is_candidate_auxiliary(record["id"], name)
    )
    independent = {
        "gurobi_feasible": gurobi_feasible,
        "gurobi_objective": gurobi_objective,
        "unknown_variables": unknown,
        "unknown_nonzero": [
            name
            for name in unknown
            if abs(float((remapped.get("variables") or {}).get(name, 0.0))) > 1e-8
            and not is_candidate_auxiliary(record["id"], name)
        ],
        "candidate_auxiliary_variables_ignored": ignored_candidate_auxiliaries,
        "duplicates": duplicates,
        "projected_feasible": projected_feasible,
        "projected_objective": projected_objective,
        "projected_correct": projected_correct,
        "auxiliary_variables_completed": sorted(
            name for name in values if is_formulation_auxiliary(record["id"], name)
        ),
    }
    return algebraic, independent, aliases


def failure_class(
    finish_reason: str,
    generated: bool,
    returncode: int | None,
    algebraic: dict | None,
    projected_correct: bool,
) -> str:
    if not generated:
        return "output_troncato_o_senza_codice" if finish_reason == "length" else "codice_non_estratto"
    if returncode != 0:
        return "errore_di_esecuzione"
    if algebraic is None:
        return "soluzione_non_leggibile"
    if projected_correct and not algebraic["correct"]:
        return "corretta_con_completamento_delle_ausiliarie"
    if projected_correct:
        return "corretta"
    if not algebraic["feasible"]:
        return "soluzione_non_ammissibile"
    if not algebraic["correct"]:
        return "soluzione_ammissibile_non_ottima"
    return "corretta"


def main() -> None:
    records = {
        item["id"]: item for item in json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))
    }
    if len(records) != 20:
        raise AssertionError(f"Attesi 20 problemi, trovati {len(records)}")
    certified_objectives = certify_ground_truth(records)

    rows = []
    request_paths = sorted(RUNS.glob("*/*/run_*/request.json"))
    if len(request_paths) != 180:
        raise AssertionError(f"Attese 180 richieste, trovate {len(request_paths)}")

    for request_path in request_paths:
        run_dir = request_path.parent
        request = json.loads(request_path.read_text(encoding="utf-8"))
        response_path = run_dir / "response.json"
        if not response_path.exists():
            raise AssertionError(f"Risposta mancante: {run_dir}")
        response = json.loads(response_path.read_text(encoding="utf-8"))
        problem_id = request["problem_id"]
        record = records[problem_id]
        choice = response["choices"][0]
        finish_reason = choice.get("finish_reason") or ""
        response_content = (choice.get("message") or {}).get("content") or ""
        saved_text = (run_dir / "response.txt").read_text(encoding="utf-8")
        if saved_text != response_content + "\n":
            raise AssertionError(f"response.txt non coincide con response.json: {run_dir}")

        requested_model = request["configuration"]["model"]
        required_provider = request["configuration"]["upstream_provider"]
        provider_match = str(response.get("provider", "")).casefold() == str(required_provider).casefold()
        model_match = response.get("model") == requested_model

        generated_path = run_dir / "generated.py"
        generated = generated_path.exists()
        extraction_error = ""
        try:
            extracted = extract_code(saved_text)
            static_check(extracted)
            if not generated:
                raise AssertionError(f"Codice valido estratto ma generated.py assente: {run_dir}")
            if generated_path.read_text(encoding="utf-8") != extracted:
                raise AssertionError(f"generated.py diverso dal blocco della risposta: {run_dir}")
        except (ValueError, SyntaxError) as exc:
            extraction_error = str(exc)
            if generated:
                raise

        execution_path = run_dir / "execution.json"
        execution = json.loads(execution_path.read_text(encoding="utf-8")) if execution_path.exists() else {}
        returncode = execution.get("returncode")
        timed_out = bool(execution.get("timed_out", False))
        candidate_path = run_dir / "candidate_solution.json"
        candidate_exists = candidate_path.exists()
        algebraic = None
        independent = None
        aliases = {}
        candidate_matches_stdout = False
        if candidate_exists:
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            parsed = parse_solution(execution.get("stdout") or "")
            candidate_matches_stdout = candidate == parsed
            if not candidate_matches_stdout:
                raise AssertionError(f"Candidato diverso dallo stdout: {run_dir}")
            algebraic, independent, aliases = audit_candidate(record, candidate)
            if independent["unknown_nonzero"]:
                raise AssertionError(
                    f"Variabili non riconosciute e non nulle in {run_dir}: {independent['unknown_nonzero']}"
                )
            stored_v2 = json.loads((run_dir / "validation_v2.json").read_text(encoding="utf-8"))
            for field in (
                "feasible", "correct", "recomputed_objective", "known_optimum",
                "relative_gap", "max_violation", "declared_objective_delta",
            ):
                if stored_v2.get(field) != algebraic.get(field):
                    raise AssertionError(f"validation_v2 non riproducibile ({field}): {run_dir}")
        elif returncode == 0:
            raise AssertionError(f"Esecuzione riuscita senza candidato: {run_dir}")

        strict_correct = bool(algebraic and algebraic["correct"])
        strict_feasible = bool(algebraic and algebraic["feasible"])
        correct = bool(independent and independent["projected_correct"])
        feasible = bool(independent and independent["projected_feasible"])
        declared_delta = None if algebraic is None else algebraic.get("declared_objective_delta")
        if correct:
            if algebraic.get("candidate_status") != "OPTIMAL":
                raise AssertionError(f"Soluzione corretta senza status OPTIMAL: {run_dir}")
            if declared_delta is None or declared_delta > 1e-6:
                raise AssertionError(f"Obiettivo dichiarato incoerente: {run_dir}")

        original_validation_path = run_dir / "validation.json"
        original_validation = (
            json.loads(original_validation_path.read_text(encoding="utf-8"))
            if original_validation_path.exists() else {}
        )
        usage = response.get("usage") or {}
        token_details = usage.get("completion_tokens_details") or {}
        rows.append({
            "model_folder": run_dir.parts[-4],
            "requested_model": requested_model,
            "actual_model": response.get("model"),
            "required_provider": required_provider,
            "actual_provider": response.get("provider"),
            "provider_match": provider_match,
            "model_match": model_match,
            "problem_id": problem_id,
            "difficulty": record["difficulty"],
            "replicate": int(request["replicate"]),
            "finish_reason": finish_reason,
            "pass": returncode == 0 and not timed_out and candidate_exists,
            "generated_code": generated,
            "extraction_error": extraction_error,
            "execution_returncode": returncode,
            "execution_timed_out": timed_out,
            "candidate_exists": candidate_exists,
            "candidate_matches_stdout": candidate_matches_stdout,
            "alias_count": len(aliases),
            "original_correct": bool(original_validation.get("correct", False)),
            "strict_feasible": strict_feasible,
            "strict_correct": strict_correct,
            "feasible": feasible,
            "recomputed_objective": None if algebraic is None else algebraic.get("recomputed_objective"),
            "known_optimum": certified_objectives[problem_id],
            "relative_gap": None if algebraic is None else algebraic.get("relative_gap"),
            "declared_objective_delta": declared_delta,
            "max_violation": None if algebraic is None else algebraic.get("max_violation"),
            "gurobi_fixed_feasible": None if independent is None else independent["gurobi_feasible"],
            "gurobi_fixed_objective": None if independent is None else independent["gurobi_objective"],
            "gurobi_projected_feasible": None if independent is None else independent["projected_feasible"],
            "gurobi_projected_objective": None if independent is None else independent["projected_objective"],
            "auxiliary_variables_completed": "" if independent is None else ";".join(independent["auxiliary_variables_completed"]),
            "unknown_nonzero_count": 0 if independent is None else len(independent["unknown_nonzero"]),
            "correct": correct,
            "failure_class": failure_class(finish_reason, generated, returncode, algebraic, correct),
            "response_seconds": (response.get("_experiment") or {}).get("elapsed_seconds"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "reasoning_tokens": token_details.get("reasoning_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "api_cost_usd": usage.get("cost"),
            "run_directory": str(run_dir.relative_to(HERE)),
        })

    summary = {
        "checks": {
            "ground_truth_problems_certified_with_gurobi": len(certified_objectives),
            "raw_api_responses": len(rows),
            "provider_and_model_match": sum(r["provider_match"] and r["model_match"] for r in rows),
            "candidate_files_reconstructed_from_stdout": sum(r["candidate_matches_stdout"] for r in rows),
            "strictly_correct_candidates": sum(r["strict_correct"] for r in rows),
            "definitively_correct_candidates_after_formulation_invariant_check": sum(r["correct"] for r in rows),
            "correct_candidates_with_nonzero_unknown_variables": sum(
                r["correct"] and r["unknown_nonzero_count"] for r in rows
            ),
        },
        "models": {},
    }
    for model in sorted({row["requested_model"] for row in rows}):
        subset = [row for row in rows if row["requested_model"] == model]
        problems = sorted({row["problem_id"] for row in subset})
        successes = {
            problem: sum(row["correct"] for row in subset if row["problem_id"] == problem)
            for problem in problems
        }
        primary = [row for row in subset if row["replicate"] == 1]
        by_difficulty = {}
        for difficulty in ("Media", "Elevata"):
            group = [row for row in subset if row["difficulty"] == difficulty]
            by_difficulty[difficulty] = {
                "correct_runs": sum(row["correct"] for row in group),
                "runs": len(group),
                "accuracy": sum(row["correct"] for row in group) / len(group),
            }
        summary["models"][model] = {
            "runs": len(subset),
            "executable_runs": sum(row["candidate_exists"] for row in subset),
            "pass_rate": sum(row["pass"] for row in subset) / len(subset),
            "correct_runs": sum(row["correct"] for row in subset),
            "run_level_accuracy": sum(row["correct"] for row in subset) / len(subset),
            "primary_run_correct": sum(row["correct"] for row in primary),
            "primary_run_accuracy": sum(row["correct"] for row in primary) / len(primary),
            "problems_correct_at_least_once_of_three": sum(value >= 1 for value in successes.values()),
            "problem_level_success_within_three": sum(value >= 1 for value in successes.values()) / len(problems),
            "problems_correct_in_all_three": sum(value == 3 for value in successes.values()),
            "problems_never_correct": [problem for problem, value in successes.items() if value == 0],
            "correct_replicates_by_problem": successes,
            "by_difficulty": by_difficulty,
            "failure_classes": dict(Counter(row["failure_class"] for row in subset)),
            "old_exact_name_accuracy": sum(row["original_correct"] for row in subset) / len(subset),
        }

    criterion = (
        "corretta se esiste una soluzione ammissibile coerente con le decisioni operative prodotte "
        "e l'obiettivo verificato coincide con l'ottimo noto; non e' richiesta uguaglianza con il "
        "vettore di variabili salvato nella ground truth"
    )
    for row in rows:
        model_summary = summary["models"][row["requested_model"]]
        row["validation_criterion"] = criterion
        row["model_pass_rate"] = model_summary["pass_rate"]
        row["model_primary_accuracy_run1"] = model_summary["primary_run_accuracy"]
        row["model_accuracy_all_60_runs"] = model_summary["run_level_accuracy"]
        row["model_problem_success_within_three"] = model_summary["problem_level_success_within_three"]

    fields = list(rows[0])
    with FINAL_RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Creato {FINAL_RESULTS.name}")


if __name__ == "__main__":
    main()
