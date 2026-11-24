import json
from gurobipy import Model, GRB, quicksum

# ---------------- DATI ----------------
products = ['A', 'B', 'C']
periods = [1, 2, 3, 4]

demand = {
    ('A',1):8, ('A',2):12, ('A',3):10, ('A',4):14,
    ('B',1):10, ('B',2):8, ('B',3):14, ('B',4):12,
    ('C',1):6, ('C',2):9, ('C',3):7, ('C',4):11,
}

prod_cost = {
    ('A',1):9, ('A',2):11, ('A',3):10, ('A',4):12,
    ('B',1):8, ('B',2):9, ('B',3):11, ('B',4):10,
    ('C',1):13, ('C',2):12, ('C',3):14, ('C',4):11,
}

setup_cost = {'A':45, 'B':40, 'C':50}
holding_cost = {'A':2, 'B':3, 'C':2}
hours_per_unit = {'A':2, 'B':3, 'C':4}
min_lot = {'A':4, 'B':4, 'C':3}

init_inv = {'A':0, 'B':0, 'C':6}

capacity = {1:90, 2:95, 3:90, 4:100}

MAX_SETUPS = 2
MAX_INV_TOTAL = 20

# Big-M: produzione totale sull'orizzonte = domanda totale - scorta iniziale
total_demand = {i: sum(demand[i,t] for t in periods) for i in products}
bigM = {i: total_demand[i] - init_inv[i] for i in products}

# ---------------- MODELLO ----------------
m = Model("H02_multiperiodo")

x = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
obj = quicksum(prod_cost[i,t]*x[i,t] for i in products for t in periods) \
    + quicksum(setup_cost[i]*y[i,t] for i in products for t in periods) \
    + quicksum(holding_cost[i]*I[i,t] for i in products for t in periods)
m.setObjective(obj, GRB.MINIMIZE)

# Bilancio di magazzino
for i in products:
    prev = init_inv[i]
    for t in periods:
        m.addConstr(prev + x[i,t] - demand[i,t] == I[i,t], name=f"bal_{i}_{t}")
        prev = I[i,t]

# Collegamento setup - produzione (big-M) e lotto minimo
for i in products:
    for t in periods:
        m.addConstr(x[i,t] <= bigM[i]*y[i,t], name=f"bigM_{i}_{t}")
        m.addConstr(x[i,t] >= min_lot[i]*y[i,t], name=f"minlot_{i}_{t}")

# Capacità produttiva
for t in periods:
    m.addConstr(quicksum(hours_per_unit[i]*x[i,t] for i in products) <= capacity[t],
                name=f"cap_{t}")

# Massimo numero di setup per periodo
for t in periods:
    m.addConstr(quicksum(y[i,t] for i in products) <= MAX_SETUPS, name=f"maxsetup_{t}")

# Scorta totale massima per periodo
for t in periods:
    m.addConstr(quicksum(I[i,t] for i in products) <= MAX_INV_TOTAL, name=f"maxinv_{t}")

# Scorta finale nulla
for i in products:
    m.addConstr(I[i,periods[-1]] == 0, name=f"finalinv_{i}")

m.optimize()

# ---------------- OUTPUT ----------------
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status = status_map.get(m.status, str(m.status))

variables = {}
objective = None

if m.status == GRB.OPTIMAL:
    objective = m.objVal
    for i in products:
        for t in periods:
            variables[f"x_{i}_{t}"] = round(x[i,t].X)
            variables[f"I_{i}_{t}"] = round(I[i,t].X)
            variables[f"y_{i}_{t}"] = round(y[i,t].X)

    print("\n--- Riepilogo decisioni non nulle ---")
    for i in products:
        for t in periods:
            if x[i,t].X > 1e-6:
                print(f"x[{i},{t}] = {x[i,t].X:.0f}")
    for i in products:
        for t in periods:
            if I[i,t].X > 1e-6:
                print(f"I[{i},{t}] = {I[i,t].X:.0f}")
    for i in products:
        for t in periods:
            if y[i,t].X > 0.5:
                print(f"y[{i},{t}] = 1")
    print(f"Costo totale ottimo = {objective:.2f}")

result = {
    "status": status,
    "objective": objective,
    "variables": variables
}
print("SOLUTION_JSON=" + json.dumps(result))
