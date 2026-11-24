import gurobipy as gp
from gurobipy import GRB
import json

# Dati
centers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
cost = {'A':24, 'B':20, 'C':27, 'D':22, 'E':25, 'F':19, 'G':23, 'H':21}

coverage = {
    'A': ['Z1','Z2','Z3'],
    'B': ['Z2','Z3','Z4','Z5'],
    'C': ['Z1','Z5','Z6'],
    'D': ['Z3','Z6','Z7'],
    'E': ['Z4','Z7','Z8'],
    'F': ['Z5','Z8','Z9'],
    'G': ['Z6','Z9','Z10'],
    'H': ['Z7','Z8','Z10'],
}

zones = [f"Z{i}" for i in range(1, 11)]
critical_zones = {'Z3', 'Z7'}
K = 5

# Matrice a[c,z]
a = {(c, z): (1 if z in coverage[c] else 0) for c in centers for z in zones}

# Modello
m = gp.Model("copertura_centri")
m.Params.OutputFlag = 0

x = m.addVars(centers, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
m.setObjective(gp.quicksum(cost[c] * x[c] for c in centers), GRB.MINIMIZE)

# Vincoli di copertura
for z in zones:
    req = 2 if z in critical_zones else 1
    m.addConstr(gp.quicksum(a[c, z] * x[c] for c in centers) >= req, name=f"cover_{z}")

# Vincolo massimo numero centri
m.addConstr(gp.quicksum(x[c] for c in centers) <= K, name="max_centri")

m.optimize()

status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = m.ObjVal
    for c in centers:
        result["variables"][f"x_{c}"] = x[c].X
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }
    result["status"] = status_map.get(status, str(status))

print("SOLUTION_JSON=" + json.dumps(result))
