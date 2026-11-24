import gurobipy as gp
from gurobipy import GRB
import json
import math

products = ["A", "B", "C"]
periods = [1, 2, 3, 4]

demand = {
    ("A", 1): 8,  ("A", 2): 12, ("A", 3): 10, ("A", 4): 14,
    ("B", 1): 10, ("B", 2): 8,  ("B", 3): 14, ("B", 4): 12,
    ("C", 1): 6,  ("C", 2): 9,  ("C", 3): 7,  ("C", 4): 11
}

production_cost = {
    ("A", 1): 9,  ("A", 2): 11, ("A", 3): 10, ("A", 4): 12,
    ("B", 1): 8,  ("B", 2): 9,  ("B", 3): 11, ("B", 4): 10,
    ("C", 1): 13, ("C", 2): 12, ("C", 3): 14, ("C", 4): 11
}

setup_cost = {"A": 45, "B": 40, "C": 50}
holding_cost = {"A": 2, "B": 3, "C": 2}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 4, "B": 4, "C": 3}
initial_inventory = {"A": 0, "B": 0, "C": 6}
capacity = {1: 90, 2: 95, 3: 90, 4: 100}

max_total_inventory = 20
max_setups_per_period = 2

big_m = {}
for i in products:
    for t in periods:
        capacity_bound = math.floor(capacity[t] / hours_per_unit[i])
        remaining_demand = sum(demand[i, tau] for tau in periods if tau >= t)
        big_m[i, t] = min(capacity_bound, remaining_demand)

model = gp.Model("H02_produzione_multi_periodo")
model.Params.OutputFlag = 0

x = {}
I = {}
y = {}

for i in products:
    for t in periods:
        x[i, t] = model.addVar(
            lb=0,
            vtype=GRB.INTEGER,
            name=f"x_{i}_{t}"
        )
        I[i, t] = model.addVar(
            lb=0,
            vtype=GRB.INTEGER,
            name=f"I_{i}_{t}"
        )
        y[i, t] = model.addVar(
            vtype=GRB.BINARY,
            name=f"y_{i}_{t}"
        )

model.setObjective(
    gp.quicksum(
        production_cost[i, t] * x[i, t]
        + setup_cost[i] * y[i, t]
        + holding_cost[i] * I[i, t]
        for i in products
        for t in periods
    ),
    GRB.MINIMIZE
)

for i in products:
    model.addConstr(
        initial_inventory[i] + x[i, 1] == demand[i, 1] + I[i, 1],
        name=f"balance_{i}_1"
    )
    for t in periods[1:]:
        model.addConstr(
            I[i, t - 1] + x[i, t] == demand[i, t] + I[i, t],
            name=f"balance_{i}_{t}"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(hours_per_unit[i] * x[i, t] for i in products)
        <= capacity[t],
        name=f"capacity_{t}"
    )

for i in products:
    for t in periods:
        model.addConstr(
            x[i, t] >= minimum_lot[i] * y[i, t],
            name=f"minimum_lot_{i}_{t}"
        )
        model.addConstr(
            x[i, t] <= big_m[i, t] * y[i, t],
            name=f"setup_link_{i}_{t}"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(y[i, t] for i in products) <= max_setups_per_period,
        name=f"max_setups_{t}"
    )
    model.addConstr(
        gp.quicksum(I[i, t] for i in products) <= max_total_inventory,
        name=f"storage_capacity_{t}"
    )

for i in products:
    model.addConstr(I[i, 4] == 0, name=f"final_inventory_{i}")

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

if model.Status == GRB.OPTIMAL:
    variables = {}
    for i in products:
        for t in periods:
            variables[f"x_{i}_{t}"] = float(round(x[i, t].X))
    for i in products:
        for t in periods:
            variables[f"I_{i}_{t}"] = float(round(I[i, t].X))
    for i in products:
        for t in periods:
            variables[f"y_{i}_{t}"] = float(round(y[i, t].X))

    result = {
        "status": status,
        "objective": float(round(model.ObjVal, 6)),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
