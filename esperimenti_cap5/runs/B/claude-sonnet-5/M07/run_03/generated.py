import gurobipy as gp
from gurobipy import GRB
import json

# Dati
suppliers = ["A", "B", "C", "D"]
c    = {"A": 11, "B": 10, "C": 12, "D": 9}
f    = {"A": 80, "B": 95, "C": 60, "D": 120}
cap  = {"A": 80, "B": 100, "C": 70, "D": 90}
m    = {"A": 20, "B": 25, "C": 15, "D": 20}
q    = {"A": 96, "B": 90, "C": 98, "D": 88}
e    = {"A": 3,  "B": 4,  "C": 2,  "D": 5}

D_tot   = 180
Q_min   = 92
E_max   = 650
S_min   = 2

model = gp.Model("Selezione_Fornitori")
model.Params.OutputFlag = 0

x = model.addVars(suppliers, lb=0, vtype=GRB.INTEGER, name="x")
y = model.addVars(suppliers, vtype=GRB.BINARY, name="y")

# Obiettivo
model.setObjective(
    gp.quicksum(c[i] * x[i] for i in suppliers) +
    gp.quicksum(f[i] * y[i] for i in suppliers),
    GRB.MINIMIZE
)

# Domanda esatta
model.addConstr(gp.quicksum(x[i] for i in suppliers) == D_tot, name="Domanda")

# Capacità e attivazione
for i in suppliers:
    model.addConstr(x[i] <= cap[i] * y[i], name=f"Capacita_{i}")
    model.addConstr(x[i] >= m[i] * y[i], name=f"OrdineMin_{i}")

# Almeno due fornitori attivi
model.addConstr(gp.quicksum(y[i] for i in suppliers) >= S_min, name="MinFornitori")

# Qualità media ponderata >= 92
model.addConstr(
    gp.quicksum(q[i] * x[i] for i in suppliers) >= Q_min * D_tot,
    name="Qualita"
)

# Emissioni totali <= 650
model.addConstr(
    gp.quicksum(e[i] * x[i] for i in suppliers) <= E_max,
    name="Emissioni"
)

model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for i in suppliers:
        variables[f"x_{i}"] = round(x[i].X, 4)
    for i in suppliers:
        variables[f"y_{i}"] = round(y[i].X, 4)
    result["variables"] = variables
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    result["status"] = status_map.get(status, str(status))
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
