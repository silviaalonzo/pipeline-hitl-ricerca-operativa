#!/usr/bin/env python3
"""Verifica che il pattern bersaglio di ogni istanza sia sostanziale.

Per ciascun problema risolve una formulazione volutamente difettosa che riproduce
il tipo di omissione osservato nel Capitolo 5. L'audit non entra nella campagna
sperimentale: serve soltanto a controllare che dimenticare il principio possa
produrre un output non corretto, anziché lasciare invariato l'ottimo per caso.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB


HERE = Path(__file__).resolve().parent


def mutated(record: dict) -> tuple[dict, str]:
    value = deepcopy(record)
    problem_id = value["id"]
    if problem_id == "L01":
        value["constraints"] = [
            con for con in value["constraints"] if not con["name"].startswith("long_limit_")
        ]
        return value, "aggregazione/omissione dei limiti individuali sulle rotte lunghe"
    if problem_id == "L02":
        value["constraints"] = [
            con for con in value["constraints"]
            if not con["name"].startswith(("min_lot_", "max_lot_"))
        ]
        return value, "assenza del collegamento tra produzione e setup"
    if problem_id == "L03":
        value["constraints"] = [
            con for con in value["constraints"] if not con["name"].startswith("lower_link_")
        ]
        return value, "binarie di utilizzo conteggiate senza quantità minima positiva"
    if problem_id == "L04":
        value["constraints"] = [
            con for con in value["constraints"]
            if not con["name"].startswith(("min_lot_", "max_lot_"))
        ]
        return value, "produzione non collegata ai setup"
    if problem_id == "L05":
        value["constraints"] = [
            con for con in value["constraints"] if con["name"] != "cover_A12"
        ]
        return value, "mancata copertura separata dell'audit A12"
    raise KeyError(problem_id)


def solve(record: dict) -> dict[str, float]:
    model = gp.Model(f"target_audit_{record['id']}")
    model.Params.OutputFlag = 0
    model.Params.MIPGap = 0.0
    model.Params.MIPGapAbs = 0.0
    types = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
    variables = {
        spec["name"]: model.addVar(
            lb=float(spec["lb"]),
            ub=GRB.INFINITY if spec["ub"] is None else float(spec["ub"]),
            vtype=types[spec["vartype"]],
            name=spec["name"],
        )
        for spec in record["variables"]
    }
    model.update()
    objective = gp.quicksum(
        float(coef) * variables[name]
        for name, coef in record["objective"]["coefficients"].items()
    )
    model.setObjective(objective, GRB.MINIMIZE)
    for con in record["constraints"]:
        lhs = gp.quicksum(float(coef) * variables[name] for name, coef in con["coeffs"].items())
        if con["sense"] == "<=":
            model.addConstr(lhs <= float(con["rhs"]))
        elif con["sense"] == ">=":
            model.addConstr(lhs >= float(con["rhs"]))
        else:
            model.addConstr(lhs == float(con["rhs"]))
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError((record["id"], model.Status))
    return {name: float(var.X) for name, var in variables.items()}


def original_validation(original: dict, values: dict[str, float]) -> dict:
    violations = []
    for con in original["constraints"]:
        lhs = sum(float(coef) * values[name] for name, coef in con["coeffs"].items())
        rhs = float(con["rhs"])
        if con["sense"] == "<=":
            amount = max(0.0, lhs - rhs)
        elif con["sense"] == ">=":
            amount = max(0.0, rhs - lhs)
        else:
            amount = abs(lhs - rhs)
        if amount > 1e-6:
            violations.append({"constraint": con["name"], "violation": amount})
    objective = sum(
        float(coef) * values[name]
        for name, coef in original["objective"]["coefficients"].items()
    )
    optimum = float(original["solution"]["objective"])
    gap = abs(objective - optimum) / max(1.0, abs(optimum))
    return {
        "original_objective_of_mutated_solution": objective,
        "known_optimum": optimum,
        "relative_gap": gap,
        "violated_original_constraints": violations,
        "would_be_accepted": not violations and gap <= 1e-3,
    }


def main() -> None:
    records = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    results = []
    for original in records:
        variant, omission = mutated(original)
        candidate = solve(variant)
        validation = original_validation(original, candidate)
        results.append(
            {
                "id": original["id"],
                "simulated_omission": omission,
                **validation,
                "target_is_consequential": not validation["would_be_accepted"],
            }
        )
    if not all(item["target_is_consequential"] for item in results):
        raise SystemExit(json.dumps(results, ensure_ascii=False, indent=2))
    (HERE / "target_pattern_audit.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
