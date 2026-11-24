import gurobipy as gp
from gurobipy import GRB
import json

# ----- Dati -----
centers = ["A", "B", "C", "D", "E", "F", "G", "H"]

cost = {
    "A": 24, "B": 20, "C": 27, "D": 22,
    "E": 25, "F": 19, "G": 23, "H": 21
}

coverage = {
    "A": ["Z1", "Z2", "Z3"],
    "B": ["Z2", "Z3", "Z4", "Z5"],
    "C": ["Z1", "Z5", "Z6"],
    "D": ["Z3", "Z6", "Z7"],
    "E": ["Z4", "Z7", "Z8"],
    "F": ["Z5", "Z8", "Z9"],
    "G": ["Z6", "Z9", "Z10"],
    "H": ["Z7", "Z8", "Z10"]
}

zones = [f"Z{k}" for k in range(1, 11)]
critical_zones = {"Z3", "Z7"}
K = 5  # massimo numero di centri apribili

# Costruzione S_j: centri che coprono la zona j
S = {j: [i for i in centers if j in coverage[i]] for j in zones}

# ----- Modello -----
model = gp.Model("copertura_zone")
model.Params.OutputFlag = 0

x = model.addVars(centers, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[i] * x[i] for i in centers), GRB.MINIMIZE)

# Vincoli di copertura
for j in zones:
    req = 2 if j in critical_zones else 1
    model.addConstr(gp.quicksum(x[i] for i in S[j]) >= req, name=f"cover_{j}")

# Vincolo sul numero massimo di centri
model.addConstr(gp.quicksum(x[i] for i in centers) <= K, name="max_centri")

model.optimize()

# ----- Output -----
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}

if model.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = model.ObjVal
    variables = {f"x_{i}": round(x[i].X, 4) for i in centers}
    print(f"Status: {status}")
    print(f"Costo totale ottimo: {objective}")
    for i in centers:
        if x[i].X > 0.5:
            print(f"Centro aperto: {i} (costo {cost[i]})")
else:
    status = status_map.get(model.status, str(model.status))
    objective = None
    variables = {}
    print(f"Status: {status}")

result = {
    "status": status,
    "objective": objective,
    "variables": variables
}

print("SOLUTION_JSON=" + json.dumps(result))
