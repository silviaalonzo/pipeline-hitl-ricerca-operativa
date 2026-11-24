import gurobipy as gp
from gurobipy import GRB
import json

sites = ["A", "B", "C", "D"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]

fixed_cost = {"A": 38, "B": 42, "C": 35, "D": 46}
capacity = {"A": 2, "B": 3, "C": 2, "D": 3}

service_cost = {
    "Z1": {"A": 8, "B": 14, "C": 11, "D": 17},
    "Z2": {"A": 10, "B": 9, "C": 13, "D": 15},
    "Z3": {"A": 12, "B": 8, "C": 14, "D": 10},
    "Z4": {"A": 15, "B": 11, "C": 9, "D": 7},
    "Z5": {"A": 9, "B": 13, "C": 8, "D": 14},
    "Z6": {"A": 14, "B": 10, "C": 7, "D": 9},
}

model = gp.Model("localizzazione_centri_assistenza")
model.setParam("OutputFlag", 0)

y = {}
for i in sites:
    y[i] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}")

x = {}
for i in sites:
    for j in zones:
        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in sites)
    + gp.quicksum(service_cost[j][i] * x[i, j] for i in sites for j in zones),
    GRB.MINIMIZE
)

model.addConstr(gp.quicksum(y[i] for i in sites) == 2, "esattamente_due_centri")

for i in sites:
    model.addConstr(
        gp.quicksum(x[i, j] for j in zones) <= capacity[i] * y[i],
        f"capacita_{i}"
    )

for j in zones:
    model.addConstr(
        gp.quicksum(x[i, j] for i in sites) == 1,
        f"zona_{j}"
    )

model.optimize()

if model.Status == GRB.OPTIMAL:
    solution = {
        "status": "OPTIMAL",
        "objective": model.ObjVal,
        "variables": {
            v.VarName: v.X for v in sorted(model.getVars(), key=lambda v: v.VarName)
        },
    }
else:
    solution = {
        "status": f"STATUS_{model.Status}",
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(solution, separators=(",", ":")))
