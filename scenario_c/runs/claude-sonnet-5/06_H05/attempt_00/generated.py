import gurobipy as gp
from gurobipy import GRB

# --- Dati ---
projects = ["A","B","C","D","E","F","G","H","I","J","K","L"]

van  = {"A":42,"B":35,"C":48,"D":31,"E":40,"F":28,
        "G":55,"H":37,"I":33,"J":50,"K":46,"L":29}
c1   = {"A":18,"B":20,"C":25,"D":15,"E":22,"F":14,
        "G":30,"H":20,"I":17,"J":27,"K":24,"L":16}
c2   = {"A":12,"B":18,"C":20,"D":14,"E":16,"F":12,
        "G":25,"H":18,"I":15,"J":21,"K":19,"L":13}
c3   = {"A":10,"B":14,"C":18,"D":12,"E":15,"F":10,
        "G":22,"H":16,"I":12,"J":18,"K":17,"L":11}
pers = {"A":4,"B":4,"C":5,"D":3,"E":4,"F":3,
        "G":6,"H":4,"I":3,"J":5,"K":5,"L":3}
risk = {"A":5,"B":4,"C":6,"D":3,"E":4,"F":2,
        "G":7,"H":5,"I":3,"J":6,"K":5,"L":3}

B1, B2, B3 = 110, 100, 90
PMAX = 28
RMAX = 32
SYN_AC = 12
SYN_EK = 10

model = gp.Model("portafoglio_pluriennale")

# --- Variabili ---
x = model.addVars(projects, vtype=GRB.BINARY, name="x")
y_AC = model.addVar(vtype=GRB.BINARY, name="y_AC")
y_EK = model.addVar(vtype=GRB.BINARY, name="y_EK")

# --- Obiettivo ---
model.setObjective(
    gp.quicksum(van[p] * x[p] for p in projects) + SYN_AC * y_AC + SYN_EK * y_EK,
    GRB.MAXIMIZE
)

# --- Vincoli di budget ---
model.addConstr(gp.quicksum(c1[p] * x[p] for p in projects) <= B1, name="budget_anno1")
model.addConstr(gp.quicksum(c2[p] * x[p] for p in projects) <= B2, name="budget_anno2")
model.addConstr(gp.quicksum(c3[p] * x[p] for p in projects) <= B3, name="budget_anno3")

# --- Personale ---
model.addConstr(gp.quicksum(pers[p] * x[p] for p in projects) <= PMAX, name="personale")

# --- Rischio ---
model.addConstr(gp.quicksum(risk[p] * x[p] for p in projects) <= RMAX, name="rischio")

# --- Precedenze ---
model.addConstr(x["G"] <= x["B"], name="G_requires_B")
model.addConstr(x["J"] <= x["E"], name="J_requires_E")
model.addConstr(x["K"] <= x["C"], name="K_requires_C")

# --- Incompatibilità ---
model.addConstr(x["D"] + x["H"] <= 1, name="incompat_D_H")
model.addConstr(x["F"] + x["L"] <= 1, name="incompat_F_L")

# --- Requisiti di composizione ---
model.addConstr(x["A"] + x["C"] + x["G"] + x["J"] >= 2, name="min_digitali")
model.addConstr(x["E"] + x["H"] + x["K"] >= 1, name="min_sostenibili")

# --- Numero massimo di progetti ---
model.addConstr(gp.quicksum(x[p] for p in projects) <= 8, name="max_progetti")

# --- Linearizzazione sinergie ---
model.addConstr(y_AC <= x["A"], name="syn_AC_1")
model.addConstr(y_AC <= x["C"], name="syn_AC_2")
model.addConstr(y_AC >= x["A"] + x["C"] - 1, name="syn_AC_3")

model.addConstr(y_EK <= x["E"], name="syn_EK_1")
model.addConstr(y_EK <= x["K"], name="syn_EK_2")
model.addConstr(y_EK >= x["E"] + x["K"] - 1, name="syn_EK_3")

model.optimize()

status = model.Status
if status == GRB.OPTIMAL:
    obj_val = model.ObjVal
    variables = {}
    for p in projects:
        variables[f"x_{p}"] = x[p].X
    variables["y_AC"] = y_AC.X
    variables["y_EK"] = y_EK.X
    sol = {"status": "OPTIMAL", "objective": obj_val, "variables": variables}
else:
    sol = {"status": model.Status, "objective": None, "variables": {}}

import json
print("SOLUTION_JSON=" + json.dumps(sol))
