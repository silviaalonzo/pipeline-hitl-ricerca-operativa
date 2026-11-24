import gurobipy as gp
from gurobipy import GRB
import json

routes = ["R1", "R2", "R3", "R4"]
types = ["Piccolo", "Medio", "Grande"]

demand = {
    "R1": 42,
    "R2": 55,
    "R3": 38,
    "R4": 64
}

capacity = {
    "Piccolo": 8,
    "Medio": 14,
    "Grande": 20
}

availability = {
    "Piccolo": 10,
    "Medio": 9,
    "Grande": 6
}

emissions = {
    "Piccolo": 5,
    "Medio": 8,
    "Grande": 11
}

cost = {
    ("R1", "Piccolo"): 45,
    ("R1", "Medio"): 62,
    ("R1", "Grande"): 82,
    ("R2", "Piccolo"): 52,
    ("R2", "Medio"): 68,
    ("R2", "Grande"): 88,
    ("R3", "Piccolo"): 40,
    ("R3", "Medio"): 58,
    ("R3", "Grande"): 79,
    ("R4", "Piccolo"): 60,
    ("R4", "Medio"): 77,
    ("R4", "Grande"): 96
}

max_emissions = 145
max_types_per_route = 2

model = gp.Model("H04_allocazione_flotta")
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

x = model.addVars(
    routes,
    types,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)

y = model.addVars(
    routes,
    types,
    vtype=GRB.BINARY,
    name="y"
)

model.setObjective(
    gp.quicksum(cost[r, t] * x[r, t] for r in routes for t in types),
    GRB.MINIMIZE
)

model.addConstrs(
    (
        gp.quicksum(capacity[t] * x[r, t] for t in types) >= demand[r]
        for r in routes
    ),
    name="copertura_domanda"
)

model.addConstrs(
    (
        gp.quicksum(x[r, t] for r in routes) <= availability[t]
        for t in types
    ),
    name="disponibilita"
)

model.addConstrs(
    (
        x[r, t] <= availability[t] * y[r, t]
        for r in routes
        for t in types
    ),
    name="link_superiore"
)

model.addConstrs(
    (
        x[r, t] >= y[r, t]
        for r in routes
        for t in types
    ),
    name="link_inferiore"
)

model.addConstrs(
    (
        gp.quicksum(y[r, t] for t in types) <= max_types_per_route
        for r in routes
    ),
    name="massimo_due_tipi"
)

model.addConstr(
    x["R4", "Grande"] >= 1,
    name="grande_su_R4"
)

model.addConstr(
    gp.quicksum(
        emissions[t] * x[r, t]
        for r in routes
        for t in types
    ) <= max_emissions,
    name="limite_emissioni"
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

    for r in routes:
        for t in types:
            variable_values[f"x[{r},{t}]"] = float(round(x[r, t].X))

    for r in routes:
        for t in types:
            variable_values[f"y[{r},{t}]"] = float(round(y[r, t].X))

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
