import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
E = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
S = ["M1", "M2", "P1", "P2", "N1", "N2"]
Night = {"N1", "N2"}

# Costi (None = indisponibile)
cost = {
    "Ana":   {"M1": 8, "M2": 7, "P1": 9, "P2": 8, "N1": None, "N2": None},
    "Bruno": {"M1": 7, "M2": 8, "P1": 8, "P2": 9, "N1": None, "N2": None},
    "Carla": {"M1": None, "M2": 9, "P1": 8, "P2": 8, "N1": 11, "N2": 12},
    "Diego": {"M1": 10, "M2": None, "P1": 9, "P2": 8, "N1": 10, "N2": 11},
    "Elena": {"M1": 8, "M2": 10, "P1": 9, "P2": 9, "N1": 12, "N2": 10},
    "Fabio": {"M1": 9, "M2": 8, "P1": 10, "P2": 7, "N1": None, "N2": None},
}

# Insieme A delle coppie disponibili
A = [(e, s) for e in E for s in S if cost[e][s] is not None]

# Modello
model = gp.Model("assegnazione_turni")
model.Params.OutputFlag = 0

# Variabili
x = model.addVars(A, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(gp.quicksum(cost[e][s] * x[e, s] for (e, s) in A), GRB.MINIMIZE)

# Vincolo: copertura esatta di ogni turno
for s in S:
    model.addConstr(
        gp.quicksum(x[e, s] for e in E if (e, s) in A) == 1,
        name=f"cover_{s}"
    )

# Vincolo: massimo due turni per dipendente
for e in E:
    model.addConstr(
        gp.quicksum(x[e, s] for s in S if (e, s) in A) <= 2,
        name=f"max2_{e}"
    )

# Vincolo: massimo un turno notturno per dipendente
for e in E:
    model.addConstr(
        gp.quicksum(x[e, s] for s in Night if (e, s) in A) <= 1,
        name=f"night_{e}"
    )

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 2)
    variables = {}
    for (e, s) in A:
        var_name = f"x_{e}_{s}"
        variables[var_name] = round(x[e, s].X, 2)
    result["variables"] = variables
else:
    result["status"] = str(status)

print("SOLUTION_JSON=" + json.dumps(result))
