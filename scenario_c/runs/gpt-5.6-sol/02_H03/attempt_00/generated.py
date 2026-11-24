import gurobipy as gp
from gurobipy import GRB
import json

employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]
specialist_days = ["Gio", "Ven"]

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
    ("E1", "Lun"): 9,  ("E1", "Mar"): 9,  ("E1", "Mer"): 10,
    ("E1", "Gio"): 9,  ("E1", "Ven"): 11, ("E1", "Sab"): 14,

    ("E2", "Lun"): 10, ("E2", "Mar"): 9,  ("E2", "Mer"): 9,
    ("E2", "Gio"): 10, ("E2", "Ven"): 10, ("E2", "Dom"): 14,

    ("E3", "Lun"): 9,  ("E3", "Mar"): 10, ("E3", "Mer"): 9,
    ("E3", "Gio"): 9,  ("E3", "Ven"): 12, ("E3", "Sab"): 12,
    ("E3", "Dom"): 13,

    ("E4", "Lun"): 7,  ("E4", "Mer"): 7,  ("E4", "Gio"): 8,
    ("E4", "Ven"): 8,  ("E4", "Sab"): 11, ("E4", "Dom"): 11,

    ("E5", "Lun"): 8,  ("E5", "Mar"): 7,  ("E5", "Mer"): 8,
    ("E5", "Ven"): 9,  ("E5", "Sab"): 10, ("E5", "Dom"): 12,

    ("E6", "Mar"): 8,  ("E6", "Mer"): 8,  ("E6", "Gio"): 7,
    ("E6", "Ven"): 8,  ("E6", "Sab"): 12, ("E6", "Dom"): 10,

    ("E7", "Lun"): 8,  ("E7", "Mar"): 8,  ("E7", "Mer"): 7,
    ("E7", "Gio"): 9,  ("E7", "Ven"): 7,  ("E7", "Sab"): 11,

    ("E8", "Lun"): 9,  ("E8", "Mar"): 7,  ("E8", "Mer"): 8,
    ("E8", "Gio"): 8,  ("E8", "Ven"): 7,  ("E8", "Sab"): 10,
    ("E8", "Dom"): 11
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H03_turnazione_settimanale", env=env)

x = model.addVars(employees, days, vtype=GRB.BINARY, name="x")

model.setObjective(
    gp.quicksum(cost[i, d] * x[i, d] for i, d in cost),
    GRB.MINIMIZE
)

# Copertura della domanda.
for d in days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in employees) >= demand[d],
        name=f"domanda_{d}"
    )

# Almeno un senior ogni giorno.
for d in days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in seniors) >= 1,
        name=f"senior_{d}"
    )

# Ogni dipendente lavora da tre a cinque giorni.
for i in employees:
    weekly_work = gp.quicksum(x[i, d] for d in days)
    model.addConstr(weekly_work >= 3, name=f"min_giorni_{i}")
    model.addConstr(weekly_work <= 5, name=f"max_giorni_{i}")

# Nessun dipendente può lavorare quattro giorni consecutivi.
for i in employees:
    for start in range(len(days) - 3):
        window = days[start:start + 4]
        model.addConstr(
            gp.quicksum(x[i, d] for d in window) <= 3,
            name=f"no_4_consecutivi_{i}_{start}"
        )

# Almeno uno tra E7 ed E8 deve essere presente giovedì e venerdì.
for d in specialist_days:
    model.addConstr(
        gp.quicksum(x[i, d] for i in specialists) >= 1,
        name=f"specialista_{d}"
    )

# E1 ed E2 lavorano al massimo uno dei due giorni del weekend.
for i in ["E1", "E2"]:
    model.addConstr(
        x[i, "Sab"] + x[i, "Dom"] <= 1,
        name=f"weekend_{i}"
    )

# Indisponibilità.
for i in employees:
    for d in days:
        if (i, d) not in cost:
            model.addConstr(x[i, d] == 0, name=f"indisponibile_{i}_{d}")

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
    for i in employees:
        for d in days:
            variable_values[f"x[{i},{d}]"] = float(round(x[i, d].X))

    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
