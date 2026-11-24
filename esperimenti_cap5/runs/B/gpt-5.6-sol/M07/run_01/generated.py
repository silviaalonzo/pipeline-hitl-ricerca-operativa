import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["A", "B", "C", "D"]

unit_cost = {"A": 11, "B": 10, "C": 12, "D": 9}
fixed_cost = {"A": 80, "B": 95, "C": 60, "D": 120}
capacity = {"A": 80, "B": 100, "C": 70, "D": 90}
min_order = {"A": 20, "B": 25, "C": 15, "D": 20}
quality = {"A": 96, "B": 90, "C": 98, "D": 88}
emissions = {"A": 3, "B": 4, "C": 2, "D": 5}

demand = 180
min_quality = 92
max_emissions = 650
min_suppliers = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.setParam("LogToConsole", 0)
env.start()

model = gp.Model("M07_selezione_fornitori", env=env)
model.Params.OutputFlag = 0

x = {
    i: model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        ub=capacity[i],
        name=f"x_{i}"
    )
    for i in suppliers
}

y = {
    i: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}"
    )
    for i in suppliers
}

model.setObjective(
    gp.quicksum(unit_cost[i] * x[i] + fixed_cost[i] * y[i]
                for i in suppliers),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(x[i] for i in suppliers) == demand,
    name="domanda"
)

for i in suppliers:
    model.addConstr(
        x[i] >= min_order[i] * y[i],
        name=f"ordine_minimo_{i}"
    )
    model.addConstr(
        x[i] <= capacity[i] * y[i],
        name=f"capacita_{i}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in suppliers) >= min_suppliers,
    name="numero_minimo_fornitori"
)

model.addConstr(
    gp.quicksum(quality[i] * x[i] for i in suppliers)
    >= min_quality * demand,
    name="qualita_minima"
)

model.addConstr(
    gp.quicksum(emissions[i] * x[i] for i in suppliers)
    <= max_emissions,
    name="emissioni_massime"
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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

def clean_value(value):
    value = round(float(value), 10)
    return 0.0 if abs(value) < 1e-9 else value

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": clean_value(model.ObjVal),
        "variables": {
            **{f"x_{i}": clean_value(x[i].X) for i in suppliers},
            **{f"y_{i}": clean_value(y[i].X) for i in suppliers}
        }
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
