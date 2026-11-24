import gurobipy as gp
from gurobipy import GRB

# Dati
types = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {"Van": 18, "Autocarro": 30, "Refrigerato": 20, "Elettrico": 16, "Bilico": 42}
portata = {"Van": 8, "Autocarro": 18, "Refrigerato": 10, "Elettrico": 7, "Bilico": 28}
costo = {"Van": 120, "Autocarro": 180, "Refrigerato": 210, "Elettrico": 150, "Bilico": 260}
emissioni = {"Van": 12, "Autocarro": 22, "Refrigerato": 15, "Elettrico": 4, "Bilico": 32}
disponibilita = {"Van": 8, "Autocarro": 6, "Refrigerato": 4, "Elettrico": 5, "Bilico": 3}

# Modello
m = gp.Model("composizione_flotta")

x = m.addVars(types, vtype=GRB.INTEGER, lb=0, name="x")

# Vincoli di disponibilità
for t in types:
    x[t].ub = disponibilita[t]

# Vincoli di volume e portata
m.addConstr(gp.quicksum(volume[t] * x[t] for t in types) >= 180, name="volume_min")
m.addConstr(gp.quicksum(portata[t] * x[t] for t in types) >= 95, name="portata_min")

# Almeno un refrigerato e un elettrico
m.addConstr(x["Refrigerato"] >= 1, name="min_refrigerato")
m.addConstr(x["Elettrico"] >= 1, name="min_elettrico")

# Vincolo di emissioni
m.addConstr(gp.quicksum(emissioni[t] * x[t] for t in types) <= 145, name="emissioni_max")

# Obiettivo: minimizzare il costo totale
m.setObjective(gp.quicksum(costo[t] * x[t] for t in types), GRB.MINIMIZE)

m.optimize()

status = m.Status
if status == GRB.OPTIMAL:
    obj_val = m.ObjVal
    variables = {t: x[t].X for t in types}
    import json
    print("SOLUTION_JSON=" + json.dumps({
        "status": "OPTIMAL",
        "objective": obj_val,
        "variables": variables
    }))
else:
    import json
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    status_str = status_map.get(status, str(status))
    print("SOLUTION_JSON=" + json.dumps({
        "status": status_str,
        "objective": None,
        "variables": {}
    }))
