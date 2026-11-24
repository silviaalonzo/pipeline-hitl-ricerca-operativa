import gurobipy as gp
import json

vehicles_data = [
    ("E1", "E", 62, 30, 3, 0),
    ("E2", "E", 58, 32, 3, 0),
    ("E3", "E", 55, 28, 3, 0),
    ("D1", "D", 46, 38, 4, 3),
    ("D2", "D", 44, 40, 4, 2),
    ("D3", "D", 41, 36, 4, 3),
    ("D4", "D", 49, 42, 4, 2),
    ("D5", "D", 43, 35, 4, 3),
]

routes_data = [
    ("R01", 5, 18),
    ("R02", 7, 28),
    ("R03", 4, 16),
    ("R04", 8, 34),
    ("R05", 6, 22),
    ("R06", 9, 51),
    ("R07", 5, 26),
    ("R08", 7, 20),
    ("R09", 8, 48),
    ("R10", 6, 31),
    ("R11", 9, 55),
    ("R12", 7, 24),
    ("R13", 10, 52),
    ("R14", 6, 29),
    ("R15", 8, 47),
    ("R16", 5, 45),
]

routes = [r[0] for r in routes_data]
load = {r[0]: r[1] for r in routes_data}
distance = {r[0]: r[2] for r in routes_data}

vehicle_names = [v[0] for v in vehicles_data]
vehicle_type = {v[0]: v[1] for v in vehicles_data}
fixed_cost = {v[0]: v[2] for v in vehicles_data}
capacity = {v[0]: v[3] for v in vehicles_data}
max_routes = {v[0]: v[4] for v in vehicles_data}
emission_factor = {v[0]: v[5] for v in vehicles_data}

electric = [v for v in vehicle_names if vehicle_type[v] == "E"]
diesel = [v for v in vehicle_names if vehicle_type[v] == "D"]

cost = {
    "E1": dict(zip(routes, [9, 12, 15, 18, 21, 2, 14, 17, 10, 10, 3, 16, 9, 9, 2, 5])),
    "E2": dict(zip(routes, [16, 19, 9, 12, 15, 9, 21, 11, 5, 17, 11, 10, 4, 16, 10, 3])),
    "E3": dict(zip(routes, [10, 13, 16, 19, 9, 3, 15, 18, 11, 11, 4, 17, 10, 10, 3, 6])),
    "D1": dict(zip(routes, [17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10])),
    "D2": dict(zip(routes, [11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17])),
    "D3": dict(zip(routes, [18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11])),
    "D4": dict(zip(routes, [12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18])),
    "D5": dict(zip(routes, [19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12])),
}

long_routes = ["R06", "R09", "R11", "R13", "R15", "R16"]
center_routes = ["R01", "R03", "R05", "R08", "R12"]

m = gp.Model("L01")
m.Params.OutputFlag = 0

y = {}
for v in vehicle_names:
    y[v] = m.addVar(vtype=gp.GRB.BINARY, name=f"y_{v}")

x = {}
for v in vehicle_names:
    for r in routes:
        x[v, r] = m.addVar(vtype=gp.GRB.BINARY, name=f"x_{v}_{r}")

m.setObjective(
    gp.quicksum(fixed_cost[v] * y[v] for v in vehicle_names)
    + gp.quicksum(cost[v][r] * x[v, r] for v in vehicle_names for r in routes),
    gp.GRB.MINIMIZE
)

for r in routes:
    m.addConstr(gp.quicksum(x[v, r] for v in vehicle_names) == 1, name=f"assign_{r}")

for v in vehicle_names:
    for r in routes:
        m.addConstr(x[v, r] <= y[v], name=f"link_{v}_{r}")

for v in vehicle_names:
    m.addConstr(y[v] <= gp.quicksum(x[v, r] for r in routes), name=f"activated_used_{v}")

for v in vehicle_names:
    m.addConstr(
        gp.quicksum(load[r] * x[v, r] for r in routes) <= capacity[v] * y[v],
        name=f"capacity_{v}"
    )
    m.addConstr(
        gp.quicksum(x[v, r] for r in routes) <= max_routes[v] * y[v],
        name=f"maxroutes_{v}"
    )

m.addConstr(gp.quicksum(y[v] for v in vehicle_names) <= 7, name="max_activation")
m.addConstr(gp.quicksum(y[v] for v in electric) >= 2, name="min_electric_activation")

for v in electric:
    m.addConstr(
        gp.quicksum(x[v, r] for r in long_routes) <= 1,
        name=f"electric_long_{v}"
    )

for v in diesel:
    m.addConstr(
        gp.quicksum(x[v, r] for r in center_routes) <= 2,
        name=f"diesel_center_{v}"
    )

m.addConstr(
    gp.quicksum(emission_factor[v] * distance[r] * x[v, r] for v in diesel for r in routes) <= 1050,
    name="emission_limit"
)

m.optimize()

status_names = {}
for sname in [
    "OPTIMAL", "INFEASIBLE", "UNBOUNDED", "INF_OR_UNBD", "CUTOFF",
    "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT", "SOLUTION_LIMIT",
    "INTERRUPTED", "NUMERIC", "SUBOPTIMAL", "INPROGRESS"
]:
    if hasattr(gp.GRB, sname):
        status_names[getattr(gp.GRB, sname)] = sname

if m.Status == gp.GRB.OPTIMAL:
    status_str = "OPTIMAL"
    objective = m.ObjVal
    solution_vars = {var.VarName: var.X for var in m.getVars()}
else:
    status_str = status_names.get(m.Status, str(m.Status))
    objective = None
    solution_vars = {}

output = {
    "status": status_str,
    "objective": objective,
    "variables": solution_vars,
}

print("SOLUTION_JSON=" + json.dumps(output, separators=(",", ":")))
