import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
projects = ['A','B','C','D','E','F','G','H','I','J','K','L']

van   = {'A':42,'B':35,'C':48,'D':31,'E':40,'F':28,'G':55,'H':37,'I':33,'J':50,'K':46,'L':29}
cost1 = {'A':18,'B':20,'C':25,'D':15,'E':22,'F':14,'G':30,'H':20,'I':17,'J':27,'K':24,'L':16}
cost2 = {'A':12,'B':18,'C':20,'D':14,'E':16,'F':12,'G':25,'H':18,'I':15,'J':21,'K':19,'L':13}
cost3 = {'A':10,'B':14,'C':18,'D':12,'E':15,'F':10,'G':22,'H':16,'I':12,'J':18,'K':17,'L':11}
pers  = {'A':4,'B':4,'C':5,'D':3,'E':4,'F':3,'G':6,'H':4,'I':3,'J':5,'K':5,'L':3}
risk  = {'A':5,'B':4,'C':6,'D':3,'E':4,'F':2,'G':7,'H':5,'I':3,'J':6,'K':5,'L':3}

B1, B2, B3 = 110, 100, 90
PERS_MAX = 28
RISK_MAX = 32
S_AC = 12
S_EK = 10

# ---------------- Modello ----------------
m = gp.Model("H05_portafoglio_sinergie")

x = m.addVars(projects, vtype=GRB.BINARY, name="x")
y_AC = m.addVar(vtype=GRB.BINARY, name="y_AC")
y_EK = m.addVar(vtype=GRB.BINARY, name="y_EK")

# Obiettivo
m.setObjective(
    gp.quicksum(van[p] * x[p] for p in projects) + S_AC * y_AC + S_EK * y_EK,
    GRB.MAXIMIZE
)

# Budget annuali
m.addConstr(gp.quicksum(cost1[p]*x[p] for p in projects) <= B1, name="budget_anno1")
m.addConstr(gp.quicksum(cost2[p]*x[p] for p in projects) <= B2, name="budget_anno2")
m.addConstr(gp.quicksum(cost3[p]*x[p] for p in projects) <= B3, name="budget_anno3")

# Personale
m.addConstr(gp.quicksum(pers[p]*x[p] for p in projects) <= PERS_MAX, name="personale")

# Rischio
m.addConstr(gp.quicksum(risk[p]*x[p] for p in projects) <= RISK_MAX, name="rischio")

# Dipendenze logiche
m.addConstr(x['G'] <= x['B'], name="G_richiede_B")
m.addConstr(x['J'] <= x['E'], name="J_richiede_E")
m.addConstr(x['K'] <= x['C'], name="K_richiede_C")

# Incompatibilità
m.addConstr(x['D'] + x['H'] <= 1, name="incompat_DH")
m.addConstr(x['F'] + x['L'] <= 1, name="incompat_FL")

# Requisiti minimi
m.addConstr(x['A'] + x['C'] + x['G'] + x['J'] >= 2, name="min_digitali")
m.addConstr(x['E'] + x['H'] + x['K'] >= 1, name="min_sostenibile")

# Limite numero progetti
m.addConstr(gp.quicksum(x[p] for p in projects) <= 8, name="max_progetti")

# Linearizzazione sinergie
m.addConstr(y_AC <= x['A'], name="syn_AC_1")
m.addConstr(y_AC <= x['C'], name="syn_AC_2")
m.addConstr(y_AC >= x['A'] + x['C'] - 1, name="syn_AC_3")

m.addConstr(y_EK <= x['E'], name="syn_EK_1")
m.addConstr(y_EK <= x['K'], name="syn_EK_2")
m.addConstr(y_EK >= x['E'] + x['K'] - 1, name="syn_EK_3")

m.optimize()

# ---------------- Output ----------------
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status = status_map.get(m.status, str(m.status))

if m.status == GRB.OPTIMAL:
    variables = {}
    for p in projects:
        variables[f"x_{p}"] = float(round(x[p].X))
    variables["y_AC"] = float(round(y_AC.X))
    variables["y_EK"] = float(round(y_EK.X))
    objective = float(m.ObjVal)
    result = {"status": status, "objective": objective, "variables": variables}
else:
    result = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
