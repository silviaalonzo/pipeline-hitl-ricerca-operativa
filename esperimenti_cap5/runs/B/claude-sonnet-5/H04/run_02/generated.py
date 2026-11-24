import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
R = ["R1", "R2", "R3", "R4"]
T = ["Piccolo", "Medio", "Grande"]

demand = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}

capacity = {"Piccolo": 8, "Medio": 14, "Grande": 20}
availability = {"Piccolo": 10, "Medio": 9, "Grande": 6}
emissions = {"Piccolo": 5, "Medio": 8, "Grande": 11}

cost = {
    ("R1", "Piccolo"): 45, ("R1", "Medio"): 62, ("R1", "Grande"): 82,
    ("R2", "Piccolo"): 52, ("R2", "Medio"): 68, ("R2", "Grande"): 88,
    ("R3", "Piccolo"): 40, ("R3", "Medio"): 58, ("R3", "Grande"): 79,
    ("R4", "Piccolo"): 60, ("R4", "Medio"): 77, ("R4", "Grande"): 96,
}

E_max = 145
K = 2

# --- Modello ---
m = gp.Model("H04_allocazione_flotta")

x = m.addVars(R, T, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(R, T, vtype=GRB.BINARY, name="y")

# Obiettivo
m.setObjective(gp.quicksum(cost[r, t] * x[r, t] for r in R for t in T), GRB.MINIMIZE)

# 1. Copertura domanda
for r in R:
    m.addConstr(gp.quicksum(capacity[t] * x[r, t] for t in T) >= demand[r], name=f"domanda_{r}")

# 2. Disponibilità per tipo
for t in T:
    m.addConstr(gp.quicksum(x[r, t] for r in R) <= availability[t], name=f"disp_{t}")

# 3. Al massimo K tipi per rotta
for r in R:
    m.addConstr(gp.quicksum(y[r, t] for t in T) <= K, name=f"maxtipi_{r}")

# 4. Linking x-y
for r in R:
    for t in T:
        m.addConstr(x[r, t] <= availability[t] * y[r, t], name=f"link_{r}_{t}")

# 5. Almeno un grande su R4
m.addConstr(x["R4", "Grande"] >= 1, name="grande_R4")

# 6. Limite emissioni
m.addConstr(gp.quicksum(emissions[t] * x[r, t] for r in R for t in T) <= E_max, name="emissioni")

m.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = m.objVal
    variables = {}
    for r in R:
        for t in T:
            variables[f"x_{r}_{t}"] = x[r, t].X
            variables[f"y_{r}_{t}"] = y[r, t].X
    result["variables"] = variables
else:
    result["status"] = str(m.status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
