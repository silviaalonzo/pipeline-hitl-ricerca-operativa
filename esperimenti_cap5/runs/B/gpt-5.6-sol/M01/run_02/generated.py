import gurobipy as gp
from gurobipy import GRB
import json

sites = ["A", "B", "C", "D"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]

fixed_cost = {
    "A": 38,
    "B": 42,
    "C": 35,
    "D": 46
}

capacity = {
    "A": 2,
    "B": 3,
    "C": 2,
    "D": 3
}

assignment_cost = {
    ("Z1", "A"): 8,  ("Z1", "B"): 14, ("Z1", "C"): 11, ("Z1", "D"): 17,
    ("Z2", "A"): 10, ("Z2", "B"): 9,  ("Z2", "C"): 13, ("Z2", "D"): 15,
    ("Z3", "A"): 12, ("Z3", "B"): 8,  ("Z3", "C"): 14, ("Z3", "D"): 10,
    ("Z4", "A"): 15, ("Z4", "B"): 11, ("Z4", "C"): 9,  ("Z4", "D"): 7,
    ("Z5", "A"): 9,  ("Z5", "B"): 13, ("Z5", "C"): 8,  ("Z5", "D"): 14,
    ("Z6", "A"): 14, ("Z6", "B"): 10, ("Z6", "C"): 7,  ("Z6", "D"): 9
}

p = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M01_localizzazione_centri", env=env)

y = model.addVars(sites, vtype=GRB.BINARY, name="y")
x = model.addVars(zones, sites, vtype=GRB.BINARY, name="x")

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in sites)
    + gp.quicksum(
        assignment_cost[j, i] * x[j, i]
        for j in zones
        for i in sites
    ),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(y[i] for i in sites) == p,
    name="numero_centri"
)

model.addConstrs(
    (
        gp.quicksum(x[j, i] for i in sites) == 1
        for j in zones
    ),
    name="assegnazione"
)

model.addConstrs(
    (
        gp.quicksum(x[j, i] for j in zones) <= capacity[i] * y[i]
        for i in sites
    ),
    name="capacita"
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

status = status_names.get(model.Status, str(model.Status))

if model.Status == GRB.OPTIMAL:
    def clean_value(value):
        rounded = round(value)
        if abs(value - rounded) <= 1e-6:
            return float(rounded)
        return float(value)

    variables = {}

    for i in sites:
        variables[f"y[{i}]"] = clean_value(y[i].X)

    for j in zones:
        for i in sites:
            variables[f"x[{j},{i}]"] = clean_value(x[j, i].X)

    result = {
        "status": status,
        "objective": clean_value(model.ObjVal),
        "variables": variables
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
