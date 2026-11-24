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

model = gp.Model("M09_piano_riordino")
model.Params.OutputFlag = 0

q = {
    t: model.addVar(
        lb=0,
        vtype=GRB.INTEGER,
        name=f"q_{t}"
    )
    for t in T
}

I = {
    t: model.addVar(
        lb=0,
        vtype=GRB.INTEGER,
        name=f"I_{t}"
    )
    for t in T
}

y = {
    t: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{t}"
    )
    for t in T
}

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
        name=f"balance_{t}"
    )
    model.addConstr(
        q[t] >= minimum_order * y[t],
        name=f"minimum_order_{t}"
    )
    model.addConstr(
        q[t] <= capacity[t] * y[t],
        name=f"capacity_{t}"
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

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variables = {}
    for variable_group in (q, I, y):
        for t in T:
            value = variable_group[t].X
            rounded_value = round(value)
            variables[variable_group[t].VarName] = (
                float(rounded_value)
                if abs(value - rounded_value) <= 1e-6
                else float(value)
            )

    objective_value = float(round(model.ObjVal, 10))
    result = {
        "status": status,
        "objective": objective_value,
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
