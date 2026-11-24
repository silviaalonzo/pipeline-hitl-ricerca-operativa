import gurobipy as gp
from gurobipy import GRB
import json

sites = ["A", "B", "C", "D", "E", "F"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8"]

north = ["A", "B", "C"]
south = ["D", "E", "F"]

demand = {
    "Z1": 30, "Z2": 25, "Z3": 35, "Z4": 20,
    "Z5": 28, "Z6": 32, "Z7": 24, "Z8": 26
}

fixed_cost = {
    "A": 110, "B": 95, "C": 120,
    "D": 90, "E": 105, "F": 100
}

capacity = {
    "A": 90, "B": 80, "C": 110,
    "D": 75, "E": 95, "F": 85
}

cost_rows = {
    "Z1": [4, 7, 6, 10, 9, 11],
    "Z2": [5, 4, 8, 9, 7, 10],
    "Z3": [7, 5, 4, 8, 9, 7],
    "Z4": [9, 8, 7, 4, 5, 6],
    "Z5": [8, 9, 6, 5, 4, 7],
    "Z6": [10, 8, 7, 6, 5, 4],
    "Z7": [6, 7, 5, 8, 6, 7],
    "Z8": [7, 6, 8, 5, 7, 4]
}

emission_rows = {
    "Z1": [1, 2, 2, 4, 3, 4],
    "Z2": [2, 1, 3, 3, 2, 4],
    "Z3": [3, 2, 1, 3, 4, 3],
    "Z4": [4, 3, 3, 1, 2, 2],
    "Z5": [3, 4, 2, 2, 1, 3],
    "Z6": [4, 3, 3, 2, 2, 1],
    "Z7": [2, 3, 1, 3, 2, 3],
    "Z8": [3, 2, 3, 1, 3, 1]
}

cost = {
    (i, j): cost_rows[j][sites.index(i)]
    for i in sites for j in zones
}

emission = {
    (i, j): emission_rows[j][sites.index(i)]
    for i in sites for j in zones
}

minimum_throughput = 20
emission_limit = 470

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H01_rete_capacitata", env=env)

y = {
    i: model.addVar(vtype=GRB.BINARY, name=f"y_{i}")
    for i in sites
}

x = {
    (i, j): model.addVar(
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name=f"x_{i}_{j}"
    )
    for i in sites for j in zones
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in sites)
    + gp.quicksum(
        cost[i, j] * x[i, j]
        for i in sites for j in zones
    ),
    GRB.MINIMIZE
)

for j in zones:
    model.addConstr(
        gp.quicksum(x[i, j] for i in sites) == demand[j],
        name=f"demand_{j}"
    )

for i in sites:
    throughput = gp.quicksum(x[i, j] for j in zones)

    model.addConstr(
        throughput <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

    model.addConstr(
        throughput >= minimum_throughput * y[i],
        name=f"minimum_throughput_{i}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in sites) >= 3,
    name="minimum_open_centers"
)

model.addConstr(
    gp.quicksum(y[i] for i in sites) <= 4,
    name="maximum_open_centers"
)

model.addConstr(
    gp.quicksum(y[i] for i in north) >= 1,
    name="north_resilience"
)

model.addConstr(
    gp.quicksum(y[i] for i in south) >= 1,
    name="south_resilience"
)

model.addConstr(
    gp.quicksum(
        emission[i, j] * x[i, j]
        for i in sites for j in zones
    ) <= emission_limit,
    name="emission_limit"
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

status = status_names.get(model.Status, "UNKNOWN")

def clean_value(value):
    if abs(value) <= 1e-8:
        return 0.0
    if abs(value - round(value)) <= 1e-8:
        return float(round(value))
    return float(value)

if model.Status == GRB.OPTIMAL:
    variable_values = {}

    for i in sites:
        variable_values[f"y_{i}"] = clean_value(y[i].X)

    for i in sites:
        for j in zones:
            variable_values[f"x_{i}_{j}"] = clean_value(x[i, j].X)

    result = {
        "status": status,
        "objective": clean_value(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))

model.dispose()
env.dispose()
