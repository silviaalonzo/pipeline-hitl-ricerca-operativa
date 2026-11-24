import gurobipy as gp
from gurobipy import GRB
import json

products = ["A", "B", "C", "D"]

margin = {"A": 42, "B": 36, "C": 50, "D": 31}
setup = {"A": 80, "B": 65, "C": 90, "D": 50}
machine = {"A": 3, "B": 2, "C": 4, "D": 1}
labor = {"A": 2, "B": 3, "C": 2, "D": 2}
min_lot = {"A": 4, "B": 5, "C": 3, "D": 6}
max_demand = {"A": 20, "B": 25, "C": 16, "D": 30}

machine_capacity = 90
labor_capacity = 100
minimum_products = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M02_piano_produzione_setup", env=env)

x = model.addVars(
    products,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)

y = model.addVars(
    products,
    vtype=GRB.BINARY,
    name="y"
)

model.setObjective(
    gp.quicksum(margin[i] * x[i] - setup[i] * y[i] for i in products),
    GRB.MAXIMIZE
)

model.addConstr(
    gp.quicksum(machine[i] * x[i] for i in products) <= machine_capacity,
    name="capacita_macchina"
)

model.addConstr(
    gp.quicksum(labor[i] * x[i] for i in products) <= labor_capacity,
    name="capacita_lavoro"
)

for i in products:
    model.addConstr(x[i] >= min_lot[i] * y[i], name=f"lotto_minimo_{i}")
    model.addConstr(x[i] <= max_demand[i] * y[i], name=f"domanda_massima_{i}")

model.addConstr(
    gp.quicksum(y[i] for i in products) >= minimum_products,
    name="numero_minimo_prodotti"
)

model.optimize()

status_names = {
    1: "LOADED",
    2: "OPTIMAL",
    3: "INFEASIBLE",
    4: "INF_OR_UNBD",
    5: "UNBOUNDED",
    6: "CUTOFF",
    7: "ITERATION_LIMIT",
    8: "NODE_LIMIT",
    9: "TIME_LIMIT",
    10: "SOLUTION_LIMIT",
    11: "INTERRUPTED",
    12: "NUMERIC",
    13: "SUBOPTIMAL",
    14: "INPROGRESS",
    15: "USER_OBJ_LIMIT",
    16: "WORK_LIMIT",
    17: "MEM_LIMIT"
}

status = status_names.get(model.Status, str(model.Status))

if model.Status == GRB.OPTIMAL:
    def numeric_value(value):
        if abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(value)

    variables = {}
    for i in products:
        variables[x[i].VarName] = numeric_value(x[i].X)
    for i in products:
        variables[y[i].VarName] = numeric_value(y[i].X)

    payload = {
        "status": status,
        "objective": numeric_value(model.ObjVal),
        "variables": variables
    }
else:
    payload = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
