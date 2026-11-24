import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
suppliers = ['A', 'B', 'C', 'D', 'E', 'F']
components = ['C1', 'C2', 'C3']

fixed_cost = {'A': 120, 'B': 140, 'C': 100, 'D': 150, 'E': 90, 'F': 110}
capacity   = {'A': 100, 'B': 110, 'C': 90, 'D': 120, 'E': 80, 'F': 95}
risk       = {'A': 2, 'B': 3, 'C': 1, 'D': 4, 'E': 2, 'F': 3}
demand     = {'C1': 80, 'C2': 70, 'C3': 60}

cost = {
    ('A', 'C1'): 9,  ('A', 'C2'): 12, ('A', 'C3'): 11,
    ('B', 'C1'): 10, ('B', 'C2'): 9,  ('B', 'C3'): 12,
    ('C', 'C1'): 11, ('C', 'C2'): 10, ('C', 'C3'): 9,
    ('D', 'C2'): 11, ('D', 'C3'): 10,
    ('E', 'C1'): 12, ('E', 'C2'): 8,
    ('F', 'C1'): 10, ('F', 'C3'): 8,
}

quality = {
    ('A', 'C1'): 96, ('A', 'C2'): 94, ('A', 'C3'): 95,
    ('B', 'C1'): 93, ('B', 'C2'): 97, ('B', 'C3'): 92,
    ('C', 'C1'): 98, ('C', 'C2'): 95, ('C', 'C3'): 96,
    ('D', 'C2'): 94, ('D', 'C3'): 93,
    ('E', 'C1'): 97, ('E', 'C2'): 98,
    ('F', 'C1'): 94, ('F', 'C3'): 98,
}

valid_pairs = list(cost.keys())

MIN_LINK = 10
MAX_SUPPLIERS = 4
MIN_QUALITY = 95
MAX_RISK = 580

# ---------------- Modello ----------------
model = gp.Model("H07_sourcing")

x = model.addVars(valid_pairs, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(suppliers, vtype=GRB.BINARY, name="y")
z = model.addVars(valid_pairs, vtype=GRB.BINARY, name="z")

model.setObjective(
    gp.quicksum(cost[p] * x[p] for p in valid_pairs) +
    gp.quicksum(fixed_cost[s] * y[s] for s in suppliers),
    GRB.MINIMIZE
)

# Domanda
for k in components:
    model.addConstr(
        gp.quicksum(x[s, k] for s in suppliers if (s, k) in valid_pairs) == demand[k],
        name=f"demand_{k}"
    )

# Capacità totale
for s in suppliers:
    model.addConstr(
        gp.quicksum(x[s, k] for k in components if (s, k) in valid_pairs) <= capacity[s] * y[s],
        name=f"cap_{s}"
    )

# Link x-z e quantità minima
for (s, k) in valid_pairs:
    model.addConstr(x[s, k] <= demand[k] * z[s, k], name=f"linkU_{s}_{k}")
    model.addConstr(x[s, k] >= MIN_LINK * z[s, k], name=f"linkL_{s}_{k}")
    model.addConstr(z[s, k] <= y[s], name=f"act_{s}_{k}")

# Almeno due fornitori per componente
for k in components:
    model.addConstr(
        gp.quicksum(z[s, k] for s in suppliers if (s, k) in valid_pairs) >= 2,
        name=f"minsup_{k}"
    )

# Massimo 4 fornitori attivi
model.addConstr(gp.quicksum(y[s] for s in suppliers) <= MAX_SUPPLIERS, name="maxsup")

# Almeno uno tra A e B
model.addConstr(y['A'] + y['B'] >= 1, name="AorB")

# Qualità media minima
for k in components:
    model.addConstr(
        gp.quicksum(quality[s, k] * x[s, k] for s in suppliers if (s, k) in valid_pairs)
        >= MIN_QUALITY * demand[k],
        name=f"qual_{k}"
    )

# Rischio totale massimo
model.addConstr(
    gp.quicksum(risk[s] * x[s, k] for (s, k) in valid_pairs) <= MAX_RISK,
    name="risk_budget"
)

model.optimize()

# ---------------- Output ----------------
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
}

result = {"status": status_map.get(model.Status, str(model.Status)),
          "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    variables = {}
    for (s, k) in valid_pairs:
        variables[f"x_{s}_{k}"] = x[s, k].X
    for s in suppliers:
        variables[f"y_{s}"] = y[s].X
    for (s, k) in valid_pairs:
        variables[f"z_{s}_{k}"] = z[s, k].X
    result["objective"] = model.ObjVal
    result["variables"] = variables

print("SOLUTION_JSON=" + json.dumps(result))
