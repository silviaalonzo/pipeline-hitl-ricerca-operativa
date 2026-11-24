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

budgets = {1: 110, 2: 100, 3: 90}
digital = ["A", "C", "G", "J"]
sustainable = ["E", "H", "K"]
dependencies = [("G", "B"), ("J", "E"), ("K", "C")]
incompatibilities = [("D", "H"), ("F", "L")]
synergies = {("A", "C"): 12, ("E", "K"): 10}

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
    for pair in synergies
}

model.setObjective(
    gp.quicksum(van[i] * x[i] for i in projects)
    + gp.quicksum(synergies[pair] * y[pair] for pair in synergies),
    GRB.MAXIMIZE
)

for t in years:
    model.addConstr(
        gp.quicksum(cost[i, t] * x[i] for i in projects) <= budgets[t],
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

for child, prerequisite in dependencies:
    model.addConstr(
        x[child] <= x[prerequisite],
        name=f"precedenza_{child}_{prerequisite}"
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

for i, j in synergies:
    model.addConstr(y[i, j] <= x[i], name=f"sinergia_{i}{j}_ub1")
    model.addConstr(y[i, j] <= x[j], name=f"sinergia_{i}{j}_ub2")
    model.addConstr(
        y[i, j] >= x[i] + x[j] - 1,
        name=f"sinergia_{i}{j}_lb"
    )

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
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT"
}

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    all_variables = [x[i] for i in projects] + [
        y[("A", "C")],
        y[("E", "K")]
    ]
    variable_values = {}
    for var in all_variables:
        value = round(float(var.X), 10)
        if abs(value) < 1e-9:
            value = 0.0
        variable_values[var.VarName] = value

    objective_value = round(float(model.ObjVal), 10)
    if abs(objective_value) < 1e-9:
        objective_value = 0.0

    result = {
        "status": solver_status,
        "objective": objective_value,
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
