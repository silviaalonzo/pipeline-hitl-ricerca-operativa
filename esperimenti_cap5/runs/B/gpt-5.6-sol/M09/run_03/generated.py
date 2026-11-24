import gurobipy as gp
from gurobipy import GRB
import json

T = range(1, 7)

d = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
c = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
U = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

I0 = 10
I_final_min = 5
L = 10
F = 40
h = 2

model = gp.Model("M09_piano_riordino")
model.Params.OutputFlag = 0

x = {
    t: model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{t}")
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
    gp.quicksum(c[t] * x[t] + F * y[t] + h * I[t] for t in T),
    GRB.MINIMIZE
)

model.addConstr(I[1] == I0 + x[1] - d[1], name="bilancio_1")

for t in range(2, 7):
    model.addConstr(
        I[t] == I[t - 1] + x[t] - d[t],
        name=f"bilancio_{t}"
    )

for t in T:
    model.addConstr(x[t] >= L * y[t], name=f"ordine_minimo_{t}")
    model.addConstr(x[t] <= U[t] * y[t], name=f"capacita_{t}")

model.addConstr(I[6] >= I_final_min, name="scorta_finale_minima")

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

status = status_names.get(model.Status, "UNKNOWN")

if model.Status == GRB.OPTIMAL:
    def numeric_value(value):
        rounded = round(value)
        if abs(value - rounded) <= 1e-6:
            return float(rounded)
        return float(value)

    variables = {}
    for t in T:
        variables[f"x_{t}"] = numeric_value(x[t].X)
    for t in T:
        variables[f"I_{t}"] = numeric_value(I[t].X)
    for t in T:
        variables[f"y_{t}"] = numeric_value(y[t].X)

    result = {
        "status": status,
        "objective": numeric_value(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
