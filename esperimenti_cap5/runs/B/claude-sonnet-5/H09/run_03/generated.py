import gurobipy as gp
from gurobipy import GRB
import json

# ------------------- Dati -------------------
P = ['A', 'B', 'C']
T = [1, 2, 3, 4, 5, 6]

demand = {
    ('A',1):12, ('A',2):18, ('A',3):14, ('A',4):20, ('A',5):16, ('A',6):19,
    ('B',1):10, ('B',2):9,  ('B',3):15, ('B',4):12, ('B',5):17, ('B',6):14,
    ('C',1):8,  ('C',2):11, ('C',3):10, ('C',4):13, ('C',5):9,  ('C',6):15,
}

cost = {
    ('A',1):7,  ('A',2):8,  ('A',3):9,  ('A',4):7,  ('A',5):10, ('A',6):8,
    ('B',1):9,  ('B',2):8,  ('B',3):8,  ('B',4):10, ('B',5):7,  ('B',6):9,
    ('C',1):11, ('C',2):10, ('C',3):12, ('C',4):9,  ('C',5):11, ('C',6):8,
}

setup_cost = {'A':35, 'B':40, 'C':45}
holding    = {'A':2,  'B':2,  'C':3}
hours      = {'A':2,  'B':3,  'C':4}
lot_min    = {'A':5,  'B':4,  'C':3}

capacity = {1:120, 2:115, 3:125, 4:110, 5:120, 6:115}

OT_max  = 20
OT_cost = 18
InvMax  = 40

# Big-M per prodotto (somma totale della domanda + scorta finale richiesta)
bigM = {p: sum(demand[p,t] for t in T) + 2 for p in P}

# Numero massimo di setup per periodo
S = {t: (3 if t == 1 else 2) for t in T}

# ------------------- Modello -------------------
m = gp.Model("H09_multiprod_scorte")

x = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="x")
I = m.addVars(P, T, vtype=GRB.INTEGER, lb=0, name="I")
y = m.addVars(P, T, vtype=GRB.BINARY, name="y")
O = m.addVars(T, vtype=GRB.CONTINUOUS, lb=0.0, ub=OT_max, name="O")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(cost[p,t]*x[p,t] for p in P for t in T) +
    gp.quicksum(setup_cost[p]*y[p,t] for p in P for t in T) +
    gp.quicksum(holding[p]*I[p,t] for p in P for t in T) +
    gp.quicksum(OT_cost*O[t] for t in T),
    GRB.MINIMIZE
)

# Bilancio di scorte
for p in P:
    for t in T:
        if t == 1:
            m.addConstr(I[p,t] == x[p,t] - demand[p,t], name=f"bal_{p}_{t}")
        else:
            m.addConstr(I[p,t] == I[p,t-1] + x[p,t] - demand[p,t], name=f"bal_{p}_{t}")

# Scorta finale minima
for p in P:
    m.addConstr(I[p,6] >= 2, name=f"final_stock_{p}")

# Scorta totale massima per periodo
for t in T:
    m.addConstr(gp.quicksum(I[p,t] for p in P) <= InvMax, name=f"invmax_{t}")

# Capacità (base + straordinario)
for t in T:
    m.addConstr(
        gp.quicksum(hours[p]*x[p,t] for p in P) <= capacity[t] + O[t],
        name=f"cap_{t}"
    )

# Setup e lotto minimo
for p in P:
    for t in T:
        m.addConstr(x[p,t] <= bigM[p]*y[p,t], name=f"link_up_{p}_{t}")
        m.addConstr(x[p,t] >= lot_min[p]*y[p,t], name=f"link_lo_{p}_{t}")

# Numero massimo di setup attivi per periodo
for t in T:
    m.addConstr(gp.quicksum(y[p,t] for p in P) <= S[t], name=f"maxsetup_{t}")

# ------------------- Risoluzione -------------------
m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.TIME_LIMIT: "TIME_LIMIT"
}
status = status_map.get(m.status, str(m.status))

result = {"status": status, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    variables = {}
    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = float(x[p,t].X)
            variables[f"I_{p}_{t}"] = float(I[p,t].X)
            variables[f"y_{p}_{t}"] = float(y[p,t].X)
    for t in T:
        variables[f"O_{t}"] = float(O[t].X)

    result["objective"] = float(m.objVal)
    result["variables"] = variables

    # Stampa leggibile (non richiesta ma utile)
    print("Stato:", status)
    print("Costo totale ottimo:", m.objVal)
    print("Decisioni non nulle:")
    for k, v in variables.items():
        if abs(v) > 1e-6:
            print(f"  {k} = {v}")

print("SOLUTION_JSON=" + json.dumps(result))
