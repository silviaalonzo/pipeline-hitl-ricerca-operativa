import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
centri = ["A", "B", "C", "D", "E", "F", "G", "H"]
costi = {"A": 24, "B": 20, "C": 27, "D": 22, "E": 25, "F": 19, "G": 23, "H": 21}

zone = [f"Z{k}" for k in range(1, 11)]

copertura = {
    "A": ["Z1", "Z2", "Z3"],
    "B": ["Z2", "Z3", "Z4", "Z5"],
    "C": ["Z1", "Z5", "Z6"],
    "D": ["Z3", "Z6", "Z7"],
    "E": ["Z4", "Z7", "Z8"],
    "F": ["Z5", "Z8", "Z9"],
    "G": ["Z6", "Z9", "Z10"],
    "H": ["Z7", "Z8", "Z10"],
}

# matrice a_ij : per ogni zona, elenco dei centri che la coprono
zona_coperta_da = {i: [] for i in zone}
for j, lista_zone in copertura.items():
    for i in lista_zone:
        zona_coperta_da[i].append(j)

# requisito di copertura per zona
r = {i: 1 for i in zone}
r["Z3"] = 2
r["Z7"] = 2

K = 5  # numero massimo di centri apribili

# --- Modello ---
m = gp.Model("copertura_zone")

x = m.addVars(centri, vtype=GRB.BINARY, name="x")

# Obiettivo: minimizzare il costo totale
m.setObjective(gp.quicksum(costi[j] * x[j] for j in centri), GRB.MINIMIZE)

# Vincoli di copertura
for i in zone:
    m.addConstr(gp.quicksum(x[j] for j in zona_coperta_da[i]) >= r[i], name=f"cop_{i}")

# Vincolo sul numero massimo di centri
m.addConstr(gp.quicksum(x[j] for j in centri) <= K, name="max_centri")

m.optimize()

# --- Output ---
status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = m.ObjVal
    result["variables"] = {f"x_{j}": x[j].X for j in centri}
else:
    result["status"] = str(status)

print("SOLUTION_JSON=" + json.dumps(result))
