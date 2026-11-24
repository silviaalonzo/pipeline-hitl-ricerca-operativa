import gurobipy as gp
from gurobipy import GRB
import json

T = range(1, 7)

d = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
c = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
U = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

I0 = 10
final_min = 5
L = 10
F = 40
h = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M09_piano_riordino", env=env)
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

q = {
    t: model.addVar(vtype=GRB.INTEGER, lb=0, name=f"q_{t}")
    for t in T
}
I = {
    t: model.addVar(vtype=GRB.INTEGER, lb=0, name=f"I_{t}")
    for t in T
}
y = {
    t: model.addVar(vtype=GRB.BINARY, name=f"y_{t}")
    for t in T
}

model.setObjective(
    gp.quicksum(c[t] * q[t] + F * y[t] + h * I[t] for t in T),
    GRB.MINIMIZE
)

for t in T:
    previous_inventory = I0 if t == 1 else I[t - 1]
    model.addConstr(
        I[t] == previous_inventory + q[t] - d[t],
        name=f"bilancio_{t}"
    )
    model.addConstr(q[t] >= L * y[t], name=f"ordine_minimo_{t}")
    model.addConstr(q[t] <= U[t] * y[t], name=f"capacita_{t}")

model.addConstr(I[6] >= final_min, name="scorta_finale_minima")

model.optimize()

status_candidates = [
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT",
    "SOLUTION_LIMIT", "INTERRUPTED", "NUMERIC", "SUBOPTIMAL",
    "INPROGRESS", "USER_OBJ_LIMIT", "WORK_LIMIT", "MEM_LIMIT"
]

status_name = f"STATUS_{model.Status}"
for candidate in status_candidates:
    if getattr(GRB, candidate, None) == model.Status:
        status_name = candidate
        break

if model.Status == GRB.OPTIMAL:
    def numeric_value(value):
        if abs(value) < 1e-7:
            return 0.0
        rounded = round(value)
        if abs(value - rounded) < 1e-6:
            return float(rounded)
        return float(value)

    variables = {}
    for t in T:
        variables[f"q_{t}"] = numeric_value(q[t].X)
    for t in T:
        variables[f"I_{t}"] = numeric_value(I[t].X)
    for t in T:
        variables[f"y_{t}"] = numeric_value(y[t].X)

    result = {
        "status": "OPTIMAL",
        "objective": numeric_value(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status_name,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":"), allow_nan=False))
