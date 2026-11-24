import gurobipy as gp
from gurobipy import GRB

# --- Dati ---
I = ['A', 'B', 'C', 'D']
J = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6']

f = {'A': 38, 'B': 42, 'C': 35, 'D': 46}
cap = {'A': 2, 'B': 3, 'C': 2, 'D': 3}

c = {
    ('A', 'Z1'): 8,  ('B', 'Z1'): 14, ('C', 'Z1'): 11, ('D', 'Z1'): 17,
    ('A', 'Z2'): 10, ('B', 'Z2'): 9,  ('C', 'Z2'): 13, ('D', 'Z2'): 15,
    ('A', 'Z3'): 12, ('B', 'Z3'): 8,  ('C', 'Z3'): 14, ('D', 'Z3'): 10,
    ('A', 'Z4'): 15, ('B', 'Z4'): 11, ('C', 'Z4'): 9,  ('D', 'Z4'): 7,
    ('A', 'Z5'): 9,  ('B', 'Z5'): 13, ('C', 'Z5'): 8,  ('D', 'Z5'): 14,
    ('A', 'Z6'): 14, ('B', 'Z6'): 10, ('C', 'Z6'): 7,  ('D', 'Z6'): 9,
}

p = 2  # numero di centri da aprire

# --- Modello ---
model = gp.Model("Localizzazione_centri_assistenza")

y = model.addVars(I, vtype=GRB.BINARY, name="y")
x = model.addVars(I, J, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(f[i] * y[i] for i in I) +
    gp.quicksum(c[i, j] * x[i, j] for i in I for j in J),
    GRB.MINIMIZE
)

# Vincolo: numero di centri aperti
model.addConstr(gp.quicksum(y[i] for i in I) == p, name="num_centri")

# Vincolo: ogni zona assegnata a un solo centro
for j in J:
    model.addConstr(gp.quicksum(x[i, j] for i in I) == 1, name=f"assegna_{j}")

# Vincolo: capacità dei siti
for i in I:
    model.addConstr(
        gp.quicksum(x[i, j] for j in J) <= cap[i] * y[i],
        name=f"capacita_{i}"
    )

model.optimize()

# --- Output ---
if model.Status == GRB.OPTIMAL:
    variables = {}
    for i in I:
        variables[f"y_{i}"] = round(y[i].X, 4)
    for i in I:
        for j in J:
            variables[f"x_{i}_{j}"] = round(x[i, j].X, 4)

    import json
    print(f'SOLUTION_JSON={{"status":"OPTIMAL","objective":{round(model.ObjVal,4)},'
          f'"variables":{json.dumps(variables)}}}')
else:
    import json
    print(f'SOLUTION_JSON={{"status":"{model.Status}","objective":null,"variables":{{}}}}')
