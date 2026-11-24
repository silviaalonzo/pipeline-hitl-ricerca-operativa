#!/usr/bin/env python3
"""Risolutore generico Gurobi per il ground truth del dataset Cap. 4."""
import argparse
import json
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB

HERE = Path(__file__).resolve().parent

def solve(record):
    model = gp.Model(record["id"])
    model.Params.OutputFlag = 0
    vars_ = {}
    types = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
    for spec in record["variables"]:
        ub = GRB.INFINITY if spec["ub"] is None else spec["ub"]
        vars_[spec["name"]] = model.addVar(lb=spec["lb"], ub=ub, vtype=types[spec["vartype"]], name=spec["name"])
    model.update()
    obj = gp.quicksum(coef * vars_[name] for name, coef in record["objective"]["coefficients"].items())
    model.setObjective(obj, GRB.MINIMIZE if record["objective"]["sense"] == "min" else GRB.MAXIMIZE)
    for con in record["constraints"]:
        lhs = gp.quicksum(coef * vars_[name] for name, coef in con["coeffs"].items())
        if con["sense"] == "<=": model.addConstr(lhs <= con["rhs"], name=con["name"])
        elif con["sense"] == ">=": model.addConstr(lhs >= con["rhs"], name=con["name"])
        else: model.addConstr(lhs == con["rhs"], name=con["name"])
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"{record['id']}: status Gurobi {model.Status}")
    expected = record["solution"]["objective"]
    if abs(model.ObjVal - expected) > 1e-5:
        raise RuntimeError(f"{record['id']}: ottimo Gurobi {model.ObjVal} diverso dal ground truth {expected}")
    values = {name: var.X for name, var in vars_.items() if abs(var.X) > 1e-8}
    return model.ObjVal, values

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="es. M01; se omesso risolve tutto")
    args = ap.parse_args()
    records = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    for rec in records:
        if args.id and rec["id"] != args.id: continue
        obj, values = solve(rec)
        print(rec["id"], "objective=", round(obj, 6))
        print(values)
