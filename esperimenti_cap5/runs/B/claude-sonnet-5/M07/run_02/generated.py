import gurobipy as gp
from gurobipy import GRB
import json

# Dati
suppliers = ["A", "B", "C", "D"]
c = {"A": 11, "B": 10, "C": 12, "D": 9}       # costo variabile/unità
f = {"A": 80, "B": 95, "C": 60, "D": 120}     # costo fisso
cap = {"A": 80, "B": 100, "C": 70, "D": 90}   # capacità
m = {"A": 20, "B": 25, "C": 15, "D": 20}      # ordine minimo
q = {"A": 96, "B": 90, "C": 98, "D": 88}      # qualità
e = {"A": 3, "B": 4, "C": 2, "D": 5}          # emissioni/unità

D_tot = 180
Qmin = 92
Emax = 650
Nmin = 2

model = gp.Model("Selezione_Fornitori")

x = model.addVars(suppliers, lb=0.0, name="x")
y = model.addVars(suppliers, vtype=GRB.BINARY, name="y")

# Obiettivo
model.setObjective(
    gp.quicksum(c[i]*x[i] + f[i]*y[i] for i in suppliers),
    GRB.MINIMIZE
)

# Vincolo di domanda
model.addConstr(gp.quicksum(x[i] for i in suppliers) == D_tot, name="Domanda")

# Capacità e ordine minimo legati all'attivazione
for i in suppliers:
    model.addConstr(x[i] <= cap[i]*y[i], name=f"Cap_{i}")
    model.addConstr(x[i] >= m[i]*y[i], name=f"MinOrd_{i}")

# Qualità media ponderata minima
model.addConstr(
    gp.quicksum(q[i]*x[i] for i in suppliers) >= Qmin * gp.quicksum(x[i] for i in suppliers),
    name="Qualita"
)

# Emissioni totali massime
model.addConstr(
    gp.quicksum(e[i]*x[i] for i in suppliers) <= Emax,
    name="Emissioni"
)

# Numero minimo di fornitori attivi
model.addConstr(gp.quicksum(y[i] for i in suppliers) >= Nmin, name="MinFornitori")

model.optimize()

result = {"status": None, "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 6)
    for i in suppliers:
        result["variables"][f"x_{i}"] = round(x[i].X, 6)
    for i in suppliers:
        result["variables"][f"y_{i}"] = round(y[i].X, 6)
else:
    result["status"] = str(model.Status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
