import gurobipy as gp
from gurobipy import GRB
import json

# Dati
progetti = [1,2,3,4,5,6,7,8]
valore = {1:30, 2:24, 3:35, 4:28, 5:33, 6:26, 7:38, 8:21}
budget = {1:20, 2:18, 3:27, 4:24, 5:22, 6:19, 7:30, 8:15}
personale = {1:4, 2:3, 3:5, 4:4, 5:4, 6:3, 7:5, 8:2}

B_max = 100
P_max = 18
digitali = [1,3,7]

# Modello
m = gp.Model("Selezione_Portafoglio_Progetti")

# Variabili
x = m.addVars(progetti, vtype=GRB.BINARY, name="x")

# Obiettivo
m.setObjective(gp.quicksum(valore[i]*x[i] for i in progetti), GRB.MAXIMIZE)

# Vincoli
m.addConstr(gp.quicksum(budget[i]*x[i] for i in progetti) <= B_max, name="Budget")
m.addConstr(gp.quicksum(personale[i]*x[i] for i in progetti) <= P_max, name="Personale")

m.addConstr(x[5] <= x[2], name="P5_richiede_P2")
m.addConstr(x[7] <= x[3], name="P7_richiede_P3")
m.addConstr(x[4] + x[6] <= 1, name="P4_P6_incompatibili")
m.addConstr(x[1] + x[3] + x[7] >= 1, name="Almeno_un_digitale")
m.addConstr(gp.quicksum(x[i] for i in progetti) >= 3, name="Almeno_tre_progetti")

# Risoluzione
m.optimize()

# Output risultati
status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 2)
    for i in progetti:
        result["variables"][f"x_{i}"] = round(x[i].X, 2)
else:
    result["status"] = str(status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
