import gurobipy as gp
from gurobipy import GRB
import json

centri = ["A", "B", "C", "D", "E", "F", "G", "H"]
zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10"]

costi = {
    "A": 24, "B": 20, "C": 27, "D": 22,
    "E": 25, "F": 19, "G": 23, "H": 21
}

zone_coperte = {
    "A": ["Z1", "Z2", "Z3"],
    "B": ["Z2", "Z3", "Z4", "Z5"],
    "C": ["Z1", "Z5", "Z6"],
    "D": ["Z3", "Z6", "Z7"],
    "E": ["Z4", "Z7", "Z8"],
    "F": ["Z5", "Z8", "Z9"],
    "G": ["Z6", "Z9", "Z10"],
    "H": ["Z7", "Z8", "Z10"]
}

copertura_richiesta = {
    z: 2 if z in ["Z3", "Z7"] else 1
    for z in zone
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("copertura_zone", env=env)

x = {
    i: model.addVar(vtype=GRB.BINARY, name="x_" + i)
    for i in centri
}

model.setObjective(
    gp.quicksum(costi[i] * x[i] for i in centri),
    GRB.MINIMIZE
)

for z in zone:
    model.addConstr(
        gp.quicksum(x[i] for i in centri if z in zone_coperte[i])
        >= copertura_richiesta[z],
        name="copertura_" + z
    )

model.addConstr(
    gp.quicksum(x[i] for i in centri) <= 5,
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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": {
            "x_" + i: float(round(x[i].X))
            for i in centri
        }
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
