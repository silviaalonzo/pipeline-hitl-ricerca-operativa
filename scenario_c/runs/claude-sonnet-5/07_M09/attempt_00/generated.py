import gurobipy as gp
from gurobipy import GRB

# --- Dati ---
T = [1, 2, 3, 4, 5, 6]

demand = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
purchase_cost = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
capacity = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

L = 10          # ordine minimo se attivato
f = 40          # costo fisso per ordine
h = 2           # costo di mantenimento per unità
I0 = 10         # scorta iniziale
I_min_final = 5 # scorta minima a fine orizzonte

# --- Modello ---
m = gp.Model("M09_piano_riordino")

x = m.addVars(T, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(T, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(T, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(f * y[t] + purchase_cost[t] * x[t] + h * I[t] for t in T),
    GRB.MINIMIZE
)

# Bilancio di inventario
for t in T:
    if t == 1:
        m.addConstr(I[t] == I0 + x[t] - demand[t], name=f"bilancio_{t}")
    else:
        m.addConstr(I[t] == I[t-1] + x[t] - demand[t], name=f"bilancio_{t}")

# Scorta finale minima
m.addConstr(I[T[-1]] >= I_min_final, name="scorta_finale_min")

# Ordine minimo (batch) e capacità, legati all'attivazione
for t in T:
    m.addConstr(x[t] >= L * y[t], name=f"min_batch_{t}")
    m.addConstr(x[t] <= capacity[t] * y[t], name=f"capacita_{t}")

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status_str = status_map.get(m.status, str(m.status))

if m.status == GRB.OPTIMAL:
    variables = {}
    for t in T:
        variables[f"x_{t}"] = round(x[t].X, 2)
        variables[f"I_{t}"] = round(I[t].X, 2)
        variables[f"y_{t}"] = round(y[t].X, 2)
    objective_val = round(m.ObjVal, 2)
else:
    variables = {}
    objective_val = None

import json
print(f"SOLUTION_JSON={json.dumps({'status': status_str, 'objective': objective_val, 'variables': variables})}")
