import json
import gurobipy as gp
from gurobipy import GRB

products = ["P1", "P2", "P3"]
periods = list(range(1, 9))

initial = {"P1": 22, "P2": 18, "P3": 25}
final_min = {"P1": 18, "P2": 15, "P3": 20}
hours_unit = {"P1": 2, "P2": 3, "P3": 1}
lot_min = {"P1": 24, "P2": 20, "P3": 28}
lot_max = {"P1": 82, "P2": 70, "P3": 90}
setup_cost = {"P1": 52, "P2": 60, "P3": 45}
hold_cost = {"P1": 1.2, "P2": 1.6, "P3": 0.9}

demand = {
    ("P1", 1): 34, ("P1", 2): 48, ("P1", 3): 42, ("P1", 4): 55,
    ("P1", 5): 38, ("P1", 6): 50, ("P1", 7): 46, ("P1", 8): 40,
    ("P2", 1): 28, ("P2", 2): 32, ("P2", 3): 45, ("P2", 4): 36,
    ("P2", 5): 50, ("P2", 6): 34, ("P2", 7): 42, ("P2", 8): 39,
    ("P3", 1): 40, ("P3", 2): 35, ("P3", 3): 38, ("P3", 4): 44,
    ("P3", 5): 36, ("P3", 6): 48, ("P3", 7): 41, ("P3", 8): 45,
}

prod_cost = {
    ("P1", 1): 5, ("P1", 2): 8, ("P1", 3): 5, ("P1", 4): 8,
    ("P1", 5): 5, ("P1", 6): 8, ("P1", 7): 5, ("P1", 8): 8,
    ("P2", 1): 7, ("P2", 2): 10, ("P2", 3): 7, ("P2", 4): 10,
    ("P2", 5): 7, ("P2", 6): 10, ("P2", 7): 7, ("P2", 8): 10,
    ("P3", 1): 9, ("P3", 2): 6, ("P3", 3): 9, ("P3", 4): 6,
    ("P3", 5): 9, ("P3", 6): 6, ("P3", 7): 9, ("P3", 8): 6,
}

capacity = {1: 250, 2: 245, 3: 235, 4: 260, 5: 240, 6: 255, 7: 245, 8: 265}

m = gp.Model("L02")
m.setParam("OutputFlag", 0)

x = {}
I = {}
y = {}

for p in products:
    for t in periods:
        x[p, t] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{p}_T{t}")
        I[p, t] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"I_{p}_T{t}")
        y[p, t] = m.addVar(vtype=GRB.BINARY, name=f"y_{p}_T{t}")

m.update()

m.setObjective(
    gp.quicksum(
        prod_cost[p, t] * x[p, t]
        + setup_cost[p] * y[p, t]
        + hold_cost[p] * I[p, t]
        for p in products
        for t in periods
    ),
    GRB.MINIMIZE,
)

# Bilanci di magazzino e limiti di scorta per prodotto
for p in products:
    for t in periods:
        if t == 1:
            m.addConstr(I[p, t] == initial[p] + x[p, t] - demand[p, t], name=f"bal_{p}_T{t}")
        else:
            m.addConstr(I[p, t] == I[p, t - 1] + x[p, t] - demand[p, t], name=f"bal_{p}_T{t}")

        m.addConstr(I[p, t] <= 75, name=f"inv_ub_{p}_T{t}")

    m.addConstr(I[p, 8] >= final_min[p], name=f"final_{p}")

# Scorta complessiva
for t in periods:
    m.addConstr(gp.quicksum(I[p, t] for p in products) <= 150, name=f"inv_tot_T{t}")

# Vincoli di setup e lotto
for p in products:
    for t in periods:
        m.addConstr(x[p, t] >= lot_min[p] * y[p, t], name=f"lotmin_{p}_T{t}")
        m.addConstr(x[p, t] <= lot_max[p] * y[p, t], name=f"lotmax_{p}_T{t}")

# Capacità produttiva condivisa
for t in periods:
    m.addConstr(
        gp.quicksum(hours_unit[p] * x[p, t] for p in products) <= capacity[t],
        name=f"capacity_T{t}",
    )

# Limiti sui setup
m.addConstr(
    gp.quicksum(y[p, t] for p in products for t in periods) <= 18,
    name="setup_total",
)

for t in [3, 6]:
    m.addConstr(
        gp.quicksum(y[p, t] for p in products) <= 2,
        name=f"setup_limit_T{t}",
    )

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INTERRUPTED: "INTERRUPTED",
}

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status = status_map.get(m.Status, str(m.Status))
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective, "variables": variables},
    ensure_ascii=False,
))
