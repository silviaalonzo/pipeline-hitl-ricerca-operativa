import gurobipy as gp
from gurobipy import GRB
import json

employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

demand = {
    "Lun": 4,
    "Mar": 3,
    "Mer": 4,
    "Gio": 4,
    "Ven": 5,
    "Sab": 3,
    "Dom": 3
}

cost = {
    "E1": {"Lun": 9,  "Mar": 9,  "Mer": 10, "Gio": 9,  "Ven": 11, "Sab": 14, "Dom": None},
    "E2": {"Lun": 10, "Mar": 9,  "Mer": 9,  "Gio": 10, "Ven": 10, "Sab": None, "Dom": 14},
    "E3": {"Lun": 9,  "Mar": 10, "Mer": 9,  "Gio": 9,  "Ven": 12, "Sab": 12, "Dom": 13},
    "E4": {"Lun": 7,  "Mar": None, "Mer": 7,  "Gio": 8,  "Ven": 8,  "Sab": 11, "Dom": 11},
    "E5": {"Lun": 8,  "Mar": 7,  "Mer": 8,  "Gio": None, "Ven": 9,  "Sab": 10, "Dom": 12},
    "E6": {"Lun": None, "Mar": 8,  "Mer": 8,  "Gio": 7,  "Ven": 8,  "Sab": 12, "Dom": 10},
    "E7": {"Lun": 8,  "Mar": 8,  "Mer": 7,  "Gio": 9,  "Ven": 7,  "Sab": 11, "Dom": None},
    "E8": {"Lun": 9,  "Mar": 7,  "Mer": 8,  "Gio": 8,  "Ven": 7,  "Sab": 10, "Dom": 11}
}

availability = {
    (i, d): 1 if cost[i][d] is not None else 0
    for i in employees
    for d in days
}

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]
specialist_days = ["Gio", "Ven"]

model = gp.Model("H03_turnazione_settimanale")
model.Params.OutputFlag = 0
model.Params.Threads = 1
model.Params.Seed = 0

x = {
    (i, d): model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{d}")
    for i in employees
    for d in days
}

model.setObjective(
    gp.quicksum(
        cost[i][d] * x[i, d]
        for i in employees
        for d in days
        if availability[i, d] == 1
    ),
    GRB.MINIMIZE
)

for d in days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in employees) >= demand[d],
        name=f"domanda_{d}"
    )

for d in days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in seniors) >= 1,
        name=f"senior_{d}"
    )

for i in employees:
    model.addConstr(
        gp.quicksum(x[i, d] for d in days) >= 3,
        name=f"min_giorni_{i}"
    )
    model.addConstr(
        gp.quicksum(x[i, d] for d in days) <= 5,
        name=f"max_giorni_{i}"
    )

for i in employees:
    for start in range(len(days) - 3):
        window = days[start:start + 4]
        model.addConstr(
            gp.quicksum(x[i, d] for d in window) <= 3,
            name=f"no_4_consecutivi_{i}_{start + 1}"
        )

for d in specialist_days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in specialists) >= 1,
        name=f"specialista_{d}"
    )

for i in ["E1", "E2"]:
    model.addConstr(
        x[i, "Sab"] + x[i, "Dom"] <= 1,
        name=f"weekend_{i}"
    )

for i in employees:
    for d in days:
        model.addConstr(
            x[i, d] <= availability[i, d],
            name=f"disponibilita_{i}_{d}"
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
    variable_values = {
        f"x_{i}_{d}": float(1.0 if x[i, d].X > 0.5 else 0.0)
        for i in employees
        for d in days
    }
    result = {
        "status": "OPTIMAL",
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
