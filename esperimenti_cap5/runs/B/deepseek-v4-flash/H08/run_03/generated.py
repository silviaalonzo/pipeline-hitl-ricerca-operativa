import gurobipy as grb
from gurobipy import GRB
import json

stations = ["A", "B", "C", "D", "E", "F", "G", "H"]
zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8", "Z9", "Z10", "Z11", "Z12"]

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
    "A": {"Z1": 3, "Z2": 6, "Z5": 6, "Z11": 6},
    "B": {"Z1": 5, "Z2": 8, "Z3": 11, "Z6": 11, "Z12": 11},
    "C": {"Z2": 10, "Z3": 4, "Z4": 7, "Z7": 7},
    "D": {"Z3": 6, "Z4": 9, "Z5": 3, "Z8": 3},
    "E": {"Z5": 5, "Z6": 8, "Z9": 8, "Z11": 5},
    "F": {"Z6": 10, "Z7": 4, "Z9": 10, "Z10": 4},
    "G": {"Z7": 6, "Z8": 9, "Z10": 6, "Z12": 3},
    "H": {"Z7": 8, "Z8": 11, "Z9": 5, "Z10": 8, "Z11": 11, "Z12": 5},
}

model = grb.Model("rete_emergenza")
model.setParam("OutputFlag", 0)

# Variabili y_i
y = {}
for i in stations:
    y[i] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}")

# Variabili x_ij
x = {}
for i in stations:
    for j in zones:
        x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

model.update()

# Funzione obiettivo
model.setObjective(
    grb.quicksum(fixed_cost[i] * y[i] for i in stations)
    + grb.quicksum(demand[j] * times[i][j] * x[i, j]
                   for i in stations for j in times[i]),
    GRB.MINIMIZE
)

# Vincoli di raggiungibilita'
for i in stations:
    for j in zones:
        if j not in times[i]:
            model.addConstr(x[i, j] == 0, name=f"unreachable_{i}_{j}")

# Ogni zona assegnata esattamente a una stazione
for j in zones:
    model.addConstr(grb.quicksum(x[i, j] for i in stations) == 1, name=f"assign_{j}")

# Vincoli di capacita'
for i in stations:
    model.addConstr(
        grb.quicksum(demand[j] * x[i, j] for j in zones) <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

# Apertura esattamente quattro stazioni
model.addConstr(grb.quicksum(y[i] for i in stations) == 4, name="open_four")

# Almeno una stazione a Ovest e una a Est
model.addConstr(grb.quicksum(y[i] for i in ["A", "B", "C", "D"]) >= 1, name="west")
model.addConstr(grb.quicksum(y[i] for i in ["E", "F", "G", "H"]) >= 1, name="east")

# Backup per zone critiche
critical_zones = ["Z3", "Z8", "Z11"]
for j in critical_zones:
    reachable_stations = [i for i in stations if j in times[i]]
    model.addConstr(
        grb.quicksum(y[i] for i in reachable_stations) >= 2,
        name=f"backup_{j}"
    )

model.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

if model.Status == GRB.OPTIMAL:
    variables = {}

    for i in stations:
        variables[f"y_{i}"] = y[i].X

    for i in stations:
        for j in zones:
            variables[f"x_{i}_{j}"] = x[i, j].X

    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variables,
    }
else:
    result = {
        "status": status_names.get(model.Status, str(model.Status)),
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
