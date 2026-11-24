import json
import gurobipy as gp
from gurobipy import GRB

nodes = ["S", "A", "B", "C", "D", "T"]
products = ["K1", "K2"]

arcs = [
    ("S", "A"),
    ("S", "B"),
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("B", "D"),
    ("C", "D"),
    ("C", "T"),
    ("D", "T"),
]

fixed_cost = {
    ("S", "A"): 55,
    ("S", "B"): 50,
    ("A", "B"): 18,
    ("A", "C"): 38,
    ("B", "C"): 22,
    ("B", "D"): 35,
    ("C", "D"): 20,
    ("C", "T"): 48,
    ("D", "T"): 44,
}

capacity = {
    ("S", "A"): 35,
    ("S", "B"): 35,
    ("A", "B"): 15,
    ("A", "C"): 30,
    ("B", "C"): 25,
    ("B", "D"): 25,
    ("C", "D"): 20,
    ("C", "T"): 35,
    ("D", "T"): 35,
}

unit_cost = {
    ("K1", "S", "A"): 2,
    ("K1", "S", "B"): 3,
    ("K1", "A", "B"): 1,
    ("K1", "A", "C"): 2,
    ("K1", "B", "C"): 2,
    ("K1", "B", "D"): 3,
    ("K1", "C", "D"): 1,
    ("K1", "C", "T"): 3,
    ("K1", "D", "T"): 2,
    ("K2", "S", "A"): 3,
    ("K2", "S", "B"): 2,
    ("K2", "A", "B"): 2,
    ("K2", "A", "C"): 3,
    ("K2", "B", "C"): 1,
    ("K2", "B", "D"): 2,
    ("K2", "C", "D"): 2,
    ("K2", "C", "T"): 2,
    ("K2", "D", "T"): 3,
}

demand = {
    "K1": 28,
    "K2": 22,
}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H10_rete_multi_prodotto", env=env)
model.Params.OutputFlag = 0

y = {
    (i, j): model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{i}_{j}"
    )
    for i, j in arcs
}

x = {
    (k, i, j): model.addVar(
        lb=0,
        vtype=GRB.INTEGER,
        name=f"x_{k}_{i}_{j}"
    )
    for k in products
    for i, j in arcs
}

total_cost = (
    gp.quicksum(fixed_cost[i, j] * y[i, j] for i, j in arcs)
    + gp.quicksum(
        unit_cost[k, i, j] * x[k, i, j]
        for k in products
        for i, j in arcs
    )
)

model.setObjective(total_cost, GRB.MINIMIZE)

for k in products:
    for v in nodes:
        if v == "S":
            balance = demand[k]
        elif v == "T":
            balance = -demand[k]
        else:
            balance = 0

        model.addConstr(
            gp.quicksum(
                x[k, i, j] for i, j in arcs if i == v
            )
            - gp.quicksum(
                x[k, i, j] for i, j in arcs if j == v
            )
            == balance,
            name=f"flow_balance_{k}_{v}"
        )

for i, j in arcs:
    model.addConstr(
        gp.quicksum(x[k, i, j] for k in products)
        <= capacity[i, j] * y[i, j],
        name=f"shared_capacity_{i}_{j}"
    )

model.addConstr(y["S", "A"] == 1, name="resilience_S_A")
model.addConstr(y["S", "B"] == 1, name="resilience_S_B")

model.addConstr(
    gp.quicksum(y[i, j] for i, j in arcs) <= 7,
    name="maximum_activated_arcs"
)

model.optimize()

status_names = {
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
    17: "MEM_LIMIT",
}

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

def clean_number(value):
    nearest_integer = round(value)
    if abs(value - nearest_integer) <= 1e-6:
        return float(nearest_integer)
    return float(value)

if model.Status == GRB.OPTIMAL:
    variables = {}
    for i, j in arcs:
        variables[y[i, j].VarName] = clean_number(y[i, j].X)
    for k in products:
        for i, j in arcs:
            variables[x[k, i, j].VarName] = clean_number(x[k, i, j].X)

    result = {
        "status": "OPTIMAL",
        "objective": clean_number(model.ObjVal),
        "variables": variables,
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
