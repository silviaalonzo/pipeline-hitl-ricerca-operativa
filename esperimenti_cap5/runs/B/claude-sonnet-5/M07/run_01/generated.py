import gurobipy as gp
from gurobipy import GRB
import json

# Dati
fornitori = ["A", "B", "C", "D"]

c = {"A": 11, "B": 10, "C": 12, "D": 9}       # costo unitario
f = {"A": 80, "B": 95, "C": 60, "D": 120}     # costo fisso
cap = {"A": 80, "B": 100, "C": 70, "D": 90}   # capacità
m = {"A": 20, "B": 25, "C": 15, "D": 20}      # ordine minimo
q = {"A": 96, "B": 90, "C": 98, "D": 88}      # qualità
e = {"A": 3, "B": 4, "C": 2, "D": 5}          # emissioni/unità

D_tot = 180
Q_min = 92
E_max = 650
K_min = 2

# Modello
model = gp.Model("SelezioneFornitori")
model.Params.OutputFlag = 0

x = model.addVars(fornitori, vtype=GRB.INTEGER, lb=0, name="x")
y = model.addVars(fornitori, vtype=GRB.BINARY, name="y")

# Obiettivo
model.setObjective(
    gp.quicksum(c[i]*x[i] + f[i]*y[i] for i in fornitori),
    GRB.MINIMIZE
)

# Vincoli
model.addConstr(gp.quicksum(x[i] for i in fornitori) == D_tot, name="domanda")

for i in fornitori:
    model.addConstr(x[i] <= cap[i]*y[i], name=f"cap_{i}")
    model.addConstr(x[i] >= m[i]*y[i], name=f"min_{i}")

model.addConstr(gp.quicksum(y[i] for i in fornitori) >= K_min, name="min_fornitori")

model.addConstr(
    gp.quicksum(q[i]*x[i] for i in fornitori) >= Q_min * gp.quicksum(x[i] for i in fornitori),
    name="qualita_min"
)

model.addConstr(
    gp.quicksum(e[i]*x[i] for i in fornitori) <= E_max,
    name="emissioni_max"
)

# Risoluzione
model.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD"
}

status = status_map.get(model.status, str(model.status))

if model.status == GRB.OPTIMAL:
    variables = {}
    for i in fornitori:
        variables[f"x_{i}"] = round(x[i].X, 4)
        variables[f"y_{i}"] = round(y[i].X, 4)
    objective = round(model.ObjVal, 4)
    result = {"status": status, "objective": objective, "variables": variables}
else:
    result = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
