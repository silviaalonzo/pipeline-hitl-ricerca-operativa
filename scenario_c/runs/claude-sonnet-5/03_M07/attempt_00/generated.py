import gurobipy as gp
from gurobipy import GRB

# Dati
suppliers = ["A", "B", "C", "D"]
cost_unit = {"A": 11, "B": 10, "C": 12, "D": 9}
fixed_cost = {"A": 80, "B": 95, "C": 60, "D": 120}
capacity = {"A": 80, "B": 100, "C": 70, "D": 90}
min_order = {"A": 20, "B": 25, "C": 15, "D": 20}
quality = {"A": 96, "B": 90, "C": 98, "D": 88}
emissions = {"A": 3, "B": 4, "C": 2, "D": 5}

DEMAND = 180
Q_MIN = 92
E_MAX = 650
N_MIN = 2

model = gp.Model("supplier_selection")
model.Params.OutputFlag = 0

x = model.addVars(suppliers, lb=0.0, vtype=GRB.CONTINUOUS, name="x")
y = model.addVars(suppliers, vtype=GRB.BINARY, name="y")

# Vincolo di domanda esatta
model.addConstr(gp.quicksum(x[i] for i in suppliers) == DEMAND, name="demand")

# Capacità e ordine minimo legati all'attivazione
for i in suppliers:
    model.addConstr(x[i] <= capacity[i] * y[i], name=f"cap_{i}")
    model.addConstr(x[i] >= min_order[i] * y[i], name=f"minorder_{i}")

# Almeno due fornitori attivi
model.addConstr(gp.quicksum(y[i] for i in suppliers) >= N_MIN, name="min_suppliers")

# Qualità media ponderata minima
model.addConstr(
    gp.quicksum(quality[i] * x[i] for i in suppliers) >= Q_MIN * gp.quicksum(x[i] for i in suppliers),
    name="quality_min"
)

# Limite emissioni totali
model.addConstr(gp.quicksum(emissions[i] * x[i] for i in suppliers) <= E_MAX, name="emissions_max")

# Obiettivo: minimizzare costi variabili + costi fissi
model.setObjective(
    gp.quicksum(cost_unit[i] * x[i] + fixed_cost[i] * y[i] for i in suppliers),
    GRB.MINIMIZE
)

model.optimize()

status = model.Status
if status == GRB.OPTIMAL:
    variables = {}
    for i in suppliers:
        variables[f"x_{i}"] = round(x[i].X, 4)
        variables[f"y_{i}"] = round(y[i].X, 4)
    obj_val = round(model.ObjVal, 4)
    import json
    print(f"SOLUTION_JSON={json.dumps({'status':'OPTIMAL','objective':obj_val,'variables':variables})}")
else:
    import json
    print(f"SOLUTION_JSON={json.dumps({'status': model.Status, 'objective': None, 'variables': {}})}")
