import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["A", "B", "C", "D", "E", "F"]
components = ["C1", "C2", "C3"]

demand = {"C1": 80, "C2": 70, "C3": 60}
fixed_cost = {"A": 120, "B": 140, "C": 100, "D": 150, "E": 90, "F": 110}
capacity = {"A": 100, "B": 110, "C": 90, "D": 120, "E": 80, "F": 95}
risk = {"A": 2, "B": 3, "C": 1, "D": 4, "E": 2, "F": 3}

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

arcs = list(unit_cost.keys())
min_lot = 10
min_quality = 95
max_risk = 580
max_suppliers = 4

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H07_sourcing", env=env)

y = {
    i: model.addVar(vtype=GRB.BINARY, name=f"y_{i}")
    for i in suppliers
}
z = {
    (i, j): model.addVar(vtype=GRB.BINARY, name=f"z_{i}_{j}")
    for i, j in arcs
}
x = {
    (i, j): model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{i}_{j}")
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
        name=f"demand_{j}"
    )

for i, j in arcs:
    model.addConstr(
        x[i, j] >= min_lot * z[i, j],
        name=f"min_lot_{i}_{j}"
    )
    model.addConstr(
        x[i, j] <= demand[j] * z[i, j],
        name=f"use_link_{i}_{j}"
    )
    model.addConstr(
        z[i, j] <= y[i],
        name=f"activation_link_{i}_{j}"
    )

for j in components:
    model.addConstr(
        gp.quicksum(z[i, j] for i in suppliers if (i, j) in z) >= 2,
        name=f"multisourcing_{j}"
    )

for i in suppliers:
    supplier_arcs = [(ii, j) for ii, j in arcs if ii == i]
    model.addConstr(
        y[i] <= gp.quicksum(z[ii, j] for ii, j in supplier_arcs),
        name=f"active_if_used_{i}"
    )
    model.addConstr(
        gp.quicksum(x[ii, j] for ii, j in supplier_arcs)
        <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

for j in components:
    model.addConstr(
        gp.quicksum(
            quality[i, j] * x[i, j]
            for i in suppliers if (i, j) in x
        ) >= min_quality * demand[j],
        name=f"quality_{j}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in suppliers) <= max_suppliers,
    name="max_suppliers"
)

model.addConstr(
    y["A"] + y["B"] >= 1,
    name="at_least_A_or_B"
)

model.addConstr(
    gp.quicksum(risk[i] * x[i, j] for i, j in arcs) <= max_risk,
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

if model.Status == GRB.OPTIMAL:
    def numeric_value(var):
        value = var.X
        if abs(value) < 1e-7:
            return 0.0
        nearest_integer = round(value)
        if abs(value - nearest_integer) < 1e-7:
            return float(nearest_integer)
        return float(value)

    variable_values = {
        var.VarName: numeric_value(var)
        for var in model.getVars()
    }
    objective_value = float(round(model.ObjVal, 10))
    payload = {
        "status": "OPTIMAL",
        "objective": objective_value,
        "variables": variable_values
    }
else:
    payload = {
        "status": status_names.get(model.Status, "STATUS_" + str(model.Status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
