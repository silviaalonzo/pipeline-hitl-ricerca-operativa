import gurobipy as gp
from gurobipy import GRB
import json
import math

# Insiemi
R = ["R1", "R2", "R3", "R4"]
T = ["P", "M", "G"]

# Parametri
demand = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}
cap = {"P": 8, "M": 14, "G": 20}
disp = {"P": 10, "M": 9, "G": 6}
em = {"P": 5, "M": 8, "G": 11}

cost = {
    ("R1", "P"): 45, ("R1", "M"): 62, ("R1", "G"): 82,
    ("R2", "P"): 52, ("R2", "M"): 68, ("R2", "G"): 88,
    ("R3", "P"): 40, ("R3", "M"): 58, ("R3", "G"): 79,
    ("R4", "P"): 60, ("R4", "M"): 77, ("R4", "G"): 96,
}

E_max = 145
K = 2

# Big-M per ogni (r,t): numero massimo di viaggi utili
M_rt = {(r, t): math.ceil(demand[r] / cap[t]) for r in R for t in T}

# Modello
model = gp.Model("Allocazione_Flotta")

x = model.addVars(R, T, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(R, T, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[r, t] * x[r, t] for r in R for t in T), GRB.MINIMIZE)

# Vincolo 1: copertura domanda
for r in R:
    model.addConstr(gp.quicksum(cap[t] * x[r, t] for t in T) >= demand[r], name=f"dom_{r}")

# Vincolo 2: disponibilità flotta
for t in T:
    model.addConstr(gp.quicksum(x[r, t] for r in R) <= disp[t], name=f"disp_{t}")

# Vincolo 3: emissioni totali
model.addConstr(gp.quicksum(em[t] * x[r, t] for r in R for t in T) <= E_max, name="emissioni")

# Vincolo 4: linking x-y e massimo 2 tipi per rotta
for r in R:
    for t in T:
        model.addConstr(x[r, t] <= M_rt[r, t] * y[r, t], name=f"link_{r}_{t}")
    model.addConstr(gp.quicksum(y[r, t] for t in T) <= K, name=f"maxtipi_{r}")

# Vincolo 5: almeno un veicolo grande su R4
model.addConstr(x["R4", "G"] >= 1, name="grande_R4")

# Risoluzione
model.optimize()

# Estrazione risultati
result = {"status": None, "objective": None, "variables": {}}

if model.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.objVal, 4)
    variables = {}
    for r in R:
        for t in T:
            variables[f"x_{r}_{t}"] = round(x[r, t].X, 4)
    for r in R:
        for t in T:
            variables[f"y_{r}_{t}"] = round(y[r, t].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(model.status)
    result["objective"] = None
    result["variables"] = {}

print(f"SOLUTION_JSON={json.dumps(result)}")
