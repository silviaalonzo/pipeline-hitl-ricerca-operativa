import gurobipy as gp
from gurobipy import GRB
import json

tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {
    "Van": 18,
    "Autocarro": 30,
    "Refrigerato": 20,
    "Elettrico": 16,
    "Bilico": 42
}

portata = {
    "Van": 8,
    "Autocarro": 18,
    "Refrigerato": 10,
    "Elettrico": 7,
    "Bilico": 28
}

costo = {
    "Van": 120,
    "Autocarro": 180,
    "Refrigerato": 210,
    "Elettrico": 150,
    "Bilico": 260
}

emissioni = {
    "Van": 12,
    "Autocarro": 22,
    "Refrigerato": 15,
    "Elettrico": 4,
    "Bilico": 32
}

disponibilita = {
    "Van": 8,
    "Autocarro": 6,
    "Refrigerato": 4,
    "Elettrico": 5,
    "Bilico": 3
}

m = gp.Model("flotta_giornaliera")
m.setParam("OutputFlag", 0)

x = {}
for t in tipi:
    x[t] = m.addVar(
        lb=0,
        ub=disponibilita[t],
        vtype=GRB.INTEGER,
        name=f"x_{t}"
    )

m.setObjective(
    gp.quicksum(costo[t] * x[t] for t in tipi),
    GRB.MINIMIZE
)

m.addConstr(gp.quicksum(volume[t] * x[t] for t in tipi) >= 180, "volume_min")
m.addConstr(gp.quicksum(portata[t] * x[t] for t in tipi) >= 95, "portata_min")
m.addConstr(x["Refrigerato"] >= 1, "refrigerato_min")
m.addConstr(x["Elettrico"] >= 1, "elettrico_min")
m.addConstr(gp.quicksum(emissioni[t] * x[t] for t in tipi) <= 145, "emissioni_max")

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: float(v.X) for v in m.getVars()}
else:
    code_to_status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.NODE_LIMIT: "NODE_LIMIT"
    }
    status = code_to_status.get(m.status, "OTHER")
    objective = None
    variables = {}

risultato = {
    "status": status,
    "objective": objective,
    "variables": variables
}

print("SOLUTION_JSON=" + json.dumps(risultato, separators=(",", ":")))
