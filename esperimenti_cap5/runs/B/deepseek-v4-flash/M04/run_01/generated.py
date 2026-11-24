import json
import gurobipy as gp
from gurobipy import GRB

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

emissione = {
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

m = gp.Model("flotta_giornaliera")
m.Params.OutputFlag = 0

x = {}
for t in tipi:
    x[t] = m.addVar(
        lb=0,
        ub=disponibilita[t],
        vtype=GRB.INTEGER,
        name=f"x_{t}"
    )

m.addConstr(gp.quicksum(volume[t] * x[t] for t in tipi) >= 180, "volume_min")
m.addConstr(gp.quicksum(portata[t] * x[t] for t in tipi) >= 95, "portata_min")
m.addConstr(x["Refrigerato"] >= 1, "refrigerato_min")
m.addConstr(x["Elettrico"] >= 1, "elettrico_min")
m.addConstr(gp.quicksum(emissione[t] * x[t] for t in tipi) <= 145, "emissioni_max")

m.setObjective(gp.quicksum(costo[t] * x[t] for t in tipi), GRB.MINIMIZE)

m.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
}

if m.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": {v.VarName: v.X for v in m.getVars()},
    }
else:
    result = {
        "status": status_names.get(m.Status, str(m.Status)),
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
