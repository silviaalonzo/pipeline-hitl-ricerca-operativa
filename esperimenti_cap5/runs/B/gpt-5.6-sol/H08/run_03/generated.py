import gurobipy as gp
from gurobipy import GRB
import json

stations = ["A", "B", "C", "D", "E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6",
         "Z7", "Z8", "Z9", "Z10", "Z11", "Z12"]

west = ["A", "B", "C", "D"]
east = ["E", "F", "G", "H"]
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

times = {
    "Z1": {"A": 3, "B": 5},
    "Z2": {"A": 6, "B": 8, "C": 10},
    "Z3": {"B": 11, "C": 4, "D": 6},
    "Z4": {"C": 7, "D": 9},
    "Z5": {"A": 6, "D": 3, "E": 5},
    "Z6": {"B": 11, "E": 8, "F": 10},
    "Z7": {"C": 7, "F": 4, "G": 6, "H": 8},
    "Z8": {"D": 3, "G": 9, "H": 11},
    "Z9": {"E": 8, "F": 10, "H": 5},
    "Z10": {"F": 4, "G": 6, "H": 8},
    "Z11": {"A": 6, "E": 5, "H": 11},
    "Z12": {"B": 11, "G": 3, "H": 5}
}

arcs = [(z, i) for z in zones for i in times[z]]

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H08_rete_emergenza", env=env)
model.Params.OutputFlag = 0

y = {
    i: model.addVar(vtype=GRB.BINARY, name="y_" + i)
    for i in stations
}

x = {
    (z, i): model.addVar(vtype=GRB.BINARY, name="x_" + z + "_" + i)
    for z, i in arcs
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in stations)
    + gp.quicksum(
        demand[z] * times[z][i] * x[z, i]
        for z, i in arcs
    ),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(y[i] for i in stations) == 4,
    name="exactly_four_stations"
)

for z in zones:
    model.addConstr(
        gp.quicksum(x[z, i] for i in times[z]) == 1,
        name="assignment_" + z
    )

for z, i in arcs:
    model.addConstr(
        x[z, i] <= y[i],
        name="open_link_" + z + "_" + i
    )

for i in stations:
    model.addConstr(
        gp.quicksum(
            demand[z] * x[z, i]
            for z in zones if (z, i) in x
        ) <= capacity[i] * y[i],
        name="capacity_" + i
    )

model.addConstr(
    gp.quicksum(y[i] for i in west) >= 1,
    name="west_station"
)

model.addConstr(
    gp.quicksum(y[i] for i in east) >= 1,
    name="east_station"
)

for z in critical:
    model.addConstr(
        gp.quicksum(y[i] for i in times[z]) >= 2,
        name="backup_" + z
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
payload = {
    "status": status,
    "objective": None,
    "variables": {}
}

if model.Status == GRB.OPTIMAL:
    values = {}
    for i in stations:
        values["y_" + i] = float(round(y[i].X))
    for z, i in arcs:
        values["x_" + z + "_" + i] = float(round(x[z, i].X))

    payload["objective"] = float(round(model.ObjVal, 10))
    payload["variables"] = values

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
