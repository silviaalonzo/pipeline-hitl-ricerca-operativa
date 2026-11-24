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
    "A": {1: 18, 2: 12, 3: 10},
    "B": {1: 20, 2: 18, 3: 14},
    "C": {1: 25, 2: 20, 3: 18},
    "D": {1: 15, 2: 14, 3: 12},
    "E": {1: 22, 2: 16, 3: 15},
    "F": {1: 14, 2: 12, 3: 10},
    "G": {1: 30, 2: 25, 3: 22},
    "H": {1: 20, 2: 18, 3: 16},
    "I": {1: 17, 2: 15, 3: 12},
    "J": {1: 27, 2: 21, 3: 18},
    "K": {1: 24, 2: 19, 3: 17},
    "L": {1: 16, 2: 13, 3: 11}
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

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H05_Portafoglio_pluriennale", env=env)
model.Params.OutputFlag = 0

x = {
    i: model.addVar(vtype=GRB.BINARY, name="x_" + i)
    for i in projects
}
y_AC = model.addVar(vtype=GRB.BINARY, name="y_AC")
y_EK = model.addVar(vtype=GRB.BINARY, name="y_EK")

model.setObjective(
    gp.quicksum(van[i] * x[i] for i in projects)
    + 12 * y_AC
    + 10 * y_EK,
    GRB.MAXIMIZE
)

for t in years:
    model.addConstr(
        gp.quicksum(cost[i][t] * x[i] for i in projects) <= budget[t],
        name="budget_A" + str(t)
    )

model.addConstr(
    gp.quicksum(personnel[i] * x[i] for i in projects) <= 28,
    name="personale"
)

model.addConstr(
    gp.quicksum(risk[i] * x[i] for i in projects) <= 32,
    name="rischio"
)

for required_project, prerequisite in precedences:
    model.addConstr(
        x[required_project] <= x[prerequisite],
        name="precedenza_" + required_project + "_" + prerequisite
    )

for i, j in incompatibilities:
    model.addConstr(
        x[i] + x[j] <= 1,
        name="incompatibilita_" + i + "_" + j
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

model.addConstr(y_AC <= x["A"], name="sinergia_AC_1")
model.addConstr(y_AC <= x["C"], name="sinergia_AC_2")
model.addConstr(y_AC >= x["A"] + x["C"] - 1, name="sinergia_AC_3")

model.addConstr(y_EK <= x["E"], name="sinergia_EK_1")
model.addConstr(y_EK <= x["K"], name="sinergia_EK_2")
model.addConstr(y_EK >= x["E"] + x["K"] - 1, name="sinergia_EK_3")

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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for i in projects:
        variable_values["x_" + i] = 1.0 if x[i].X > 0.5 else 0.0
    variable_values["y_AC"] = 1.0 if y_AC.X > 0.5 else 0.0
    variable_values["y_EK"] = 1.0 if y_EK.X > 0.5 else 0.0

    payload = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    payload = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
