import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["A", "B", "C", "D"]

unit_cost = {"A": 11, "B": 10, "C": 12, "D": 9}
fixed_cost = {"A": 80, "B": 95, "C": 60, "D": 120}
capacity = {"A": 80, "B": 100, "C": 70, "D": 90}
minimum_order = {"A": 20, "B": 25, "C": 15, "D": 20}
quality = {"A": 96, "B": 90, "C": 98, "D": 88}
emissions = {"A": 3, "B": 4, "C": 2, "D": 5}

demand = 180
minimum_quality = 92
maximum_emissions = 650

model = gp.Model("M07_supplier_selection")
model.Params.OutputFlag = 0

x = {
    i: model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name="x_" + i
    )
    for i in suppliers
}

y = {
    i: model.addVar(
        vtype=GRB.BINARY,
        name="y_" + i
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
    name="exact_demand"
)

model.addConstr(
    gp.quicksum(y[i] for i in suppliers) >= 2,
    name="minimum_two_suppliers"
)

for i in suppliers:
    model.addConstr(
        x[i] >= minimum_order[i] * y[i],
        name="minimum_order_" + i
    )
    model.addConstr(
        x[i] <= capacity[i] * y[i],
        name="capacity_" + i
    )

model.addConstr(
    gp.quicksum(quality[i] * x[i] for i in suppliers)
    >= minimum_quality * demand,
    name="minimum_weighted_quality"
)

model.addConstr(
    gp.quicksum(emissions[i] * x[i] for i in suppliers)
    <= maximum_emissions,
    name="maximum_emissions"
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

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for i in suppliers:
        variable_values["x_" + i] = float(round(x[i].X))
    for i in suppliers:
        variable_values["y_" + i] = float(round(y[i].X))

    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
