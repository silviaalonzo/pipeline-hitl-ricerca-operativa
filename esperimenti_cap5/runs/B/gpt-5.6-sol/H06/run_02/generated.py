import gurobipy as gp
from gurobipy import GRB
import json

jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]

p = {"J1": 5, "J2": 7, "J3": 4, "J4": 6, "J5": 3, "J6": 8, "J7": 5}
r = {"J1": 0, "J2": 0, "J3": 2, "J4": 3, "J5": 5, "J6": 0, "J7": 6}
d = {"J1": 9, "J2": 17, "J3": 12, "J4": 22, "J5": 15, "J6": 28, "J7": 25}
w = {"J1": 4, "J2": 3, "J3": 5, "J4": 2, "J5": 6, "J6": 2, "J7": 4}

pairs = [(jobs[a], jobs[b])
         for a in range(len(jobs))
         for b in range(a + 1, len(jobs))]

H = max(r.values()) + sum(p.values())
M = H

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H06_sequenziamento_ritardi_pesati", env=env)

S = {
    i: model.addVar(
        lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name=f"S_{i}"
    )
    for i in jobs
}
C = {
    i: model.addVar(
        lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name=f"C_{i}"
    )
    for i in jobs
}
T = {
    i: model.addVar(
        lb=0.0, vtype=GRB.CONTINUOUS, name=f"T_{i}"
    )
    for i in jobs
}
x = {
    (i, j): model.addVar(
        vtype=GRB.BINARY, name=f"x_{i}_{j}"
    )
    for i, j in pairs
}

model.setObjective(
    gp.quicksum(w[i] * T[i] for i in jobs),
    GRB.MINIMIZE
)

for i in jobs:
    model.addConstr(S[i] >= r[i], name=f"availability_{i}")
    model.addConstr(C[i] == S[i] + p[i], name=f"completion_{i}")
    model.addConstr(T[i] >= C[i] - d[i], name=f"tardiness_{i}")

for i, j in pairs:
    model.addConstr(
        S[j] >= C[i] - M * (1 - x[i, j]),
        name=f"order_{i}_before_{j}"
    )
    model.addConstr(
        S[i] >= C[j] - M * x[i, j],
        name=f"order_{j}_before_{i}"
    )

model.addConstr(C["J1"] <= S["J2"], name="precedence_J1_J2")
model.addConstr(C["J3"] <= S["J5"], name="precedence_J3_J5")

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

def clean(value):
    if abs(value) < 1e-9:
        return 0.0
    return float(round(value, 10))

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": clean(model.ObjVal),
        "variables": {
            var.VarName: clean(var.X)
            for var in model.getVars()
        }
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
