import json
import gurobipy as gp
from gurobipy import GRB

zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]
site = ["A", "B", "C", "D"]

fisso = {"A": 38, "B": 42, "C": 35, "D": 46}
capacita = {"A": 2, "B": 3, "C": 2, "D": 3}

costo = {
    "Z1": {"A": 8, "B": 14, "C": 11, "D": 17},
    "Z2": {"A": 10, "B": 9, "C": 13, "D": 15},
    "Z3": {"A": 12, "B": 8, "C": 14, "D": 10},
    "Z4": {"A": 15, "B": 11, "C": 9, "D": 7},
    "Z5": {"A": 9, "B": 13, "C": 8, "D": 14},
    "Z6": {"A": 14, "B": 10, "C": 7, "D": 9},
}

m = gp.Model("M01")
m.Params.OutputFlag = 0

y = m.addVars(site, vtype=GRB.BINARY, name="y")
x = m.addVars(zone, site, vtype=GRB.BINARY, name="x")

# Vincolo: esattamente due centri aperti
m.addConstr(gp.quicksum(y[j] for j in site) == 2, "due_centri")

# Vincolo: ogni zona assegnata esattamente a un sito
for i in zone:
    m.addConstr(gp.quicksum(x[i, j] for j in site) == 1, f"assegnazione_{i}")

# Vincolo: capacità dei siti
for j in site:
    m.addConstr(gp.quicksum(x[i, j] for i in zone) <= capacita[j], f"capacita_{j}")

# Vincolo: una zona puo' essere assegnata solo a un centro aperto
for i in zone:
    for j in site:
        m.addConstr(x[i, j] <= y[j], f"apertura_{i}_{j}")

# Funzione obiettivo
obiettivo = gp.quicksum(fisso[j] * y[j] for j in site) + gp.quicksum(
    costo[i][j] * x[i, j] for i in zone for j in site
)
m.setObjective(obiettivo, GRB.MINIMIZE)

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    valore = float(m.ObjVal)
    variabili = {}

    for j in site:
        variabili[f"y_{j}"] = float(y[j].X)

    for i in zone:
        for j in site:
            variabili[f"x_{i}_{j}"] = float(x[i, j].X)
else:
    status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.ITERATION_LIMIT: "ITERATION_LIMIT"
    }.get(m.status, str(m.status))
    valore = None
    variabili = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": valore,
    "variables": variabili
}, ensure_ascii=False))
