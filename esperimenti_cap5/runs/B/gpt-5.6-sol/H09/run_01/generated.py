import gurobipy as gp
from gurobipy import GRB
import json

P = ["A", "B", "C"]
T = [1, 2, 3, 4, 5, 6]

demand = {
    "A": {1: 12, 2: 18, 3: 14, 4: 20, 5: 16, 6: 19},
    "B": {1: 10, 2: 9, 3: 15, 4: 12, 5: 17, 6: 14},
    "C": {1: 8, 2: 11, 3: 10, 4: 13, 5: 9, 6: 15},
}

production_cost = {
    "A": {1: 7, 2: 8, 3: 9, 4: 7, 5: 10, 6: 8},
    "B": {1: 9, 2: 8, 3: 8, 4: 10, 5: 7, 6: 9},
    "C": {1: 11, 2: 10, 3: 12, 4: 9, 5: 11, 6: 8},
}

setup_cost = {"A": 35, "B": 40, "C": 45}
holding_cost = {"A": 2, "B": 2, "C": 3}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
minimum_lot = {"A": 5, "B": 4, "C": 3}

base_capacity = {1: 120, 2: 115, 3: 125, 4: 110, 5: 120, 6: 115}
max_overtime = 20
overtime_cost = 18
max_total_inventory = 40
minimum_final_inventory = 2

model = gp.Model("H09")
model.Params.OutputFlag = 0
model.Params.MIPGap = 0.0

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

o = {
    t: model.addVar(
        vtype=GRB.CONTINUOUS,
        lb=0,
        ub=max_overtime,
        name=f"o_{t}"
    )
    for t in T
}

model.setObjective(
    gp.quicksum(
        production_cost[p][t] * x[p, t]
        for p in P for t in T
    )
    + gp.quicksum(
        holding_cost[p] * I[p, t]
        for p in P for t in T
    )
    + gp.quicksum(
        setup_cost[p] * y[p, t]
        for p in P for t in T
    )
    + gp.quicksum(
        overtime_cost * o[t]
        for t in T
    ),
    GRB.MINIMIZE
)

for p in P:
    model.addConstr(
        x[p, 1] == demand[p][1] + I[p, 1],
        name=f"balance_{p}_1"
    )
    for t in T[1:]:
        model.addConstr(
            I[p, t - 1] + x[p, t] == demand[p][t] + I[p, t],
            name=f"balance_{p}_{t}"
        )

for p in P:
    model.addConstr(
        I[p, 6] >= minimum_final_inventory,
        name=f"final_inventory_{p}"
    )

for t in T:
    model.addConstr(
        gp.quicksum(hours_per_unit[p] * x[p, t] for p in P)
        <= base_capacity[t] + o[t],
        name=f"capacity_{t}"
    )

for p in P:
    for t in T:
        M_pt = demand[p][t] + max_total_inventory
        model.addConstr(
            x[p, t] >= minimum_lot[p] * y[p, t],
            name=f"minimum_lot_{p}_{t}"
        )
        model.addConstr(
            x[p, t] <= M_pt * y[p, t],
            name=f"setup_link_{p}_{t}"
        )

model.addConstr(
    gp.quicksum(y[p, 1] for p in P) <= 3,
    name="setups_1"
)

for t in T[1:]:
    model.addConstr(
        gp.quicksum(y[p, t] for p in P) <= 2,
        name=f"setups_{t}"
    )

for t in T:
    model.addConstr(
        gp.quicksum(I[p, t] for p in P) <= max_total_inventory,
        name=f"inventory_capacity_{t}"
    )

model.optimize()

status_map = {
    1: "LOADED",
    2: "OPTIMAL",
    3: "INFEASIBLE",
    4: "INF_OR_UNBD",
    5: "UNBOUNDED",
    6: "CUTOFF",
    7: "ITERATION_LIMIT",
    8: "NODE_LIMIT",
    9: "TIME_LIMIT",
    10: "SOLUTION_LIMIT",
    11: "INTERRUPTED",
    12: "NUMERIC",
    13: "SUBOPTIMAL",
    14: "INPROGRESS",
    15: "USER_OBJ_LIMIT",
    16: "WORK_LIMIT",
    17: "MEM_LIMIT"
}

status = status_map.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    def clean_value(value, integer=False):
        if integer or abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(round(value, 6))

    variables = {}

    for p in P:
        for t in T:
            variables[f"x_{p}_{t}"] = clean_value(x[p, t].X, True)

    for p in P:
        for t in T:
            variables[f"I_{p}_{t}"] = clean_value(I[p, t].X, True)

    for p in P:
        for t in T:
            variables[f"y_{p}_{t}"] = clean_value(y[p, t].X, True)

    for t in T:
        variables[f"o_{t}"] = clean_value(o[t].X)

    result = {
        "status": status,
        "objective": clean_value(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
