import gurobipy as gp
from gurobipy import GRB
import json

V = ["Piccolo", "Medio", "Grande"]
R = ["R1", "R2", "R3", "R4"]

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

emission = {
    "Piccolo": 5,
    "Medio": 8,
    "Grande": 11
}

cost = {
    ("Piccolo", "R1"): 45,
    ("Medio", "R1"): 62,
    ("Grande", "R1"): 82,
    ("Piccolo", "R2"): 52,
    ("Medio", "R2"): 68,
    ("Grande", "R2"): 88,
    ("Piccolo", "R3"): 40,
    ("Medio", "R3"): 58,
    ("Grande", "R3"): 79,
    ("Piccolo", "R4"): 60,
    ("Medio", "R4"): 77,
    ("Grande", "R4"): 96
}

emission_limit = 145
max_types_per_route = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("Allocazione_flotta", env=env)

x = model.addVars(V, R, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(V, R, vtype=GRB.BINARY, name="y")

model.setObjective(
    gp.quicksum(cost[v, r] * x[v, r] for v in V for r in R),
    GRB.MINIMIZE
)

model.addConstrs(
    (
        gp.quicksum(capacity[v] * x[v, r] for v in V) >= demand[r]
        for r in R
    ),
    name="copertura_domanda"
)

model.addConstrs(
    (
        gp.quicksum(x[v, r] for r in R) <= availability[v]
        for v in V
    ),
    name="disponibilita"
)

model.addConstrs(
    (
        x[v, r] <= availability[v] * y[v, r]
        for v in V for r in R
    ),
    name="attivazione_superiore"
)

model.addConstrs(
    (
        x[v, r] >= y[v, r]
        for v in V for r in R
    ),
    name="attivazione_inferiore"
)

model.addConstrs(
    (
        gp.quicksum(y[v, r] for v in V) <= max_types_per_route
        for r in R
    ),
    name="massimo_due_tipi"
)

model.addConstr(
    x["Grande", "R4"] >= 1,
    name="grande_su_R4"
)

model.addConstr(
    gp.quicksum(
        emission[v] * x[v, r]
        for v in V for r in R
    ) <= emission_limit,
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

status_code = int(model.Status)
status = status_names.get(status_code, "STATUS_" + str(status_code))

if status_code == GRB.OPTIMAL:
    variables = {}
    for v in V:
        for r in R:
            variables[x[v, r].VarName] = float(round(x[v, r].X))
    for v in V:
        for r in R:
            variables[y[v, r].VarName] = float(round(y[v, r].X))

    payload = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variables
    }
else:
    payload = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
