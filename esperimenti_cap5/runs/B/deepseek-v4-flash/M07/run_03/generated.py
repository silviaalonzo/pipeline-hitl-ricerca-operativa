import json
import gurobipy as gp
from gurobipy import GRB

fornitori = ["A", "B", "C", "D"]

costo = {"A": 11, "B": 10, "C": 12, "D": 9}
fisso = {"A": 80, "B": 95, "C": 60, "D": 120}
capacita = {"A": 80, "B": 100, "C": 70, "D": 90}
ordine_min = {"A": 20, "B": 25, "C": 15, "D": 20}
qualita = {"A": 96, "B": 90, "C": 98, "D": 88}
emissioni = {"A": 3, "B": 4, "C": 2, "D": 5}

model = gp.Model("M07_selezione_fornitori")
model.Params.OutputFlag = 0

x = model.addVars(fornitori, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(fornitori, vtype=GRB.BINARY, name="y")

# Vincolo sulla quantità totale
model.addConstr(gp.quicksum(x[i] for i in fornitori) == 180, "totale")

# Almeno due fornitori attivi
model.addConstr(gp.quicksum(y[i] for i in fornitori) >= 2, "almeno_due")

# Ordine minimo e capacità se il fornitore è attivo
for i in fornitori:
    model.addConstr(x[i] >= ordine_min[i] * y[i], f"ordine_min_{i}")
    model.addConstr(x[i] <= capacita[i] * y[i], f"capacita_{i}")

# Qualità media ponderata almeno 92
model.addConstr(gp.quicksum(qualita[i] * x[i] for i in fornitori) >= 92 * 180, "qualita")

# Emissioni totali massime
model.addConstr(gp.quicksum(emissioni[i] * x[i] for i in fornitori) <= 650, "emissioni")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(fisso[i] * y[i] for i in fornitori) +
    gp.quicksum(costo[i] * x[i] for i in fornitori),
    GRB.MINIMIZE
)

model.optimize()

if model.Status == GRB.OPTIMAL:
    variabili = {f"x_{i}": x[i].X for i in fornitori}
    variabili.update({f"y_{i}": y[i].X for i in fornitori})
    result = {
        "status": "OPTIMAL",
        "objective": model.ObjVal,
        "variables": variabili
    }
else:
    result = {
        "status": "INFEASIBLE" if model.Status == GRB.INFEASIBLE else str(model.Status),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
