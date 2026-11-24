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

minimum_throughput = 20
emission_limit = 470

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
    (site, zone): cost_rows[zone][k]
    for zone in zones
    for k, site in enumerate(sites)
}

emission = {
    (site, zone): emission_rows[zone][k]
    for zone in zones
    for k, site in enumerate(sites)
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("capacitated_distribution_network", env=env)
model.Params.OutputFlag = 0

y = {
    site: model.addVar(vtype=GRB.BINARY, name="y_" + site)
    for site in sites
}

x = {
    (site, zone): model.addVar(
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="x_" + site + "_" + zone
    )
    for site in sites
    for zone in zones
}

model.setObjective(
    gp.quicksum(fixed_cost[site] * y[site] for site in sites)
    + gp.quicksum(
        unit_cost[site, zone] * x[site, zone]
        for site in sites
        for zone in zones
    ),
    GRB.MINIMIZE
)

for zone in zones:
    model.addConstr(
        gp.quicksum(x[site, zone] for site in sites) == demand[zone],
        name="demand_" + zone
    )

for site in sites:
    throughput = gp.quicksum(x[site, zone] for zone in zones)
    model.addConstr(
        throughput >= minimum_throughput * y[site],
        name="minimum_throughput_" + site
    )
    model.addConstr(
        throughput <= capacity[site] * y[site],
        name="capacity_" + site
    )

model.addConstr(
    gp.quicksum(y[site] for site in sites) >= 3,
    name="minimum_open_centers"
)

model.addConstr(
    gp.quicksum(y[site] for site in sites) <= 4,
    name="maximum_open_centers"
)

model.addConstr(
    gp.quicksum(y[site] for site in north) >= 1,
    name="north_resilience"
)

model.addConstr(
    gp.quicksum(y[site] for site in south) >= 1,
    name="south_resilience"
)

model.addConstr(
    gp.quicksum(
        emission[site, zone] * x[site, zone]
        for site in sites
        for zone in zones
    ) <= emission_limit,
    name="emission_limit"
)

model.optimize()

status_names = {}
for status_name in [
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT",
    "SOLUTION_LIMIT", "INTERRUPTED", "NUMERIC", "SUBOPTIMAL",
    "INPROGRESS", "USER_OBJ_LIMIT", "WORK_LIMIT", "MEM_LIMIT"
]:
    status_code = getattr(GRB, status_name, None)
    if status_code is not None:
        status_names[status_code] = status_name

solver_status = status_names.get(model.Status, "STATUS_" + str(model.Status))

def clean_value(value):
    if abs(value) <= 1e-9:
        return 0.0
    nearest_integer = round(value)
    if abs(value - nearest_integer) <= 1e-9:
        return float(nearest_integer)
    return float(value)

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": clean_value(model.ObjVal),
        "variables": {
            variable.VarName: clean_value(variable.X)
            for variable in model.getVars()
        }
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
