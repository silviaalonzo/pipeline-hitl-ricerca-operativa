import gurobipy as gp
from gurobipy import GRB
import json

periods = range(1, 7)
demand = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
buy_cost = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
capacity = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}
initial_stock = 10
final_min = 5
fixed_cost = 40
holding_cost = 2
min_lot = 10

m = gp.Model("M09")
m.Params.OutputFlag = 0

x = {}
y = {}
I = {0: initial_stock}

for t in periods:
    x[t] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{t}")
    y[t] = m.addVar(vtype=GRB.BINARY, name=f"y_{t}")
    I[t] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"I_{t}")

m.setObjective(
    gp.quicksum(
        buy_cost[t] * x[t] + fixed_cost * y[t] + holding_cost * I[t]
        for t in periods
    ),
    GRB.MINIMIZE
)

for t in periods:
    m.addConstr(I[t] == I[t - 1] + x[t] - demand[t], name=f"balance_{t}")
    m.addConstr(x[t] >= min_lot * y[t], name=f"min_lot_{t}")
    m.addConstr(x[t] <= capacity[t] * y[t], name=f"capacity_{t}")

m.addConstr(I[6] >= final_min, name="final_stock")

m.optimize()

if m.Status == GRB.OPTIMAL:
    variables = {}
    for t in periods:
        variables[f"x_{t}"] = x[t].X
        variables[f"y_{t}"] = y[t].X
        variables[f"I_{t}"] = I[t].X
    result = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": variables,
    }
else:
    result = {"status": m.Status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
