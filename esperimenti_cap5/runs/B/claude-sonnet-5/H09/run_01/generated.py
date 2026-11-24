import gurobipy as gp
from gurobipy import GRB
import json

P = ['A', 'B', 'C']
T = [1, 2, 3, 4, 5, 6]

d = {
    'A': {1:12,2:18,3:14,4:20,5:16,6:19},
    'B': {1:10,2:9,3:15,4:12,5:17,6:14},
    'C': {1:8,2:11,3:10,4:13,5:9,6:15}
}

c = {
    'A': {1:7,2:8,3:9,4:7,5:10,6:8},
    'B': {1:9,2:8,3:8,4:10,5:7,6:9},
    'C': {1:11,2:10,3:12,4:9,5:11,6:8}
}

setup = {'A':35, 'B':40, 'C':45}
hold  = {'A':2,  'B':2,  'C':3}
hours = {'A':2,  'B':3,  'C':4}
lotmin= {'A':5,  'B':4,  'C':3}

Cap = {1:120, 2:115, 3:125, 4:110, 5:120, 6:115}

OT_MAX = 20.0
OT_COST = 18.0
INV_MAX_TOTAL = 40
FINAL_MIN = 2

# Big-M per prodotto: somma domande + scorta massima
M = {p: sum(d[p][t] for t in T) + INV_MAX_TOTAL for p in P}

model = gp.Model("H09_ProdInv_Overtime")

x = model.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="x")
I = model.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="I")
y = model.addVars(P, T, vtype=GRB.BINARY, name="y")
O = model.addVars(T, vtype=GRB.CONTINUOUS, lb=0.0, ub=OT_MAX, name="O")

# Bilancio di magazzino
for p in P:
    prev = 0
    for t in T:
        model.addConstr(I[p, t] == prev + x[p, t] - d[p][t], name=f"bal_{p}_{t}")
        prev = I[p, t]

# Scorta finale minima
for p in P:
    model.addConstr(I[p, 6] >= FINAL_MIN, name=f"finalstock_{p}")

# Lotto minimo e linking con setup
for p in P:
    for t in T:
        model.addConstr(x[p, t] <= M[p] * y[p, t], name=f"linkU_{p}_{t}")
        model.addConstr(x[p, t] >= lotmin[p] * y[p, t], name=f"linkL_{p}_{t}")

# Limite numero setup per periodo
for t in T:
    limit = 3 if t == 1 else 2
    model.addConstr(gp.quicksum(y[p, t] for p in P) <= limit, name=f"setuplim_{t}")

# Capacità con straordinario
for t in T:
    model.addConstr(
        gp.quicksum(hours[p] * x[p, t] for p in P) <= Cap[t] + O[t],
        name=f"cap_{t}"
    )

# Scorta totale massima
for t in T:
    model.addConstr(gp.quicksum(I[p, t] for p in P) <= INV_MAX_TOTAL, name=f"invmax_{t}")

# Funzione obiettivo
obj = gp.quicksum(c[p][t] * x[p, t] for p in P for t in T) \
    + gp.quicksum(hold[p] * I[p, t] for p in P for t in T) \
    + gp.quicksum(setup[p] * y[p, t] for p in P for t in T) \
    + gp.quicksum(OT_COST * O[t] for t in T)

model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = round(x[p, t].X, 4)
            variables[f"I_{p}_{t}"] = round(I[p, t].X, 4)
            variables[f"y_{p}_{t}"] = round(y[p, t].X, 4)
    for t in T:
        variables[f"O_{t}"] = round(O[t].X, 4)
    result["variables"] = variables

    print("=== Riepilogo soluzione ===")
    print(f"Stato: {result['status']}")
    print(f"Costo totale ottimo: {result['objective']}")
    print("\nDecisioni non nulle:")
    for k, v in variables.items():
        if abs(v) > 1e-6:
            print(f"  {k} = {v}")
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    result["status"] = status_map.get(status, f"STATUS_{status}")
    print(f"Solver non ha trovato soluzione ottima. Stato: {result['status']}")

print("SOLUTION_JSON=" + json.dumps(result))
