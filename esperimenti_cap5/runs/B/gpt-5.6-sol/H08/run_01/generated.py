import gurobipy as gp
from gurobipy import GRB
import json

stations = ["A", "B", "C", "D", "E", "F", "G", "H"]
west = ["A", "B", "C", "D"]
east = ["E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6",
         "Z7", "Z8", "Z9", "Z10", "Z11", "Z12"]
critical = ["Z3", "Z8", "Z11"]

fixed_cost = {
    "A": 35, "B": 32, "C": 40, "D": 30,
    "E": 38, "F": 33, "G": 36, "H": 31
}

capacity = {
    "A": 42, "B": 44, "C": 46, "D": 40,
    "E": 45, "F": 43, "G": 44, "H": 42
}

demand = {
    "Z1": 8, "Z2": 7, "Z3": 10, "Z4": 6,
    "Z5": 9, "Z6": 8, "Z7": 7, "Z8": 11,
    "Z9": 6, "Z10": 9, "Z11": 8, "Z12": 7
}

reachable = {
    "Z1": ["A", "B"],
    "Z2": ["A", "B", "C"],
    "Z3": ["B", "C", "D"],
    "Z4": ["C", "D"],
    "Z5": ["A", "D", "E"],
    "Z6": ["B", "E", "F"],
    "Z7": ["C", "F", "G", "H"],
    "Z8": ["D", "G", "H"],
    "Z9": ["E", "F", "H"],
    "Z10": ["F", "G", "H"],
    "Z11": ["A", "E", "H"],
    "Z12": ["B", "G", "H"]
}

travel_time = {
    ("Z1", "A"): 3, ("Z1", "B"): 5,
    ("Z2", "A"): 6, ("Z2", "B"): 8, ("Z2", "C"): 10,
    ("Z3", "B"): 11, ("Z3", "C"): 4, ("Z3", "D"): 6,
    ("Z4", "C"): 7, ("Z4", "D"): 9,
    ("Z5", "A"): 6, ("Z5", "D"): 3, ("Z5", "E"): 5,
    ("Z6", "B"): 11, ("Z6", "E"): 8, ("Z6", "F"): 10,
    ("Z7", "C"): 7, ("Z7", "F"): 4, ("Z7", "G"): 6, ("Z7", "H"): 8,
    ("Z8", "D"): 3, ("Z8", "G"): 9, ("Z8", "H"): 11,
    ("Z9", "E"): 8, ("Z9", "F"): 10, ("Z9", "H"): 5,
    ("Z10", "F"): 4, ("Z10", "G"): 6, ("Z10", "H"): 8,
    ("Z11", "A"): 6, ("Z11", "E"): 5, ("Z11", "H"): 11,
    ("Z12", "B"): 11, ("Z12", "G"): 3, ("Z12", "H"): 5
}

arcs = [(j, i) for j in zones for i in reachable[j]]

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H08_rete_emergenza", env=env)
model.Params.OutputFlag = 0

y = {
    i: model.addVar(vtype=GRB.BINARY, name=f"y_{i}")
    for i in stations
}

x = {
    (j, i): model.addVar(vtype=GRB.BINARY, name=f"x_{j}_{i}")
    for j, i in arcs
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in stations)
    + gp.quicksum(
        demand[j] * travel_time[j, i] * x[j, i]
        for j, i in arcs
    ),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(y[i] for i in stations) == 4,
    name="exactly_four_stations"
)

for j in zones:
    model.addConstr(
        gp.quicksum(x[j, i] for i in reachable[j]) == 1,
        name=f"assign_{j}"
    )

for j, i in arcs:
    model.addConstr(
        x[j, i] <= y[i],
        name=f"open_link_{j}_{i}"
    )

for i in stations:
    model.addConstr(
        gp.quicksum(
            demand[j] * x[j, i]
            for j in zones
            if (j, i) in x
        ) <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

model.addConstr(
    gp.quicksum(y[i] for i in west) >= 1,
    name="at_least_one_west"
)

model.addConstr(
    gp.quicksum(y[i] for i in east) >= 1,
    name="at_least_one_east"
)

for j in critical:
    model.addConstr(
        gp.quicksum(y[i] for i in reachable[j]) >= 2,
        name=f"backup_{j}"
    )

model.optimize()

status_names = {}
for status_name in [
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT",
    "SOLUTION_LIMIT", "INTERRUPTED", "NUMERIC", "SUBOPTIMAL",
    "INPROGRESS", "USER_OBJ_LIMIT", "WORK_LIMIT", "MEM_LIMIT"
]:
    if hasattr(GRB, status_name):
        status_names[getattr(GRB, status_name)] = status_name

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    all_variables = (
        [y[i] for i in stations]
        + [x[j, i] for j, i in arcs]
    )
    variable_values = {
        variable.VarName: float(round(variable.X))
        for variable in all_variables
    }
    payload = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    payload = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
