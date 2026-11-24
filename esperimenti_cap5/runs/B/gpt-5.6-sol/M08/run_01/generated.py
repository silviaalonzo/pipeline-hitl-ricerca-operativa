import gurobipy as gp
from gurobipy import GRB
import json

centers = ["A", "B", "C", "D", "E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10"]

cost = {
    "A": 24, "B": 20, "C": 27, "D": 22,
    "E": 25, "F": 19, "G": 23, "H": 21
}

covered_zones = {
    "A": {"Z1", "Z2", "Z3"},
    "B": {"Z2", "Z3", "Z4", "Z5"},
    "C": {"Z1", "Z5", "Z6"},
    "D": {"Z3", "Z6", "Z7"},
    "E": {"Z4", "Z7", "Z8"},
    "F": {"Z5", "Z8", "Z9"},
    "G": {"Z6", "Z9", "Z10"},
    "H": {"Z7", "Z8", "Z10"}
}

required_coverage = {
    z: (2 if z in {"Z3", "Z7"} else 1)
    for z in zones
}

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

with gp.Env(empty=True) as env:
    env.setParam("OutputFlag", 0)
    env.start()

    with gp.Model("copertura_zone", env=env) as model:
        x = {
            i: model.addVar(vtype=GRB.BINARY, name=f"x_{i}")
            for i in centers
        }

        model.setObjective(
            gp.quicksum(cost[i] * x[i] for i in centers),
            GRB.MINIMIZE
        )

        for z in zones:
            model.addConstr(
                gp.quicksum(
                    x[i] for i in centers if z in covered_zones[i]
                ) >= required_coverage[z],
                name=f"copertura_{z}"
            )

        model.addConstr(
            gp.quicksum(x[i] for i in centers) <= 5,
            name="massimo_centri"
        )

        model.optimize()

        status_code = model.Status
        status = status_names.get(status_code, f"STATUS_{status_code}")

        if status_code == GRB.OPTIMAL:
            objective = float(round(model.ObjVal, 10))
            variables = {
                f"x_{i}": float(round(x[i].X))
                for i in centers
            }
        else:
            objective = None
            variables = {}

        result = {
            "status": status,
            "objective": objective,
            "variables": variables
        }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
