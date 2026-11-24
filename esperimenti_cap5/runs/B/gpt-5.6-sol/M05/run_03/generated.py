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

staff = {
    "P1": 4, "P2": 3, "P3": 5, "P4": 4,
    "P5": 4, "P6": 3, "P7": 5, "P8": 2
}

digital_projects = ["P1", "P3", "P7"]

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

with gp.Env(empty=True) as env:
    env.setParam("OutputFlag", 0)
    env.start()

    with gp.Model("selezione_portafoglio_progetti", env=env) as model:
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
            name="budget"
        )

        model.addConstr(
            gp.quicksum(staff[p] * x[p] for p in projects) <= 18,
            name="personale"
        )

        model.addConstr(x["P5"] <= x["P2"], name="precedenza_P5_P2")
        model.addConstr(x["P7"] <= x["P3"], name="precedenza_P7_P3")
        model.addConstr(x["P4"] + x["P6"] <= 1, name="incompatibilita_P4_P6")

        model.addConstr(
            gp.quicksum(x[p] for p in digital_projects) >= 1,
            name="almeno_un_digitale"
        )

        model.addConstr(
            gp.quicksum(x[p] for p in projects) >= 3,
            name="almeno_tre_progetti"
        )

        model.optimize()

        solver_status = status_names.get(
            model.Status, "STATUS_" + str(model.Status)
        )

        if model.Status == GRB.OPTIMAL:
            result = {
                "status": "OPTIMAL",
                "objective": float(round(model.ObjVal, 10)),
                "variables": {
                    f"x_{p}": float(round(x[p].X))
                    for p in projects
                }
            }
        else:
            result = {
                "status": solver_status,
                "objective": None,
                "variables": {}
            }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
