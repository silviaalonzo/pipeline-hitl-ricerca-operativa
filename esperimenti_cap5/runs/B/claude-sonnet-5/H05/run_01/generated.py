import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
projects = ["A","B","C","D","E","F","G","H","I","J","K","L"]

van = {"A":42,"B":35,"C":48,"D":31,"E":40,"F":28,
       "G":55,"H":37,"I":33,"J":50,"K":46,"L":29}

cost = {
    "A":(18,12,10), "B":(20,18,14), "C":(25,20,18), "D":(15,14,12),
    "E":(22,16,15), "F":(14,12,10), "G":(30,25,22), "H":(20,18,16),
    "I":(17,15,12), "J":(27,21,18), "K":(24,19,17), "L":(16,13,11)
}

personale = {"A":4,"B":4,"C":5,"D":3,"E":4,"F":3,
             "G":6,"H":4,"I":3,"J":5,"K":5,"L":3}

rischio = {"A":5,"B":4,"C":6,"D":3,"E":4,"F":2,
           "G":7,"H":5,"I":3,"J":6,"K":5,"L":3}

budget = [110, 100, 90]
PERS_MAX = 28
RISK_MAX = 32
SYN_AC = 12
SYN_EK = 10

# --- Modello ---
m = gp.Model("H05_portafoglio")

x = m.addVars(projects, vtype=GRB.BINARY, name="x")
y_AC = m.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name="y_AC")
y_EK = m.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name="y_EK")

# Obiettivo
m.setObjective(
    gp.quicksum(van[p]*x[p] for p in projects) + SYN_AC*y_AC + SYN_EK*y_EK,
    GRB.MAXIMIZE
)

# Budget annuali
for t in range(3):
    m.addConstr(gp.quicksum(cost[p][t]*x[p] for p in projects) <= budget[t],
                name=f"budget_anno_{t+1}")

# Personale
m.addConstr(gp.quicksum(personale[p]*x[p] for p in projects) <= PERS_MAX, name="personale")

# Rischio
m.addConstr(gp.quicksum(rischio[p]*x[p] for p in projects) <= RISK_MAX, name="rischio")

# Precedenze
m.addConstr(x["G"] <= x["B"], name="G_richiede_B")
m.addConstr(x["J"] <= x["E"], name="J_richiede_E")
m.addConstr(x["K"] <= x["C"], name="K_richiede_C")

# Incompatibilità
m.addConstr(x["D"] + x["H"] <= 1, name="incompat_DH")
m.addConstr(x["F"] + x["L"] <= 1, name="incompat_FL")

# Requisiti minimi
m.addConstr(x["A"]+x["C"]+x["G"]+x["J"] >= 2, name="min_digitali")
m.addConstr(x["E"]+x["H"]+x["K"] >= 1, name="min_sostenibili")

# Numero massimo progetti
m.addConstr(gp.quicksum(x[p] for p in projects) <= 8, name="max_progetti")

# Sinergie (linearizzazione AND)
m.addConstr(y_AC <= x["A"], name="syn_AC_1")
m.addConstr(y_AC <= x["C"], name="syn_AC_2")
m.addConstr(y_EK <= x["E"], name="syn_EK_1")
m.addConstr(y_EK <= x["K"], name="syn_EK_2")

m.optimize()

# --- Output ---
if m.Status == GRB.OPTIMAL:
    variables = {}
    for p in projects:
        variables[f"x_{p}"] = round(x[p].X, 4)
    variables["y_AC"] = round(y_AC.X, 4)
    variables["y_EK"] = round(y_EK.X, 4)
    result = {
        "status": "OPTIMAL",
        "objective": round(m.ObjVal, 4),
        "variables": variables
    }
else:
    result = {
        "status": str(m.Status),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result))
