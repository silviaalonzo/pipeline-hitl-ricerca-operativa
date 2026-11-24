import json
from gurobipy import Model, GRB, quicksum

jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5,
}

E = [(i, m) for i in jobs for m in machines if (i, m) in p]

status = "ERROR"
objective = None
variables = {}

try:
    model = Model("M06_bilanciamento")
    model.Params.OutputFlag = 0

    x = {}
    for i, m in E:
        x[i, m] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{m}")

    C = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="C")
    model.update()

    model.setObjective(C, GRB.MINIMIZE)

    for i in jobs:
        model.addConstr(
            quicksum(x[i, m] for m in machines if (i, m) in E) == 1,
            name=f"assegnamento_{i}"
        )

    for m in machines:
        model.addConstr(
            C >= quicksum(p[i, m] * x[i, m] for i in jobs if (i, m) in E),
            name=f"carico_{m}"
        )

    model.optimize()

    if model.Status == GRB.OPTIMAL:
        status = "OPTIMAL"
        objective = C.X
        variables = {v.VarName: v.X for v in model.getVars()}
    elif model.Status == GRB.INFEASIBLE:
        status = "INFEASIBLE"
    elif model.Status == GRB.UNBOUNDED:
        status = "UNBOUNDED"
    else:
        status = str(model.Status)

except Exception:
    status = "ERROR"

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables
}))
