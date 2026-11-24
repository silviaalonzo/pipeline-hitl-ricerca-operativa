import gurobipy as gp
from gurobipy import GRB

# Dati
jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

# tempi di lavorazione: solo le coppie ammesse
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5,  # J7 non compatibile con A
}

allowed_pairs = list(p.keys())

# Machine ammesse per ciascun lavoro
machines_for_job = {j: [m for (jj, m) in allowed_pairs if jj == j] for j in jobs}

model = gp.Model("Bilanciamento_2_macchine")

# Variabili decisionali
x = model.addVars(allowed_pairs, vtype=GRB.BINARY, name="x")
Load = model.addVars(machines, vtype=GRB.CONTINUOUS, lb=0.0, name="Load")
Cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="Cmax")

# Vincolo: ogni lavoro assegnato a esattamente una macchina ammessa
for j in jobs:
    model.addConstr(
        gp.quicksum(x[j, m] for m in machines_for_job[j]) == 1,
        name=f"assign_{j}"
    )

# Vincolo: definizione del carico di ciascuna macchina
for m in machines:
    model.addConstr(
        Load[m] == gp.quicksum(p[j, m] * x[j, m] for j in jobs if (j, m) in p),
        name=f"load_{m}"
    )

# Vincolo: makespan >= carico di ogni macchina
for m in machines:
    model.addConstr(Cmax >= Load[m], name=f"makespan_{m}")

# Funzione obiettivo
model.setObjective(Cmax, GRB.MINIMIZE)

model.optimize()

import json

status = model.Status
if status == GRB.OPTIMAL:
    variables = {}
    for (j, m) in allowed_pairs:
        variables[f"x_{j}_{m}"] = round(x[j, m].X, 4)
    for m in machines:
        variables[f"Load_{m}"] = round(Load[m].X, 4)
    variables["Cmax"] = round(Cmax.X, 4)
    objective = round(model.ObjVal, 4)
    print(f"SOLUTION_JSON={json.dumps({'status': 'OPTIMAL', 'objective': objective, 'variables': variables})}")
else:
    status_name = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }.get(status, "NOT_OPTIMAL")
    print(f"SOLUTION_JSON={json.dumps({'status': status_name, 'objective': None, 'variables': {}})}")
