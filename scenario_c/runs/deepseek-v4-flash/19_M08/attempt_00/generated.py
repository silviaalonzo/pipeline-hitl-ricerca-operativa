import gurobipy as gp
import json

zone = list(range(1, 11))
centri = ["A", "B", "C", "D", "E", "F", "G", "H"]

costi = {
    "A": 24, "B": 20, "C": 27, "D": 22,
    "E": 25, "F": 19, "G": 23, "H": 21
}

copertura = {
    1: ["A", "C"],
    2: ["A", "B"],
    3: ["A", "B", "D"],
    4: ["B", "E"],
    5: ["B", "C", "F"],
    6: ["C", "D", "G"],
    7: ["D", "E", "H"],
    8: ["E", "F", "H"],
    9: ["F", "G"],
    10: ["G", "H"]
}

richiesta = {i: 2 if i in (3, 7) else 1 for i in zone}

m = gp.Model("copertura_centri")

x = {j: m.addVar(vtype=gp.GRB.BINARY, name=f"x_{j}") for j in centri}

m.setObjective(gp.quicksum(costi[j] * x[j] for j in centri), gp.GRB.MINIMIZE)

for i in zone:
    m.addConstr(
        gp.quicksum(x[j] for j in copertura[i]) >= richiesta[i],
        name=f"copertura_Z{i}"
    )

m.addConstr(gp.quicksum(x[j] for j in centri) <= 5, name="limite_centri")

m.optimize()

if m.status == gp.GRB.OPTIMAL:
    sol = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": {v.VarName: v.X for v in m.getVars()}
    }
else:
    sol = {
        "status": m.status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(sol))
