import json
import gurobipy as gp
from gurobipy import GRB

siti = ["A", "B", "C", "D"]
zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]

f = {"A": 38, "B": 42, "C": 35, "D": 46}
q = {"A": 2, "B": 3, "C": 2, "D": 3}
c = {
    ("A", "Z1"): 8, ("A", "Z2"): 10, ("A", "Z3"): 12,
    ("A", "Z4"): 15, ("A", "Z5"): 9, ("A", "Z6"): 14,
    ("B", "Z1"): 14, ("B", "Z2"): 9, ("B", "Z3"): 8,
    ("B", "Z4"): 11, ("B", "Z5"): 13, ("B", "Z6"): 10,
    ("C", "Z1"): 11, ("C", "Z2"): 13, ("C", "Z3"): 14,
    ("C", "Z4"): 9, ("C", "Z5"): 8, ("C", "Z6"): 7,
    ("D", "Z1"): 17, ("D", "Z2"): 15, ("D", "Z3"): 10,
    ("D", "Z4"): 7, ("D", "Z5"): 14, ("D", "Z6"): 9,
}

m = gp.Model("M01_localizzazione")
m.Params.OutputFlag = 0

y = {i: m.addVar(vtype=GRB.BINARY, name=f"y_{i}") for i in siti}
x = {}
for i in siti:
    for j in zone:
        x[i, j] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

m.setObjective(
    gp.quicksum(f[i] * y[i] for i in siti)
    + gp.quicksum(c[i, j] * x[i, j] for i in siti for j in zone),
    GRB.MINIMIZE,
)

m.addConstr(gp.quicksum(y[i] for i in siti) == 2, "esattamente_due")
for j in zone:
    m.addConstr(gp.quicksum(x[i, j] for i in siti) == 1, f"assegnazione_{j}")
for i in siti:
    m.addConstr(gp.quicksum(x[i, j] for j in zone) <= q[i] * y[i], f"capacita_{i}")

m.optimize()

if m.Status == GRB.OPTIMAL:
    stato = "OPTIMAL"
    obiettivo = float(m.ObjVal)
    variabili = {v.VarName: v.X for v in m.getVars()}
else:
    if m.Status == GRB.INFEASIBLE:
        stato = "INFEASIBLE"
    elif m.Status == GRB.UNBOUNDED:
        stato = "UNBOUNDED"
    elif m.Status == GRB.INF_OR_UNBD:
        stato = "INF_OR_UNBD"
    else:
        stato = str(m.Status)
    obiettivo = None
    variabili = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": stato, "objective": obiettivo, "variables": variabili},
    separators=(",", ":")
))
