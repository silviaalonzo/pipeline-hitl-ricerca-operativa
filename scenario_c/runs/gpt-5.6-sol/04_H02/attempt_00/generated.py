import gurobipy as gp
from gurobipy import GRB
import json

products = ["A", "B", "C"]
periods = ["T1", "T2", "T3", "T4"]

demand = {
    ("A", "T1"): 8,  ("A", "T2"): 12, ("A", "T3"): 10, ("A", "T4"): 14,
    ("B", "T1"): 10, ("B", "T2"): 8,  ("B", "T3"): 14, ("B", "T4"): 12,
    ("C", "T1"): 6,  ("C", "T2"): 9,  ("C", "T3"): 7,  ("C", "T4"): 11,
}

production_cost = {
    ("A", "T1"): 9,  ("A", "T2"): 11, ("A", "T3"): 10, ("A", "T4"): 12,
    ("B", "T1"): 8,  ("B", "T2"): 9,  ("B", "T3"): 11, ("B", "T4"): 10,
    ("C", "T1"): 13, ("C", "T2"): 12, ("C", "T3"): 14, ("C", "T4"): 11,
}

setup_cost = {"A": 45, "B": 40, "C": 50}
holding_cost = {"A": 2, "B": 3, "C": 2}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 4, "B": 4, "C": 3}
initial_inventory = {"A": 0, "B": 0, "C": 6}
capacity = {"T1": 90, "T2": 95, "T3": 90, "T4": 100}
max_total_inventory = 20

big_m = {}
for i in products:
    for position, t in enumerate(periods):
        big_m[i, t] = sum(demand[i, tau] for tau in periods[position:])

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H02_produzione_multi_periodo", env=env)
model.Params.OutputFlag = 0

x = model.addVars(
    products,
    periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)
inventory = model.addVars(
    products,
    periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="I"
)
setup = model.addVars(
    products,
    periods,
    vtype=GRB.BINARY,
    name="y"
)

model.setObjective(
    gp.quicksum(
        production_cost[i, t] * x[i, t]
        for i in products for t in periods
    )
    + gp.quicksum(
        setup_cost[i] * setup[i, t]
        for i in products for t in periods
    )
    + gp.quicksum(
        holding_cost[i] * inventory[i, t]
        for i in products for t in periods
    ),
    GRB.MINIMIZE
)

for i in products:
    model.addConstr(
        initial_inventory[i] + x[i, "T1"]
        == demand[i, "T1"] + inventory[i, "T1"],
        name=f"balance[{i},T1]"
    )
    for position in range(1, len(periods)):
        previous_t = periods[position - 1]
        t = periods[position]
        model.addConstr(
            inventory[i, previous_t] + x[i, t]
            == demand[i, t] + inventory[i, t],
            name=f"balance[{i},{t}]"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(hours_per_unit[i] * x[i, t] for i in products)
        <= capacity[t],
        name=f"capacity[{t}]"
    )

for i in products:
    for t in periods:
        model.addConstr(
            x[i, t] >= minimum_lot[i] * setup[i, t],
            name=f"minimum_lot[{i},{t}]"
        )
        model.addConstr(
            x[i, t] <= big_m[i, t] * setup[i, t],
            name=f"setup_link[{i},{t}]"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(setup[i, t] for i in products) <= 2,
        name=f"maximum_setups[{t}]"
    )
    model.addConstr(
        gp.quicksum(inventory[i, t] for i in products)
        <= max_total_inventory,
        name=f"inventory_limit[{t}]"
    )

for i in products:
    model.addConstr(
        inventory[i, "T4"] == 0,
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

solver_status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    def numeric_value(value):
        if abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(value)

    variable_values = {}

    for i in products:
        for t in periods:
            variable_values[f"x[{i},{t}]"] = numeric_value(x[i, t].X)

    for i in products:
        for t in periods:
            variable_values[f"I[{i},{t}]"] = numeric_value(inventory[i, t].X)

    for i in products:
        for t in periods:
            variable_values[f"y[{i},{t}]"] = numeric_value(setup[i, t].X)

    payload = {
        "status": solver_status,
        "objective": numeric_value(model.ObjVal),
        "variables": variable_values,
    }
else:
    payload = {
        "status": solver_status,
        "objective": None,
        "variables": {},
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
