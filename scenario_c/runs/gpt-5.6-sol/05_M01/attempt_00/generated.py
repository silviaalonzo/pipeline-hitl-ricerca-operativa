import gurobipy as gp
from gurobipy import GRB
import json

I = ["A", "B", "C", "D"]
J = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]
K = 2

f = {
    "A": 38,
    "B": 42,
    "C": 35,
    "D": 46
}

q = {
    "A": 2,
    "B": 3,
    "C": 2,
    "D": 3
}

c = {
    ("Z1", "A"): 8,  ("Z1", "B"): 14, ("Z1", "C"): 11, ("Z1", "D"): 17,
    ("Z2", "A"): 10, ("Z2", "B"): 9,  ("Z2", "C"): 13, ("Z2", "D"): 15,
    ("Z3", "A"): 12, ("Z3", "B"): 8,  ("Z3", "C"): 14, ("Z3", "D"): 10,
    ("Z4", "A"): 15, ("Z4", "B"): 11, ("Z4", "C"): 9,  ("Z4", "D"): 7,
    ("Z5", "A"): 9,  ("Z5", "B"): 13, ("Z5", "C"): 8,  ("Z5", "D"): 14,
    ("Z6", "A"): 14, ("Z6", "B"): 10, ("Z6", "C"): 7,  ("Z6", "D"): 9
}

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

def numeric_value(value):
    if abs(value - round(value)) <= 1e-6:
        return float(round(value))
    return float(value)

with gp.Env(empty=True) as env:
    env.setParam("OutputFlag", 0)
    env.start()

    with gp.Model("localizzazione_centri", env=env) as model:
        y = model.addVars(I, vtype=GRB.BINARY, name="y")
        x = model.addVars(J, I, vtype=GRB.BINARY, name="x")

        model.setObjective(
            gp.quicksum(f[i] * y[i] for i in I)
            + gp.quicksum(c[j, i] * x[j, i] for j in J for i in I),
            GRB.MINIMIZE
        )

        model.addConstr(
            gp.quicksum(y[i] for i in I) == K,
            name="numero_centri"
        )

        model.addConstrs(
            (gp.quicksum(x[j, i] for i in I) == 1 for j in J),
            name="assegnazione_unica"
        )

        model.addConstrs(
            (gp.quicksum(x[j, i] for j in J) <= q[i] * y[i] for i in I),
            name="capacita"
        )

        model.addConstrs(
            (x[j, i] <= y[i] for j in J for i in I),
            name="collegamento_apertura"
        )

        model.optimize()

        solver_status = status_names.get(
            int(model.Status),
            "STATUS_" + str(int(model.Status))
        )

        if model.Status == GRB.OPTIMAL:
            variables = {}

            for i in I:
                variables[f"y[{i}]"] = numeric_value(y[i].X)

            for j in J:
                for i in I:
                    variables[f"x[{j},{i}]"] = numeric_value(x[j, i].X)

            result = {
                "status": "OPTIMAL",
                "objective": numeric_value(model.ObjVal),
                "variables": variables
            }
        else:
            result = {
                "status": solver_status,
                "objective": None,
                "variables": {}
            }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":"), allow_nan=False))
