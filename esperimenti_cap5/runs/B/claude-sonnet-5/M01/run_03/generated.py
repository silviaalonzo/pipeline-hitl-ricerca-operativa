import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
siti = ['A', 'B', 'C', 'D']
zone = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6']

# Parametri
costo_fisso = {'A': 38, 'B': 42, 'C': 35, 'D': 46}
capacita = {'A': 2, 'B': 3, 'C': 2, 'D': 3}
P = 2  # numero esatto di centri da aprire

costo_assegnazione = {
    ('Z1', 'A'): 8,  ('Z1', 'B'): 14, ('Z1', 'C'): 11, ('Z1', 'D'): 17,
    ('Z2', 'A'): 10, ('Z2', 'B'): 9,  ('Z2', 'C'): 13, ('Z2', 'D'): 15,
    ('Z3', 'A'): 12, ('Z3', 'B'): 8,  ('Z3', 'C'): 14, ('Z3', 'D'): 10,
    ('Z4', 'A'): 15, ('Z4', 'B'): 11, ('Z4', 'C'): 9,  ('Z4', 'D'): 7,
    ('Z5', 'A'): 9,  ('Z5', 'B'): 13, ('Z5', 'C'): 8,  ('Z5', 'D'): 14,
    ('Z6', 'A'): 14, ('Z6', 'B'): 10, ('Z6', 'C'): 7,  ('Z6', 'D'): 9,
}

# Modello
m = gp.Model("Localizzazione_centri_assistenza")

# Variabili decisionali
y = m.addVars(siti, vtype=GRB.BINARY, name="y")
x = m.addVars(zone, siti, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(costo_fisso[i] * y[i] for i in siti) +
    gp.quicksum(costo_assegnazione[j, i] * x[j, i] for j in zone for i in siti),
    GRB.MINIMIZE
)

# Vincolo 1: ogni zona assegnata a esattamente un sito
for j in zone:
    m.addConstr(gp.quicksum(x[j, i] for i in siti) == 1, name=f"assegna_{j}")

# Vincolo 2: assegnazione solo a siti aperti
for j in zone:
    for i in siti:
        m.addConstr(x[j, i] <= y[i], name=f"link_{j}_{i}")

# Vincolo 3: capacità dei siti
for i in siti:
    m.addConstr(gp.quicksum(x[j, i] for j in zone) <= capacita[i] * y[i], name=f"cap_{i}")

# Vincolo 4: numero esatto di centri aperti
m.addConstr(gp.quicksum(y[i] for i in siti) == P, name="num_centri")

# Risoluzione
m.optimize()

# Costruzione output
result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for i in siti:
        variables[f"y_{i}"] = round(y[i].X, 4)
    for j in zone:
        for i in siti:
            variables[f"x_{j}_{i}"] = round(x[j, i].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(m.Status)

print("SOLUTION_JSON=" + json.dumps(result))
