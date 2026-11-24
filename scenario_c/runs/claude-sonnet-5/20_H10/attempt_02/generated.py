import gurobipy as gp
from gurobipy import GRB
import json

# --- Insiemi ---
ARCS = [('S','A'), ('S','B'), ('A','B'), ('A','C'), ('B','C'),
         ('B','D'), ('C','D'), ('C','T'), ('D','T')]
NODES = ['S','A','B','C','D','T']
PRODUCTS = ['K1','K2']

# --- Parametri ---
fixed = {
    ('S','A'):55, ('S','B'):50, ('A','B'):18, ('A','C'):38,
    ('B','C'):22, ('B','D'):35, ('C','D'):20, ('C','T'):48, ('D','T'):44
}
cap = {
    ('S','A'):35, ('S','B'):35, ('A','B'):15, ('A','C'):30,
    ('B','C'):25, ('B','D'):25, ('C','D'):20, ('C','T'):35, ('D','T'):35
}
cost = {
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
demand = {'K1':28, 'K2':22}
MAXARCS = 7

model = gp.Model("H10_multiproduct_network")
model.setParam('OutputFlag', 0)

# --- Variabili ---
y = model.addVars(ARCS, vtype=GRB.BINARY, name="y")
x = model.addVars(ARCS, PRODUCTS, vtype=GRB.INTEGER, lb=0, name="x")

# --- Funzione obiettivo ---
obj = gp.quicksum(fixed[a] * y[a] for a in ARCS) + \
      gp.quicksum(cost[a][k] * x[a, k] for a in ARCS for k in PRODUCTS)
model.setObjective(obj, GRB.MINIMIZE)

# --- Vincoli di conservazione del flusso ---
for n in NODES:
    for k in PRODUCTS:
        inflow = gp.quicksum(x[a, k] for a in ARCS if a[1] == n)
        outflow = gp.quicksum(x[a, k] for a in ARCS if a[0] == n)
        if n == 'S':
            rhs = -demand[k]
        elif n == 'T':
            rhs = demand[k]
        else:
            rhs = 0
        model.addConstr(inflow - outflow == rhs, name=f"balance_{n}_{k}")

# --- Capacità condivisa ---
for a in ARCS:
    model.addConstr(
        gp.quicksum(x[a, k] for k in PRODUCTS) <= cap[a] * y[a],
        name=f"cap_{a[0]}_{a[1]}"
    )

# --- Attivazione obbligatoria degli archi da S ---
model.addConstr(y[('S','A')] == 1, name="force_SA")
model.addConstr(y[('S','B')] == 1, name="force_SB")

# --- Limite sul numero di archi attivati ---
model.addConstr(gp.quicksum(y[a] for a in ARCS) <= MAXARCS, name="max_arcs")

model.optimize()

variables = {}
status_str = "UNKNOWN"
objective_value = None

if model.status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    objective_value = model.ObjVal
    for a in ARCS:
        variables[f"y_{a[0]}_{a[1]}"] = float(round(y[a].X))
    for a in ARCS:
        for k in PRODUCTS:
            variables[f"x_{a[0]}_{a[1]}_{k}"] = float(round(x[a, k].X))
else:
    status_str = "INFEASIBLE" if model.status == GRB.INFEASIBLE else str(model.status)
    objective_value = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status_str,
    "objective": objective_value,
    "variables": variables
}))
