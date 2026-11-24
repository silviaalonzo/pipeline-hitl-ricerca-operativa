import gurobipy as gp
from gurobipy import GRB

# Dati
projects = [1, 2, 3, 4, 5, 6, 7, 8]
value = {1:30, 2:24, 3:35, 4:28, 5:33, 6:26, 7:38, 8:21}
budget = {1:20, 2:18, 3:27, 4:24, 5:22, 6:19, 7:30, 8:15}
personnel = {1:4, 2:3, 3:5, 4:4, 5:4, 6:3, 7:5, 8:2}

B_max = 100
L_max = 18
digital = [1, 3, 7]

# Modello
m = gp.Model("Selezione_Portafoglio_Progetti")

# Variabili decisionali
x = m.addVars(projects, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
m.setObjective(gp.quicksum(value[i] * x[i] for i in projects), GRB.MAXIMIZE)

# Vincolo di budget
m.addConstr(gp.quicksum(budget[i] * x[i] for i in projects) <= B_max, name="Budget")

# Vincolo di personale
m.addConstr(gp.quicksum(personnel[i] * x[i] for i in projects) <= L_max, name="Personale")

# P5 richiede P2
m.addConstr(x[5] <= x[2], name="P5_richiede_P2")

# P7 richiede P3
m.addConstr(x[7] <= x[3], name="P7_richiede_P3")

# P4 e P6 incompatibili
m.addConstr(x[4] + x[6] <= 1, name="P4_P6_incompatibili")

# Almeno un progetto digitale tra P1, P3, P7
m.addConstr(gp.quicksum(x[i] for i in digital) >= 1, name="Almeno_un_digitale")

# Almeno tre progetti totali
m.addConstr(gp.quicksum(x[i] for i in projects) >= 3, name="Almeno_tre_progetti")

# Risoluzione
m.optimize()

# Output risultati
status = m.Status
if status == GRB.OPTIMAL:
    obj_val = m.ObjVal
    variables = {f"x_{i}": x[i].X for i in projects}
    status_str = "OPTIMAL"
else:
    obj_val = None
    variables = {}
    status_str = str(status)

import json
print("SOLUTION_JSON=" + json.dumps({
    "status": status_str,
    "objective": obj_val,
    "variables": variables
}))
