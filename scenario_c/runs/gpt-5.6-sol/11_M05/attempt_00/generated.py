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
dependencies = [("P5", "P2"), ("P7", "P3")]
incompatibilities = [("P4", "P6")]

model = gp.Model("project_portfolio")
model.Params.OutputFlag = 0

x = {
    p: model.addVar(vtype=GRB.BINARY, name=f"x_{p}")
    for p in projects
}

model.setObjective(
    gp.quicksum(value[p] * x[p] for p in projects),
    GRB.MAXIMIZE
)

model.addConstr(
    gp.quicksum(budget[p] * x[p] for p in projects) <= 100,
    name="budget_limit"
)

model.addConstr(
    gp.quicksum(personnel[p] * x[p] for p in projects) <= 18,
    name="personnel_limit"
)

for required_project, prerequisite in dependencies:
    model.addConstr(
        x[required_project] <= x[prerequisite],
        name=f"dependency_{required_project}_{prerequisite}"
    )

for p, q in incompatibilities:
    model.addConstr(
        x[p] + x[q] <= 1,
        name=f"incompatibility_{p}_{q}"
    )

model.addConstr(
    gp.quicksum(x[p] for p in digital_projects) >= 1,
    name="digital_project"
)

model.addConstr(
    gp.quicksum(x[p] for p in projects) >= 3,
    name="minimum_projects"
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

solver_status = status_names.get(model.Status, f"STATUS_{model.Status}")

if model.Status == GRB.OPTIMAL:
    variable_values = {
        f"x_{p}": float(round(x[p].X))
        for p in projects
    }
    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variable_values
    }
else:
    result = {
        "status": solver_status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
