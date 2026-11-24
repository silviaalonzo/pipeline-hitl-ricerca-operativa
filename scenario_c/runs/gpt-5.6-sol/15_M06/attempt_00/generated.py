import gurobipy as gp
from gurobipy import GRB
import json

jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

# Sono incluse esclusivamente le coppie compatibili.
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5
}

arcs = list(p.keys())

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M06_bilanciamento_due_macchine", env=env)
model.Params.OutputFlag = 0

x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
C_max = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="C_max")

for j in jobs:
    model.addConstr(
        gp.quicksum(x[j, m] for m in machines if (j, m) in p) == 1,
        name=f"assegnazione[{j}]"
    )

for m in machines:
    model.addConstr(
        gp.quicksum(p[j, m] * x[j, m] for j in jobs if (j, m) in p) <= C_max,
        name=f"carico[{m}]"
    )

model.setObjective(C_max, GRB.MINIMIZE)
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

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variables = {}
    for j, m in arcs:
        value = float(x[j, m].X)
        if abs(value - round(value)) <= 1e-6:
            value = float(round(value))
        variables[f"x[{j},{m}]"] = value

    c_value = float(C_max.X)
    if abs(c_value - round(c_value)) <= 1e-6:
        c_value = float(round(c_value))
    variables["C_max"] = c_value

    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
