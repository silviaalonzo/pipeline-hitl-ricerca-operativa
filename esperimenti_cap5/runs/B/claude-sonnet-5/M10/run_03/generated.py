import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
arcs = [
    ("S","A"), ("S","B"),
    ("A","B"), ("A","C"),
    ("B","C"), ("B","T"),
    ("C","T")
]

fixed_cost = {
    ("S","A"): 40, ("S","B"): 35,
    ("A","B"): 15, ("A","C"): 30,
    ("B","C"): 18, ("B","T"): 45,
    ("C","T"): 38
}

unit_cost = {
    ("S","A"): 2, ("S","B"): 3,
    ("A","B"): 1, ("A","C"): 2,
    ("B","C"): 2, ("B","T"): 4,
    ("C","T"): 2
}

capacity = {
    ("S","A"): 30, ("S","B"): 35,
    ("A","B"): 15, ("A","C"): 25,
    ("B","C"): 20, ("B","T"): 25,
    ("C","T"): 35
}

D = 40  # domanda totale da S a T

# --- Modello ---
m = gp.Model("rete_distributiva")

x = m.addVars(arcs, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(arcs, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[a]*y[a] + unit_cost[a]*x[a] for a in arcs),
    GRB.MINIMIZE
)

# Vincoli di capacità/attivazione
for a in arcs:
    m.addConstr(x[a] <= capacity[a]*y[a], name=f"cap_{a[0]}{a[1]}")

# Bilancio nodi intermedi
m.addConstr(x[("S","A")] == x[("A","B")] + x[("A","C")], name="flow_A")
m.addConstr(x[("S","B")] + x[("A","B")] == x[("B","C")] + x[("B","T")], name="flow_B")
m.addConstr(x[("A","C")] + x[("B","C")] == x[("C","T")], name="flow_C")

# Bilancio globale S e T
m.addConstr(x[("S","A")] + x[("S","B")] == D, name="supply_S")
m.addConstr(x[("B","T")] + x[("C","T")] == D, name="demand_T")

m.optimize()

# --- Estrazione risultati ---
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status = status_map.get(m.status, str(m.status))

variables = {}
objective = None

if m.status == GRB.OPTIMAL:
    objective = m.objVal
    for a in arcs:
        vname_x = f"x_{a[0]}{a[1]}"
        vname_y = f"y_{a[0]}{a[1]}"
        variables[vname_x] = float(round(x[a].X))
        variables[vname_y] = float(round(y[a].X))

    # Stampa dettagliata (facoltativa, per leggibilità)
    print(f"Stato solver: {status}")
    print(f"Valore ottimo: {objective}")
    print("Decisioni non nulle:")
    for a in arcs:
        if x[a].X > 1e-6:
            print(f"  x_{a[0]}{a[1]} = {round(x[a].X)}  (y_{a[0]}{a[1]} = {round(y[a].X)})")
else:
    print(f"Stato solver: {status}")

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables
}))
