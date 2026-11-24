import gurobipy as gp
from gurobipy import GRB
import json

# Dati dei progetti
progetti = [1, 2, 3, 4, 5, 6, 7, 8]

valore = {1: 30, 2: 24, 3: 35, 4: 28, 5: 33, 6: 26, 7: 38, 8: 21}
budget = {1: 20, 2: 18, 3: 27, 4: 24, 5: 22, 6: 19, 7: 30, 8: 15}
personale = {1: 4, 2: 3, 3: 5, 4: 4, 5: 4, 6: 3, 7: 5, 8: 2}

B_TOT = 100
P_TOT = 18
digitali = [1, 3, 7]

# Creazione modello
m = gp.Model("Selezione_Portafoglio_Progetti")

# Variabili decisionali binarie
x = m.addVars(progetti, vtype=GRB.BINARY, name="x")

# Funzione obiettivo: massimizzare il valore totale
m.setObjective(gp.quicksum(valore[i] * x[i] for i in progetti), GRB.MAXIMIZE)

# Vincolo di budget
m.addConstr(gp.quicksum(budget[i] * x[i] for i in progetti) <= B_TOT, name="Budget")

# Vincolo di personale
m.addConstr(gp.quicksum(personale[i] * x[i] for i in progetti) <= P_TOT, name="Personale")

# P5 richiede P2
m.addConstr(x[5] <= x[2], name="P5_richiede_P2")

# P7 richiede P3
m.addConstr(x[7] <= x[3], name="P7_richiede_P3")

# P4 e P6 incompatibili
m.addConstr(x[4] + x[6] <= 1, name="P4_P6_incompatibili")

# Almeno un progetto digitale tra P1, P3, P7
m.addConstr(gp.quicksum(x[i] for i in digitali) >= 1, name="Almeno_un_digitale")

# Almeno tre progetti totali
m.addConstr(gp.quicksum(x[i] for i in progetti) >= 3, name="Almeno_tre_progetti")

# Risoluzione
m.optimize()

# Preparazione output
if m.status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    objective_val = m.objVal
    variables_dict = {f"x_{i}": x[i].X for i in progetti}
else:
    status_str = str(m.status)
    objective_val = None
    variables_dict = {}

result = {
    "status": status_str,
    "objective": objective_val,
    "variables": variables_dict
}

print(f"SOLUTION_JSON={json.dumps(result)}")
