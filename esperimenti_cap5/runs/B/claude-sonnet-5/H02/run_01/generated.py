import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
P = ['A', 'B', 'C']
T = [1, 2, 3, 4]

d = {
    ('A',1):8, ('A',2):12, ('A',3):10, ('A',4):14,
    ('B',1):10,('B',2):8,  ('B',3):14, ('B',4):12,
    ('C',1):6, ('C',2):9,  ('C',3):7,  ('C',4):11,
}

c = {
    ('A',1):9, ('A',2):11, ('A',3):10, ('A',4):12,
    ('B',1):8, ('B',2):9,  ('B',3):11, ('B',4):10,
    ('C',1):13,('C',2):12, ('C',3):14, ('C',4):11,
}

s = {'A':45, 'B':40, 'C':50}
h = {'A':2,  'B':3,  'C':2}
a = {'A':2,  'B':3,  'C':4}
L = {'A':4,  'B':4,  'C':3}
Cap = {1:90, 2:95, 3:90, 4:100}
I0 = {'A':0, 'B':0, 'C':6}

M = {p: sum(d[(p,t)] for t in T) for p in P}

MaxSet = 2
MaxInv = 20

# ---------------- Modello ----------------
m = gp.Model("H02_produzione_multiperiodo")

x = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(P, T, vtype=GRB.BINARY, name="y")

# Bilancio di magazzino
for p in P:
    for t in T:
        prev = I0[p] if t == 1 else I[p, t-1]
        m.addConstr(prev + x[p, t] - d[(p, t)] == I[p, t], name=f"bal_{p}_{t}")

# Legame produzione-setup e lotto minimo
for p in P:
    for t in T:
        m.addConstr(x[p, t] <= M[p] * y[p, t], name=f"link_{p}_{t}")
        m.addConstr(x[p, t] >= L[p] * y[p, t], name=f"minlot_{p}_{t}")

# Massimo numero di setup attivi per periodo
for t in T:
    m.addConstr(gp.quicksum(y[p, t] for p in P) <= MaxSet, name=f"maxset_{t}")

# Capacità produttiva
for t in T:
    m.addConstr(gp.quicksum(a[p] * x[p, t] for p in P) <= Cap[t], name=f"cap_{t}")

# Scorta totale massima
for t in T:
    m.addConstr(gp.quicksum(I[p, t] for p in P) <= MaxInv, name=f"maxinv_{t}")

# Scorta finale nulla
for p in P:
    m.addConstr(I[p, 4] == 0, name=f"finalinv_{p}")

# Funzione obiettivo
obj = gp.quicksum(c[(p, t)] * x[p, t] + s[p] * y[p, t] + h[p] * I[p, t]
                   for p in P for t in T)
m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.objVal, 4)
    variables = {}
    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = round(x[p, t].X, 4)
            variables[f"I_{p}_{t}"] = round(I[p, t].X, 4)
            variables[f"y_{p}_{t}"] = round(y[p, t].X, 4)
    result["variables"] = variables

    # Stampa decisioni non nulle (report leggibile)
    print("Stato solver:", result["status"])
    print("Valore ottimo:", result["objective"])
    print("Decisioni non nulle:")
    for k, v in variables.items():
        if abs(v) > 1e-6:
            print(f"  {k} = {v}")
else:
    result["status"] = str(m.status)

print("SOLUTION_JSON=" + json.dumps(result))
