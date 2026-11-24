import gurobipy as gp
from gurobipy import GRB
import json

zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]
siti = ["A", "B", "C", "D"]

fisso = {"A": 38, "B": 42, "C": 35, "D": 46}
capacita = {"A": 2, "B": 3, "C": 2, "D": 3}

costo = {
    ("Z1", "A"): 8, ("Z1", "B"): 14, ("Z1", "C"): 11, ("Z1", "D"): 17,
    ("Z2", "A"): 10, ("Z2", "B"): 9, ("Z2", "C"): 13, ("Z2", "D"): 15,
    ("Z3", "A"): 12, ("Z3", "B"): 8, ("Z3", "C"): 14, ("Z3", "D"): 10,
    ("Z4", "A"): 15, ("Z4", "B"): 11, ("Z4", "C"): 9, ("Z4", "D"): 7,
    ("Z5", "A"): 9, ("Z5", "B"): 13, ("Z5", "C"): 8, ("Z5", "D"): 14,
    ("Z6", "A"): 14, ("Z6", "B"): 10, ("Z6", "C"): 7, ("Z6", "D"): 9,
}

m = gp.Model("M01")
m.setParam("OutputFlag", 0)

y = {}
for j in siti:
    y[j] = m.addVar(vtype=GRB.BINARY, name=f"y_{j}")

x = {}
for i in zone:
    for j in siti:
        x[i, j] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

# Ogni zona deve essere assegnata esattamente a un centro
for i in zone:
    m.addConstr(gp.quicksum(x[i, j] for j in siti) == 1, name=f"assegnazione_{i}")

# Vincoli di capacità
for j in siti:
    m.addConstr(gp.quicksum(x[i, j] for i in zone) <= capacita[j] * y[j], name=f"capacita_{j}")

# Esattamente due centri aperti
m.addConstr(gp.quicksum(y[j] for j in siti) == 2, name="esattamente_due")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fisso[j] * y[j] for j in siti)
    + gp.quicksum(costo[i, j] * x[i, j] for i in zone for j in siti),
    GRB.MINIMIZE
)

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}
status = status_map.get(m.status, "UNKNOWN")

if m.status == GRB.OPTIMAL:
    result = {
        "status": status,
        "objective": float(m.ObjVal),
        "variables": {v.varName: v.X for v in m.getVars()},
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
