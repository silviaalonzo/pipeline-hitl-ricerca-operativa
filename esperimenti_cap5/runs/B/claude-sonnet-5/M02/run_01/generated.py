import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
products = ['A', 'B', 'C', 'D']

margin = {'A': 42, 'B': 36, 'C': 50, 'D': 31}
setup  = {'A': 80, 'B': 65, 'C': 90, 'D': 50}
mach   = {'A': 3,  'B': 2,  'C': 4,  'D': 1}
labor  = {'A': 2,  'B': 3,  'C': 2,  'D': 2}
lmin   = {'A': 4,  'B': 5,  'C': 3,  'D': 6}
dmax   = {'A': 20, 'B': 25, 'C': 16, 'D': 30}

MACH_CAP = 90
LABOR_CAP = 100
MIN_PRODUCTS = 2

# --- Modello ---
model = gp.Model("Piano_Produzione_Setup")

x = model.addVars(products, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(products, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(margin[i]*x[i] - setup[i]*y[i] for i in products),
    GRB.MAXIMIZE
)

# Vincoli di capacità
model.addConstr(gp.quicksum(mach[i]*x[i] for i in products) <= MACH_CAP, name="mach_cap")
model.addConstr(gp.quicksum(labor[i]*x[i] for i in products) <= LABOR_CAP, name="labor_cap")

# Vincoli lotto minimo / domanda massima (link con y)
for i in products:
    model.addConstr(x[i] >= lmin[i]*y[i], name=f"lotto_min_{i}")
    model.addConstr(x[i] <= dmax[i]*y[i], name=f"dom_max_{i}")

# Almeno due prodotti diversi
model.addConstr(gp.quicksum(y[i] for i in products) >= MIN_PRODUCTS, name="min_prodotti")

model.optimize()

# --- Output ---
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status = status_map.get(model.status, str(model.status))

if model.status == GRB.OPTIMAL:
    variables = {}
    for i in products:
        variables[f"x_{i}"] = round(x[i].X, 4)
    for i in products:
        variables[f"y_{i}"] = round(y[i].X, 4)
    objective = round(model.ObjVal, 4)

    print("=== Risultati ===")
    print(f"Stato solver: {status}")
    print(f"Margine netto totale: {objective}")
    for i in products:
        if x[i].X > 1e-6:
            print(f"Prodotto {i}: quantità = {x[i].X:.0f}, setup attivo = {int(round(y[i].X))}")

    result = {"status": status, "objective": objective, "variables": variables}
else:
    result = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
