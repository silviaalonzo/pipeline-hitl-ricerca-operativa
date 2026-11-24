import gurobipy as gp
from gurobipy import GRB
import json

centri = ["A", "B", "C", "D", "E", "F", "G", "H"]

costo = {
    "A": 24,
    "B": 20,
    "C": 27,
    "D": 22,
    "E": 25,
    "F": 19,
    "G": 23,
    "H": 21,
}

zone_coperte = {
    "A": [1, 2, 3],
    "B": [2, 3, 4, 5],
    "C": [1, 5, 6],
    "D": [3, 6, 7],
    "E": [4, 7, 8],
    "F": [5, 8, 9],
    "G": [6, 9, 10],
    "H": [7, 8, 10],
}

zone = list(range(1, 11))
critiche = {3, 7}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

modello = gp.Model("copertura_zone", env=env)

x = {}
for c in centri:
    x[c] = modello.addVar(vtype=GRB.BINARY, name=f"x_{c}")

for z in zone:
    domanda = 2 if z in critiche else 1
    modello.addConstr(
        gp.quicksum(x[c] for c in centri if z in zone_coperte[c]) >= domanda,
        name=f"copertura_Z{z}"
    )

modello.addConstr(gp.quicksum(x[c] for c in centri) <= 5, name="max_centri")

modello.setObjective(gp.quicksum(costo[c] * x[c] for c in centri), GRB.MINIMIZE)

modello.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
}

stato = status_map.get(modello.Status, str(modello.Status))

if modello.Status == GRB.OPTIMAL:
    obiettivo = modello.ObjVal
    variabili = {v.VarName: v.X for v in modello.getVars()}
else:
    obiettivo = None
    variabili = {}

print("SOLUTION_JSON=" + json.dumps(
    {
        "status": stato,
        "objective": obiettivo,
        "variables": variabili
    },
    separators=(",", ":")
))
