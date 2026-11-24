import json
import gurobipy as gp
from gurobipy import GRB

fornitori = ["A", "B", "C", "D"]

costo = {"A": 11, "B": 10, "C": 12, "D": 9}
fisso = {"A": 80, "B": 95, "C": 60, "D": 120}
capacita = {"A": 80, "B": 100, "C": 70, "D": 90}
ordine_minimo = {"A": 20, "B": 25, "C": 15, "D": 20}
qualita = {"A": 96, "B": 90, "C": 98, "D": 88}
emissioni = {"A": 3, "B": 4, "C": 2, "D": 5}

domanda = 180
qualita_min = 92
emissioni_max = 650
min_fornitori = 2

m = gp.Model("M07")
m.setParam("OutputFlag", 0)

x = m.addVars(fornitori, name="x", vtype=GRB.INTEGER, lb=0)
y = m.addVars(fornitori, name="y", vtype=GRB.BINARY)

m.setObjective(
    gp.quicksum(costo[i] * x[i] + fisso[i] * y[i] for i in fornitori),
    GRB.MINIMIZE,
)

m.addConstr(gp.quicksum(x[i] for i in fornitori) == domanda, "domanda")
m.addConstr(gp.quicksum(y[i] for i in fornitori) >= min_fornitori, "min_fornitori")

for i in fornitori:
    m.addConstr(x[i] >= ordine_minimo[i] * y[i], f"ordine_min_{i}")
    m.addConstr(x[i] <= capacita[i] * y[i], f"capacita_{i}")

m.addConstr(
    gp.quicksum(qualita[i] * x[i] for i in fornitori) >= qualita_min * domanda,
    "qualita_media",
)
m.addConstr(
    gp.quicksum(emissioni[i] * x[i] for i in fornitori) <= emissioni_max,
    "emissioni_totali",
)

m.optimize()

if m.Status == GRB.OPTIMAL:
    variables = {}
    for i in fornitori:
        variables[f"x_{i}"] = x[i].X
        variables[f"y_{i}"] = y[i].X
    solution = {"status": "OPTIMAL", "objective": m.ObjVal, "variables": variables}
else:
    solution = {"status": str(m.Status), "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(solution))
