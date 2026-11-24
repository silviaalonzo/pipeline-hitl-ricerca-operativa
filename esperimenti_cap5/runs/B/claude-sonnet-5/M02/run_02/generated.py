import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
prodotti = ['A', 'B', 'C', 'D']
margine   = {'A': 42, 'B': 36, 'C': 50, 'D': 31}
setup     = {'A': 80, 'B': 65, 'C': 90, 'D': 50}
ore_macc  = {'A': 3,  'B': 2,  'C': 4,  'D': 1}
ore_lav   = {'A': 2,  'B': 3,  'C': 2,  'D': 2}
lotto_min = {'A': 4,  'B': 5,  'C': 3,  'D': 6}
dom_max   = {'A': 20, 'B': 25, 'C': 16, 'D': 30}

CAP_MACCHINA = 90
CAP_LAVORO   = 100
MIN_ARTICOLI = 2

# --- Modello ---
m = gp.Model("Piano_produzione_setup")

x = m.addVars(prodotti, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(prodotti, vtype=GRB.BINARY, name="y")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(margine[i] * x[i] for i in prodotti)
    - gp.quicksum(setup[i] * y[i] for i in prodotti),
    GRB.MAXIMIZE
)

# Vincoli di capacità
m.addConstr(gp.quicksum(ore_macc[i] * x[i] for i in prodotti) <= CAP_MACCHINA, name="ore_macchina")
m.addConstr(gp.quicksum(ore_lav[i] * x[i] for i in prodotti) <= CAP_LAVORO, name="ore_lavoro")

# Vincoli lotto minimo / domanda massima legati al setup
for i in prodotti:
    m.addConstr(x[i] >= lotto_min[i] * y[i], name=f"lotto_min_{i}")
    m.addConstr(x[i] <= dom_max[i] * y[i], name=f"dom_max_{i}")

# Almeno 2 articoli diversi
m.addConstr(gp.quicksum(y[i] for i in prodotti) >= MIN_ARTICOLI, name="min_articoli")

m.optimize()

# --- Output ---
status = m.Status
if status == GRB.OPTIMAL:
    variables = {}
    for i in prodotti:
        variables[f"x_{i}"] = float(x[i].X)
        variables[f"y_{i}"] = float(y[i].X)
    result = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": str(status),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result))
