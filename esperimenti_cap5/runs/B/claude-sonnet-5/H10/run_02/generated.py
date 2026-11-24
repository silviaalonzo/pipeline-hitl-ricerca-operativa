import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
nodes = ['S', 'A', 'B', 'C', 'D', 'T']

arcs = [('S','A'), ('S','B'), ('A','B'), ('A','C'),
        ('B','C'), ('B','D'), ('C','D'), ('C','T'), ('D','T')]

fixed_cost = {
    ('S','A'): 55, ('S','B'): 50, ('A','B'): 18, ('A','C'): 38,
    ('B','C'): 22, ('B','D'): 35, ('C','D'): 20, ('C','T'): 48, ('D','T'): 44
}

capacity = {
    ('S','A'): 35, ('S','B'): 35, ('A','B'): 15, ('A','C'): 30,
    ('B','C'): 25, ('B','D'): 25, ('C','D'): 20, ('C','T'): 35, ('D','T'): 35
}

products = ['K1', 'K2']
demand = {'K1': 28, 'K2': 22}

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

# ---------------- Modello ----------------
m = gp.Model("H10_multiproduct_network")

x = m.addVars(arcs, products, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(arcs, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[a] * y[a] for a in arcs) +
    gp.quicksum(unit_cost[a][k] * x[a, k] for a in arcs for k in products),
    GRB.MINIMIZE
)

# Conservazione del flusso per ciascun prodotto e nodo
for k in products:
    for n in nodes:
        inflow = gp.quicksum(x[a, k] for a in arcs if a[1] == n)
        outflow = gp.quicksum(x[a, k] for a in arcs if a[0] == n)
        if n == 'S':
            m.addConstr(outflow - inflow == demand[k], name=f"flow_{n}_{k}")
        elif n == 'T':
            m.addConstr(inflow - outflow == demand[k], name=f"flow_{n}_{k}")
        else:
            m.addConstr(inflow - outflow == 0, name=f"flow_{n}_{k}")

# Capacità condivisa
for a in arcs:
    m.addConstr(gp.quicksum(x[a, k] for k in products) <= capacity[a] * y[a],
                name=f"cap_{a}")

# Attivazione obbligatoria degli archi da S
m.addConstr(y[('S','A')] == 1, name="force_SA")
m.addConstr(y[('S','B')] == 1, name="force_SB")

# Limite massimo di archi attivati
m.addConstr(gp.quicksum(y[a] for a in arcs) <= 7, name="max_arcs")

m.optimize()

# ---------------- Output ----------------
result = {"status": None, "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for a in arcs:
        variables[f"y_{a[0]}_{a[1]}"] = round(y[a].X, 4)
        for k in products:
            variables[f"x_{a[0]}_{a[1]}_{k}"] = round(x[a, k].X, 4)
    result["variables"] = variables
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    result["status"] = status_map.get(m.Status, str(m.Status))
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
