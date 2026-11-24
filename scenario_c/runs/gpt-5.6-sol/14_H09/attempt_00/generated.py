import gurobipy as gp
from gurobipy import GRB
import json

products = ["A", "B", "C"]
periods = [1, 2, 3, 4, 5, 6]

demand = {
    "A": {1: 12, 2: 18, 3: 14, 4: 20, 5: 16, 6: 19},
    "B": {1: 10, 2: 9, 3: 15, 4: 12, 5: 17, 6: 14},
    "C": {1: 8, 2: 11, 3: 10, 4: 13, 5: 9, 6: 15},
}

production_cost = {
    "A": {1: 7, 2: 8, 3: 9, 4: 7, 5: 10, 6: 8},
    "B": {1: 9, 2: 8, 3: 8, 4: 10, 5: 7, 6: 9},
    "C": {1: 11, 2: 10, 3: 12, 4: 9, 5: 11, 6: 8},
}

setup_cost = {"A": 35, "B": 40, "C": 45}
holding_cost = {"A": 2, "B": 2, "C": 3}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 5, "B": 4, "C": 3}

base_capacity = {1: 120, 2: 115, 3: 125, 4: 110, 5: 120, 6: 115}
overtime_cost = 18
max_overtime = 20
max_total_inventory = 40
required_final_inventory = 2

big_m = {
    (i, t): demand[i][t] + max_total_inventory
    for i in products
    for t in periods
}

model = gp.Model("H09_produzione_scorte_straordinario")
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

x = model.addVars(
    products, periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)

inventory = model.addVars(
    products, periods,
    vtype=GRB.INTEGER,
    lb=0,
    name="I"
)

setup = model.addVars(
    products, periods,
    vtype=GRB.BINARY,
    name="y"
)

overtime = model.addVars(
    periods,
    vtype=GRB.CONTINUOUS,
    lb=0,
    ub=max_overtime,
    name="o"
)

model.setObjective(
    gp.quicksum(
        production_cost[i][t] * x[i, t]
        + setup_cost[i] * setup[i, t]
        + holding_cost[i] * inventory[i, t]
        for i in products
        for t in periods
    )
    + gp.quicksum(overtime_cost * overtime[t] for t in periods),
    GRB.MINIMIZE
)

for i in products:
    model.addConstr(
        x[i, 1] - inventory[i, 1] == demand[i][1],
        name=f"balance_{i}_1"
    )
    for t in periods[1:]:
        model.addConstr(
            inventory[i, t - 1] + x[i, t] - inventory[i, t]
            == demand[i][t],
            name=f"balance_{i}_{t}"
        )

for i in products:
    for t in periods:
        model.addConstr(
            x[i, t] >= minimum_lot[i] * setup[i, t],
            name=f"minimum_lot_{i}_{t}"
        )
        model.addConstr(
            x[i, t] <= big_m[i, t] * setup[i, t],
            name=f"setup_link_{i}_{t}"
        )

for t in periods:
    model.addConstr(
        gp.quicksum(hours_per_unit[i] * x[i, t] for i in products)
        <= base_capacity[t] + overtime[t],
        name=f"capacity_{t}"
    )

model.addConstr(
    gp.quicksum(setup[i, 1] for i in products) <= 3,
    name="activations_1"
)

for t in periods[1:]:
    model.addConstr(
        gp.quicksum(setup[i, t] for i in products) <= 2,
        name=f"activations_{t}"
    )

for t in periods:
    model.addConstr(
        gp.quicksum(inventory[i, t] for i in products)
        <= max_total_inventory,
        name=f"inventory_limit_{t}"
    )

for i in products:
    model.addConstr(
        inventory[i, 6] >= required_final_inventory,
        name=f"final_inventory_{i}"
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
}

solver_status = status_names.get(model.Status, str(model.Status))

if model.Status == GRB.OPTIMAL:
    def clean_value(variable):
        value = variable.X
        if abs(value) <= 1e-8:
            return 0.0
        if variable.VType != GRB.CONTINUOUS and abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(value)

    all_variables = {}
    for variable in model.getVars():
        all_variables[variable.VarName] = clean_value(variable)

    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": all_variables
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":"), allow_nan=False))
