import json
import gurobipy as gp
from gurobipy import GRB

# ---------------- Dati ----------------
products = ['A', 'B', 'C']
periods = [1, 2, 3, 4]

demand = {
    ('A',1):8, ('A',2):12, ('A',3):10, ('A',4):14,
    ('B',1):10,('B',2):8,  ('B',3):14, ('B',4):12,
    ('C',1):6, ('C',2):9,  ('C',3):7,  ('C',4):11,
}

prod_cost = {
    ('A',1):9,  ('A',2):11, ('A',3):10, ('A',4):12,
    ('B',1):8,  ('B',2):9,  ('B',3):11, ('B',4):10,
    ('C',1):13, ('C',2):12, ('C',3):14, ('C',4):11,
}

setup_cost = {'A':45, 'B':40, 'C':50}
holding_cost = {'A':2, 'B':3, 'C':2}
hours_per_unit = {'A':2, 'B':3, 'C':4}
min_lot = {'A':4, 'B':4, 'C':3}
initial_inv = {'A':0, 'B':0, 'C':6}

capacity = {1:90, 2:95, 3:90, 4:100}

max_setups_per_period = 2
max_total_inventory = 20

# Big-M: somma totale della domanda per prodotto (limite sicuro sulla produzione in un periodo)
bigM = {i: sum(demand[(i,t)] for t in periods) for i in products}

# ---------------- Modello ----------------
m = gp.Model("H02_produzione_multiperiodo")

x = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="x")
s = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="s")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")

# Bilancio di scorte
for i in products:
    prev = initial_inv[i]
    for t in periods:
        m.addConstr(prev + x[i,t] - demand[(i,t)] == s[i,t], name=f"bal_{i}_{t}")
        prev = s[i,t]

# Scorte finali nulle
last_t = periods[-1]
for i in products:
    m.addConstr(s[i,last_t] == 0, name=f"final_inv_{i}")

# Legame produzione-setup (big-M) e lotto minimo
for i in products:
    for t in periods:
        m.addConstr(x[i,t] <= bigM[i] * y[i,t], name=f"link_{i}_{t}")
        m.addConstr(x[i,t] >= min_lot[i] * y[i,t], name=f"minlot_{i}_{t}")

# Massimo due articoli attivi per periodo
for t in periods:
    m.addConstr(gp.quicksum(y[i,t] for i in products) <= max_setups_per_period,
                name=f"max_setups_{t}")

# Scorta totale massima
for t in periods:
    m.addConstr(gp.quicksum(s[i,t] for i in products) <= max_total_inventory,
                name=f"max_inv_{t}")

# Capacità oraria
for t in periods:
    m.addConstr(gp.quicksum(hours_per_unit[i] * x[i,t] for i in products) <= capacity[t],
                name=f"cap_{t}")

# ---------------- Obiettivo ----------------
obj = gp.quicksum(prod_cost[(i,t)] * x[i,t] for i in products for t in periods) \
    + gp.quicksum(setup_cost[i] * y[i,t] for i in products for t in periods) \
    + gp.quicksum(holding_cost[i] * s[i,t] for i in products for t in periods)

m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for i in products:
        for t in periods:
            variables[f"x_{i}_{t}"] = round(x[i,t].X, 4)
            variables[f"s_{i}_{t}"] = round(s[i,t].X, 4)
            variables[f"y_{i}_{t}"] = round(y[i,t].X, 4)
    result["variables"] = variables
else:
    result["status"] = "NOT_OPTIMAL_STATUS_%d" % status
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
