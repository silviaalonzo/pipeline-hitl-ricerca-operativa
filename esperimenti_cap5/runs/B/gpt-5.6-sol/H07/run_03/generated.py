import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["A", "B", "C", "D", "E", "F"]
components = ["C1", "C2", "C3"]

demand = {
    "C1": 80,
    "C2": 70,
    "C3": 60
}

fixed_cost = {
    "A": 120,
    "B": 140,
    "C": 100,
    "D": 150,
    "E": 90,
    "F": 110
}

capacity = {
    "A": 100,
    "B": 110,
    "C": 90,
    "D": 120,
    "E": 80,
    "F": 95
}

risk = {
    "A": 2,
    "B": 3,
    "C": 1,
    "D": 4,
    "E": 2,
    "F": 3
}

unit_cost = {
    ("A", "C1"): 9,  ("A", "C2"): 12, ("A", "C3"): 11,
    ("B", "C1"): 10, ("B", "C2"): 9,  ("B", "C3"): 12,
    ("C", "C1"): 11, ("C", "C2"): 10, ("C", "C3"): 9,
    ("D", "C2"): 11, ("D", "C3"): 10,
    ("E", "C1"): 12, ("E", "C2"): 8,
    ("F", "C1"): 10, ("F", "C3"): 8
}

quality = {
    ("A", "C1"): 96, ("A", "C2"): 94, ("A", "C3"): 95,
    ("B", "C1"): 93, ("B", "C2"): 97, ("B", "C3"): 92,
    ("C", "C1"): 98, ("C", "C2"): 95, ("C", "C3"): 96,
    ("D", "C2"): 94, ("D", "C3"): 93,
    ("E", "C1"): 97, ("E", "C2"): 98,
    ("F", "C1"): 94, ("F", "C3"): 98
}

arcs = [
    (i, j)
    for i in suppliers
    for j in components
    if (i, j) in unit_cost
]

minimum_order = 10
minimum_quality = 95
maximum_suppliers = 4
maximum_risk = 580

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.setParam("LogToConsole", 0)
env.start()

model = gp.Model("H07_sourcing", env=env)

y = {
    i: model.addVar(vtype=GRB.BINARY, name="y_" + i)
    for i in suppliers
}

z = {
    (i, j): model.addVar(vtype=GRB.BINARY, name="z_" + i + "_" + j)
    for i, j in arcs
}

x = {
    (i, j): model.addVar(vtype=GRB.INTEGER, lb=0, name="x_" + i + "_" + j)
    for i, j in arcs
}

model.setObjective(
    gp.quicksum(unit_cost[i, j] * x[i, j] for i, j in arcs)
    + gp.quicksum(fixed_cost[i] * y[i] for i in suppliers),
    GRB.MINIMIZE
)

for j in components:
    model.addConstr(
        gp.quicksum(x[i, j] for i in suppliers if (i, j) in x) == demand[j],
        name="demand_" + j
    )

for i in suppliers:
    model.addConstr(
        gp.quicksum(x[i, j] for j in components if (i, j) in x)
        <= capacity[i] * y[i],
        name="capacity_" + i
    )

for i, j in arcs:
    upper_bound = min(capacity[i], demand[j])
    model.addConstr(
        x[i, j] >= minimum_order * z[i, j],
        name="minimum_order_" + i + "_" + j
    )
    model.addConstr(
        x[i, j] <= upper_bound * z[i, j],
        name="maximum_order_" + i + "_" + j
    )
    model.addConstr(
        z[i, j] <= y[i],
        name="arc_activation_" + i + "_" + j
    )

for i in suppliers:
    model.addConstr(
        y[i] <= gp.quicksum(z[i, j] for j in components if (i, j) in z),
        name="supplier_usage_" + i
    )

for j in components:
    model.addConstr(
        gp.quicksum(z[i, j] for i in suppliers if (i, j) in z) >= 2,
        name="multisourcing_" + j
    )

for j in components:
    model.addConstr(
        gp.quicksum(
            quality[i, j] * x[i, j]
            for i in suppliers
            if (i, j) in x
        ) >= minimum_quality * demand[j],
        name="quality_" + j
    )

model.addConstr(
    gp.quicksum(y[i] for i in suppliers) <= maximum_suppliers,
    name="maximum_suppliers"
)

model.addConstr(
    y["A"] + y["B"] >= 1,
    name="at_least_A_or_B"
)

model.addConstr(
    gp.quicksum(risk[i] * x[i, j] for i, j in arcs) <= maximum_risk,
    name="risk_limit"
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
    ordered_variables = (
        [y[i] for i in suppliers]
        + [z[i, j] for i, j in arcs]
        + [x[i, j] for i, j in arcs]
    )
    variable_values = {
        variable.VarName: float(round(variable.X))
        for variable in ordered_variables
    }
    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 6)),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
