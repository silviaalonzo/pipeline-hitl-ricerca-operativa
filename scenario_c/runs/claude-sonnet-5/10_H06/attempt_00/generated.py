import gurobipy as gp
from gurobipy import GRB
import itertools

# Dati
jobs = [1,2,3,4,5,6,7]
p = {1:5, 2:7, 3:4, 4:6, 5:3, 6:8, 7:5}
r = {1:0, 2:0, 3:2, 4:3, 5:5, 6:0, 7:6}
d = {1:9, 2:17, 3:12, 4:22, 5:15, 6:28, 7:25}
w = {1:4, 2:3, 3:5, 4:2, 5:6, 6:2, 7:4}

M = sum(p.values()) + max(r.values())  # big-M = 44

model = gp.Model("H06_scheduling")
model.Params.OutputFlag = 0

# Variabili
S = model.addVars(jobs, lb=0.0, vtype=GRB.CONTINUOUS, name="S")
T = model.addVars(jobs, lb=0.0, vtype=GRB.CONTINUOUS, name="T")
pairs = list(itertools.combinations(jobs, 2))
x = model.addVars(pairs, vtype=GRB.BINARY, name="x")

# Vincoli di disponibilità
for i in jobs:
    model.addConstr(S[i] >= r[i], name=f"release_{i}")

# Vincoli di ritardo
for i in jobs:
    model.addConstr(T[i] >= S[i] + p[i] - d[i], name=f"tardiness_{i}")

# Vincoli disgiuntivi di non sovrapposizione
for (i, j) in pairs:
    model.addConstr(S[i] + p[i] <= S[j] + M * (1 - x[i, j]), name=f"disj1_{i}_{j}")
    model.addConstr(S[j] + p[j] <= S[i] + M * x[i, j], name=f"disj2_{i}_{j}")

# Vincoli di precedenza
model.addConstr(S[1] + p[1] <= S[2], name="prec_1_2")
model.addConstr(S[3] + p[3] <= S[5], name="prec_3_5")

# Obiettivo
model.setObjective(gp.quicksum(w[i] * T[i] for i in jobs), GRB.MINIMIZE)

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for i in jobs:
        variables[f"S_{i}"] = round(S[i].X, 4)
        variables[f"T_{i}"] = round(T[i].X, 4)
    for (i, j) in pairs:
        variables[f"x_{i}_{j}"] = round(x[i, j].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(status)

import json
print("SOLUTION_JSON=" + json.dumps(result))
