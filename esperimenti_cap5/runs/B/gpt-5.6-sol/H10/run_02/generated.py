import gurobipy as gp
import json

nodes = ["S", "A", "B", "C", "D", "T"]
products = ["K1", "K2"]
demand = {"K1": 28, "K2": 22}

fixed_cost = {
    ("S", "A"): 55,
    ("S", "B"): 50,
    ("A", "B"): 18,
    ("A", "C"): 38,
    ("B", "C"): 22,
    ("B", "D"): 35,
    ("C", "D"): 20,
    ("C", "T"): 48,
    ("D", "T"): 44
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
    ("D", "T"): 35
}

unit_cost = {
    ("S", "A"): {"K1": 2, "K2": 3},
    ("S", "B"): {"K1": 3, "K2": 2},
    ("A", "B"): {"K1": 1, "K2": 2},
    ("A", "C"): {"K1": 2, "K2": 3},
    ("B", "C"): {"K1": 2, "K2": 1},
    ("B", "D"): {"K1": 3, "K2": 2},
    ("C", "D"): {"K1": 1, "K2": 2},
    ("C", "T"): {"K1": 3, "K2": 2},
    ("D", "T"): {"K1": 2, "K2": 3}
}

arcs = list(fixed_cost.keys())
mandatory_arcs = [("S", "A"), ("S", "B")]
max_active_arcs = 7

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H10_rete_multi_prodotto", env=env)
model.Params.MIPGap = 0.0

y = {}
for i, j in arcs:
    y[(i, j)] = model.addVar(
        vtype=gp.GRB.BINARY,
        name=f"y_{i}_{j}"
    )

x = {}
for i, j in arcs:
    for k in products:
        x[(i, j, k)] = model.addVar(
            lb=0,
            vtype=gp.GRB.INTEGER,
            name=f"x_{i}_{j}_{k}"
        )

model.setObjective(
    gp.quicksum(fixed_cost[a] * y[a] for a in arcs)
    + gp.quicksum(
        unit_cost[(i, j)][k] * x[(i, j, k)]
        for i, j in arcs
        for k in products
    ),
    gp.GRB.MINIMIZE
)

for v in nodes:
    for k in products:
        rhs = demand[k] if v == "S" else (-demand[k] if v == "T" else 0)

        outgoing = gp.quicksum(
            x[(i, j, k)] for i, j in arcs if i == v
        )
        incoming = gp.quicksum(
            x[(i, j, k)] for i, j in arcs if j == v
        )

        model.addConstr(
            outgoing - incoming == rhs,
            name=f"balance_{v}_{k}"
        )

for i, j in arcs:
    model.addConstr(
        gp.quicksum(x[(i, j, k)] for k in products)
        <= capacity[(i, j)] * y[(i, j)],
        name=f"capacity_{i}_{j}"
    )

for a in mandatory_arcs:
    model.addConstr(y[a] == 1, name=f"mandatory_{a[0]}_{a[1]}")

model.addConstr(
    gp.quicksum(y[a] for a in arcs) <= max_active_arcs,
    name="max_active_arcs"
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
    17: "MEM_LIMIT"
}

status_code = model.Status
status_text = status_names.get(status_code, f"STATUS_{status_code}")

if status_code == gp.GRB.OPTIMAL:
    def clean_number(value):
        if abs(value - round(value)) <= 1e-6:
            return float(round(value))
        return float(round(value, 10))

    variable_values = {}

    for a in arcs:
        variable_values[y[a].VarName] = clean_number(y[a].X)

    for i, j in arcs:
        for k in products:
            variable_values[x[(i, j, k)].VarName] = clean_number(
                x[(i, j, k)].X
            )

    payload = {
        "status": status_text,
        "objective": clean_number(model.ObjVal),
        "variables": variable_values
    }
else:
    payload = {
        "status": status_text,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
