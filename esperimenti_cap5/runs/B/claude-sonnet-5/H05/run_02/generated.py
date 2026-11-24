import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
projects = ["A","B","C","D","E","F","G","H","I","J","K","L"]

van   = {"A":42,"B":35,"C":48,"D":31,"E":40,"F":28,
         "G":55,"H":37,"I":33,"J":50,"K":46,"L":29}

cost1 = {"A":18,"B":20,"C":25,"D":15,"E":22,"F":14,
         "G":30,"H":20,"I":17,"J":27,"K":24,"L":16}

cost2 = {"A":12,"B":18,"C":20,"D":14,"E":16,"F":12,
         "G":25,"H":18,"I":15,"J":21,"K":19,"L":13}

cost3 = {"A":10,"B":14,"C":18,"D":12,"E":15,"F":10,
         "G":22,"H":16,"I":12,"J":18,"K":17,"L":11}

personnel = {"A":4,"B":4,"C":5,"D":3,"E":4,"F":3,
             "G":6,"H":4,"I":3,"J":5,"K":5,"L":3}

risk = {"A":5,"B":4,"C":6,"D":3,"E":4,"F":2,
        "G":7,"H":5,"I":3,"J":6,"K":5,"L":3}

budget = {1:110, 2:100, 3:90}
Pmax = 28
Rmax = 32
Nmax = 8
digital = ["A","C","G","J"]
sustainable = ["E","H","K"]
s_AC = 12
s_EK = 10

# --- Modello ---
m = gp.Model("H05_portafoglio")

x = m.addVars(projects, vtype=GRB.BINARY, name="x")
y_AC = m.addVar(vtype=GRB.BINARY, name="y_AC")
y_EK = m.addVar(vtype=GRB.BINARY, name="y_EK")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(van[i]*x[i] for i in projects) + s_AC*y_AC + s_EK*y_EK,
    GRB.MAXIMIZE
)

# Budget annuali
m.addConstr(gp.quicksum(cost1[i]*x[i] for i in projects) <= budget[1], name="budget_y1")
m.addConstr(gp.quicksum(cost2[i]*x[i] for i in projects) <= budget[2], name="budget_y2")
m.addConstr(gp.quicksum(cost3[i]*x[i] for i in projects) <= budget[3], name="budget_y3")

# Personale
m.addConstr(gp.quicksum(personnel[i]*x[i] for i in projects) <= Pmax, name="personnel")

# Rischio
m.addConstr(gp.quicksum(risk[i]*x[i] for i in projects) <= Rmax, name="risk")

# Dipendenze
m.addConstr(x["G"] <= x["B"], name="G_requires_B")
m.addConstr(x["J"] <= x["E"], name="J_requires_E")
m.addConstr(x["K"] <= x["C"], name="K_requires_C")

# Incompatibilità
m.addConstr(x["D"] + x["H"] <= 1, name="incomp_DH")
m.addConstr(x["F"] + x["L"] <= 1, name="incomp_FL")

# Requisiti minimi
m.addConstr(gp.quicksum(x[i] for i in digital) >= 2, name="min_digital")
m.addConstr(gp.quicksum(x[i] for i in sustainable) >= 1, name="min_sostenibile")

# Numero massimo di progetti
m.addConstr(gp.quicksum(x[i] for i in projects) <= Nmax, name="max_progetti")

# Linearizzazione sinergie (AND logico)
m.addConstr(y_AC <= x["A"], name="syn_AC_1")
m.addConstr(y_AC <= x["C"], name="syn_AC_2")
m.addConstr(y_AC >= x["A"] + x["C"] - 1, name="syn_AC_3")

m.addConstr(y_EK <= x["E"], name="syn_EK_1")
m.addConstr(y_EK <= x["K"], name="syn_EK_2")
m.addConstr(y_EK >= x["E"] + x["K"] - 1, name="syn_EK_3")

m.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.objVal, 4)
    variables = {}
    for i in projects:
        variables[f"x_{i}"] = round(x[i].X, 4)
    variables["y_AC"] = round(y_AC.X, 4)
    variables["y_EK"] = round(y_EK.X, 4)
    result["variables"] = variables
else:
    result["status"] = str(m.status)

print("SOLUTION_JSON=" + json.dumps(result))
