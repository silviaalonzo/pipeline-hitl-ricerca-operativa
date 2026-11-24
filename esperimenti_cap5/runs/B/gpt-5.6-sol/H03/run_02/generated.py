import gurobipy as gp
from gurobipy import GRB
import json

employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

demand = {
    "Lun": 4, "Mar": 3, "Mer": 4, "Gio": 4,
    "Ven": 5, "Sab": 3, "Dom": 3
}

raw_costs = {
    "E1": {"Lun": 9, "Mar": 9, "Mer": 10, "Gio": 9, "Ven": 11, "Sab": 14, "Dom": None},
    "E2": {"Lun": 10, "Mar": 9, "Mer": 9, "Gio": 10, "Ven": 10, "Sab": None, "Dom": 14},
    "E3": {"Lun": 9, "Mar": 10, "Mer": 9, "Gio": 9, "Ven": 12, "Sab": 12, "Dom": 13},
    "E4": {"Lun": 7, "Mar": None, "Mer": 7, "Gio": 8, "Ven": 8, "Sab": 11, "Dom": 11},
    "E5": {"Lun": 8, "Mar": 7, "Mer": 8, "Gio": None, "Ven": 9, "Sab": 10, "Dom": 12},
    "E6": {"Lun": None, "Mar": 8, "Mer": 8, "Gio": 7, "Ven": 8, "Sab": 12, "Dom": 10},
    "E7": {"Lun": 8, "Mar": 8, "Mer": 7, "Gio": 9, "Ven": 7, "Sab": 11, "Dom": None},
    "E8": {"Lun": 9, "Mar": 7, "Mer": 8, "Gio": 8, "Ven": 7, "Sab": 10, "Dom": 11}
}

availability = {
    (i, d): int(raw_costs[i][d] is not None)
    for i in employees
    for d in days
}

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]
specialist_days = ["Gio", "Ven"]
weekend_limited = ["E1", "E2"]

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H03_turnazione_settimanale", env=env)

x = model.addVars(
    employees,
    days,
    vtype=GRB.BINARY,
    name="x"
)

model.setObjective(
    gp.quicksum(
        raw_costs[i][d] * x[i, d]
        for i in employees
        for d in days
        if raw_costs[i][d] is not None
    ),
    GRB.MINIMIZE
)

model.addConstrs(
    (
        gp.quicksum(x[i, d] for i in employees) >= demand[d]
        for d in days
    ),
    name="domanda"
)

model.addConstrs(
    (
        gp.quicksum(x[i, d] for i in seniors) >= 1
        for d in days
    ),
    name="senior"
)

model.addConstrs(
    (
        gp.quicksum(x[i, d] for d in days) >= 3
        for i in employees
    ),
    name="min_giorni"
)

model.addConstrs(
    (
        gp.quicksum(x[i, d] for d in days) <= 5
        for i in employees
    ),
    name="max_giorni"
)

model.addConstrs(
    (
        gp.quicksum(x[i, days[k + h]] for h in range(4)) <= 3
        for i in employees
        for k in range(len(days) - 3)
    ),
    name="no_quattro_consecutivi"
)

model.addConstrs(
    (
        gp.quicksum(x[i, d] for i in specialists) >= 1
        for d in specialist_days
    ),
    name="specialista"
)

model.addConstrs(
    (
        x[i, "Sab"] + x[i, "Dom"] <= 1
        for i in weekend_limited
    ),
    name="limite_weekend"
)

model.addConstrs(
    (
        x[i, d] <= availability[i, d]
        for i in employees
        for d in days
    ),
    name="disponibilita"
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
    objective = float(round(model.ObjVal, 10))
    variables = {
        x[i, d].VarName: float(round(x[i, d].X, 10))
        for i in employees
        for d in days
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
