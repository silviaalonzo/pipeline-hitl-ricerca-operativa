import itertools
import json
from gurobipy import Model, GRB, quicksum

# ---------------- Dati ----------------
jobs = [1, 2, 3, 4, 5, 6, 7]

p = {1: 5, 2: 7, 3: 4, 4: 6, 5: 3, 6: 8, 7: 5}
r = {1: 0, 2: 0, 3: 2, 4: 3, 5: 5, 6: 0, 7: 6}
d = {1: 9, 2: 17, 3: 12, 4: 22, 5: 15, 6: 28, 7: 25}
w = {1: 4, 2: 3, 3: 5, 4: 2, 5: 6, 6: 2, 7: 4}

M = sum(p.values()) + max(r.values()) + 1  # big-M giustificato

pairs = list(itertools.combinations(jobs, 2))

# ---------------- Modello ----------------
m = Model("H06_weighted_tardiness")

S = m.addVars(jobs, lb=0.0, name="S")
C = m.addVars(jobs, lb=0.0, name="C")
T = m.addVars(jobs, lb=0.0, name="T")
x = m.addVars(pairs, vtype=GRB.BINARY, name="x")

# Precedenze fissate: J1 prima di J2, J3 prima di J5
x[(1, 2)].lb = 1
x[(1, 2)].ub = 1
x[(3, 5)].lb = 1
x[(3, 5)].ub = 1

# Completamento
for j in jobs:
    m.addConstr(C[j] == S[j] + p[j], name=f"comp_{j}")

# Rilascio
for j in jobs:
    m.addConstr(S[j] >= r[j], name=f"rel_{j}")

# Tardiness
for j in jobs:
    m.addConstr(T[j] >= C[j] - d[j], name=f"tard_{j}")

# Non sovrapposizione (disgiuntiva) per ogni coppia
for (i, j) in pairs:
    m.addConstr(S[j] >= C[i] - M * (1 - x[(i, j)]), name=f"seq1_{i}_{j}")
    m.addConstr(S[i] >= C[j] - M * x[(i, j)], name=f"seq2_{i}_{j}")

# Obiettivo
m.setObjective(quicksum(w[j] * T[j] for j in jobs), GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for j in jobs:
        variables[f"S_{j}"] = round(S[j].X, 4)
        variables[f"C_{j}"] = round(C[j].X, 4)
        variables[f"T_{j}"] = round(T[j].X, 4)
    for (i, j) in pairs:
        variables[f"x_{i}_{j}"] = round(x[(i, j)].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(m.status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
