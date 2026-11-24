import gurobipy as gp
from gurobipy import GRB
import json

# ----- Dati -----
routes = ["R1", "R2", "R3", "R4"]
types  = ["Piccolo", "Medio", "Grande"]

demand = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}

cap  = {"Piccolo": 8,  "Medio": 14, "Grande": 20}
disp = {"Piccolo": 10, "Medio": 9,  "Grande": 6}
em   = {"Piccolo": 5,  "Medio": 8,  "Grande": 11}

cost = {
    ("R1", "Piccolo"): 45, ("R1", "Medio"): 62, ("R1", "Grande"): 82,
    ("R2", "Piccolo"): 52, ("R2", "Medio"): 68, ("R2", "Grande"): 88,
    ("R3", "Piccolo"): 40, ("R3", "Medio"): 58, ("R3", "Grande"): 79,
    ("R4", "Piccolo"): 60, ("R4", "Medio"): 77, ("R4", "Grande"): 96,
}

EM_MAX = 145
K_MAX_TYPES = 2

# ----- Modello -----
m = gp.Model("H04_Flotta")
m.Params.OutputFlag = 0

x = m.addVars(routes, types, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(routes, types, vtype=GRB.BINARY, name="y")

# Obiettivo
m.setObjective(gp.quicksum(cost[r, t] * x[r, t] for r in routes for t in types),
               GRB.MINIMIZE)

# Copertura domanda
for r in routes:
    m.addConstr(gp.quicksum(cap[t] * x[r, t] for t in types) >= demand[r],
                name=f"Domanda_{r}")

# Disponibilità flotta
for t in types:
    m.addConstr(gp.quicksum(x[r, t] for r in routes) <= disp[t],
                name=f"Disponibilita_{t}")

# Linking x-y e massimo 2 tipi per rotta
for r in routes:
    for t in types:
        m.addConstr(x[r, t] <= disp[t] * y[r, t], name=f"Link_{r}_{t}")
    m.addConstr(gp.quicksum(y[r, t] for t in types) <= K_MAX_TYPES,
                name=f"MaxTipi_{r}")

# Almeno un grande su R4
m.addConstr(x["R4", "Grande"] >= 1, name="MinGrandeR4")

# Limite emissioni
m.addConstr(gp.quicksum(em[t] * x[r, t] for r in routes for t in types) <= EM_MAX,
            name="LimiteEmissioni")

# ----- Risoluzione -----
m.optimize()

result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for r in routes:
        for t in types:
            variables[f"x_{r}_{t}"] = round(x[r, t].X, 4)
            variables[f"y_{r}_{t}"] = round(y[r, t].X, 4)
    result["variables"] = variables

    # ----- Stampa leggibile -----
    print(f"Stato solver: {m.Status} (OPTIMAL)")
    print(f"Costo totale ottimo: {m.ObjVal:.2f}")
    print("\nDecisioni non nulle:")
    for r in routes:
        for t in types:
            if x[r, t].X > 1e-6:
                print(f"  x[{r},{t}] = {int(round(x[r, t].X))}  "
                      f"(costo unit.={cost[r,t]}, cap={cap[t]}, em={em[t]})")
    tot_em = sum(em[t] * x[r, t].X for r in routes for t in types)
    print(f"\nEmissioni totali usate: {tot_em:.2f} / {EM_MAX}")
else:
    print(f"Stato solver: {m.Status} (non OPTIMAL)")

print("SOLUTION_JSON=" + json.dumps(result))
