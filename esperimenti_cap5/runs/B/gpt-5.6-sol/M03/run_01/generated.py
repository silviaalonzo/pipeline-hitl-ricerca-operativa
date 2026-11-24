import gurobipy as gp
from gurobipy import GRB
import json

employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
night_shifts = ["N1", "N2"]

cost = {
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

available_pairs = list(cost.keys())

model = gp.Model("M03_Assegnazione_personale")
model.Params.OutputFlag = 0

x = {
    (i, s): model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{s}")
    for i, s in available_pairs
}

model.setObjective(
    gp.quicksum(cost[i, s] * x[i, s] for i, s in available_pairs),
    GRB.MINIMIZE
)

for s in shifts:
    model.addConstr(
        gp.quicksum(x[i, s] for i in employees if (i, s) in x) == 1,
        name=f"copertura_{s}"
    )

for i in employees:
    model.addConstr(
        gp.quicksum(x[i, s] for s in shifts if (i, s) in x) <= 2,
        name=f"max_turni_{i}"
    )

for i in employees:
    model.addConstr(
        gp.quicksum(x[i, s] for s in night_shifts if (i, s) in x) <= 1,
        name=f"max_notturni_{i}"
    )

model.optimize()

status_names = {
    1: "LOADED",
    2: "OPTIMAL",
    3: "INFEASIBLE",
    4: "INF_OR_UNBD",
    5: "UNBOUNDED",
    6: "CUTOFF",
    7: "ITERATION_LIMIT",
    8: "NODE_LIMIT",
    9: "TIME_LIMIT",
    10: "SOLUTION_LIMIT",
    11: "INTERRUPTED",
    12: "NUMERIC",
    13: "SUBOPTIMAL",
    14: "INPROGRESS",
    15: "USER_OBJ_LIMIT",
    16: "WORK_LIMIT",
    17: "MEM_LIMIT"
}

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variable_values = {
        f"x_{i}_{s}": float(round(x[i, s].X))
        for i, s in available_pairs
    }
    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
