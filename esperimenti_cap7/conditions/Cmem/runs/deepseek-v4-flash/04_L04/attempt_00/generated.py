import json
import gurobipy as gp
from gurobipy import GRB

products = ["A", "B", "C", "D", "E"]
periods = ["T1", "T2", "T3", "T4", "T5", "T6"]

initial_stock = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
final_min = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
hours = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
lot_min = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
lot_max = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
holding_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

demand_data = {
    "A": [38, 42, 35, 50, 45, 40],
    "B": [32, 36, 44, 38, 46, 34],
    "C": [25, 30, 28, 35, 30, 32],
    "D": [40, 35, 45, 42, 38, 48],
    "E": [20, 24, 22, 28, 26, 25]
}
demand = {p: {periods[i]: v for i, v in enumerate(vals)} for p, vals in demand_data.items()}

production_cost_data = {
    "A": [4, 6, 8, 10, 5, 7],
    "B": [7, 9, 4, 6, 8, 10],
    "C": [10, 5, 7, 9, 4, 6],
    "D": [6, 8, 10, 5, 7, 9],
    "E": [9, 4, 6, 8, 10, 5]
}
production_cost = {p: {periods[i]: v for i, v in enumerate(vals)} for p, vals in production_cost_data.items()}

capacity = {"T1": 350, "T2": 360, "T3": 345, "T4": 370, "T5": 355, "T6": 380}
ot_max = {"T1": 85, "T2": 80, "T3": 90, "T4": 75, "T5": 85, "T6": 80}
ot_cost = {"T1": 7, "T2": 8, "T3": 7, "T4": 9, "T5": 8, "T6": 7}

fixed_ot = 25
stock_max = 75
total_stock_max = 210
max_total_setups = 26
max_period_setups = 4

m = gp.Model("L04")
m.Params.OutputFlag = 0

x = m.addVars(products, periods, lb=0, vtype=GRB.INTEGER, name="x")
s = m.addVars(products, periods, lb=0, vtype=GRB.INTEGER, name="s")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")
o = m.addVars(periods, lb=0, vtype=GRB.INTEGER, name="o")
z = m.addVars(periods, vtype=GRB.BINARY, name="z")

# Bilanci di scorta
for p in products:
    for idx, t in enumerate(periods):
        if idx == 0:
            m.addConstr(s[p, t] == initial_stock[p] + x[p, t] - demand[p][t], name=f"balance_{p}_{t}")
        else:
            prev = periods[idx - 1]
            m.addConstr(s[p, t] == s[p, prev] + x[p, t] - demand[p][t], name=f"balance_{p}_{t}")

# Setup e limiti di lotto
for p in products:
    for t in periods:
        m.addConstr(x[p, t] >= lot_min[p] * y[p, t], name=f"lotmin_{p}_{t}")
        m.addConstr(x[p, t] <= lot_max[p] * y[p, t], name=f"lotmax_{p}_{t}")

# Limiti di scorta
for p in products:
    for t in periods:
        m.addConstr(s[p, t] <= stock_max, name=f"stockmax_{p}_{t}")

for t in periods:
    m.addConstr(gp.quicksum(s[p, t] for p in products) <= total_stock_max, name=f"totalstock_{t}")

# Scorta finale minima
for p in products:
    m.addConstr(s[p, "T6"] >= final_min[p], name=f"final_{p}")

# Capacità ordinaria e straordinario
for t in periods:
    m.addConstr(gp.quicksum(hours[p] * x[p, t] for p in products) <= capacity[t] + o[t], name=f"capacity_{t}")

for t in periods:
    m.addConstr(o[t] >= 10 * z[t], name=f"otmin_{t}")
    m.addConstr(o[t] <= ot_max[t] * z[t], name=f"otmax_{t}")

# Limiti sui setup
m.addConstr(gp.quicksum(y[p, t] for p in products for t in periods) <= max_total_setups, name="total_setups")

for t in periods:
    m.addConstr(gp.quicksum(y[p, t] for p in products) <= max_period_setups, name=f"setups_{t}")

# Funzione obiettivo
obj = gp.quicksum(production_cost[p][t] * x[p, t] for p in products for t in periods)
obj += gp.quicksum(setup_cost[p] * y[p, t] for p in products for t in periods)
obj += gp.quicksum(holding_cost[p] * s[p, t] for p in products for t in periods)
obj += fixed_ot * gp.quicksum(z[t] for t in periods)
obj += gp.quicksum(ot_cost[t] * o[t] for t in periods)

m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

if m.status == GRB.OPTIMAL:
    variables = {}
    for p in products:
        for t in periods:
            variables[f"x_{p}_{t}"] = x[p, t].X
            variables[f"s_{p}_{t}"] = s[p, t].X
            variables[f"y_{p}_{t}"] = y[p, t].X
    for t in periods:
        variables[f"o_{t}"] = o[t].X
        variables[f"z_{t}"] = z[t].X

    solution = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variables
    }
else:
    status_names = {
        1: "LOADED", 2: "OPTIMAL", 3: "INFEASIBLE",
        4: "INF_OR_UNBD", 5: "UNBOUNDED", 6: "CUTOFF",
        7: "ITERATION_LIMIT", 8: "NODE_LIMIT", 9: "TIME_LIMIT",
        10: "SOLUTION_LIMIT", 11: "INTERRUPTED", 12: "NUMERIC",
        13: "SUBOPTIMAL", 14: "INPROGRESS", 15: "USER_OBJ_LIMIT"
    }
    solution = {
        "status": status_names.get(m.status, str(m.status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(solution))
