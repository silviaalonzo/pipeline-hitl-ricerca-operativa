import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
night_shifts = ["N1", "N2"]

# Costi (None = indisponibile)
cost = {
    "Ana":   {"M1": 8,  "M2": 7,  "P1": 9,  "P2": 8,  "N1": None, "N2": None},
    "Bruno": {"M1": 7,  "M2": 8,  "P1": 8,  "P2": 9,  "N1": None, "N2": None},
    "Carla": {"M1": None,"M2": 9,  "P1": 8,  "P2": 8,  "N1": 11,   "N2": 12},
    "Diego": {"M1": 10, "M2": None,"P1": 9,  "P2": 8,  "N1": 10,   "N2": 11},
    "Elena": {"M1": 8,  "M2": 10, "P1": 9,  "P2": 9,  "N1": 12,   "N2": 10},
    "Fabio": {"M1": 9,  "M2": 8,  "P1": 10, "P2": 7,  "N1": None, "N2": None},
}

# Insieme delle coppie disponibili A
A = [(e, s) for e in employees for s in shifts if cost[e][s] is not None]

model = gp.Model("assegnazione_turni")

# Variabili decisionali
x = model.addVars(A, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[e][s] * x[e, s] for (e, s) in A), GRB.MINIMIZE)

# Vincolo 1: copertura di ogni turno
for s in shifts:
    model.addConstr(
        gp.quicksum(x[e, s] for e in employees if (e, s) in A) == 1,
        name=f"copertura_{s}"
    )

# Vincolo 2: al massimo due turni per dipendente
for e in employees:
    model.addConstr(
        gp.quicksum(x[e, s] for s in shifts if (e, s) in A) <= 2,
        name=f"max2turni_{e}"
    )

# Vincolo 3: al massimo un turno notturno per dipendente
for e in employees:
    model.addConstr(
        gp.quicksum(x[e, s] for s in night_shifts if (e, s) in A) <= 1,
        name=f"max1notte_{e}"
    )

model.optimize()

status = model.Status
if status == GRB.OPTIMAL:
    variables = {f"x_{e}_{s}": x[e, s].X for (e, s) in A}
    objective = model.ObjVal
    result = {"status": "OPTIMAL", "objective": objective, "variables": variables}
else:
    result = {"status": str(status), "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
