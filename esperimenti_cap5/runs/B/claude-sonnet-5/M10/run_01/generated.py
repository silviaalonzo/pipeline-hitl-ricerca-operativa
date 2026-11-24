import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
arcs = [
    ("S","A"), ("S","B"), ("A","B"),
    ("A","C"), ("B","C"), ("B","T"), ("C","T")
]

fixed_cost = {
    ("S","A"): 40, ("S","B"): 35, ("A","B"): 15,
    ("A","C"): 30, ("B","C"): 18, ("B","T"): 45, ("C","T"): 38
}

unit_cost = {
    ("S","A"): 2, ("S","B"): 3, ("A","B"): 1,
    ("A","C"): 2, ("B","C"): 2, ("B","T"): 4, ("C","T"): 2
}

capacity = {
    ("S","A"): 30, ("S","B"): 35, ("A","B"): 15,
    ("A","C"): 25, ("B","C"): 20, ("B","T"): 25, ("C","T"): 35
}

DEMAND = 40

# --- Modello ---
m = gp.Model("Rete_Distributiva_M10")

x = m.addVars(arcs, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(arcs, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[a]*y[a] + unit_cost[a]*x[a] for a in arcs),
    GRB.MINIMIZE
)

# Capacità legata all'attivazione
for a in arcs:
    m.addConstr(x[a] <= capacity[a]*y[a], name=f"cap_{a}")

# Conservazione del flusso
m.addConstr(x[("S","A")] + x[("S","B")] == DEMAND, name="flow_S")
m.addConstr(x[("S","A")] == x[("A","B")] + x[("A","C")], name="flow_A")
m.addConstr(x[("S","B")] + x[("A","B")] == x[("B","C")] + x[("B","T")], name="flow_B")
m.addConstr(x[("A","C")] + x[("B","C")] == x[("C","T")], name="flow_C")
m.addConstr(x[("B","T")] + x[("C","T")] == DEMAND, name="flow_T")

m.optimize()

# --- Output ---
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status = status_map.get(m.Status, str(m.Status))

if m.Status == GRB.OPTIMAL:
    variables = {}
    for a in arcs:
        varname_x = f"x_{a[0]}{a[1]}"
        varname_y = f"y_{a[0]}{a[1]}"
        variables[varname_x] = float(round(x[a].X))
        variables[varname_y] = float(round(y[a].X))
    result = {
        "status": status,
        "objective": float(round(m.ObjVal, 2)),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result))
