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

unit_cost = {
    (i, j): cost_rows[j][sites.index(i)]
    for i in sites for j in zones
}

emission = {
    (i, j): emission_rows[j][sites.index(i)]
    for i in sites for j in zones
}

min_throughput = 20
emission_limit = 470
min_open = 3
max_open = 4

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H01_rete_capacitata", env=env)
model.Params.OutputFlag = 0

y = {
    i: model.addVar(vtype=GRB.BINARY, name=f"y_{i}")
    for i in sites
}

x = {
    (i, j): model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"x_{i}_{j}")
    for i in sites for j in zones
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in sites)
    + gp.quicksum(unit_cost[i, j] * x[i, j] for i in sites for j in zones),
    GRB.MINIMIZE
)

for j in zones:
    model.addConstr(
        gp.quicksum(x[i, j] for i in sites) == demand[j],
        name=f"domanda_{j}"
    )

for i in sites:
    throughput = gp.quicksum(x[i, j] for j in zones)
    model.addConstr(
        throughput >= min_throughput * y[i],
        name=f"movimentazione_minima_{i}"
    )
    model.addConstr(
        throughput <= capacity[i] * y[i],
        name=f"capacita_{i}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in sites) >= min_open,
    name="numero_minimo_centri"
)

model.addConstr(
    gp.quicksum(y[i] for i in sites) <= max_open,
    name="numero_massimo_centri"
)

model.addConstr(
    gp.quicksum(y[i] for i in north) >= 1,
    name="resilienza_nord"
)

model.addConstr(
    gp.quicksum(y[i] for i in south) >= 1,
    name="resilienza_sud"
)

model.addConstr(
    gp.quicksum(
        emission[i, j] * x[i, j]
        for i in sites for j in zones
    ) <= emission_limit,
    name="limite_emissioni"
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
    GRB.SUBOPTIMAL: "SUBOPTIMAL"
}

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    def clean(value):
        value = round(float(value), 10)
        return 0.0 if abs(value) < 1e-9 else value

    variables = {}
    for i in sites:
        variables[f"y_{i}"] = clean(y[i].X)
    for i in sites:
        for j in zones:
            variables[f"x_{i}_{j}"] = clean(x[i, j].X)

    result = {
        "status": status,
        "objective": clean(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
