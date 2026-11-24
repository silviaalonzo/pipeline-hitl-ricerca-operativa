#!/usr/bin/env python3
"""Valida una soluzione candidata rispetto al modello originale e all'ottimo noto."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GT_PATH = ROOT / "dataset_cap4" / "ground_truth.json"

FEAS_TOL = 1e-6
INT_TOL = 1e-5
GAP_TOL = 1e-3


def canonicalize_variable_name(name: str) -> str:
    """Uniforma y[A] e x[Z1,A] ai nomi y_A e x_Z1_A della ground truth."""
    normalized = str(name).strip()
    normalized = normalized.replace("[", "_").replace("]", "")
    normalized = normalized.replace("(", "_").replace(")", "")
    normalized = normalized.replace(",", "_").replace(" ", "")
    return re.sub(r"_+", "_", normalized).strip("_")


def variable_signature(name: str) -> tuple[str, tuple[str, ...]]:
    """Firma indipendente dall'ordine degli indici: x_A_Z1 equivale a x_Z1_A."""
    parts = canonicalize_variable_name(name).split("_")
    return parts[0], tuple(sorted(parts[1:]))


def load_ground_truth(problem_id: str) -> dict:
    for record in json.loads(GT_PATH.read_text(encoding="utf-8")):
        if record["id"] == problem_id:
            return record
    raise KeyError(f"Problema non trovato: {problem_id}")


def violation(lhs: float, sense: str, rhs: float) -> float:
    if sense == "<=":
        return max(0.0, lhs - rhs)
    if sense == ">=":
        return max(0.0, rhs - lhs)
    return abs(lhs - rhs)


def validate(record: dict, candidate: dict) -> dict:
    raw_values = candidate.get("variables") or {}
    specs = {v["name"]: v for v in record["variables"]}
    expected_names = set(specs)
    signatures: dict[tuple[str, tuple[str, ...]], list[str]] = {}
    for expected_name in expected_names:
        signatures.setdefault(variable_signature(expected_name), []).append(expected_name)
    mapped_values = {}
    name_mapping = {}
    unknown = []
    duplicate_names = []
    for raw_name, value in raw_values.items():
        canonical = canonicalize_variable_name(raw_name)
        target = raw_name if raw_name in expected_names else canonical
        if target not in expected_names:
            matches = signatures.get(variable_signature(canonical), [])
            if len(matches) == 1:
                target = matches[0]
            else:
                unknown.append(raw_name)
                continue
        if target in mapped_values:
            duplicate_names.append({"target": target, "raw_name": raw_name})
            continue
        mapped_values[target] = value
        if raw_name != target:
            name_mapping[raw_name] = target
    missing = sorted(expected_names - set(mapped_values))

    values: dict[str, float] = {}
    numeric_error = None
    try:
        values = {name: float(mapped_values.get(name, 0.0)) for name in expected_names}
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError("sono presenti valori non finiti")
    except (TypeError, ValueError) as exc:
        numeric_error = str(exc)

    bound_violations = []
    integrality_violations = []
    constraint_violations = []
    objective = None
    gap = None
    max_violation = math.inf

    if numeric_error is None:
        for name, spec in specs.items():
            value = values[name]
            low_v = max(0.0, float(spec["lb"]) - value)
            up_v = 0.0 if spec["ub"] is None else max(0.0, value - float(spec["ub"]))
            if max(low_v, up_v) > FEAS_TOL:
                bound_violations.append({"variable": name, "value": value, "violation": max(low_v, up_v)})
            if spec["vartype"] in {"B", "I"}:
                int_v = abs(value - round(value))
                if int_v > INT_TOL:
                    integrality_violations.append({"variable": name, "value": value, "violation": int_v})

        for con in record["constraints"]:
            lhs = sum(float(coef) * values[name] for name, coef in con["coeffs"].items())
            v = violation(lhs, con["sense"], float(con["rhs"]))
            if v > FEAS_TOL:
                constraint_violations.append({
                    "constraint": con["name"], "lhs": lhs, "sense": con["sense"],
                    "rhs": float(con["rhs"]), "violation": v,
                })

        objective = sum(
            float(coef) * values[name]
            for name, coef in record["objective"]["coefficients"].items()
        )
        optimum = float(record["solution"]["objective"])
        gap = abs(objective - optimum) / max(1.0, abs(optimum))
        all_v = [x["violation"] for x in bound_violations + integrality_violations + constraint_violations]
        max_violation = max(all_v, default=0.0)

    feasible = (
        numeric_error is None and not duplicate_names and not bound_violations
        and not integrality_violations and not constraint_violations
    )
    correct = feasible and gap is not None and gap <= GAP_TOL
    declared_obj = candidate.get("objective")
    declared_delta = None
    if declared_obj is not None and objective is not None:
        try:
            declared_delta = abs(float(declared_obj) - objective)
        except (TypeError, ValueError):
            pass

    return {
        "problem_id": record["id"],
        "candidate_status": candidate.get("status"),
        "feasible": feasible,
        "correct": correct,
        "recomputed_objective": objective,
        "known_optimum": float(record["solution"]["objective"]),
        "relative_gap": gap,
        "max_violation": max_violation,
        "declared_objective": declared_obj,
        "declared_objective_delta": declared_delta,
        "missing_variables_assumed_zero": missing,
        "unknown_variables": sorted(unknown),
        "duplicate_variable_names": duplicate_names,
        "normalized_variable_names": name_mapping,
        "numeric_error": numeric_error,
        "bound_violations": bound_violations,
        "integrality_violations": integrality_violations,
        "constraint_violations": constraint_violations,
        "tolerances": {"feasibility": FEAS_TOL, "integrality": INT_TOL, "relative_gap": GAP_TOL},
    }


def infer_problem_id(run_dir: Path) -> str:
    request = json.loads((run_dir / "request.json").read_text(encoding="utf-8"))
    return request["problem_id"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--problem")
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()

    if args.run_dir:
        problem_id = infer_problem_id(args.run_dir)
        candidate_path = args.run_dir / "candidate_solution.json"
        output_path = args.run_dir / "validation.json"
    else:
        if not args.problem or not args.candidate:
            parser.error("usare --run-dir oppure --problem e --candidate")
        problem_id = args.problem
        candidate_path = args.candidate
        output_path = None

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    result = validate(load_ground_truth(problem_id), candidate)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
