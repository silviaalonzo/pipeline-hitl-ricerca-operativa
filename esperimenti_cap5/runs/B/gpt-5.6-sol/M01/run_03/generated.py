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

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("localizzazione_centri", env=env)

y = {
    i: model.addVar(vtype=GRB.BINARY, name=f"y[{i}]")
    for i in sites
}

x = {
    (z, i): model.addVar(vtype=GRB.BINARY, name=f"x[{z},{i}]")
    for z in zones
    for i in sites
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in sites)
    + gp.quicksum(
        assignment_cost[z, i] * x[z, i]
        for z in zones
        for i in sites
    ),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(y[i] for i in sites) == 2,
    name="numero_centri"
)

for z in zones:
    model.addConstr(
        gp.quicksum(x[z, i] for i in sites) == 1,
        name=f"assegnazione[{z}]"
    )

for i in sites:
    model.addConstr(
        gp.quicksum(x[z, i] for z in zones) <= capacity[i] * y[i],
        name=f"capacita[{i}]"
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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variable_values = {}

    for i in sites:
        variable_values[f"y[{i}]"] = 1.0 if y[i].X > 0.5 else 0.0

    for z in zones:
        for i in sites:
            variable_values[f"x[{z},{i}]"] = (
                1.0 if x[z, i].X > 0.5 else 0.0
            )

    result = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
