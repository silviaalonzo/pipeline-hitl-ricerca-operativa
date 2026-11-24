import gurobipy as gp
from gurobipy import GRB
import json

T = range(1, 7)

demand = {
    1: 20,
    2: 30,
    3: 15,
    4: 35,
    5: 25,
    6: 20
}

purchase_cost = {
    1: 9,
    2: 8,
    3: 11,
    4: 7,
    5: 10,
    6: 9
}

capacity = {
    1: 50,
    2: 50,
    3: 45,
    4: 55,
    5: 45,
    6: 50
}

initial_inventory = 10
minimum_final_inventory = 5
minimum_order = 10
fixed_order_cost = 40
holding_cost = 2

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("piano_riordino_costi_fissi", env=env)
model.Params.MIPGap = 0.0

q = model.addVars(T, vtype=GRB.INTEGER, lb=0, name="q")
I = model.addVars(T, vtype=GRB.INTEGER, lb=0, name="I")
y = model.addVars(T, vtype=GRB.BINARY, name="y")

model.setObjective(
    gp.quicksum(
        purchase_cost[t] * q[t]
        + fixed_order_cost * y[t]
        + holding_cost * I[t]
        for t in T
    ),
    GRB.MINIMIZE
)

for t in T:
    previous_inventory = initial_inventory if t == 1 else I[t - 1]
    model.addConstr(
        I[t] == previous_inventory + q[t] - demand[t],
        name=f"inventory_balance_{t}"
    )

    model.addConstr(
        q[t] >= minimum_order * y[t],
        name=f"minimum_order_{t}"
    )

    model.addConstr(
        q[t] <= capacity[t] * y[t],
        name=f"order_capacity_{t}"
    )

model.addConstr(
    I[6] >= minimum_final_inventory,
    name="minimum_final_inventory"
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

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    def clean_number(value):
        if abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(value)

    variable_values = {}

    for t in T:
        variable_values[f"q_{t}"] = clean_number(q[t].X)
    for t in T:
        variable_values[f"I_{t}"] = clean_number(I[t].X)
    for t in T:
        variable_values[f"y_{t}"] = clean_number(y[t].X)

    result = {
        "status": "OPTIMAL",
        "objective": clean_number(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
