import gurobipy as gp
from gurobipy import GRB
import json

# ---------- Dati ----------
arcs = [("S","A"), ("S","B"), ("A","B"), ("A","C"),
        ("B","C"), ("B","D"), ("C","D"), ("C","T"), ("D","T")]

fixed_cost = {
    ("S","A"): 55, ("S","B"): 50, ("A","B"): 18, ("A","C"): 38,
    ("B","C"): 22, ("B","D"): 35, ("C","D"): 20, ("C","T"): 48, ("D","T"): 44
}

capacity = {
    ("S","A"): 35, ("S","B"): 35, ("A","B"): 15, ("A","C"): 30,
    ("B","C"): 25, ("B","D"): 25, ("C","D"): 20, ("C","T"): 35, ("D","T"): 35
}

cost_k1 = {
    ("S","A"): 2, ("S","B"): 3, ("A","B"): 1, ("A","C"): 2,
    ("B","C"): 2, ("B","D"): 3, ("C","D"): 1, ("C","T"): 3, ("D","T"): 2
}

cost_k2 = {
    ("S","A"): 3, ("S","B"): 2, ("A","B"): 2, ("A","C"): 3,
    ("B","C"): 1, ("B","D"): 2, ("C","D"): 2, ("C","T"): 2, ("D","T"): 3
}

unit_cost = {"K1": cost_k1, "K2": cost_k2}

nodes = ["S","A","B","C","D","T"]
products = ["K1","K2"]
demand = {"K1": 28, "K2": 22}

# ---------- Modello ----------
m = gp.Model("H10_multiproduct_network")

x = m.addVars(arcs, vtype=GRB.BINARY, name="x")
f = m.addVars(arcs, products, vtype=GRB.INTEGER, lb=0, name="f")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[a] * x[a] for a in arcs) +
    gp.quicksum(unit_cost[k][a] * f[a, k] for a in arcs for k in products),
    GRB.MINIMIZE
)

# Conservazione del flusso
for n in nodes:
    for k in products:
        inflow = gp.quicksum(f[a, k] for a in arcs if a[1] == n)
        outflow = gp.quicksum(f[a, k] for a in arcs if a[0] == n)
        if n == "S":
            rhs = -demand[k]
        elif n == "T":
            rhs = demand[k]
        else:
            rhs = 0
        m.addConstr(inflow - outflow == rhs, name=f"cons_{n}_{k}")

# Capacità condivisa
for a in arcs:
    m.addConstr(gp.quicksum(f[a, k] for k in products) <= capacity[a] * x[a],
                name=f"cap_{a}")

# Attivazione obbligatoria degli archi in uscita da S
m.addConstr(x[("S","A")] == 1, name="force_SA")
m.addConstr(x[("S","B")] == 1, name="force_SB")

# Numero massimo di archi attivi
m.addConstr(gp.quicksum(x[a] for a in arcs) <= 7, name="max_arcs")

m.optimize()

# ---------- Output ----------
result = {"status": None, "objective": None, "variables": {}}

if m.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = m.ObjVal
    variables = {}
    for a in arcs:
        name = f"x_{a[0]}_{a[1]}"
        variables[name] = x[a].X
    for a in arcs:
        for k in products:
            name = f"f_{a[0]}_{a[1]}_{k}"
            variables[name] = f[a, k].X
    result["variables"] = variables
else:
    result["status"] = str(m.Status)

print("SOLUTION_JSON=" + json.dumps(result))
