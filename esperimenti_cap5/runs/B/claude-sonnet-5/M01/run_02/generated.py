import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
sites = ['A', 'B', 'C', 'D']
zones = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6']

fixed_cost = {'A': 38, 'B': 42, 'C': 35, 'D': 46}
capacity   = {'A': 2,  'B': 3,  'C': 2,  'D': 3}

assign_cost = {
    ('Z1','A'): 8,  ('Z1','B'): 14, ('Z1','C'): 11, ('Z1','D'): 17,
    ('Z2','A'): 10, ('Z2','B'): 9,  ('Z2','C'): 13, ('Z2','D'): 15,
    ('Z3','A'): 12, ('Z3','B'): 8,  ('Z3','C'): 14, ('Z3','D'): 10,
    ('Z4','A'): 15, ('Z4','B'): 11, ('Z4','C'): 9,  ('Z4','D'): 7,
    ('Z5','A'): 9,  ('Z5','B'): 13, ('Z5','C'): 8,  ('Z5','D'): 14,
    ('Z6','A'): 14, ('Z6','B'): 10, ('Z6','C'): 7,  ('Z6','D'): 9,
}

p = 2  # numero di centri da aprire

# --- Modello ---
model = gp.Model("Localizzazione_centri")
model.Params.OutputFlag = 0

y = model.addVars(sites, vtype=GRB.BINARY, name="y")
x = model.addVars(zones, sites, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(fixed_cost[s] * y[s] for s in sites) +
    gp.quicksum(assign_cost[z, s] * x[z, s] for z in zones for s in sites),
    GRB.MINIMIZE
)

# Vincolo: esattamente p centri aperti
model.addConstr(gp.quicksum(y[s] for s in sites) == p, name="num_centri")

# Vincolo: ogni zona assegnata ad un solo sito
for z in zones:
    model.addConstr(gp.quicksum(x[z, s] for s in sites) == 1, name=f"assign_{z}")

# Vincolo: assegnazione solo a siti aperti
for z in zones:
    for s in sites:
        model.addConstr(x[z, s] <= y[s], name=f"link_{z}_{s}")

# Vincolo di capacità
for s in sites:
    model.addConstr(gp.quicksum(x[z, s] for z in zones) <= capacity[s] * y[s],
                     name=f"cap_{s}")

model.optimize()

# --- Output ---
result = {"status": None, "objective": None, "variables": {}}

if model.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for s in sites:
        variables[f"y_{s}"] = round(y[s].X, 4)
    for z in zones:
        for s in sites:
            variables[f"x_{z}_{s}"] = round(x[z, s].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(model.status)

print("SOLUTION_JSON=" + json.dumps(result))
