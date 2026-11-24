import gurobipy as gp
from gurobipy import GRB
import json

I = ["A", "B", "C", "D"]

c = {"A": 11, "B": 10, "C": 12, "D": 9}
f = {"A": 80, "B": 95, "C": 60, "D": 120}
u = {"A": 80, "B": 100, "C": 70, "D": 90}
l = {"A": 20, "B": 25, "C": 15, "D": 20}
q = {"A": 96, "B": 90, "C": 98, "D": 88}
e = {"A": 3, "B": 4, "C": 2, "D": 5}

demand = 180
minimum_quality = 92
maximum_emissions = 650

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
    if abs(value) < 1e-9:
        return 0.0
    nearest_integer = round(value)
    if abs(value - nearest_integer) < 1e-6:
        return float(nearest_integer)
    return float(value)

with gp.Env(empty=True) as env:
    env.setParam("OutputFlag", 0)
    env.start()

    with gp.Model("M07_selezione_fornitori", env=env) as model:
        x = {
            i: model.addVar(
                lb=0,
                vtype=GRB.INTEGER,
                name=f"x_{i}"
            )
            for i in I
        }

        y = {
            i: model.addVar(
                vtype=GRB.BINARY,
                name=f"y_{i}"
            )
            for i in I
        }

        model.setObjective(
            gp.quicksum(c[i] * x[i] + f[i] * y[i] for i in I),
            GRB.MINIMIZE
        )

        model.addConstr(
            gp.quicksum(x[i] for i in I) == demand,
            name="domanda_esatta"
        )

        for i in I:
            model.addConstr(
                x[i] >= l[i] * y[i],
                name=f"ordine_minimo_{i}"
            )
            model.addConstr(
                x[i] <= u[i] * y[i],
                name=f"capacita_{i}"
            )

        model.addConstr(
            gp.quicksum(y[i] for i in I) >= 2,
            name="almeno_due_fornitori"
        )

        model.addConstr(
            gp.quicksum(q[i] * x[i] for i in I)
            >= minimum_quality * demand,
            name="qualita_minima"
        )

        model.addConstr(
            gp.quicksum(e[i] * x[i] for i in I)
            <= maximum_emissions,
            name="emissioni_massime"
        )

        model.optimize()

        status_code = model.Status
        status = status_names.get(status_code, f"STATUS_{status_code}")

        if status_code == GRB.OPTIMAL:
            variable_values = {}

            for i in I:
                variable_values[f"x_{i}"] = numeric_value(x[i].X)
            for i in I:
                variable_values[f"y_{i}"] = numeric_value(y[i].X)

            result = {
                "status": "OPTIMAL",
                "objective": numeric_value(model.ObjVal),
                "variables": variable_values
            }
        else:
            result = {
                "status": status,
                "objective": None,
                "variables": {}
            }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
