import gurobipy as gp
from gurobipy import GRB

# ---------------- Dati ----------------
P = ["A", "B", "C"]
T = [1, 2, 3, 4, 5, 6]

demand = {
    ("A",1):12, ("A",2):18, ("A",3):14, ("A",4):20, ("A",5):16, ("A",6):19,
    ("B",1):10, ("B",2):9,  ("B",3):15, ("B",4):12, ("B",5):17, ("B",6):14,
    ("C",1):8,  ("C",2):11, ("C",3):10, ("C",4):13, ("C",5):9,  ("C",6):15,
}

cost = {
    ("A",1):7, ("A",2):8, ("A",3):9, ("A",4):7, ("A",5):10, ("A",6):8,
    ("B",1):9, ("B",2):8, ("B",3):8, ("B",4):10,("B",5):7,  ("B",6):9,
    ("C",1):11,("C",2):10,("C",3):12,("C",4):9, ("C",5):11, ("C",6):8,
}

setup   = {"A":35, "B":40, "C":45}
holding = {"A":2,  "B":2,  "C":3}
hours   = {"A":2,  "B":3,  "C":4}
minlot  = {"A":5,  "B":4,  "C":3}

cap = {1:120, 2:115, 3:125, 4:110, 5:120, 6:115}

OC = 18.0
OMAX = 20.0
STOCKMAX = 40
ENDMIN = 2

maxset = {t: (3 if t == 1 else 2) for t in T}

bigM = {p: sum(demand[p, t] for t in T) + ENDMIN for p in P}

# ---------------- Modello ----------------
m = gp.Model("H09_multiprodotto_scorte")

x = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(P, T, vtype=GRB.BINARY, name="y")
O = m.addVars(T, vtype=GRB.CONTINUOUS, lb=0.0, ub=OMAX, name="O")

# Bilancio di magazzino
for p in P:
    prev = 0
    for t in T:
        m.addConstr(I[p, t] == prev + x[p, t] - demand[p, t], name=f"bal_{p}_{t}")
        prev = I[p, t]

# Scorta finale minima
for p in P:
    m.addConstr(I[p, 6] >= ENDMIN, name=f"endmin_{p}")

# Scorta totale massima per periodo
for t in T:
    m.addConstr(gp.quicksum(I[p, t] for p in P) <= STOCKMAX, name=f"stockmax_{t}")

# Linking produzione/setup e lotto minimo
for p in P:
    for t in T:
        m.addConstr(x[p, t] <= bigM[p] * y[p, t], name=f"link_{p}_{t}")
        m.addConstr(x[p, t] >= minlot[p] * y[p, t], name=f"minlot_{p}_{t}")

# Numero massimo di prodotti attivi per periodo
for t in T:
    m.addConstr(gp.quicksum(y[p, t] for p in P) <= maxset[t], name=f"maxset_{t}")

# Capacità con straordinario
for t in T:
    m.addConstr(
        gp.quicksum(hours[p] * x[p, t] for p in P) <= cap[t] + O[t],
        name=f"cap_{t}"
    )

# ---------------- Obiettivo ----------------
obj = (
    gp.quicksum(cost[p, t] * x[p, t] for p in P for t in T)
    + gp.quicksum(setup[p] * y[p, t] for p in P for t in T)
    + gp.quicksum(holding[p] * I[p, t] for p in P for t in T)
    + gp.quicksum(OC * O[t] for t in T)
)
m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status = status_map.get(m.Status, str(m.Status))

result = {"status": status, "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    variables = {}
    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = round(x[p, t].X, 4)
            variables[f"I_{p}_{t}"] = round(I[p, t].X, 4)
            variables[f"y_{p}_{t}"] = round(y[p, t].X, 4)
    for t in T:
        variables[f"O_{t}"] = round(O[t].X, 4)
    result["objective"] = round(m.ObjVal, 4)
    result["variables"] = variables

import json
print("SOLUTION_JSON=" + json.dumps(result))
