import gurobipy as gp
from gurobipy import GRB
import json
import itertools

jobs = ("J1", "J2", "J3", "J4", "J5", "J6", "J7")

duration = {
    "J1": 5, "J2": 7, "J3": 4, "J4": 6,
    "J5": 3, "J6": 8, "J7": 5
}
release = {
    "J1": 0, "J2": 0, "J3": 2, "J4": 3,
    "J5": 5, "J6": 0, "J7": 6
}
due = {
    "J1": 9, "J2": 17, "J3": 12, "J4": 22,
    "J5": 15, "J6": 28, "J7": 25
}
weight = {
    "J1": 4, "J2": 3, "J3": 5, "J4": 2,
    "J5": 6, "J6": 2, "J7": 4
}

precedence = (("J1", "J2"), ("J3", "J5"))
pairs = tuple(itertools.combinations(jobs, 2))

H = max(release.values()) + sum(duration.values())
M = H

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H06_sequenziamento_ritardi_pesati", env=env)
model.Params.MIPGap = 0.0

S = model.addVars(
    jobs, lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name="S"
)
C = model.addVars(
    jobs, lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name="C"
)
T = model.addVars(
    jobs, lb=0.0, vtype=GRB.CONTINUOUS, name="T"
)
y = model.addVars(
    pairs, vtype=GRB.BINARY, name="y"
)

model.setObjective(
    gp.quicksum(weight[j] * T[j] for j in jobs),
    GRB.MINIMIZE
)

for j in jobs:
    model.addConstr(C[j] == S[j] + duration[j], name="completion_" + j)
    model.addConstr(S[j] >= release[j], name="release_" + j)
    model.addConstr(T[j] >= C[j] - due[j], name="tardiness_" + j)

for i, j in pairs:
    model.addConstr(
        S[j] >= C[i] - M * (1 - y[i, j]),
        name="order_forward_" + i + "_" + j
    )
    model.addConstr(
        S[i] >= C[j] - M * y[i, j],
        name="order_reverse_" + i + "_" + j
    )

for i, j in precedence:
    model.addConstr(S[j] >= C[i], name="precedence_" + i + "_" + j)

model.optimize()

status_names = {}
for name in (
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT",
    "SOLUTION_LIMIT", "INTERRUPTED", "NUMERIC", "SUBOPTIMAL",
    "INPROGRESS", "USER_OBJ_LIMIT", "WORK_LIMIT", "MEM_LIMIT"
):
    if hasattr(GRB, name):
        status_names[getattr(GRB, name)] = name

status = status_names.get(model.Status, str(model.Status))

def clean_number(value):
    if abs(value) <= 1e-8:
        return 0.0
    nearest_integer = round(value)
    if abs(value - nearest_integer) <= 1e-8:
        return float(nearest_integer)
    return float(value)

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": clean_number(model.ObjVal),
        "variables": {
            variable.VarName: clean_number(variable.X)
            for variable in model.getVars()
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
