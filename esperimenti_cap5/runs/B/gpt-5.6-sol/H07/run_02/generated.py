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
    ("A", "C1"): 9,
    ("A", "C2"): 12,
    ("A", "C3"): 11,
    ("B", "C1"): 10,
    ("B", "C2"): 9,
    ("B", "C3"): 12,
    ("C", "C1"): 11,
    ("C", "C2"): 10,
    ("C", "C3"): 9,
    ("D", "C2"): 11,
    ("D", "C3"): 10,
    ("E", "C1"): 12,
    ("E", "C2"): 8,
    ("F", "C1"): 10,
    ("F", "C3"): 8
}

quality = {
    ("A", "C1"): 96,
    ("A", "C2"): 94,
    ("A", "C3"): 95,
    ("B", "C1"): 93,
    ("B", "C2"): 97,
    ("B", "C3"): 92,
    ("C", "C1"): 98,
    ("C", "C2"): 95,
    ("C", "C3"): 96,
    ("D", "C2"): 94,
    ("D", "C3"): 93,
    ("E", "C1"): 97,
    ("E", "C2"): 98,
    ("F", "C1"): 94,
    ("F", "C3"): 98
}

arcs = list(unit_cost.keys())
minimum_lot = 10
minimum_quality = 95
maximum_risk = 580
maximum_suppliers = 4

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H07_sourcing", env=env)
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

x = {
    (i, j): model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name=f"x_{i}_{j}"
    )
    for i, j in arcs
}

z = {
    (i, j): model.addVar(
        vtype=GRB.BINARY,
        name=f"z_{i}_{j}"
    )
    for i, j in arcs
}

y = {
    i: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}"
    )
    for i in suppliers
}

model.setObjective(
    gp.quicksum(unit_cost[i, j] * x[i, j] for i, j in arcs)
    + gp.quicksum(fixed_cost[i] * y[i] for i in suppliers),
    GRB.MINIMIZE
)

for j in components:
    model.addConstr(
        gp.quicksum(x[i, j] for i in suppliers if (i, j) in x)
        == demand[j],
        name=f"demand_{j}"
    )

for i in suppliers:
    model.addConstr(
        gp.quicksum(x[i, j] for j in components if (i, j) in x)
        <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

for i, j in arcs:
    model.addConstr(
        x[i, j] >= minimum_lot * z[i, j],
        name=f"minimum_lot_{i}_{j}"
    )
    model.addConstr(
        x[i, j] <= demand[j] * z[i, j],
        name=f"usage_link_{i}_{j}"
    )
    model.addConstr(
        z[i, j] <= y[i],
        name=f"supplier_link_{i}_{j}"
    )

for i in suppliers:
    model.addConstr(
        y[i] <= gp.quicksum(z[i, j] for j in components if (i, j) in z),
        name=f"activation_definition_{i}"
    )

for j in components:
    model.addConstr(
        gp.quicksum(z[i, j] for i in suppliers if (i, j) in z) >= 2,
        name=f"multisourcing_{j}"
    )

for j in components:
    model.addConstr(
        gp.quicksum(
            quality[i, j] * x[i, j]
            for i in suppliers
            if (i, j) in x
        ) >= minimum_quality * demand[j],
        name=f"quality_{j}"
    )

model.addConstr(
    gp.quicksum(risk[i] * x[i, j] for i, j in arcs) <= maximum_risk,
    name="total_risk"
)

model.addConstr(
    gp.quicksum(y[i] for i in suppliers) <= maximum_suppliers,
    name="maximum_suppliers"
)

model.addConstr(
    y["A"] + y["B"] >= 1,
    name="at_least_A_or_B"
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

def clean_value(value):
    rounded = round(value)
    if abs(value - rounded) <= 1e-6:
        return float(rounded)
    return float(value)

if model.Status == GRB.OPTIMAL:
    all_variables = (
        [x[i, j] for i, j in arcs]
        + [z[i, j] for i, j in arcs]
        + [y[i] for i in suppliers]
    )
    result = {
        "status": "OPTIMAL",
        "objective": clean_value(model.ObjVal),
        "variables": {
            variable.VarName: clean_value(variable.X)
            for variable in all_variables
        }
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
