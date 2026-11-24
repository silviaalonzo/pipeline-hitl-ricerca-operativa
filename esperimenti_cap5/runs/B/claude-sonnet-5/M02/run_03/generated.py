import gurobipy as gp
from gurobipy import GRB
import json

# Dati
products = ['A', 'B', 'C', 'D']

margin   = {'A': 42, 'B': 36, 'C': 50, 'D': 31}
setup    = {'A': 80, 'B': 65, 'C': 90, 'D': 50}
machine  = {'A': 3,  'B': 2,  'C': 4,  'D': 1}
labor    = {'A': 2,  'B': 3,  'C': 2,  'D': 2}
minlot   = {'A': 4,  'B': 5,  'C': 3,  'D': 6}
maxdem   = {'A': 20, 'B': 25, 'C': 16, 'D': 30}

H = 90   # ore macchina disponibili
W = 100  # ore lavoro disponibili
K = 2    # numero minimo di articoli diversi

# Modello
model = gp.Model("Piano_produzione_setup")

x = model.addVars(products, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(products, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(margin[i] * x[i] - setup[i] * y[i] for i in products),
    GRB.MAXIMIZE
)

# Vincoli risorse
model.addConstr(gp.quicksum(machine[i] * x[i] for i in products) <= H, name="ore_macchina")
model.addConstr(gp.quicksum(labor[i] * x[i] for i in products) <= W, name="ore_lavoro")

# Vincoli lotto minimo / domanda massima legati al setup
for i in products:
    model.addConstr(x[i] >= minlot[i] * y[i], name=f"lotto_min_{i}")
    model.addConstr(x[i] <= maxdem[i] * y[i], name=f"domanda_max_{i}")

# Numero minimo di articoli diversi
model.addConstr(gp.quicksum(y[i] for i in products) >= K, name="min_articoli")

model.optimize()

# Estrazione risultati
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status = status_map.get(model.status, str(model.status))

result = {"status": status, "objective": None, "variables": {}}

if model.status == GRB.OPTIMAL:
    result["objective"] = round(model.objVal, 4)
    variables = {}
    for i in products:
        variables[f"x_{i}"] = round(x[i].X, 4)
    for i in products:
        variables[f"y_{i}"] = round(y[i].X, 4)
    result["variables"] = variables

    # Stampa leggibile dello stato
    print(f"Stato solver: {status}")
    print(f"Valore ottimo (margine netto): {result['objective']}")
    print("Decisioni non nulle:")
    for k, v in variables.items():
        if v != 0:
            print(f"  {k} = {v}")

print("SOLUTION_JSON=" + json.dumps(result))
