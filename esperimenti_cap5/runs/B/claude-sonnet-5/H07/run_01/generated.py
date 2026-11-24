import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
S = ["A", "B", "C", "D", "E", "F"]
K = ["C1", "C2", "C3"]

demand = {"C1": 80, "C2": 70, "C3": 60}

fixed_cost = {"A": 120, "B": 140, "C": 100, "D": 150, "E": 90, "F": 110}
capacity   = {"A": 100, "B": 110, "C": 90,  "D": 120, "E": 80,  "F": 95}
risk       = {"A": 2,   "B": 3,   "C": 1,   "D": 4,   "E": 2,   "F": 3}

cost = {
    ("A","C1"):9, ("A","C2"):12, ("A","C3"):11,
    ("B","C1"):10,("B","C2"):9,  ("B","C3"):12,
    ("C","C1"):11,("C","C2"):10, ("C","C3"):9,
    ("D","C2"):11,("D","C3"):10,
    ("E","C1"):12,("E","C2"):8,
    ("F","C1"):10,("F","C3"):8,
}

quality = {
    ("A","C1"):96, ("A","C2"):94, ("A","C3"):95,
    ("B","C1"):93, ("B","C2"):97, ("B","C3"):92,
    ("C","C1"):98, ("C","C2"):95, ("C","C3"):96,
    ("D","C2"):94, ("D","C3"):93,
    ("E","C1"):97, ("E","C2"):98,
    ("F","C1"):94, ("F","C3"):98,
}

V = list(cost.keys())  # coppie ammissibili

Qmin = 95
Rmax = 580
Nmax = 4
umin = 10

# ---------------- Modello ----------------
m = gp.Model("H07_sourcing")

x = m.addVars(V, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(S, vtype=GRB.BINARY, name="y")
z = m.addVars(V, vtype=GRB.BINARY, name="z")

# Obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[s]*y[s] for s in S) +
    gp.quicksum(cost[(s,k)]*x[(s,k)] for (s,k) in V),
    GRB.MINIMIZE
)

# Domanda esatta
for k in K:
    m.addConstr(gp.quicksum(x[(s,k)] for (s,kk) in V if kk==k for s in [s] ) == demand[k],
                name=f"demand_{k}")

# (ricostruzione corretta della somma per componente)
m.remove([m.getConstrByName(f"demand_{k}") for k in K])
for k in K:
    m.addConstr(gp.quicksum(x[(s,kk)] for (s,kk) in V if kk == k) == demand[k],
                name=f"demand_{k}")

# Capacità complessiva
for s in S:
    m.addConstr(gp.quicksum(x[(s,kk)] for (ss,kk) in V if ss == s) <= capacity[s]*y[s],
                name=f"cap_{s}")

# Link x-z e soglia minima
for (s,k) in V:
    m.addConstr(x[(s,k)] <= demand[k]*z[(s,k)], name=f"linkUB_{s}_{k}")
    m.addConstr(x[(s,k)] >= umin*z[(s,k)], name=f"linkLB_{s}_{k}")
    m.addConstr(z[(s,k)] <= y[s], name=f"zy_{s}_{k}")

# Almeno due fornitori per componente
for k in K:
    m.addConstr(gp.quicksum(z[(s,kk)] for (s,kk) in V if kk == k) >= 2,
                name=f"twosup_{k}")

# Qualità media minima
for k in K:
    m.addConstr(gp.quicksum(quality[(s,kk)]*x[(s,kk)] for (s,kk) in V if kk == k) >= Qmin*demand[k],
                name=f"qual_{k}")

# Numero massimo fornitori attivi
m.addConstr(gp.quicksum(y[s] for s in S) <= Nmax, name="maxsup")

# Almeno uno tra A e B
m.addConstr(y["A"] + y["B"] >= 1, name="AorB")

# Rischio totale
m.addConstr(gp.quicksum(risk[s]*x[(s,k)] for (s,k) in V) <= Rmax, name="risk")

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
    for (s,k) in V:
        variables[f"x_{s}_{k}"] = round(x[(s,k)].X, 4)
    for s in S:
        variables[f"y_{s}"] = round(y[s].X, 4)
    for (s,k) in V:
        variables[f"z_{s}_{k}"] = round(z[(s,k)].X, 4)

    result["objective"] = round(m.ObjVal, 4)
    result["variables"] = variables

    print("Status:", status)
    print("Obiettivo (costo totale):", m.ObjVal)
    print("Decisioni non nulle:")
    for name, val in variables.items():
        if val != 0:
            print(f"  {name} = {val}")

print("SOLUTION_JSON=" + json.dumps(result))
