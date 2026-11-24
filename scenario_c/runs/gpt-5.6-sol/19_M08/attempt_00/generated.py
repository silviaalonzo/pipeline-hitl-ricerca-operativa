import gurobipy as gp
from gurobipy import GRB
import json

centers = ["A", "B", "C", "D", "E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10"]

cost = {
    "A": 24,
    "B": 20,
    "C": 27,
    "D": 22,
    "E": 25,
    "F": 19,
    "G": 23,
    "H": 21
}

coverage = {
    "Z1": ["A", "C"],
    "Z2": ["A", "B"],
    "Z3": ["A", "B", "D"],
    "Z4": ["B", "E"],
    "Z5": ["B", "C", "F"],
    "Z6": ["C", "D", "G"],
    "Z7": ["D", "E", "H"],
    "Z8": ["E", "F", "H"],
    "Z9": ["F", "G"],
    "Z10": ["G", "H"]
}

required_coverage = {
    zone: 2 if zone in ["Z3", "Z7"] else 1
    for zone in zones
}

max_open_centers = 5

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("copertura_zone", env=env)

x = {
    center: model.addVar(vtype=GRB.BINARY, name="x_" + center)
    for center in centers
}

model.setObjective(
    gp.quicksum(cost[center] * x[center] for center in centers),
    GRB.MINIMIZE
)

for zone in zones:
    model.addConstr(
        gp.quicksum(x[center] for center in coverage[zone])
        >= required_coverage[zone],
        name="coverage_" + zone
    )

model.addConstr(
    gp.quicksum(x[center] for center in centers) <= max_open_centers,
    name="max_open_centers"
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

solver_status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for center in centers:
        value = x[center].X
        if abs(value - round(value)) <= 1e-9:
            value = float(round(value))
        else:
            value = float(value)
        variable_values["x_" + center] = value

    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
