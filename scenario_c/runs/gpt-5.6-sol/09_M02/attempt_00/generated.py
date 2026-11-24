import json
import gurobipy as gp
from gurobipy import GRB

products = ["A", "B", "C", "D"]

margin = {"A": 42, "B": 36, "C": 50, "D": 31}
setup = {"A": 80, "B": 65, "C": 90, "D": 50}
machine_hours = {"A": 3, "B": 2, "C": 4, "D": 1}
labor_hours = {"A": 2, "B": 3, "C": 2, "D": 2}
minimum_lot = {"A": 4, "B": 5, "C": 3, "D": 6}
maximum_demand = {"A": 20, "B": 25, "C": 16, "D": 30}

machine_capacity = 90
labor_capacity = 100

model = gp.Model("production_with_setup")
model.Params.OutputFlag = 0

x = {
    i: model.addVar(
        lb=0,
        ub=maximum_demand[i],
        vtype=GRB.INTEGER,
        name=f"x_{i}"
    )
    for i in products
}

y = {
    i: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}"
    )
    for i in products
}

model.setObjective(
    gp.quicksum(margin[i] * x[i] - setup[i] * y[i] for i in products),
    GRB.MAXIMIZE
)

model.addConstr(
    gp.quicksum(machine_hours[i] * x[i] for i in products)
    <= machine_capacity,
    name="machine_capacity"
)

model.addConstr(
    gp.quicksum(labor_hours[i] * x[i] for i in products)
    <= labor_capacity,
    name="labor_capacity"
)

for i in products:
    model.addConstr(
        x[i] >= minimum_lot[i] * y[i],
        name=f"minimum_lot_{i}"
    )
    model.addConstr(
        x[i] <= maximum_demand[i] * y[i],
        name=f"maximum_demand_{i}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in products) >= 2,
    name="minimum_number_of_products"
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
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT"
}

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    def clean(value):
        value = float(value)
        if abs(value) < 1e-9:
            return 0.0
        nearest_integer = round(value)
        if abs(value - nearest_integer) < 1e-9:
            return float(nearest_integer)
        return float(round(value, 10))

    variable_values = {}
    for i in products:
        variable_values[f"x_{i}"] = clean(x[i].X)
    for i in products:
        variable_values[f"y_{i}"] = clean(y[i].X)

    result = {
        "status": solver_status,
        "objective": clean(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
