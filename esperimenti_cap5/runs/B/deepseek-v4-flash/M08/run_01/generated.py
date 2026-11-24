import gurobipy as gp
from gurobipy import GRB
import json

centri = ["A", "B", "C", "D", "E", "F", "G", "H"]
zone = list(range(1, 11))

costi = {
    "A": 24, "B": 20, "C": 27, "D": 22,
    "E": 25, "F": 19, "G": 23, "H": 21,
}

coperture = {
    "A": {1, 2, 3},
    "B": {2, 3, 4, 5},
    "C": {1, 5, 6},
    "D": {3, 6, 7},
    "E": {4, 7, 8},
    "F": {5, 8, 9},
    "G": {6, 9, 10},
    "H": {7, 8, 10},
}

richieste = {i: 2 if i in {3, 7} else 1 for i in zone}
max_centri = 5

m = gp.Model("M08_copertura")
m.setParam("OutputFlag", 0)

x = {j: m.addVar(vtype=GRB.BINARY, name=f"x_{j}") for j in centri}
m.update()

m.setObjective(
    gp.quicksum(costi[j] * x[j] for j in centri),
    GRB.MINIMIZE
)

for i in zone:
    m.addConstr(
        gp.quicksum(x[j] for j in centri if i in coperture[j]) >= richieste[i],
        name=f"copertura_Z{i}"
    )

m.addConstr(
    gp.quicksum(x[j] for j in centri) <= max_centri,
    name="max_centri"
)

m.optimize()

status = m.getAttr("Status")

if status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": float(m.getAttr("ObjVal")),
        "variables": {f"x_{j}": float(x[j].x) for j in centri},
    }
else:
    status_label = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
    }.get(status, str(status))

    result = {
        "status": status_label,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
