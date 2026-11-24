import json
import gurobipy as gp
from gurobipy import GRB

veicoli = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

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

m = gp.Model("M04_Composizione_Flotta")
m.Params.OutputFlag = 0

x = {
    v: m.addVar(vtype=GRB.INTEGER, lb=0, ub=disponibilita[v], name=f"x_{v}")
    for v in veicoli
}

m.addConstr(
    gp.quicksum(volume[v] * x[v] for v in veicoli) >= 180,
    "volume_min",
)
m.addConstr(
    gp.quicksum(portata[v] * x[v] for v in veicoli) >= 95,
    "portata_min",
)
m.addConstr(x["Refrigerato"] >= 1, "refrigerato_min")
m.addConstr(x["Elettrico"] >= 1, "elettrico_min")
m.addConstr(
    gp.quicksum(emissioni[v] * x[v] for v in veicoli) <= 145,
    "emissioni_max",
)

m.setObjective(
    gp.quicksum(costo[v] * x[v] for v in veicoli),
    GRB.MINIMIZE,
)

m.optimize()

if m.Status == GRB.OPTIMAL:
    risultato = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": {v.varName: v.X for v in m.getVars()},
    }
else:
    risultato = {
        "status": str(m.Status),
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(risultato))
