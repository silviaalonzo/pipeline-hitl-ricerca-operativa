import gurobipy as gp
from gurobipy import GRB
import json

nodes = ["S", "A", "B", "C", "T"]

arcs = [
    ("S", "A"),
    ("S", "B"),
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("B", "T"),
    ("C", "T"),
]

fixed_cost = {
    ("S", "A"): 40,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 30,
    ("B", "C"): 18,
    ("B", "T"): 45,
    ("C", "T"): 38,
}

unit_cost = {
    ("S", "A"): 2,
    ("S", "B"): 3,
    ("A", "B"): 1,
    ("A", "C"): 2,
    ("B", "C"): 2,
    ("B", "T"): 4,
    ("C", "T"): 2,
}

capacity = {
    ("S", "A"): 30,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 25,
    ("B", "C"): 20,
    ("B", "T"): 25,
    ("C", "T"): 35,
}

balance = {
    "S": 40,
    "A": 0,
    "B": 0,
    "C": 0,
    "T": -40,
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M10_rete_distributiva", env=env)

x = {
    (i, j): model.addVar(
        lb=0,
        ub=capacity[i, j],
        vtype=GRB.INTEGER,
        name=f"x_{i}_{j}"
    )
    for i, j in arcs
}

y = {
    (i, j): model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}_{j}"
    )
    for i, j in arcs
}

model.setObjective(
    gp.quicksum(
        fixed_cost[i, j] * y[i, j] + unit_cost[i, j] * x[i, j]
        for i, j in arcs
    ),
    GRB.MINIMIZE
)

for node in nodes:
    outgoing = gp.quicksum(x[i, j] for i, j in arcs if i == node)
    incoming = gp.quicksum(x[i, j] for i, j in arcs if j == node)
    model.addConstr(
        outgoing - incoming == balance[node],
        name=f"balance_{node}"
    )

for i, j in arcs:
    model.addConstr(
        x[i, j] <= capacity[i, j] * y[i, j],
        name=f"activation_{i}_{j}"
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
    17: "MEM_LIMIT",
}

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    def numeric_value(value):
        rounded = round(value)
        if abs(value - rounded) <= 1e-6:
            return float(rounded)
        return float(value)

    variable_values = {}
    for i, j in arcs:
        variable_values[f"x_{i}_{j}"] = numeric_value(x[i, j].X)
    for i, j in arcs:
        variable_values[f"y_{i}_{j}"] = numeric_value(y[i, j].X)

    result = {
        "status": status,
        "objective": numeric_value(model.ObjVal),
        "variables": variable_values,
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
