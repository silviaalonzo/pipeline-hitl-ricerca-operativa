import gurobipy as gp
from gurobipy import GRB
import json
import itertools

# Dati
jobs = [1, 2, 3, 4, 5, 6, 7]
p = {1: 5, 2: 7, 3: 4, 4: 6, 5: 3, 6: 8, 7: 5}
r = {1: 0, 2: 0, 3: 2, 4: 3, 5: 5, 6: 0, 7: 6}
d = {1: 9, 2: 17, 3: 12, 4: 22, 5: 15, 6: 28, 7: 25}
w = {1: 4, 2: 3, 3: 5, 4: 2, 5: 6, 6: 2, 7: 4}

M = 50  # Big-M: somma durate (38) + max release date (6) = 44, arrotondato per sicurezza

pairs = list(itertools.combinations(jobs, 2))

model = gp.Model("H06_sequenziamento")
model.Params.OutputFlag = 0

# Variabili
S = model.addVars(jobs, lb=0.0, name="S")
C = model.addVars(jobs, lb=0.0, name="C")
T = model.addVars(jobs, lb=0.0, name="T")
x = model.addVars(pairs, vtype=GRB.BINARY, name="x")

# Vincoli di completamento
for j in jobs:
    model.addConstr(C[j] == S[j] + p[j], name=f"comp_{j}")

# Disponibilita'
for j in jobs:
    model.addConstr(S[j] >= r[j], name=f"rel_{j}")

# Ritardo
for j in jobs:
    model.addConstr(T[j] >= C[j] - d[j], name=f"tard_{j}")

# Non sovrapposizione (disgiuntiva) con Big-M
for (i, j) in pairs:
    model.addConstr(S[j] >= C[i] - M * (1 - x[i, j]), name=f"seq1_{i}_{j}")
    model.addConstr(S[i] >= C[j] - M * x[i, j], name=f"seq2_{i}_{j}")

# Precedenze specifiche
model.addConstr(C[1] <= S[2], name="prec_J1_J2")
model.addConstr(C[3] <= S[5], name="prec_J3_J5")

# Obiettivo
model.setObjective(gp.quicksum(w[j] * T[j] for j in jobs), GRB.MINIMIZE)

model.optimize()

variables = {}
status_str = None
obj_val = None

if model.Status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    obj_val = model.ObjVal
    for j in jobs:
        variables[f"S_{j}"] = round(S[j].X, 4)
        variables[f"C_{j}"] = round(C[j].X, 4)
        variables[f"T_{j}"] = round(T[j].X, 4)
    for (i, j) in pairs:
        variables[f"x_{i}_{j}"] = round(x[i, j].X, 4)
else:
    status_str = str(model.Status)

result = {
    "status": status_str,
    "objective": obj_val,
    "variables": variables if status_str == "OPTIMAL" else {}
}

print("SOLUTION_JSON=" + json.dumps(result))
