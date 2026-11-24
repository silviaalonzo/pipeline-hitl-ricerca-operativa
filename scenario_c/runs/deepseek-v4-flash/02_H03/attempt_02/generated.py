import json
import gurobipy as gp
from gurobipy import GRB

employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

demand = {
    "Lun": 4,
    "Mar": 3,
    "Mer": 4,
    "Gio": 4,
    "Ven": 5,
    "Sab": 3,
    "Dom": 3,
}

cost = {
    "E1": [9, 9, 10, 9, 11, 14, None],
    "E2": [10, 9, 9, 10, 10, None, 14],
    "E3": [9, 10, 9, 9, 12, 12, 13],
    "E4": [7, None, 7, 8, 8, 11, 11],
    "E5": [8, 7, 8, None, 9, 10, 12],
    "E6": [None, 8, 8, 7, 8, 12, 10],
    "E7": [8, 8, 7, 9, 7, 11, None],
    "E8": [9, 7, 8, 8, 7, 10, 11],
}

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]

model = gp.Model("turnazione_settimanale")
model.Params.OutputFlag = 0

x = model.addVars(employees, days, vtype=GRB.BINARY, name="x")

for emp in employees:
    for idx, day in enumerate(days):
        if cost[emp][idx] is None:
            model.addConstr(x[emp, day] == 0, name=f"unavail_{emp}_{day}")

model.setObjective(
    gp.quicksum(
        cost[emp][idx] * x[emp, days[idx]]
        for emp in employees
        for idx in range(len(days))
        if cost[emp][idx] is not None
    ),
    GRB.MINIMIZE,
)

for day in days:
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in employees) >= demand[day],
        name=f"demand_{day}",
    )
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in seniors) >= 1,
        name=f"senior_{day}",
    )

for emp in employees:
    model.addConstr(
        gp.quicksum(x[emp, day] for day in days) >= 3,
        name=f"min_days_{emp}",
    )
    model.addConstr(
        gp.quicksum(x[emp, day] for day in days) <= 5,
        name=f"max_days_{emp}",
    )
    for start in range(4):
        model.addConstr(
            gp.quicksum(x[emp, days[start + k]] for k in range(4)) <= 3,
            name=f"no4_{emp}_{days[start]}",
        )

for day in ["Gio", "Ven"]:
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in specialists) >= 1,
        name=f"specialist_{day}",
    )

model.addConstr(
    x["E1", "Sab"] + x["E1", "Dom"] + x["E2", "Sab"] + x["E2", "Dom"] <= 1,
    name="weekend_E1_E2",
)

model.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": {v.VarName: v.X for v in model.getVars()},
    }
else:
    result = {
        "status": status_names.get(model.Status, str(model.Status)),
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
