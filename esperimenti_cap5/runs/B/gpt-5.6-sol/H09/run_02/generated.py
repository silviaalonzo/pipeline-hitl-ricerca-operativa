import gurobipy as gp
from gurobipy import GRB
import json
import math

products = ["A", "B", "C"]
periods = [1, 2, 3, 4, 5, 6]

demand = {
    "A": [12, 18, 14, 20, 16, 19],
    "B": [10, 9, 15, 12, 17, 14],
    "C": [8, 11, 10, 13, 9, 15],
}

production_cost = {
    "A": [7, 8, 9, 7, 10, 8],
    "B": [9, 8, 8, 10, 7, 9],
    "C": [11, 10, 12, 9, 11, 8],
}

setup_cost = {"A": 35, "B": 40, "C": 45}
holding_cost = {"A": 2, "B": 2, "C": 3}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 5, "B": 4, "C": 3}

base_capacity = {
    1: 120,
    2: 115,
    3: 125,
    4: 110,
    5: 120,
    6: 115,
}

max_overtime = 20
overtime_cost = 18
max_total_inventory = 40
minimum_final_inventory = 2
max_setups = {1: 3, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}

d = {
    (i, t): demand[i][t - 1]
    for i in products
    for t in periods
}
c = {
    (i, t): production_cost[i][t - 1]
    for i in products
    for t in periods
}
M = {
    (i, t): math.floor(
        (base_capacity[t] + max_overtime) / hours_per_unit[i]
    )
    for i in products
    for t in periods
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H09", env=env)
model.Params.OutputFlag = 0

x = model.addVars(
    products, periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)
s = model.addVars(
    products, periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="s"
)
y = model.addVars(
    products, periods,
    vtype=GRB.BINARY,
    name="y"
)
o = model.addVars(
    periods,
    vtype=GRB.CONTINUOUS,
    lb=0,
    ub=max_overtime,
    name="o"
)

model.setObjective(
    gp.quicksum(
        c[i, t] * x[i, t]
        + setup_cost[i] * y[i, t]
        + holding_cost[i] * s[i, t]
        for i in products
        for t in periods
    )
    + overtime_cost * gp.quicksum(o[t] for t in periods),
    GRB.MINIMIZE
)

for i in products:
    for t in periods:
        previous_inventory = 0 if t == 1 else s[i, t - 1]
        model.addConstr(
            previous_inventory + x[i, t] == d[i, t] + s[i, t],
            name=f"balance[{i},{t}]"
        )

for i in products:
    for t in periods:
        model.addConstr(
            x[i, t] >= minimum_lot[i] * y[i, t],
            name=f"minimum_lot[{i},{t}]"
        )
        model.addConstr(
            x[i, t] <= M[i, t] * y[i, t],
            name=f"setup_link[{i},{t}]"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(y[i, t] for i in products) <= max_setups[t],
        name=f"setup_limit[{t}]"
    )
    model.addConstr(
        gp.quicksum(
            hours_per_unit[i] * x[i, t] for i in products
        ) <= base_capacity[t] + o[t],
        name=f"capacity[{t}]"
    )
    model.addConstr(
        gp.quicksum(s[i, t] for i in products)
        <= max_total_inventory,
        name=f"inventory_capacity[{t}]"
    )

for i in products:
    model.addConstr(
        s[i, 6] >= minimum_final_inventory,
        name=f"final_inventory[{i}]"
    )

model.optimize()

status_names = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INPROGRESS: "INPROGRESS",
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT",
}

status = status_names.get(model.Status, str(model.Status))

if model.Status == GRB.OPTIMAL:
    def clean_value(var, integer=False):
        value = var.X
        if abs(value) <= 1e-8:
            return 0.0
        if integer:
            return float(round(value))
        return float(round(value, 10))

    variables = {}

    for i in products:
        for t in periods:
            variables[f"x[{i},{t}]"] = clean_value(x[i, t], True)

    for i in products:
        for t in periods:
            variables[f"s[{i},{t}]"] = clean_value(s[i, t], True)

    for i in products:
        for t in periods:
            variables[f"y[{i},{t}]"] = clean_value(y[i, t], True)

    for t in periods:
        variables[f"o[{t}]"] = clean_value(o[t], False)

    result = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": variables,
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
