import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
arcs = [('S','A'), ('S','B'), ('A','B'), ('A','C'), ('B','C'),
        ('B','D'), ('C','D'), ('C','T'), ('D','T')]

fixed_cost = {
    ('S','A'): 55, ('S','B'): 50, ('A','B'): 18, ('A','C'): 38,
    ('B','C'): 22, ('B','D'): 35, ('C','D'): 20, ('C','T'): 48, ('D','T'): 44
}

capacity = {
    ('S','A'): 35, ('S','B'): 35, ('A','B'): 15, ('A','C'): 30,
    ('B','C'): 25, ('B','D'): 25, ('C','D'): 20, ('C','T'): 35, ('D','T'): 35
}

unit_cost = {
    ('S','A'): {'K1':2, 'K2':3},
    ('S','B'): {'K1':3, 'K2':2},
    ('A','B'): {'K1':1, 'K2':2},
    ('A','C'): {'K1':2, 'K2':3},
    ('B','C'): {'K1':2, 'K2':1},
    ('B','D'): {'K1':3, 'K2':2},
    ('C','D'): {'K1':1, 'K2':2},
    ('C','T'): {'K1':3, 'K2':2},
    ('D','T'): {'K1':2, 'K2':3},
}

products = ['K1', 'K2']
demand = {'K1': 28, 'K2': 22}
nodes = ['S','A','B','C','D','T']
max_arcs = 7

# --- Modello ---
m = gp.Model("H10_multiproduct_network")

y = m.addVars(arcs, vtype=GRB.BINARY, name="y")
x = m.addVars(arcs, products, vtype=GRB.INTEGER, lb=0, name="x")

# Obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[a] * y[a] for a in arcs) +
    gp.quicksum(unit_cost[a][k] * x[a, k] for a in arcs for k in products),
    GRB.MINIMIZE
)

# Conservazione del flusso
for n in nodes:
    for k in products:
        outflow = gp.quicksum(x[a, k] for a in arcs if a[0] == n)
        inflow  = gp.quicksum(x[a, k] for a in arcs if a[1] == n)
        if n == 'S':
            b = demand[k]
        elif n == 'T':
            b = -demand[k]
        else:
            b = 0
        m.addConstr(outflow - inflow == b, name=f"flow_{n}_{k}")

# Capacità condivisa
for a in arcs:
    m.addConstr(gp.quicksum(x[a, k] for k in products) <= capacity[a] * y[a],
                name=f"cap_{a[0]}_{a[1]}")

# Attivazione obbligatoria archi da S
m.addConstr(y[('S','A')] == 1, name="force_SA")
m.addConstr(y[('S','B')] == 1, name="force_SB")

# Limite numero archi attivi
m.addConstr(gp.quicksum(y[a] for a in arcs) <= max_arcs, name="max_arcs")

m.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for a in arcs:
        name = f"y_{a[0]}{a[1]}"
        variables[name] = float(round(y[a].X))
    for a in arcs:
        for k in products:
            name = f"x_{a[0]}{a[1]}_{k}"
            variables[name] = float(round(x[a, k].X))
    result["variables"] = variables
else:
    result["status"] = str(m.Status)

print("SOLUTION_JSON=" + json.dumps(result))
