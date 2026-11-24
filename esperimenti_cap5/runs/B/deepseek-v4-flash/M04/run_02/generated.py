import gurobipy as gp
from gurobipy import GRB
import json

tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {
    "Van": 18,
    "Autocarro": 30,
    "Refrigerato": 20,
    "Elettrico": 16,
    "Bilico": 42,
}

portata = {
    "Van": 8,
    "Autocarro": 18,
    "Refrigerato": 10,
    "Elettrico": 7,
    "Bilico": 28,
}

costo = {
    "Van": 120,
    "Autocarro": 180,
    "Refrigerato": 210,
    "Elettrico": 150,
    "Bilico": 260,
}

emissioni = {
    "Van": 12,
    "Autocarro": 22,
    "Refrigerato": 15,
    "Elettrico": 4,
    "Bilico": 32,
}

disponibilita = {
    "Van": 8,
    "Autocarro": 6,
    "Refrigerato": 4,
    "Elettrico": 5,
    "Bilico": 3,
}

modello = gp.Model("flotta_giornaliera")
modello.setParam("OutputFlag", 0)

x = {}
for t in tipi:
    x[t] = modello.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        ub=disponibilita[t],
        name=f"x_{t}"
    )

modello.update()

modello.setObjective(
    gp.quicksum(costo[t] * x[t] for t in tipi),
    GRB.MINIMIZE
)

modello.addConstr(
    gp.quicksum(volume[t] * x[t] for t in tipi) >= 180,
    "volume_min"
)

modello.addConstr(
    gp.quicksum(portata[t] * x[t] for t in tipi) >= 95,
    "portata_min"
)

modello.addConstr(
    gp.quicksum(emissioni[t] * x[t] for t in tipi) <= 145,
    "emissioni_max"
)

modello.addConstr(x["Refrigerato"] >= 1, "refrigerato_min")
modello.addConstr(x["Elettrico"] >= 1, "elettrico_min")

modello.optimize()

stati = {
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
}

if modello.Status == GRB.OPTIMAL:
    variabili = {f"x_{t}": float(x[t].X) for t in tipi}
    payload = {
        "status": "OPTIMAL",
        "objective": float(modello.ObjVal),
        "variables": variabili,
    }
else:
    payload = {
        "status": stati.get(modello.Status, "UNKNOWN"),
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(payload, ensure_ascii=False))
