import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

# Parametri
volume = {"Van": 18, "Autocarro": 30, "Refrigerato": 20, "Elettrico": 16, "Bilico": 42}
portata = {"Van": 8, "Autocarro": 18, "Refrigerato": 10, "Elettrico": 7, "Bilico": 28}
costo = {"Van": 120, "Autocarro": 180, "Refrigerato": 210, "Elettrico": 150, "Bilico": 260}
emissioni = {"Van": 12, "Autocarro": 22, "Refrigerato": 15, "Elettrico": 4, "Bilico": 32}
disponibilita = {"Van": 8, "Autocarro": 6, "Refrigerato": 4, "Elettrico": 5, "Bilico": 3}

VOL_MIN = 180
PORT_MIN = 95
EMIS_MAX = 145

# Modello
m = gp.Model("Composizione_Flotta")

# Variabili decisionali: numero di veicoli per tipo
x = m.addVars(tipi, vtype=GRB.INTEGER, lb=0, ub=disponibilita, name="x")

# Funzione obiettivo: minimizzare il costo totale
m.setObjective(gp.quicksum(costo[i] * x[i] for i in tipi), GRB.MINIMIZE)

# Vincolo di volume
m.addConstr(gp.quicksum(volume[i] * x[i] for i in tipi) >= VOL_MIN, name="Volume_min")

# Vincolo di portata
m.addConstr(gp.quicksum(portata[i] * x[i] for i in tipi) >= PORT_MIN, name="Portata_min")

# Vincolo emissioni
m.addConstr(gp.quicksum(emissioni[i] * x[i] for i in tipi) <= EMIS_MAX, name="Emissioni_max")

# Almeno un refrigerato
m.addConstr(x["Refrigerato"] >= 1, name="Min_Refrigerato")

# Almeno un elettrico
m.addConstr(x["Elettrico"] >= 1, name="Min_Elettrico")

# Risoluzione
m.optimize()

# Estrazione risultati e stampa nel formato richiesto
if m.status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    obj_val = m.objVal
    variables = {f"x_{i}": x[i].X for i in tipi}
else:
    status_str = str(m.status)
    obj_val = None
    variables = {}

solution = {
    "status": status_str,
    "objective": obj_val,
    "variables": variables
}

print("SOLUTION_JSON=" + json.dumps(solution))
