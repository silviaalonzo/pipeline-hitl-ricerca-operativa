import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
periods = [1, 2, 3, 4, 5, 6]

demand   = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
cost     = {1: 9,  2: 8,  3: 11, 4: 7,  5: 10, 6: 9}
capacity = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

I0 = 10
minQ = 10
F = 40
h = 2
minFinal = 5

# ---------------- Modello ----------------
m = gp.Model("M09_piano_riordino")

x = m.addVars(periods, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(periods, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(periods, vtype=GRB.BINARY, name="y")

# Bilancio scorte
prev = I0
for t in periods:
    m.addConstr(prev + x[t] - demand[t] == I[t], name=f"bilancio_{t}")
    prev = I[t]

# Capacità e minimo ordine legati all'attivazione
for t in periods:
    m.addConstr(x[t] <= capacity[t] * y[t], name=f"cap_{t}")
    m.addConstr(x[t] >= minQ * y[t], name=f"minq_{t}")

# Scorta finale minima
m.addConstr(I[6] >= minFinal, name="scorta_finale")

# Funzione obiettivo
obj = gp.quicksum(cost[t] * x[t] + F * y[t] + h * I[t] for t in periods)
m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
status = m.Status
result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    variables = {}
    for t in periods:
        variables[f"x_{t}"] = round(x[t].X, 4)
        variables[f"I_{t}"] = round(I[t].X, 4)
        variables[f"y_{t}"] = round(y[t].X, 4)

    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    result["variables"] = variables

    print("=== Riepilogo soluzione ===")
    print(f"Stato solver: OPTIMAL")
    print(f"Costo totale ottimo: {m.ObjVal:.2f}")
    for t in periods:
        print(f"Periodo {t}: ordine x={x[t].X:.0f}, scorta I={I[t].X:.0f}, "
              f"ordine attivato y={y[t].X:.0f}")
else:
    result["status"] = str(status)

print("SOLUTION_JSON=" + json.dumps(result))
