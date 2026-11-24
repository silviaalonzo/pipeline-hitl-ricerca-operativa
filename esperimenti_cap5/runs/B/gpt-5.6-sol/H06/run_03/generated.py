import gurobipy as gp
from gurobipy import GRB
import json

jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]

p = {
    "J1": 5, "J2": 7, "J3": 4, "J4": 6,
    "J5": 3, "J6": 8, "J7": 5
}
r = {
    "J1": 0, "J2": 0, "J3": 2, "J4": 3,
    "J5": 5, "J6": 0, "J7": 6
}
d = {
    "J1": 9, "J2": 17, "J3": 12, "J4": 22,
    "J5": 15, "J6": 28, "J7": 25
}
w = {
    "J1": 4, "J2": 3, "J3": 5, "J4": 2,
    "J5": 6, "J6": 2, "J7": 4
}

precedences = [("J1", "J2"), ("J3", "J5")]
pairs = [(jobs[a], jobs[b])
         for a in range(len(jobs))
         for b in range(a + 1, len(jobs))]

H = max(r.values()) + sum(p.values())
M = H

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.setParam("LogToConsole", 0)
env.start()

model = gp.Model("H06_sequenziamento", env=env)
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

S = model.addVars(jobs, lb=0.0, vtype=GRB.CONTINUOUS, name="S")
C = model.addVars(jobs, lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name="C")
T = model.addVars(jobs, lb=0.0, vtype=GRB.CONTINUOUS, name="T")
y = model.addVars(pairs, vtype=GRB.BINARY, name="y")

model.setObjective(
    gp.quicksum(w[j] * T[j] for j in jobs),
    GRB.MINIMIZE
)

for j in jobs:
    model.addConstr(S[j] >= r[j], name="availability_" + j)
    model.addConstr(C[j] == S[j] + p[j], name="completion_" + j)
    model.addConstr(T[j] >= C[j] - d[j], name="tardiness_" + j)

for i, j in pairs:
    model.addConstr(
        S[j] >= C[i] - M * (1 - y[i, j]),
        name="order_forward_" + i + "_" + j
    )
    model.addConstr(
        S[i] >= C[j] - M * y[i, j],
        name="order_reverse_" + i + "_" + j
    )

for i, j in precedences:
    model.addConstr(C[i] <= S[j], name="precedence_" + i + "_" + j)
    model.addConstr(y[i, j] == 1, name="fix_order_" + i + "_" + j)

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

def clean_number(value):
    value = float(value)
    if abs(value) <= 1e-8:
        return 0.0
    nearest_integer = round(value)
    if abs(value - nearest_integer) <= 1e-7:
        return float(nearest_integer)
    return float(round(value, 10))

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    all_variables = (
        [S[j] for j in jobs]
        + [C[j] for j in jobs]
        + [T[j] for j in jobs]
        + [y[i, j] for i, j in pairs]
    )
    payload = {
        "status": "OPTIMAL",
        "objective": clean_number(model.ObjVal),
        "variables": {
            variable.VarName: clean_number(variable.X)
            for variable in all_variables
        }
    }
else:
    payload = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
