import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
E = ['Ana', 'Bruno', 'Carla', 'Diego', 'Elena', 'Fabio']
S = ['M1', 'M2', 'P1', 'P2', 'N1', 'N2']
N = ['N1', 'N2']  # turni notturni

# Matrice costi (None = indisponibile "—")
cost = {
    'Ana':   {'M1':8, 'M2':7, 'P1':9, 'P2':8, 'N1':None, 'N2':None},
    'Bruno': {'M1':7, 'M2':8, 'P1':8, 'P2':9, 'N1':None, 'N2':None},
    'Carla': {'M1':None, 'M2':9, 'P1':8, 'P2':8, 'N1':11, 'N2':12},
    'Diego': {'M1':10, 'M2':None, 'P1':9, 'P2':8, 'N1':10, 'N2':11},
    'Elena': {'M1':8, 'M2':10, 'P1':9, 'P2':9, 'N1':12, 'N2':10},
    'Fabio': {'M1':9, 'M2':8, 'P1':10, 'P2':7, 'N1':None, 'N2':None},
}

# Insieme A delle coppie disponibili
A = [(e, s) for e in E for s in S if cost[e][s] is not None]

model = gp.Model("Assegnazione_Turni")
model.Params.OutputFlag = 0

# Variabili decisionali
x = model.addVars(A, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[e][s] * x[e, s] for (e, s) in A), GRB.MINIMIZE)

# Vincolo: ogni turno coperto esattamente da 1 dipendente
for s in S:
    model.addConstr(
        gp.quicksum(x[e, s] for e in E if (e, s) in A) == 1,
        name=f"coverage_{s}"
    )

# Vincolo: ogni dipendente al massimo 2 turni
for e in E:
    model.addConstr(
        gp.quicksum(x[e, s] for s in S if (e, s) in A) <= 2,
        name=f"maxshifts_{e}"
    )

# Vincolo: ogni dipendente al massimo 1 turno notturno
for e in E:
    model.addConstr(
        gp.quicksum(x[e, s] for s in N if (e, s) in A) <= 1,
        name=f"maxnight_{e}"
    )

model.optimize()

result = {"status": "UNKNOWN", "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 2)
    variables = {}
    for e in E:
        for s in S:
            var_name = f"x_{e}_{s}"
            if (e, s) in A:
                variables[var_name] = round(x[e, s].X, 2)
            else:
                variables[var_name] = 0.0
    result["variables"] = variables

    # Stampa leggibile delle decisioni non nulle
    print("=== Assegnazioni ottime ===")
    for (e, s) in A:
        if x[e, s].X > 0.5:
            print(f"  {e:8s} -> {s}  (costo {cost[e][s]})")
    print(f"Costo totale ottimo: {model.ObjVal}")
else:
    result["status"] = str(model.Status)

print(f"SOLUTION_JSON={json.dumps(result)}")
