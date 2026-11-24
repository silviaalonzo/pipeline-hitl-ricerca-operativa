import gurobipy as gp
from gurobipy import GRB
import json

projects = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
years = [1, 2, 3]

van = {
    "A": 42, "B": 35, "C": 48, "D": 31,
    "E": 40, "F": 28, "G": 55, "H": 37,
    "I": 33, "J": 50, "K": 46, "L": 29
}

cost = {
    ("A", 1): 18, ("A", 2): 12, ("A", 3): 10,
    ("B", 1): 20, ("B", 2): 18, ("B", 3): 14,
    ("C", 1): 25, ("C", 2): 20, ("C", 3): 18,
    ("D", 1): 15, ("D", 2): 14, ("D", 3): 12,
    ("E", 1): 22, ("E", 2): 16, ("E", 3): 15,
    ("F", 1): 14, ("F", 2): 12, ("F", 3): 10,
    ("G", 1): 30, ("G", 2): 25, ("G", 3): 22,
    ("H", 1): 20, ("H", 2): 18, ("H", 3): 16,
    ("I", 1): 17, ("I", 2): 15, ("I", 3): 12,
    ("J", 1): 27, ("J", 2): 21, ("J", 3): 18,
    ("K", 1): 24, ("K", 2): 19, ("K", 3): 17,
    ("L", 1): 16, ("L", 2): 13, ("L", 3): 11
}

personnel = {
    "A": 4, "B": 4, "C": 5, "D": 3,
    "E": 4, "F": 3, "G": 6, "H": 4,
    "I": 3, "J": 5, "K": 5, "L": 3
}

risk = {
    "A": 5, "B": 4, "C": 6, "D": 3,
    "E": 4, "F": 2, "G": 7, "H": 5,
    "I": 3, "J": 6, "K": 5, "L": 3
}

budget = {1: 110, 2: 100, 3: 90}
digital = ["A", "C", "G", "J"]
sustainable = ["E", "H", "K"]
precedences = [("G", "B"), ("J", "E"), ("K", "C")]
incompatibilities = [("D", "H"), ("F", "L")]
synergy_bonus = {("A", "C"): 12, ("E", "K"): 10}

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H05_portafoglio_pluriennale", env=env)

x = {
    i: model.addVar(vtype=GRB.BINARY, name=f"x_{i}")
    for i in projects
}
y = {
    pair: model.addVar(
        vtype=GRB.BINARY,
        name=f"y_{pair[0]}{pair[1]}"
    )
    for pair in synergy_bonus
}

model.setObjective(
    gp.quicksum(van[i] * x[i] for i in projects)
    + gp.quicksum(synergy_bonus[pair] * y[pair]
                  for pair in synergy_bonus),
    GRB.MAXIMIZE
)

for t in years:
    model.addConstr(
        gp.quicksum(cost[i, t] * x[i] for i in projects) <= budget[t],
        name=f"budget_A{t}"
    )

model.addConstr(
    gp.quicksum(personnel[i] * x[i] for i in projects) <= 28,
    name="personale"
)

model.addConstr(
    gp.quicksum(risk[i] * x[i] for i in projects) <= 32,
    name="rischio"
)

for required, prerequisite in precedences:
    model.addConstr(
        x[required] <= x[prerequisite],
        name=f"precedenza_{required}_{prerequisite}"
    )

for i, j in incompatibilities:
    model.addConstr(
        x[i] + x[j] <= 1,
        name=f"incompatibilita_{i}_{j}"
    )

model.addConstr(
    gp.quicksum(x[i] for i in digital) >= 2,
    name="minimo_digitali"
)

model.addConstr(
    gp.quicksum(x[i] for i in sustainable) >= 1,
    name="minimo_sostenibili"
)

model.addConstr(
    gp.quicksum(x[i] for i in projects) <= 8,
    name="massimo_progetti"
)

for i, j in synergy_bonus:
    model.addConstr(y[i, j] <= x[i], name=f"sinergia_{i}{j}_ub1")
    model.addConstr(y[i, j] <= x[j], name=f"sinergia_{i}{j}_ub2")
    model.addConstr(
        y[i, j] >= x[i] + x[j] - 1,
        name=f"sinergia_{i}{j}_lb"
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

status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    def clean(value):
        if abs(value) < 1e-6:
            return 0.0
        if abs(value - round(value)) < 1e-6:
            return float(round(value))
        return float(value)

    variable_values = {}
    for i in projects:
        variable_values[f"x_{i}"] = clean(x[i].X)
    for i, j in synergy_bonus:
        variable_values[f"y_{i}{j}"] = clean(y[i, j].X)

    result = {
        "status": "OPTIMAL",
        "objective": clean(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
