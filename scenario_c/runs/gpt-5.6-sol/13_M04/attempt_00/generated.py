import gurobipy as gp
from gurobipy import GRB
import json

types = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {
    "Van": 18,
    "Autocarro": 30,
    "Refrigerato": 20,
    "Elettrico": 16,
    "Bilico": 42
}

payload = {
    "Van": 8,
    "Autocarro": 18,
    "Refrigerato": 10,
    "Elettrico": 7,
    "Bilico": 28
}

cost = {
    "Van": 120,
    "Autocarro": 180,
    "Refrigerato": 210,
    "Elettrico": 150,
    "Bilico": 260
}

emissions = {
    "Van": 12,
    "Autocarro": 22,
    "Refrigerato": 15,
    "Elettrico": 4,
    "Bilico": 32
}

availability = {
    "Van": 8,
    "Autocarro": 6,
    "Refrigerato": 4,
    "Elettrico": 5,
    "Bilico": 3
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("composizione_flotta_giornaliera", env=env)

x = {
    t: model.addVar(
        lb=0,
        ub=availability[t],
        vtype=GRB.INTEGER,
        name=f"x_{t}"
    )
    for t in types
}

model.setObjective(
    gp.quicksum(cost[t] * x[t] for t in types),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(volume[t] * x[t] for t in types) >= 180,
    name="volume_minimo"
)

model.addConstr(
    gp.quicksum(payload[t] * x[t] for t in types) >= 95,
    name="portata_minima"
)

model.addConstr(
    x["Refrigerato"] >= 1,
    name="almeno_un_refrigerato"
)

model.addConstr(
    x["Elettrico"] >= 1,
    name="almeno_un_elettrico"
)

model.addConstr(
    gp.quicksum(emissions[t] * x[t] for t in types) <= 145,
    name="emissioni_massime"
)

model.optimize()

status_names = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INPROGRESS: "INPROGRESS",
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT"
}

status_code = model.Status
status = status_names.get(status_code, f"STATUS_{status_code}")

if status_code == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": {
            f"x_{t}": float(round(x[t].X))
            for t in types
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

print("SOLUTION_JSON=" + json.dumps(result, ensure_ascii=False, separators=(",", ":")))
