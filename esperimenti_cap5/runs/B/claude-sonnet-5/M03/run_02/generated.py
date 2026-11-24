import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
night_shifts = ["N1", "N2"]

# Costi (None = indisponibile)
cost_table = {
    "Ana":   {"M1": 8,    "M2": 7,    "P1": 9, "P2": 8, "N1": None, "N2": None},
    "Bruno": {"M1": 7,    "M2": 8,    "P1": 8, "P2": 9, "N1": None, "N2": None},
    "Carla": {"M1": None, "M2": 9,    "P1": 8, "P2": 8, "N1": 11,   "N2": 12},
    "Diego": {"M1": 10,   "M2": None, "P1": 9, "P2": 8, "N1": 10,   "N2": 11},
    "Elena": {"M1": 8,    "M2": 10,   "P1": 9, "P2": 9, "N1": 12,   "N2": 10},
    "Fabio": {"M1": 9,    "M2": 8,    "P1": 10,"P2": 7, "N1": None, "N2": None},
}

# Coppie ammissibili A
A = [(e, s) for e in employees for s in shifts if cost_table[e][s] is not None]
cost = {(e, s): cost_table[e][s] for (e, s) in A}

K = 2      # massimo turni per dipendente
KN = 1     # massimo turni notturni per dipendente

model = gp.Model("assegnazione_turni")
model.Params.OutputFlag = 0

# Variabili decisionali
x = model.addVars(A, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[e, s] * x[e, s] for (e, s) in A), GRB.MINIMIZE)

# Copertura esatta di ogni turno
for s in shifts:
    model.addConstr(
        gp.quicksum(x[e, s] for e in employees if (e, s) in A) == 1,
        name=f"cover_{s}"
    )

# Massimo K turni per dipendente
for e in employees:
    model.addConstr(
        gp.quicksum(x[e, s] for s in shifts if (e, s) in A) <= K,
        name=f"maxshifts_{e}"
    )

# Massimo KN turni notturni per dipendente
for e in employees:
    model.addConstr(
        gp.quicksum(x[e, s] for s in night_shifts if (e, s) in A) <= KN,
        name=f"maxnight_{e}"
    )

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = model.ObjVal
    variables = {}
    for e in employees:
        for s in shifts:
            var_name = f"x_{e}_{s}"
            if (e, s) in A:
                variables[var_name] = x[e, s].X
            else:
                variables[var_name] = 0.0
    result["variables"] = variables
else:
    result["status"] = str(status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
