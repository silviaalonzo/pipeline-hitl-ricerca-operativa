import gurobipy as gp
from gurobipy import GRB
import json

projects = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]

value = {
    "P1": 30, "P2": 24, "P3": 35, "P4": 28,
    "P5": 33, "P6": 26, "P7": 38, "P8": 21
}

budget = {
    "P1": 20, "P2": 18, "P3": 27, "P4": 24,
    "P5": 22, "P6": 19, "P7": 30, "P8": 15
}

personnel = {
    "P1": 4, "P2": 3, "P3": 5, "P4": 4,
    "P5": 4, "P6": 3, "P7": 5, "P8": 2
}

digital_projects = ["P1", "P3", "P7"]
requirements = [("P5", "P2"), ("P7", "P3")]

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("project_portfolio", env=env)

x = {
    i: model.addVar(vtype=GRB.BINARY, name="x_" + i)
    for i in projects
}

total_value = gp.quicksum(value[i] * x[i] for i in projects)

model.setObjective(total_value, GRB.MAXIMIZE)

model.addConstr(
    gp.quicksum(budget[i] * x[i] for i in projects) <= 100,
    name="budget_limit"
)

model.addConstr(
    gp.quicksum(personnel[i] * x[i] for i in projects) <= 18,
    name="personnel_limit"
)

for dependent, required in requirements:
    model.addConstr(
        x[dependent] <= x[required],
        name="requirement_" + dependent + "_" + required
    )

model.addConstr(
    x["P4"] + x["P6"] <= 1,
    name="incompatibility_P4_P6"
)

model.addConstr(
    gp.quicksum(x[i] for i in digital_projects) >= 1,
    name="minimum_digital_projects"
)

model.addConstr(
    gp.quicksum(x[i] for i in projects) >= 3,
    name="minimum_total_projects"
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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variable_values = {}
    for i in projects:
        variable_values["x_" + i] = float(round(x[i].X))
    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variable_values
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
