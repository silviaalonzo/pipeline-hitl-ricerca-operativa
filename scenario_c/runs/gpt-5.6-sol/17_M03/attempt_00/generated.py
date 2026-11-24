import gurobipy as gp
from gurobipy import GRB
import json

employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
night_shifts = ["N1", "N2"]

costs = {
    ("Ana", "M1"): 8,
    ("Ana", "M2"): 7,
    ("Ana", "P1"): 9,
    ("Ana", "P2"): 8,

    ("Bruno", "M1"): 7,
    ("Bruno", "M2"): 8,
    ("Bruno", "P1"): 8,
    ("Bruno", "P2"): 9,

    ("Carla", "M2"): 9,
    ("Carla", "P1"): 8,
    ("Carla", "P2"): 8,
    ("Carla", "N1"): 11,
    ("Carla", "N2"): 12,

    ("Diego", "M1"): 10,
    ("Diego", "P1"): 9,
    ("Diego", "P2"): 8,
    ("Diego", "N1"): 10,
    ("Diego", "N2"): 11,

    ("Elena", "M1"): 8,
    ("Elena", "M2"): 10,
    ("Elena", "P1"): 9,
    ("Elena", "P2"): 9,
    ("Elena", "N1"): 12,
    ("Elena", "N2"): 10,

    ("Fabio", "M1"): 9,
    ("Fabio", "M2"): 8,
    ("Fabio", "P1"): 10,
    ("Fabio", "P2"): 7
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("assegnazione_personale_turni", env=env)

x = {
    (i, t): model.addVar(vtype=GRB.BINARY, name=f"x[{i},{t}]")
    for i in employees
    for t in shifts
}

model.setObjective(
    gp.quicksum(costs[i, t] * x[i, t] for (i, t) in costs),
    GRB.MINIMIZE
)

for t in shifts:
    model.addConstr(
        gp.quicksum(x[i, t] for i in employees) == 1,
        name=f"copertura[{t}]"
    )

for i in employees:
    model.addConstr(
        gp.quicksum(x[i, t] for t in shifts) <= 2,
        name=f"massimo_due_turni[{i}]"
    )

for i in employees:
    model.addConstr(
        gp.quicksum(x[i, t] for t in night_shifts) <= 1,
        name=f"massimo_un_notturno[{i}]"
    )

for i in employees:
    for t in shifts:
        if (i, t) not in costs:
            model.addConstr(
                x[i, t] == 0,
                name=f"indisponibilita[{i},{t}]"
            )

model.optimize()

status_map = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT"
}

solver_status = status_map.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for i in employees:
        for t in shifts:
            value = float(round(x[i, t].X, 10))
            if abs(value) < 1e-9:
                value = 0.0
            variable_values[f"x[{i},{t}]"] = value

    payload = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    payload = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
