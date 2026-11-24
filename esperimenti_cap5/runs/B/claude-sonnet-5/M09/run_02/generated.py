import gurobipy as gp
from gurobipy import GRB
import json

# Dati
T = [1, 2, 3, 4, 5, 6]
demand = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
cost   = {1: 9,  2: 8,  3: 11, 4: 7,  5: 10, 6: 9}
cap    = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

I0 = 10
Imin_final = 5
L = 10      # ordine minimo
K = 40      # costo fisso
h = 2       # costo mantenimento

model = gp.Model("Lot_sizing_fixed_cost")

# Variabili
x = model.addVars(T, vtype=GRB.INTEGER, lb=0, name="x")
I = model.addVars(T, vtype=GRB.INTEGER, lb=0, name="I")
y = model.addVars(T, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(cost[t] * x[t] + K * y[t] + h * I[t] for t in T),
    GRB.MINIMIZE
)

# Vincoli di bilancio scorte
for t in T:
    prev_inv = I0 if t == 1 else I[t - 1]
    model.addConstr(prev_inv + x[t] - demand[t] == I[t], name=f"balance_{t}")

# Scorta finale minima
model.addConstr(I[6] >= Imin_final, name="final_stock")

# Capacità e minimo ordine legati all'attivazione
for t in T:
    model.addConstr(x[t] <= cap[t] * y[t], name=f"cap_{t}")
    model.addConstr(x[t] >= L * y[t], name=f"minlot_{t}")

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = model.ObjVal
    variables = {}
    for t in T:
        variables[f"x_{t}"] = x[t].X
        variables[f"I_{t}"] = I[t].X
        variables[f"y_{t}"] = y[t].X
    result["variables"] = variables
else:
    result["status"] = str(status)

print("SOLUTION_JSON=" + json.dumps(result))
