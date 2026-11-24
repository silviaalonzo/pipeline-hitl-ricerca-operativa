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
    "H": 21
}

coperture = {
    "A": ["Z1", "Z2", "Z3"],
    "B": ["Z2", "Z3", "Z4", "Z5"],
    "C": ["Z1", "Z5", "Z6"],
    "D": ["Z3", "Z6", "Z7"],
    "E": ["Z4", "Z7", "Z8"],
    "F": ["Z5", "Z8", "Z9"],
    "G": ["Z6", "Z9", "Z10"],
    "H": ["Z7", "Z8", "Z10"]
}

zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10"]
critiche = {"Z3", "Z7"}

m = gp.Model("M08")
m.Params.OutputFlag = 0

x = {}
for i in centri:
    x[i] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}")

m.setObjective(
    gp.quicksum(costo[i] * x[i] for i in centri),
    GRB.MINIMIZE
)

for z in zone:
    richiesta = 2 if z in critiche else 1
    m.addConstr(
        gp.quicksum(x[i] for i in centri if z in coperture[i]) >= richiesta,
        name=f"copertura_{z}"
    )

m.addConstr(
    gp.quicksum(x[i] for i in centri) <= 5,
    name="max_centri"
)

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD"
}

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = m.ObjVal
    variables = {f"x_{i}": x[i].X for i in centri}
else:
    status = status_map.get(m.Status, str(m.Status))
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables
}, separators=(",", ":")))
