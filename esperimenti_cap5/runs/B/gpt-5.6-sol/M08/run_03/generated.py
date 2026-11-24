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
    "A": ["Z1", "Z2", "Z3"],
    "B": ["Z2", "Z3", "Z4", "Z5"],
    "C": ["Z1", "Z5", "Z6"],
    "D": ["Z3", "Z6", "Z7"],
    "E": ["Z4", "Z7", "Z8"],
    "F": ["Z5", "Z8", "Z9"],
    "G": ["Z6", "Z9", "Z10"],
    "H": ["Z7", "Z8", "Z10"]
}

required_coverage = {
    zone: 2 if zone in {"Z3", "Z7"} else 1
    for zone in zones
}

max_centers = 5

model = gp.Model("M08_copertura_zone")
model.Params.OutputFlag = 0

x = {
    center: model.addVar(vtype=GRB.BINARY, name=f"x_{center}")
    for center in centers
}

model.setObjective(
    gp.quicksum(cost[center] * x[center] for center in centers),
    GRB.MINIMIZE
)

for zone in zones:
    model.addConstr(
        gp.quicksum(
            x[center]
            for center in centers
            if zone in coverage[center]
        ) >= required_coverage[zone],
        name=f"copertura_{zone}"
    )

model.addConstr(
    gp.quicksum(x[center] for center in centers) <= max_centers,
    name="massimo_centri"
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

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    result = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": {
            f"x_{center}": float(round(x[center].X))
            for center in centers
        }
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
