import json
import gurobipy as gp
from gurobipy import GRB

vehicles = [
    "E1", "E2", "E3",
    "D1", "D2", "D3", "D4", "D5"
]

routes = [
    "R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08",
    "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16"
]

electric_vehicles = ["E1", "E2", "E3"]
diesel_vehicles = ["D1", "D2", "D3", "D4", "D5"]

long_routes = ["R06", "R09", "R11", "R13", "R15", "R16"]
center_routes = ["R01", "R03", "R05", "R08", "R12"]

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

load = {
    "R01": 5, "R02": 7, "R03": 4, "R04": 8, "R05": 6, "R06": 9, "R07": 5, "R08": 7,
    "R09": 8, "R10": 6, "R11": 9, "R12": 7, "R13": 10, "R14": 6, "R15": 8, "R16": 5
}

distance = {
    "R01": 18, "R02": 28, "R03": 16, "R04": 34, "R05": 22, "R06": 51, "R07": 26, "R08": 20,
    "R09": 48, "R10": 31, "R11": 55, "R12": 24, "R13": 52, "R14": 29, "R15": 47, "R16": 45
}

assign_cost = {
    "E1": [9, 12, 15, 18, 21, 2, 14, 17, 10, 10, 3, 16, 9, 9, 2, 5],
    "E2": [16, 19, 9, 12, 15, 9, 21, 11, 5, 17, 11, 10, 4, 16, 10, 3],
    "E3": [10, 13, 16, 19, 9, 3, 15, 18, 11, 11, 4, 17, 10, 10, 3, 6],
    "D1": [17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10],
    "D2": [11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17],
    "D3": [18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11],
    "D4": [12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18],
    "D5": [19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12]
}

assignment_cost = {
    (v, r): assign_cost[v][routes.index(r)]
    for v in vehicles
    for r in routes
}

m = gp.Model("L01")
m.Params.OutputFlag = 0

x = {}
for v in vehicles:
    for r in routes:
        x[v, r] = m.addVar(vtype=GRB.BINARY, name=f"x_{v}_{r}")

y = {}
for v in vehicles:
    y[v] = m.addVar(vtype=GRB.BINARY, name=f"y_{v}")

m.update()

m.setObjective(
    gp.quicksum(fixed_cost[v] * y[v] for v in vehicles)
    + gp.quicksum(assignment_cost[v, r] * x[v, r] for v in vehicles for r in routes),
    GRB.MINIMIZE
)

for r in routes:
    m.addConstr(gp.quicksum(x[v, r] for v in vehicles) == 1, name=f"route_{r}")

for v in vehicles:
    for r in routes:
        m.addConstr(x[v, r] <= y[v], name=f"link_{v}_{r}")

    m.addConstr(
        gp.quicksum(load[r] * x[v, r] for r in routes) <= capacity[v] * y[v],
        name=f"capacity_{v}"
    )

    m.addConstr(
        gp.quicksum(x[v, r] for r in routes) <= max_routes[v] * y[v],
        name=f"max_routes_{v}"
    )

m.addConstr(gp.quicksum(y[v] for v in vehicles) <= 7, name="max_active_vehicles")
m.addConstr(gp.quicksum(y[v] for v in electric_vehicles) >= 2, name="min_electric")

for v in electric_vehicles:
    m.addConstr(
        gp.quicksum(x[v, r] for r in long_routes) <= 1,
        name=f"electric_long_{v}"
    )

for v in diesel_vehicles:
    m.addConstr(
        gp.quicksum(x[v, r] for r in center_routes) <= 2,
        name=f"diesel_center_{v}"
    )

m.addConstr(
    gp.quicksum(distance[r] * emission_factor[v] * x[v, r] for v in vehicles for r in routes) <= 1050,
    name="emission_limit"
)

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED"
}

status = status_map.get(m.status, f"STATUS_{m.status}")
objective = None
variables = {}

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {var.VarName: float(var.X) for var in m.getVars()}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective, "variables": variables},
    separators=(",", ":")
))
