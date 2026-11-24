import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

# tempi di lavorazione; None = incompatibile
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5,   # J7 non compatibile con A -> nessuna voce (J7,A)
}

# coppie (j,m) valide
valid_pairs = list(p.keys())

# ---------------- Modello ----------------
model = gp.Model("bilanciamento_2_macchine")

x = model.addVars(valid_pairs, vtype=GRB.BINARY, name="x")
Cmax = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Cmax")

# Ogni lavoro assegnato a esattamente una macchina compatibile
for j in jobs:
    model.addConstr(
        gp.quicksum(x[j, m] for (jj, m) in valid_pairs if jj == j) == 1,
        name=f"assign_{j}"
    )

# Carico di ciascuna macchina <= Cmax
for m in machines:
    model.addConstr(
        gp.quicksum(p[j, m] * x[j, m] for (j, mm) in valid_pairs if mm == m) <= Cmax,
        name=f"load_{m}"
    )

model.setObjective(Cmax, GRB.MINIMIZE)

model.optimize()

# ---------------- Output ----------------
result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    variables = {}
    for (j, m) in valid_pairs:
        variables[f"x_{j}_{m}"] = round(x[j, m].X, 4)
    # includiamo esplicitamente anche x_J7_A come non definita/0 (incompatibile)
    variables["x_J7_A"] = 0.0
    variables["Cmax"] = round(Cmax.X, 4)

    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    result["variables"] = variables
else:
    result["status"] = str(model.Status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
