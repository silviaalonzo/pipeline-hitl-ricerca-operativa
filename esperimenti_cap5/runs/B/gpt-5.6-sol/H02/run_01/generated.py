import gurobipy as gp
from gurobipy import GRB
import json

products = ["A", "B", "C"]
periods = ["T1", "T2", "T3", "T4"]

demand = {
    ("A", "T1"): 8,  ("A", "T2"): 12, ("A", "T3"): 10, ("A", "T4"): 14,
    ("B", "T1"): 10, ("B", "T2"): 8,  ("B", "T3"): 14, ("B", "T4"): 12,
    ("C", "T1"): 6,  ("C", "T2"): 9,  ("C", "T3"): 7,  ("C", "T4"): 11
}

production_cost = {
    ("A", "T1"): 9,  ("A", "T2"): 11, ("A", "T3"): 10, ("A", "T4"): 12,
    ("B", "T1"): 8,  ("B", "T2"): 9,  ("B", "T3"): 11, ("B", "T4"): 10,
    ("C", "T1"): 13, ("C", "T2"): 12, ("C", "T3"): 14, ("C", "T4"): 11
}

setup_cost = {"A": 45, "B": 40, "C": 50}
holding_cost = {"A": 2, "B": 3, "C": 2}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 4, "B": 4, "C": 3}
capacity = {"T1": 90, "T2": 95, "T3": 90, "T4": 100}
initial_inventory = {"A": 0, "B": 0, "C": 6}
maximum_total_inventory = 20
maximum_setups = 2

big_m = {}
for p in products:
    for t_index, t in enumerate(periods):
        remaining_demand = sum(demand[p, tau] for tau in periods[t_index:])
        capacity_bound = capacity[t] // hours_per_unit[p]
        big_m[p, t] = min(remaining_demand, capacity_bound)

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H02_produzione_multi_periodo", env=env)
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

x = {
    (p, t): model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name=f"x_{p}_{t}"
    )
    for p in products for t in periods
}

I = {
    (p, t): model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name=f"I_{p}_{t}"
    )
    for p in products for t in periods
}

y = {
    (p, t): model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{p}_{t}"
    )
    for p in products for t in periods
}

model.setObjective(
    gp.quicksum(
        production_cost[p, t] * x[p, t]
        + setup_cost[p] * y[p, t]
        + holding_cost[p] * I[p, t]
        for p in products for t in periods
    ),
    GRB.MINIMIZE
)

for p in products:
    for t_index, t in enumerate(periods):
        previous_inventory = (
            initial_inventory[p] if t_index == 0 else I[p, periods[t_index - 1]]
        )
        model.addConstr(
            previous_inventory + x[p, t] == demand[p, t] + I[p, t],
            name=f"balance_{p}_{t}"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(hours_per_unit[p] * x[p, t] for p in products)
        <= capacity[t],
        name=f"capacity_{t}"
    )

for p in products:
    for t in periods:
        model.addConstr(
            x[p, t] <= big_m[p, t] * y[p, t],
            name=f"setup_upper_{p}_{t}"
        )
        model.addConstr(
            x[p, t] >= minimum_lot[p] * y[p, t],
            name=f"minimum_lot_{p}_{t}"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(y[p, t] for p in products) <= maximum_setups,
        name=f"maximum_setups_{t}"
    )
    model.addConstr(
        gp.quicksum(I[p, t] for p in products) <= maximum_total_inventory,
        name=f"maximum_inventory_{t}"
    )

for p in products:
    model.addConstr(I[p, "T4"] == 0, name=f"final_inventory_{p}")

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

def clean_number(value):
    if abs(value) < 1e-6:
        return 0.0
    nearest_integer = round(value)
    if abs(value - nearest_integer) < 1e-6:
        return float(nearest_integer)
    return float(value)

if model.Status == GRB.OPTIMAL:
    all_variables = (
        [x[p, t] for p in products for t in periods]
        + [I[p, t] for p in products for t in periods]
        + [y[p, t] for p in products for t in periods]
    )
    result = {
        "status": "OPTIMAL",
        "objective": clean_number(model.ObjVal),
        "variables": {
            variable.VarName: clean_number(variable.X)
            for variable in all_variables
        }
    }
else:
    result = {
        "status": status_names.get(model.Status, "STATUS_" + str(model.Status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
