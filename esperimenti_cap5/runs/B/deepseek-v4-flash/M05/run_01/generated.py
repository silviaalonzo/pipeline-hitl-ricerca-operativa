import json
import gurobipy as gp
from gurobipy import GRB

projects = [1, 2, 3, 4, 5, 6, 7, 8]
val = {1: 30, 2: 24, 3: 35, 4: 28, 5: 33, 6: 26, 7: 38, 8: 21}
bud = {1: 20, 2: 18, 3: 27, 4: 24, 5: 22, 6: 19, 7: 30, 8: 15}
staff = {1: 4, 2: 3, 3: 5, 4: 4, 5: 4, 6: 3, 7: 5, 8: 2}

m = gp.Model("portfolio")
m.setParam("OutputFlag", 0)

x = {}
for i in projects:
    x[i] = m.addVar(vtype=GRB.BINARY, name=f"x{i}")

m.setObjective(gp.quicksum(val[i] * x[i] for i in projects), GRB.MAXIMIZE)

m.addConstr(gp.quicksum(bud[i] * x[i] for i in projects) <= 100, "budget")
m.addConstr(gp.quicksum(staff[i] * x[i] for i in projects) <= 18, "personnel")
m.addConstr(x[5] <= x[2], "req_P5_P2")
m.addConstr(x[7] <= x[3], "req_P7_P3")
m.addConstr(x[4] + x[6] <= 1, "incompat_P4_P6")
m.addConstr(x[1] + x[3] + x[7] >= 1, "digital")
m.addConstr(gp.quicksum(x[i] for i in projects) >= 3, "at_least_three")

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {f"x{i}": float(x[i].X) for i in projects}
else:
    status = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.NODE_LIMIT: "NODE_LIMIT",
    }.get(m.status, str(m.status))
    objective = 0.0
    variables = {}

out = {
    "status": status,
    "objective": objective,
    "variables": variables,
}
print("SOLUTION_JSON=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False))
