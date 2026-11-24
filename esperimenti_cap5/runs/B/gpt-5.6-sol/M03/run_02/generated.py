import gurobipy as gp
from gurobipy import GRB
import json

employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
night_shifts = ["N1", "N2"]

costs = {
    ("Ana", "M1"): 8,
    ("Ana", "M2"): 7,
    ("Ana", "P1"): 9,
    ("Ana", "P2"): 8,

    ("Bruno", "M1"): 7,
    ("Bruno", "M2"): 8,
    ("Bruno", "P1"): 8,
    ("Bruno", "P2"): 9,

    ("Carla", "M2"): 9,
    ("Carla", "P1"): 8,
    ("Carla", "P2"): 8,
    ("Carla", "N1"): 11,
    ("Carla", "N2"): 12,

    ("Diego", "M1"): 10,
    ("Diego", "P1"): 9,
    ("Diego", "P2"): 8,
    ("Diego", "N1"): 10,
    ("Diego", "N2"): 11,

    ("Elena", "M1"): 8,
    ("Elena", "M2"): 10,
    ("Elena", "P1"): 9,
    ("Elena", "P2"): 9,
    ("Elena", "N1"): 12,
    ("Elena", "N2"): 10,

    ("Fabio", "M1"): 9,
    ("Fabio", "M2"): 8,
    ("Fabio", "P1"): 10,
    ("Fabio", "P2"): 7
}

available_assignments = list(costs.keys())

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("assegnazione_personale_turni", env=env)

x = model.addVars(
    available_assignments,
    vtype=GRB.BINARY,
    name="x"
)

model.setObjective(
    gp.quicksum(costs[i, s] * x[i, s] for i, s in available_assignments),
    GRB.MINIMIZE
)

model.addConstrs(
    (
        gp.quicksum(
            x[i, s]
            for i in employees
            if (i, s) in costs
        ) == 1
        for s in shifts
    ),
    name="copertura"
)

model.addConstrs(
    (
        gp.quicksum(
            x[i, s]
            for s in shifts
            if (i, s) in costs
        ) <= 2
        for i in employees
    ),
    name="massimo_due_turni"
)

model.addConstrs(
    (
        gp.quicksum(
            x[i, s]
            for s in night_shifts
            if (i, s) in costs
        ) <= 1
        for i in employees
    ),
    name="massimo_un_notturno"
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
    objective = float(round(model.ObjVal, 10))
    variables = {
        x[i, s].VarName: float(1 if x[i, s].X > 0.5 else 0)
        for i, s in available_assignments
    }
else:
    objective = None
    variables = {}

result = {
    "status": status,
    "objective": objective,
    "variables": variables
}

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
