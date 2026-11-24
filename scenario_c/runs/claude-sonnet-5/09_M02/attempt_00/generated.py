import gurobipy as gp
from gurobipy import GRB

# Dati
products = ["A", "B", "C", "D"]
margin   = {"A": 42, "B": 36, "C": 50, "D": 31}
setup    = {"A": 80, "B": 65, "C": 90, "D": 50}
machine  = {"A": 3,  "B": 2,  "C": 4,  "D": 1}
labor    = {"A": 2,  "B": 3,  "C": 2,  "D": 2}
lot_min  = {"A": 4,  "B": 5,  "C": 3,  "D": 6}
dem_max  = {"A": 20, "B": 25, "C": 16, "D": 30}

MAC_TOT = 90
LAV_TOT = 100
K_MIN = 2

model = gp.Model("Piano_produzione_setup")

# Variabili
x = model.addVars(products, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(products, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(margin[i] * x[i] - setup[i] * y[i] for i in products),
    GRB.MAXIMIZE
)

# Vincoli
model.addConstr(
    gp.quicksum(machine[i] * x[i] for i in products) <= MAC_TOT,
    name="capacita_macchina"
)

model.addConstr(
    gp.quicksum(labor[i] * x[i] for i in products) <= LAV_TOT,
    name="capacita_lavoro"
)

for i in products:
    model.addConstr(x[i] >= lot_min[i] * y[i], name=f"lotto_min_{i}")
    model.addConstr(x[i] <= dem_max[i] * y[i], name=f"domanda_max_{i}")

model.addConstr(
    gp.quicksum(y[i] for i in products) >= K_MIN,
    name="min_prodotti_diversi"
)

model.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status = status_map.get(model.status, str(model.status))

if model.status == GRB.OPTIMAL:
    objective = model.ObjVal
    variables = {}
    for i in products:
        variables[f"x_{i}"] = x[i].X
        variables[f"y_{i}"] = y[i].X
else:
    objective = None
    variables = {}

import json
print(f"SOLUTION_JSON={json.dumps({'status': status, 'objective': objective, 'variables': variables})}")
