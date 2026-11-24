import gurobipy as gp
from gurobipy import GRB
import json

P = ["A", "B", "C"]
T = [1, 2, 3, 4]

demand = {
    ("A", 1): 8,  ("A", 2): 12, ("A", 3): 10, ("A", 4): 14,
    ("B", 1): 10, ("B", 2): 8,  ("B", 3): 14, ("B", 4): 12,
    ("C", 1): 6,  ("C", 2): 9,  ("C", 3): 7,  ("C", 4): 11
}

production_cost = {
    ("A", 1): 9,  ("A", 2): 11, ("A", 3): 10, ("A", 4): 12,
    ("B", 1): 8,  ("B", 2): 9,  ("B", 3): 11, ("B", 4): 10,
    ("C", 1): 13, ("C", 2): 12, ("C", 3): 14, ("C", 4): 11
}

setup_cost = {"A": 45, "B": 40, "C": 50}
holding_cost = {"A": 2, "B": 3, "C": 2}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 4, "B": 4, "C": 3}
initial_inventory = {"A": 0, "B": 0, "C": 6}
capacity = {1: 90, 2: 95, 3: 90, 4: 100}

max_total_inventory = 20
max_setups_per_period = 2

M = {
    (p, t): sum(demand[p, tau] for tau in T if tau >= t)
    for p in P for t in T
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H02_produzione_multi_periodo", env=env)

x = {
    (p, t): model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name=f"x_{p}_{t}"
    )
    for p in P for t in T
}

I = {
    (p, t): model.addVar(
        vtype=GRB.INTEGER,
        lb=0,
        name=f"I_{p}_{t}"
    )
    for p in P for t in T
}

y = {
    (p, t): model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{p}_{t}"
    )
    for p in P for t in T
}

model.setObjective(
    gp.quicksum(
        production_cost[p, t] * x[p, t]
        + setup_cost[p] * y[p, t]
        + holding_cost[p] * I[p, t]
        for p in P for t in T
    ),
    GRB.MINIMIZE
)

for p in P:
    model.addConstr(
        initial_inventory[p] + x[p, 1]
        == demand[p, 1] + I[p, 1],
        name=f"balance_{p}_1"
    )
    for t in T[1:]:
        model.addConstr(
            I[p, t - 1] + x[p, t]
            == demand[p, t] + I[p, t],
            name=f"balance_{p}_{t}"
        )

for p in P:
    for t in T:
        model.addConstr(
            x[p, t] >= minimum_lot[p] * y[p, t],
            name=f"minimum_lot_{p}_{t}"
        )
        model.addConstr(
            x[p, t] <= M[p, t] * y[p, t],
            name=f"setup_link_{p}_{t}"
        )

for t in T:
    model.addConstr(
        gp.quicksum(hours_per_unit[p] * x[p, t] for p in P)
        <= capacity[t],
        name=f"capacity_{t}"
    )
    model.addConstr(
        gp.quicksum(y[p, t] for p in P)
        <= max_setups_per_period,
        name=f"max_setups_{t}"
    )
    model.addConstr(
        gp.quicksum(I[p, t] for p in P)
        <= max_total_inventory,
        name=f"max_inventory_{t}"
    )

for p in P:
    model.addConstr(I[p, 4] == 0, name=f"final_inventory_{p}")

model.optimize()

status_names = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INPROGRESS: "INPROGRESS"
}

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variables = {}
    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = float(round(x[p, t].X))
    for p in P:
        for t in T:
            variables[f"I_{p}_{t}"] = float(round(I[p, t].X))
    for p in P:
        for t in T:
            variables[f"y_{p}_{t}"] = float(round(y[p, t].X))

    result = {
        "status": status,
        "objective": float(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
