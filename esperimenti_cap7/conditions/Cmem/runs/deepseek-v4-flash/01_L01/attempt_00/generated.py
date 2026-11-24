import json
import gurobipy as gp
from gurobipy import GRB

vehicles = ["E1", "E2", "E3", "D1", "D2", "D3", "D4", "D5"]
routes = ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08",
          "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16"]

electric = {"E1", "E2", "E3"}
diesel = {"D1", "D2", "D3", "D4", "D5"}
long_routes = {"R06", "R09", "R11", "R13", "R15", "R16"}
center_routes = {"R01", "R03", "R05", "R08", "R12"}

load = {
    "R01": 5, "R02": 7, "R03": 4, "R04": 8, "R05": 6, "R06": 9,
    "R07": 5, "R08": 7, "R09": 8, "R10": 6, "R11": 9, "R12": 7,
    "R13": 10, "R14": 6, "R15": 8, "R16": 5
}

distance = {
    "R01": 18, "R02": 28, "R03": 16, "R04": 34, "R05": 22, "R06": 51,
    "R07": 26, "R08": 20, "R09": 48, "R10": 31, "R11": 55, "R12": 24,
    "R13": 52, "R14": 29, "R15": 47, "R16": 45
}

fixed_cost = {
    "E1": 62, "E2": 58, "E3": 55,
    "D1": 46, "D2": 44, "D3": 41, "D4": 49, "D5": 43
}

capacity = {
    "E1": 30, "E2": 32, "E3": 28,
    "D1": 38, "D2": 40, "D3": 36, "D4": 42, "D5": 35
}

max_routes = {
    "E1": 3, "E2": 3, "E3": 3,
    "D1": 4, "D2": 4, "D3": 4, "D4": 4, "D5": 4
}

emission_factor = {
    "E1": 0, "E2": 0, "E3": 0,
    "D1": 3, "D2": 2, "D3": 3, "D4": 2, "D5": 3
}

cost_rows = {
    "E1": [9, 12, 15, 18, 21, 2, 14, 17, 10, 10, 3, 16, 9, 9, 2, 5],
    "E2": [16, 19, 9, 12, 15, 9, 21, 11, 5, 17, 11, 10, 4, 16, 10, 3],
    "E3": [10, 13, 16, 19, 9, 3, 15, 18, 11, 11, 4, 17, 10, 10, 3, 6],
    "D1": [17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10],
    "D2": [11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17],
    "D3": [18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11],
    "D4": [12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18],
    "D5": [19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12]
}

cost = {}
for i in vehicles:
    for j, r in enumerate(routes):
        cost[i, r] = cost_rows[i][j]

m = gp.Model("route_assignment")
m.Params.OutputFlag = 0

y = {}
for i in vehicles:
    y[i] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}")

x = {}
for i in vehicles:
    for r in routes:
        x[i, r] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{r}")

m.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in vehicles) +
    gp.quicksum(cost[i, r] * x[i, r] for i in vehicles for r in routes),
    GRB.MINIMIZE
)

# Ogni rotta assegnata esattamente a un veicolo
for r in routes:
    m.addConstr(gp.quicksum(x[i, r] for i in vehicles) == 1, name=f"assign_{r}")

# Veicolo usato solo se attivato
for i in vehicles:
    for r in routes:
        m.addConstr(x[i, r] <= y[i], name=f"link_{i}_{r}")

# Capacità complessiva di carico
for i in vehicles:
    m.addConstr(
        gp.quicksum(load[r] * x[i, r] for r in routes) <= capacity[i] * y[i],
        name=f"capacity_{i}"
    )

# Numero massimo di rotte per veicolo
for i in vehicles:
    m.addConstr(
        gp.quicksum(x[i, r] for r in routes) <= max_routes[i] * y[i],
        name=f"max_routes_{i}"
    )

# Numero massimo di veicoli attivati
m.addConstr(gp.quicksum(y[i] for i in vehicles) <= 7, name="max_active_vehicles")

# Almeno due veicoli elettrici attivi
m.addConstr(gp.quicksum(y[i] for i in electric) >= 2, name="min_electric")

# Ogni elettrico può servire al massimo una rotta lunga
for i in electric:
    m.addConstr(
        gp.quicksum(x[i, r] for r in long_routes) <= 1,
        name=f"long_limit_{i}"
    )

# Ogni diesel può servire al massimo due rotte di centro
for i in diesel:
    m.addConstr(
        gp.quicksum(x[i, r] for r in center_routes) <= 2,
        name=f"center_limit_{i}"
    )

# Limite complessivo di emissioni
m.addConstr(
    gp.quicksum(distance[r] * emission_factor[i] * x[i, r]
                for i in vehicles for r in routes) <= 1050,
    name="emission_limit"
)

m.optimize()

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {}
    for i in vehicles:
        variables[f"y_{i}"] = float(y[i].X)
    for i in vehicles:
        for r in routes:
            variables[f"x_{i}_{r}"] = float(x[i, r].X)
else:
    status = str(m.Status)
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables
}))
