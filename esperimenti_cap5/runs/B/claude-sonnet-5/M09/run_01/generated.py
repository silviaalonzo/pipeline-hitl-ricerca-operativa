import gurobipy as gp
from gurobipy import GRB
import json

# Dati
T = [1, 2, 3, 4, 5, 6]
demand = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
cost   = {1: 9,  2: 8,  3: 11, 4: 7,  5: 10, 6: 9}
cap    = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

f = 40          # costo fisso ordine
h = 2           # costo mantenimento
I0 = 10         # scorta iniziale
q_min = 10      # ordine minimo se attivato
I_final_min = 5 # scorta finale minima

m = gp.Model("Lot_sizing_costi_fissi")

x = m.addVars(T, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(T, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(T, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(cost[t] * x[t] + f * y[t] + h * I[t] for t in T),
    GRB.MINIMIZE
)

# Vincoli di bilancio scorte
prev = I0
for t in T:
    m.addConstr(I[t] == prev + x[t] - demand[t], name=f"balance_{t}")
    prev = I[t]

# Scorta finale minima
m.addConstr(I[T[-1]] >= I_final_min, name="final_inventory")

# Capacità e ordine minimo legati alla decisione y
for t in T:
    m.addConstr(x[t] <= cap[t] * y[t], name=f"cap_{t}")
    m.addConstr(x[t] >= q_min * y[t], name=f"minorder_{t}")

m.optimize()

status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for t in T:
        variables[f"x_{t}"] = float(round(x[t].X))
        variables[f"I_{t}"] = float(round(I[t].X))
        variables[f"y_{t}"] = float(round(y[t].X))
    result["variables"] = variables
else:
    result["status"] = m.Status
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
