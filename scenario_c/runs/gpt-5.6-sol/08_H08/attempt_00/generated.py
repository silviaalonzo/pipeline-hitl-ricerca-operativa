import gurobipy as gp
from gurobipy import GRB
import json

stations = ["A", "B", "C", "D", "E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6",
         "Z7", "Z8", "Z9", "Z10", "Z11", "Z12"]

west = ["A", "B", "C", "D"]
east = ["E", "F", "G", "H"]
critical_zones = ["Z3", "Z8", "Z11"]

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

travel_time = {
    "Z1":  {"A": 3,  "B": 5},
    "Z2":  {"A": 6,  "B": 8,  "C": 10},
    "Z3":  {"B": 11, "C": 4,  "D": 6},
    "Z4":  {"C": 7,  "D": 9},
    "Z5":  {"A": 6,  "D": 3,  "E": 5},
    "Z6":  {"B": 11, "E": 8,  "F": 10},
    "Z7":  {"C": 7,  "F": 4,  "G": 6, "H": 8},
    "Z8":  {"D": 3,  "G": 9,  "H": 11},
    "Z9":  {"E": 8,  "F": 10, "H": 5},
    "Z10": {"F": 4,  "G": 6,  "H": 8},
    "Z11": {"A": 6,  "E": 5,  "H": 11},
    "Z12": {"B": 11, "G": 3,  "H": 5}
}

model = gp.Model("H08_rete_emergenza_backup")
model.Params.OutputFlag = 0

y = {
    i: model.addVar(vtype=GRB.BINARY, name="y_" + i)
    for i in stations
}

x = {
    (j, i): model.addVar(vtype=GRB.BINARY, name="x_" + j + "_" + i)
    for j in zones
    for i in travel_time[j]
}

model.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in stations)
    + gp.quicksum(
        demand[j] * travel_time[j][i] * x[j, i]
        for j in zones
        for i in travel_time[j]
    ),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(y[i] for i in stations) == 4,
    name="exactly_four_stations"
)

model.addConstr(
    gp.quicksum(y[i] for i in west) >= 1,
    name="at_least_one_west"
)

model.addConstr(
    gp.quicksum(y[i] for i in east) >= 1,
    name="at_least_one_east"
)

for j in zones:
    model.addConstr(
        gp.quicksum(x[j, i] for i in travel_time[j]) == 1,
        name="assign_" + j
    )

for j in zones:
    for i in travel_time[j]:
        model.addConstr(
            x[j, i] <= y[i],
            name="activation_" + j + "_" + i
        )

for i in stations:
    model.addConstr(
        gp.quicksum(
            demand[j] * x[j, i]
            for j in zones
            if i in travel_time[j]
        ) <= capacity[i] * y[i],
        name="capacity_" + i
    )

for j in critical_zones:
    model.addConstr(
        gp.quicksum(y[i] for i in travel_time[j]) >= 2,
        name="backup_" + j
    )

model.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.NUMERIC: "NUMERIC"
}

solver_status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    decision_variables = (
        [y[i] for i in stations]
        + [x[j, i] for j in zones for i in travel_time[j]]
    )
    variable_values = {
        var.VarName: float(round(var.X))
        for var in decision_variables
    }
    result = {
        "status": solver_status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
