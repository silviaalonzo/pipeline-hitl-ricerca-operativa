import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
centri = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
zone = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6', 'Z7', 'Z8', 'Z9', 'Z10']
zone_critiche = ['Z3', 'Z7']

# Parametri: costi
costo = {
    'A': 24, 'B': 20, 'C': 27, 'D': 22,
    'E': 25, 'F': 19, 'G': 23, 'H': 21
}

# Parametri: copertura zone per centro
copertura = {
    'A': ['Z1', 'Z2', 'Z3'],
    'B': ['Z2', 'Z3', 'Z4', 'Z5'],
    'C': ['Z1', 'Z5', 'Z6'],
    'D': ['Z3', 'Z6', 'Z7'],
    'E': ['Z4', 'Z7', 'Z8'],
    'F': ['Z5', 'Z8', 'Z9'],
    'G': ['Z6', 'Z9', 'Z10'],
    'H': ['Z7', 'Z8', 'Z10']
}

# Matrice a_{i,j}
a = {(i, j): 1 if j in copertura[i] else 0 for i in centri for j in zone}

K = 5  # numero massimo di centri apribili

# Modello
m = gp.Model("copertura_zone")

# Variabili decisionali
x = m.addVars(centri, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
m.setObjective(gp.quicksum(costo[i] * x[i] for i in centri), GRB.MINIMIZE)

# Vincoli di copertura
for j in zone:
    coeff = gp.quicksum(a[i, j] * x[i] for i in centri)
    if j in zone_critiche:
        m.addConstr(coeff >= 2, name=f"copertura_critica_{j}")
    else:
        m.addConstr(coeff >= 1, name=f"copertura_{j}")

# Vincolo sul numero massimo di centri aperti
m.addConstr(gp.quicksum(x[i] for i in centri) <= K, name="max_centri")

# Risoluzione
m.optimize()

# Output
if m.Status == GRB.OPTIMAL:
    variables = {f"x_{i}": x[i].X for i in centri}
    solution = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variables
    }
else:
    solution = {
        "status": str(m.Status),
        "objective": None,
        "variables": {}
    }

print(f"SOLUTION_JSON={json.dumps(solution)}")
