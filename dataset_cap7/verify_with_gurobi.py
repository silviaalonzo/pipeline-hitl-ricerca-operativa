#!/usr/bin/env python3
"""Ricostruisce da ``ground_truth.json`` e ricertifica le cinque istanze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB


HERE = Path(__file__).resolve().parent


def solve(record: dict) -> dict:
    model = gp.Model(f"verify_{record['id']}")
    model.Params.OutputFlag = 0
    model.Params.MIPGap = 0.0
    model.Params.MIPGapAbs = 0.0
    vars_by_name = {}
    type_map = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
    for spec in record["variables"]:
        vars_by_name[spec["name"]] = model.addVar(
            lb=float(spec["lb"]),
            ub=GRB.INFINITY if spec["ub"] is None else float(spec["ub"]),
            vtype=type_map[spec["vartype"]],
            name=spec["name"],
        )
    model.update()
    objective = gp.quicksum(
        float(coefficient) * vars_by_name[name]
        for name, coefficient in record["objective"]["coefficients"].items()
    )
    model.setObjective(
        objective,
        GRB.MINIMIZE if record["objective"]["sense"] == "min" else GRB.MAXIMIZE,
    )
    for con in record["constraints"]:
        lhs = gp.quicksum(
            float(coefficient) * vars_by_name[name]
            for name, coefficient in con["coeffs"].items()
        )
        rhs = float(con["rhs"])
        if con["sense"] == "<=":
            model.addConstr(lhs <= rhs, name=con["name"])
        elif con["sense"] == ">=":
            model.addConstr(lhs >= rhs, name=con["name"])
        else:
            model.addConstr(lhs == rhs, name=con["name"])
    model.optimize()
    expected = float(record["solution"]["objective"])
    actual = float(model.ObjVal) if model.Status == GRB.OPTIMAL else None
    return {
        "id": record["id"],
        "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else str(model.Status),
        "expected_objective": expected,
        "verified_objective": actual,
        "objective_match": actual is not None and abs(actual - expected) <= 1e-7,
        "mip_gap": float(model.MIPGap) if model.Status == GRB.OPTIMAL else None,
        "nonzero_variables": {
            name: float(var.X)
            for name, var in vars_by_name.items()
            if model.Status == GRB.OPTIMAL and abs(var.X) > 1e-8
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="problem_id")
    args = parser.parse_args()
    records = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    if args.problem_id:
        records = [record for record in records if record["id"] == args.problem_id]
        if not records:
            raise SystemExit(f"Problema non trovato: {args.problem_id}")
    results = [solve(record) for record in records]
    if not all(result["objective_match"] and result["mip_gap"] == 0 for result in results):
        raise SystemExit(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
