import gurobipy as gp
from gurobipy import GRB
import json

jobs = [1, 2, 3, 4, 5, 6, 7]
machines = ["A", "B"]

p = {
    (1, "A"): 7, (1, "B"): 9,
    (2, "A"): 6, (2, "B"): 5,
    (3, "A"): 8, (3, "B"): 7,
    (4, "A"): 5, (4, "B"): 8,
    (5, "A"): 9, (5, "B"): 6,
    (6, "A"): 4, (6, "B"): 7,
    (7, "A"): 0, (7, "B"): 5,
}

model = gp.Model("M06")
model.Params.OutputFlag = 0

x = {}
for j in jobs:
    for m in machines:
        x[j, m] = model.addVar(vtype=GRB.BINARY, name=f"x_{j}_{m}")

C = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="C")

model.update()

for j in jobs:
    model.addConstr(gp.quicksum(x[j, m] for m in machines) == 1, name=f"assegnazione_{j}")

for m in machines:
    model.addConstr(gp.quicksum(p[j, m] * x[j, m] for j in jobs) <= C, name=f"carico_{m}")

model.addConstr(x[7, "A"] == 0, name="incompatibilita_J7_A")

model.setObjective(C, GRB.MINIMIZE)

model.optimize()

if model.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = model.ObjVal
    variables = {v.VarName: v.X for v in model.getVars()}
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }
    status = status_map.get(model.Status, "UNKNOWN")
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective, "variables": variables},
    separators=(",", ":")
))
