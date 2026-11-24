import gurobipy as gp
from gurobipy import GRB
import json

projects = range(1, 9)

value = {
    1: 30, 2: 24, 3: 35, 4: 28,
    5: 33, 6: 26, 7: 38, 8: 21
}

budget = {
    1: 20, 2: 18, 3: 27, 4: 24,
    5: 22, 6: 19, 7: 30, 8: 15
}

staff = {
    1: 4, 2: 3, 3: 5, 4: 4,
    5: 4, 6: 3, 7: 5, 8: 2
}

m = gp.Model("portfolio")
m.setParam("OutputFlag", 0)

x = m.addVars(projects, vtype=GRB.BINARY, name="x")

m.setObjective(
    gp.quicksum(value[i] * x[i] for i in projects),
    GRB.MAXIMIZE
)

m.addConstr(gp.quicksum(budget[i] * x[i] for i in projects) <= 100, "budget")
m.addConstr(gp.quicksum(staff[i] * x[i] for i in projects) <= 18, "personale")

m.addConstr(x[5] <= x[2], "P5_richiede_P2")
m.addConstr(x[7] <= x[3], "P7_richiede_P3")
m.addConstr(x[4] + x[6] <= 1, "P4_incompatibile_P6")
m.addConstr(x[1] + x[3] + x[7] >= 1, "almeno_un_digitale")
m.addConstr(gp.quicksum(x[i] for i in projects) >= 3, "almeno_tre_progetti")

m.optimize()

if m.Status == GRB.OPTIMAL:
    sol = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": {f"x{i}": int(round(x[i].X)) for i in projects}
    }
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED"
    }
    sol = {
        "status": status_map.get(m.Status, str(m.Status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(sol, separators=(",", ":")))
