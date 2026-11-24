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

emission_limit = 145

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H04_allocazione_flotta", env=env)

x = {}
y = {}

for r in routes:
    for t in types:
        x[r, t] = model.addVar(
            lb=0,
            vtype=GRB.INTEGER,
            name=f"x_{r}_{t}"
        )
        y[r, t] = model.addVar(
            vtype=GRB.BINARY,
            name=f"y_{r}_{t}"
        )

model.setObjective(
    gp.quicksum(cost[r, t] * x[r, t] for r in routes for t in types),
    GRB.MINIMIZE
)

for r in routes:
    model.addConstr(
        gp.quicksum(capacity[t] * x[r, t] for t in types) >= demand[r],
        name=f"domanda_{r}"
    )

for t in types:
    model.addConstr(
        gp.quicksum(x[r, t] for r in routes) <= availability[t],
        name=f"disponibilita_{t}"
    )

for r in routes:
    for t in types:
        model.addConstr(
            x[r, t] <= availability[t] * y[r, t],
            name=f"link_superiore_{r}_{t}"
        )
        model.addConstr(
            x[r, t] >= y[r, t],
            name=f"link_inferiore_{r}_{t}"
        )

for r in routes:
    model.addConstr(
        gp.quicksum(y[r, t] for t in types) <= 2,
        name=f"massimo_due_tipi_{r}"
    )

model.addConstr(
    x["R4", "Grande"] >= 1,
    name="grande_obbligatorio_R4"
)

model.addConstr(
    gp.quicksum(
        emissions[t] * x[r, t]
        for r in routes
        for t in types
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

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variable_values = {}

    for r in routes:
        for t in types:
            variable_values[f"x_{r}_{t}"] = float(round(x[r, t].X))

    for r in routes:
        for t in types:
            variable_values[f"y_{r}_{t}"] = float(round(y[r, t].X))

    result = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
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
