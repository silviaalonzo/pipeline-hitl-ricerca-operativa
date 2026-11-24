import json
import gurobipy as gp
from gurobipy import GRB

products = ["A", "B", "C", "D", "E"]
periods = list(range(1, 7))

initial_stock = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
final_min_stock = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
hours_per_unit = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
lot_min = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
lot_max = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
holding_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

demand = {
    ("A", 1): 38, ("A", 2): 42, ("A", 3): 35, ("A", 4): 50, ("A", 5): 45, ("A", 6): 40,
    ("B", 1): 32, ("B", 2): 36, ("B", 3): 44, ("B", 4): 38, ("B", 5): 46, ("B", 6): 34,
    ("C", 1): 25, ("C", 2): 30, ("C", 3): 28, ("C", 4): 35, ("C", 5): 30, ("C", 6): 32,
    ("D", 1): 40, ("D", 2): 35, ("D", 3): 45, ("D", 4): 42, ("D", 5): 38, ("D", 6): 48,
    ("E", 1): 20, ("E", 2): 24, ("E", 3): 22, ("E", 4): 28, ("E", 5): 26, ("E", 6): 25,
}

prod_cost = {
    ("A", 1): 4, ("A", 2): 6, ("A", 3): 8, ("A", 4): 10, ("A", 5): 5, ("A", 6): 7,
    ("B", 1): 7, ("B", 2): 9, ("B", 3): 4, ("B", 4): 6, ("B", 5): 8, ("B", 6): 10,
    ("C", 1): 10, ("C", 2): 5, ("C", 3): 7, ("C", 4): 9, ("C", 5): 4, ("C", 6): 6,
    ("D", 1): 6, ("D", 2): 8, ("D", 3): 10, ("D", 4): 5, ("D", 5): 7, ("D", 6): 9,
    ("E", 1): 9, ("E", 2): 4, ("E", 3): 6, ("E", 4): 8, ("E", 5): 10, ("E", 6): 5,
}

cap_ord = {1: 350, 2: 360, 3: 345, 4: 370, 5: 355, 6: 380}
overtime_max = {1: 85, 2: 80, 3: 90, 4: 75, 5: 85, 6: 80}
overtime_cost = {1: 7, 2: 8, 3: 7, 4: 9, 5: 8, 6: 7}
fixed_overtime = 25
min_overtime = 10

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

m = gp.Model("L04")
m.Params.OutputFlag = 0
m.Params.MIPGap = 0

Prod = m.addVars(products, periods, name="Prod", lb=0, vtype=GRB.INTEGER)
Inv = m.addVars(products, periods, name="Inv", lb=0, vtype=GRB.INTEGER)
Setup = m.addVars(products, periods, name="Setup", vtype=GRB.BINARY)
OT = m.addVars(periods, name="OT", lb=0, vtype=GRB.CONTINUOUS)
OTact = m.addVars(periods, name="OTact", vtype=GRB.BINARY)

for i in products:
    for t in periods:
        prev = initial_stock[i] if t == 1 else Inv[i, t - 1]
        m.addConstr(Inv[i, t] == prev + Prod[i, t] - demand[i, t], name=f"Balance_{i}_{t}")

for i in products:
    for t in periods:
        m.addConstr(Inv[i, t] <= 75, name=f"InvUB_{i}_{t}")

for i in products:
    m.addConstr(Inv[i, 6] >= final_min_stock[i], name=f"FinalMin_{i}")

for t in periods:
    m.addConstr(gp.quicksum(Inv[i, t] for i in products) <= 210, name=f"TotalInv_{t}")

for i in products:
    for t in periods:
        m.addConstr(Prod[i, t] <= lot_max[i] * Setup[i, t], name=f"MaxLot_{i}_{t}")
        m.addConstr(Prod[i, t] >= lot_min[i] * Setup[i, t], name=f"MinLot_{i}_{t}")

for t in periods:
    m.addConstr(gp.quicksum(Setup[i, t] for i in products) <= 4, name=f"SetupPeriod_{t}")

m.addConstr(gp.quicksum(Setup[i, t] for i in products for t in periods) <= 26, name="SetupTotal")

for t in periods:
    m.addConstr(gp.quicksum(hours_per_unit[i] * Prod[i, t] for i in products) <= cap_ord[t] + OT[t], name=f"Capacity_{t}")
    m.addConstr(OT[t] >= min_overtime * OTact[t], name=f"OTmin_{t}")
    m.addConstr(OT[t] <= overtime_max[t] * OTact[t], name=f"OTmax_{t}")

objective = (
    gp.quicksum(prod_cost[i, t] * Prod[i, t] for i in products for t in periods)
    + gp.quicksum(setup_cost[i] * Setup[i, t] for i in products for t in periods)
    + gp.quicksum(holding_cost[i] * Inv[i, t] for i in products for t in periods)
    + gp.quicksum(overtime_cost[t] * OT[t] for t in periods)
    + fixed_overtime * gp.quicksum(OTact[t] for t in periods)
)

m.setObjective(objective, GRB.MINIMIZE)
m.optimize()

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective_value = float(m.ObjVal)
    variables = {
        v.VarName: float(v.X)
        for v in sorted(m.getVars(), key=lambda var: var.VarName)
    }
else:
    status = status_names.get(m.Status, str(m.Status))
    objective_value = 0.0
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective_value, "variables": variables},
    separators=(",", ":"),
    ensure_ascii=False,
))
