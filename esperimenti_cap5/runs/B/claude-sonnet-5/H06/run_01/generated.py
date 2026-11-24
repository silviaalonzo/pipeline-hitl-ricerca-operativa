import gurobipy as gp
from gurobipy import GRB
import json
import itertools

# ---- Dati ----
jobs = [1, 2, 3, 4, 5, 6, 7]
p = {1: 5, 2: 7, 3: 4, 4: 6, 5: 3, 6: 8, 7: 5}
r = {1: 0, 2: 0, 3: 2, 4: 3, 5: 5, 6: 0, 7: 6}
d = {1: 9, 2: 17, 3: 12, 4: 22, 5: 15, 6: 28, 7: 25}
w = {1: 4, 2: 3, 3: 5, 4: 2, 5: 6, 6: 2, 7: 4}

M = sum(p.values()) + max(r.values())  # big-M giustificato

pairs = [(i, j) for i, j in itertools.combinations(jobs, 2)]

# ---- Modello ----
model = gp.Model("H06_sequenziamento")

S = model.addVars(jobs, lb=0.0, name="S")
C = model.addVars(jobs, lb=0.0, name="C")
T = model.addVars(jobs, lb=0.0, name="T")
x = model.addVars(pairs, vtype=GRB.BINARY, name="x")

# Completamento
model.addConstrs((C[i] == S[i] + p[i] for i in jobs), name="completamento")

# Disponibilità
model.addConstrs((S[i] >= r[i] for i in jobs), name="release")

# Ritardo
model.addConstrs((T[i] >= C[i] - d[i] for i in jobs), name="ritardo")

# Non sovrapposizione (disgiuntivo big-M)
for (i, j) in pairs:
    model.addConstr(S[j] >= C[i] - M * (1 - x[i, j]), name=f"disj1_{i}_{j}")
    model.addConstr(S[i] >= C[j] - M * x[i, j], name=f"disj2_{i}_{j}")

# Precedenze specifiche
model.addConstr(C[1] <= S[2], name="prec_J1_J2")
model.addConstr(C[3] <= S[5], name="prec_J3_J5")

# Obiettivo
model.setObjective(gp.quicksum(w[i] * T[i] for i in jobs), GRB.MINIMIZE)

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = model.ObjVal
    variables = {}
    for i in jobs:
        variables[f"S{i}"] = round(S[i].X, 4)
        variables[f"C{i}"] = round(C[i].X, 4)
        variables[f"T{i}"] = round(T[i].X, 4)
    for (i, j) in pairs:
        variables[f"x_{i}_{j}"] = round(x[i, j].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
