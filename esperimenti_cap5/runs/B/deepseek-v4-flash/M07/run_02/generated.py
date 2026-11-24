from gurobipy import Model, GRB, quicksum
import json

fornitori = ["A", "B", "C", "D"]

costo = {"A": 11, "B": 10, "C": 12, "D": 9}
fisso = {"A": 80, "B": 95, "C": 60, "D": 120}
capacita = {"A": 80, "B": 100, "C": 70, "D": 90}
minimo = {"A": 20, "B": 25, "C": 15, "D": 20}
qualita = {"A": 96, "B": 90, "C": 98, "D": 88}
emissioni = {"A": 3, "B": 4, "C": 2, "D": 5}

domanda = 180
qualita_minima = 92
emissioni_max = 650
fornitori_minimi = 2

m = Model("M07")
m.Params.OutputFlag = 0

x = {}
y = {}

for i in fornitori:
    x[i] = m.addVar(vtype=GRB.INTEGER, lb=0, ub=capacita[i], name=f"x_{i}")
    y[i] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}")

m.addConstr(quicksum(x[i] for i in fornitori) == domanda, "domanda")
m.addConstr(quicksum(y[i] for i in fornitori) >= fornitori_minimi, "fornitori_minimi")
m.addConstr(quicksum(qualita[i] * x[i] for i in fornitori) >= qualita_minima * domanda, "qualita")
m.addConstr(quicksum(emissioni[i] * x[i] for i in fornitori) <= emissioni_max, "emissioni")

for i in fornitori:
    m.addConstr(x[i] >= minimo[i] * y[i], f"min_{i}")
    m.addConstr(x[i] <= capacita[i] * y[i], f"max_{i}")

m.setObjective(
    quicksum(costo[i] * x[i] + fisso[i] * y[i] for i in fornitori),
    GRB.MINIMIZE
)

m.optimize()

if m.Status == GRB.OPTIMAL:
    variabili = {}
    for i in fornitori:
        variabili[f"x_{i}"] = x[i].X
    for i in fornitori:
        variabili[f"y_{i}"] = y[i].X

    payload = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variabili
    }
else:
    payload = {
        "status": f"STATUS_{m.Status}",
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
