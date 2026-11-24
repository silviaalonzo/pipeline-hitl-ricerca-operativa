import gurobipy as gp
from gurobipy import GRB
import json

# Dati del problema
arcs = {
    ('S', 'A'): {'fixed': 40, 'unit': 2, 'cap': 30},
    ('S', 'B'): {'fixed': 35, 'unit': 3, 'cap': 35},
    ('A', 'B'): {'fixed': 15, 'unit': 1, 'cap': 15},
    ('A', 'C'): {'fixed': 30, 'unit': 2, 'cap': 25},
    ('B', 'C'): {'fixed': 18, 'unit': 2, 'cap': 20},
    ('B', 'T'): {'fixed': 45, 'unit': 4, 'cap': 25},
    ('C', 'T'): {'fixed': 38, 'unit': 2, 'cap': 35},
}

nodes = ['S', 'A', 'B', 'C', 'T']
demand = 40

model = gp.Model("network_design")
model.setParam('OutputFlag', 0)

# Variabili
x = model.addVars(arcs.keys(), vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(arcs.keys(), vtype=GRB.BINARY, name="y")

# Vincoli di capacità legati all'attivazione
for (i, j), data in arcs.items():
    model.addConstr(x[i, j] <= data['cap'] * y[i, j], name=f"cap_{i}_{j}")

# Vincoli di conservazione del flusso
for n in nodes:
    inflow = gp.quicksum(x[i, j] for (i, j) in arcs if j == n)
    outflow = gp.quicksum(x[i, j] for (i, j) in arcs if i == n)
    if n == 'S':
        model.addConstr(outflow - inflow == demand, name="balance_S")
    elif n == 'T':
        model.addConstr(inflow - outflow == demand, name="balance_T")
    else:
        model.addConstr(inflow - outflow == 0, name=f"balance_{n}")

# Funzione obiettivo
obj = gp.quicksum(arcs[a]['fixed'] * y[a] + arcs[a]['unit'] * x[a] for a in arcs)
model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if model.status == GRB.OPTIMAL:
    variables = {}
    for (i, j) in arcs:
        variables[f"x_{i}{j}"] = float(x[i, j].X)
        variables[f"y_{i}{j}"] = float(y[i, j].X)
    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variables
    }
else:
    result = {"status": str(model.status), "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
