import gurobipy as gp
from gurobipy import GRB
import json
import math

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
init_inv = {'A':0, 'B':0, 'C':6}
capacity = {1:90, 2:95, 3:90, 4:100}

MAX_SETUPS = 2
MAX_INV = 20

# Big-M per legame x <= M*y (limite dato dalla capacità del periodo)
bigM = {(i,t): math.floor(capacity[t] / hours_per_unit[i]) for i in products for t in periods}

# ---------------- Modello ----------------
m = gp.Model("H02_multiperiodo")

x = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="x")
Inv = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="Inv")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")

# Obiettivo
m.setObjective(
    gp.quicksum(prod_cost[i,t]*x[i,t] + setup_cost[i]*y[i,t] + holding_cost[i]*Inv[i,t]
                for i in products for t in periods),
    GRB.MINIMIZE
)

# Bilancio di scorta
for i in products:
    prev = init_inv[i]
    for t in periods:
        m.addConstr(prev + x[i,t] - demand[i,t] == Inv[i,t], name=f"bal_{i}_{t}")
        prev = Inv[i,t]

# Legame produzione-setup (big M)
for i in products:
    for t in periods:
        m.addConstr(x[i,t] <= bigM[i,t]*y[i,t], name=f"bigM_{i}_{t}")

# Lotto minimo
for i in products:
    for t in periods:
        m.addConstr(x[i,t] >= min_lot[i]*y[i,t], name=f"minlot_{i}_{t}")

# Massimo 2 setup per periodo
for t in periods:
    m.addConstr(gp.quicksum(y[i,t] for i in products) <= MAX_SETUPS, name=f"maxsetup_{t}")

# Capacità produttiva
for t in periods:
    m.addConstr(gp.quicksum(hours_per_unit[i]*x[i,t] for i in products) <= capacity[t],
                name=f"cap_{t}")

# Scorta totale massima
for t in periods:
    m.addConstr(gp.quicksum(Inv[i,t] for i in products) <= MAX_INV, name=f"maxinv_{t}")

# Scorte finali nulle
for i in products:
    m.addConstr(Inv[i,4] == 0, name=f"finalzero_{i}")

m.optimize()

# ---------------- Output ----------------
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.objVal, 4)
    variables = {}
    for i in products:
        for t in periods:
            variables[f"x_{i}_{t}"] = round(x[i,t].X, 4)
            variables[f"Inv_{i}_{t}"] = round(Inv[i,t].X, 4)
            variables[f"y_{i}_{t}"] = round(y[i,t].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(m.status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
