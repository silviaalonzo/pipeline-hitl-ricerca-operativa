import gurobipy as gp
from gurobipy import GRB

# ------------------- Dati -------------------
R = ["R1", "R2", "R3", "R4"]
T = ["S", "M", "L"]  # Piccolo, Medio, Grande

demand = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}

cap   = {"S": 8,  "M": 14, "L": 20}
avail = {"S": 10, "M": 9,  "L": 6}
emis  = {"S": 5,  "M": 8,  "L": 11}

cost = {
    ("R1", "S"): 45, ("R1", "M"): 62, ("R1", "L"): 82,
    ("R2", "S"): 52, ("R2", "M"): 68, ("R2", "L"): 88,
    ("R3", "S"): 40, ("R3", "M"): 58, ("R3", "L"): 79,
    ("R4", "S"): 60, ("R4", "M"): 77, ("R4", "L"): 96,
}

MAXTYPES = 2
EMIS_MAX = 145
BigM = avail  # limite superiore naturale per x[r,t]

# ------------------- Modello -------------------
m = gp.Model("H04_allocazione_flotta")

x = m.addVars(R, T, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(R, T, vtype=GRB.BINARY, name="y")

# Obiettivo: minimizzare il costo totale
m.setObjective(
    gp.quicksum(cost[r, t] * x[r, t] for r in R for t in T),
    GRB.MINIMIZE
)

# 1. Copertura della domanda
for r in R:
    m.addConstr(
        gp.quicksum(cap[t] * x[r, t] for t in T) >= demand[r],
        name=f"demand_{r}"
    )

# 2. Disponibilità totale per tipo
for t in T:
    m.addConstr(
        gp.quicksum(x[r, t] for r in R) <= avail[t],
        name=f"avail_{t}"
    )

# 3. Al massimo due tipi per rotta
for r in R:
    m.addConstr(
        gp.quicksum(y[r, t] for t in T) <= MAXTYPES,
        name=f"maxtypes_{r}"
    )

# 4. Collegamento x-y (big-M)
for r in R:
    for t in T:
        m.addConstr(
            x[r, t] <= BigM[t] * y[r, t],
            name=f"link_{r}_{t}"
        )

# 5. R4 almeno un veicolo grande
m.addConstr(x["R4", "L"] >= 1, name="R4_large_min")

# 6. Limite emissioni totali
m.addConstr(
    gp.quicksum(emis[t] * x[r, t] for r in R for t in T) <= EMIS_MAX,
    name="emissions_limit"
)

# ------------------- Risoluzione -------------------
m.optimize()

status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for r in R:
        for t in T:
            variables[f"x_{r}_{t}"] = round(x[r, t].X, 4)
    for r in R:
        for t in T:
            variables[f"y_{r}_{t}"] = round(y[r, t].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(status)

import json
print(f"SOLUTION_JSON={json.dumps(result)}")
