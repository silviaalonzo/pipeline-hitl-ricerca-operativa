import gurobipy as gp
from gurobipy import GRB
import json

prodotti = ["A", "B", "C", "D"]

margine = {"A": 42, "B": 36, "C": 50, "D": 31}
setup = {"A": 80, "B": 65, "C": 90, "D": 50}
ore_macchina = {"A": 3, "B": 2, "C": 4, "D": 1}
ore_lavoro = {"A": 2, "B": 3, "C": 2, "D": 2}
lotto_min = {"A": 4, "B": 5, "C": 3, "D": 6}
domanda_max = {"A": 20, "B": 25, "C": 16, "D": 30}

R_M = 90
R_L = 100

modello = gp.Model("Piano_produzione")
modello.setParam("OutputFlag", 0)

x = modello.addVars(prodotti, vtype=GRB.INTEGER, lb=0, name="x")
y = modello.addVars(prodotti, vtype=GRB.BINARY, name="y")

modello.setObjective(
    gp.quicksum(margine[i] * x[i] - setup[i] * y[i] for i in prodotti),
    GRB.MAXIMIZE
)

modello.addConstrs(
    (x[i] <= domanda_max[i] * y[i] for i in prodotti),
    name="max_domanda"
)

modello.addConstrs(
    (x[i] >= lotto_min[i] * y[i] for i in prodotti),
    name="lotto_minimo"
)

modello.addConstr(
    gp.quicksum(ore_macchina[i] * x[i] for i in prodotti) <= R_M,
    name="capacita_macchine"
)

modello.addConstr(
    gp.quicksum(ore_lavoro[i] * x[i] for i in prodotti) <= R_L,
    name="capacita_lavoro"
)

modello.addConstr(
    gp.quicksum(y[i] for i in prodotti) >= 2,
    name="almeno_due_articoli"
)

modello.optimize()

if modello.status == GRB.OPTIMAL:
    variabili = {}
    for i in prodotti:
        variabili[f"x_{i}"] = x[i].X
        variabili[f"y_{i}"] = y[i].X

    soluzione = {
        "status": "OPTIMAL",
        "objective": modello.ObjVal,
        "variables": variabili
    }
else:
    soluzione = {
        "status": "NOT_OPTIMAL",
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(soluzione))
