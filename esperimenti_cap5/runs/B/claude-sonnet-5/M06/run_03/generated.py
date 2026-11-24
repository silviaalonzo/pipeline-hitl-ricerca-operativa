import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
jobs = [1,2,3,4,5,6,7]
machines = ["A","B"]

p = {
    (1,"A"):7, (1,"B"):9,
    (2,"A"):6, (2,"B"):5,
    (3,"A"):8, (3,"B"):7,
    (4,"A"):5, (4,"B"):8,
    (5,"A"):9, (5,"B"):6,
    (6,"A"):4, (6,"B"):7,
    (7,"B"):5   # J7 non compatibile con A -> nessuna voce (7,"A")
}

model = gp.Model("bilanciamento_2_macchine")

# --- Variabili ---
x = {}
for j in jobs:
    for m in machines:
        if (j,m) in p:
            x[j,m] = model.addVar(vtype=GRB.BINARY, name=f"x_{j}_{m}")

Cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="Cmax")

# --- Vincolo: J7 non compatibile con A (non creiamo x[7,'A'], quindi vincolo implicito) ---

# --- Vincolo: ogni lavoro assegnato esattamente a una macchina ---
for j in jobs:
    model.addConstr(gp.quicksum(x[j,m] for m in machines if (j,m) in p) == 1,
                     name=f"assign_{j}")

# --- Vincoli di carico ---
model.addConstr(gp.quicksum(p[j,"A"]*x[j,"A"] for j in jobs if (j,"A") in p) <= Cmax,
                 name="loadA")
model.addConstr(gp.quicksum(p[j,"B"]*x[j,"B"] for j in jobs if (j,"B") in p) <= Cmax,
                 name="loadB")

# --- Obiettivo ---
model.setObjective(Cmax, GRB.MINIMIZE)

model.optimize()

# --- Estrazione risultati ---
status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = float(model.ObjVal)
    variables = {}
    for j in jobs:
        for m in machines:
            if (j,m) in p:
                variables[f"x_{j}_{m}"] = float(round(x[j,m].X))
    variables["Cmax"] = float(model.ObjVal)
    result["variables"] = variables
else:
    result["status"] = str(status)

print("SOLUTION_JSON=" + json.dumps(result))
