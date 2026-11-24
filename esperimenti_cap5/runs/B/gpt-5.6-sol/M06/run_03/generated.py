import gurobipy as gp
from gurobipy import GRB
import json

jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

processing_time = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M06_bilanciamento_due_macchine", env=env)
model.Params.OutputFlag = 0

x = {
    (j, m): model.addVar(vtype=GRB.BINARY, name=f"x_{j}_{m}")
    for j in jobs
    for m in machines
}
C_max = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="C_max")

model.setObjective(C_max, GRB.MINIMIZE)

for j in jobs:
    model.addConstr(
        gp.quicksum(x[j, m] for m in machines) == 1,
        name=f"assegnazione_{j}"
    )

model.addConstr(x["J7", "A"] == 0, name="incompatibilita_J7_A")

for m in machines:
    model.addConstr(
        gp.quicksum(
            processing_time[j, m] * x[j, m]
            for j in jobs
            if (j, m) in processing_time
        ) <= C_max,
        name=f"makespan_{m}"
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

solver_status = status_names.get(int(model.Status), f"STATUS_{int(model.Status)}")

def clean_value(value):
    value = float(value)
    if abs(value) < 1e-9:
        return 0.0
    if abs(value - round(value)) < 1e-9:
        return float(round(value))
    return value

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for j in jobs:
        for m in machines:
            variable_values[f"x_{j}_{m}"] = clean_value(x[j, m].X)
    variable_values["C_max"] = clean_value(C_max.X)

    result = {
        "status": solver_status,
        "objective": clean_value(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
