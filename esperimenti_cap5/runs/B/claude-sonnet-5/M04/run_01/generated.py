import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {"Van": 18, "Autocarro": 30, "Refrigerato": 20, "Elettrico": 16, "Bilico": 42}
portata = {"Van": 8, "Autocarro": 18, "Refrigerato": 10, "Elettrico": 7, "Bilico": 28}
costo = {"Van": 120, "Autocarro": 180, "Refrigerato": 210, "Elettrico": 150, "Bilico": 260}
emissioni = {"Van": 12, "Autocarro": 22, "Refrigerato": 15, "Elettrico": 4, "Bilico": 32}
disponibilita = {"Van": 8, "Autocarro": 6, "Refrigerato": 4, "Elettrico": 5, "Bilico": 3}

VOL_MIN = 180
PORT_MIN = 95
EM_MAX = 145

# --- Modello ---
m = gp.Model("Composizione_Flotta")

x = m.addVars(tipi, vtype=GRB.INTEGER, lb=0, name="x")

# Vincoli di disponibilità
for i in tipi:
    x[i].UB = disponibilita[i]

# Volume minimo
m.addConstr(gp.quicksum(volume[i] * x[i] for i in tipi) >= VOL_MIN, name="volume_min")

# Portata minima
m.addConstr(gp.quicksum(portata[i] * x[i] for i in tipi) >= PORT_MIN, name="portata_min")

# Emissioni massime
m.addConstr(gp.quicksum(emissioni[i] * x[i] for i in tipi) <= EM_MAX, name="emissioni_max")

# Almeno un refrigerato e un elettrico
m.addConstr(x["Refrigerato"] >= 1, name="min_refrigerato")
m.addConstr(x["Elettrico"] >= 1, name="min_elettrico")

# Funzione obiettivo
m.setObjective(gp.quicksum(costo[i] * x[i] for i in tipi), GRB.MINIMIZE)

# --- Risoluzione ---
m.optimize()

# --- Output ---
if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = m.ObjVal
    variables = {f"x_{i}": x[i].X for i in tipi}
else:
    status = str(m.Status)
    objective = None
    variables = {}

result = {"status": status, "objective": objective, "variables": variables}
print("SOLUTION_JSON=" + json.dumps(result))
