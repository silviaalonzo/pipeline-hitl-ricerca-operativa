import json
import gurobipy as gp
from gurobipy import GRB

inspectors = [f"I{i+1}" for i in range(12)]
audits = [f"A{i+1:02d}" for i in range(20)]

fixed_cost = [18, 23, 28, 22, 27, 21, 26, 20, 25, 19, 24, 18]
hours_max = [13, 14, 15, 16, 17, 13, 14, 15, 16, 17, 13, 14]
audit_max = [3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4]
duration = [3, 4, 2, 6, 5, 3, 4, 7, 2, 5, 3, 6, 4, 2, 5, 7, 3, 4, 5, 6]
required = [1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2]

high_risk = {3, 7, 11, 15, 19}
senior = {0, 1, 2, 3}

cost = [
    [None, 6, 9, 12, None, 18, 8, 11, 14, 17, 7, 10, 13, 16, None, 9, 12, 15, None, 8],
    [10, 13, None, 6, 9, None, 15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, 15],
    [None, 7, 10, 13, 16, 6, 9, 12, 15, 18, None, 11, 14, 17, None, 10, 13, None, 6, 9],
    [11, None, 17, 7, 10, None, 16, 6, None, 12, 15, 18, None, 11, 14, 17, 7, 10, 13, 16],
    [18, 8, 11, None, 17, 7, None, 13, 16, 6, None, 12, 15, None, 8, 11, 14, None, 7, 10],
    [12, None, 18, 8, None, 14, 17, 7, None, 13, 16, None, 9, 12, 15, None, 8, 11, None, 17],
    [6, 9, None, 15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, None, 18, 8, 11],
    [None, 16, 6, 9, None, 15, 18, None, 11, 14, 17, None, 10, 13, None, 6, 9, 12, None, 18],
    [7, 10, None, 16, 6, None, 12, 15, 18, None, 11, 14, None, 7, 10, 13, None, 6, 9, None],
    [None, 17, 7, None, 13, 16, 6, None, 12, 15, None, 8, 11, 14, None, 7, 10, None, 16, 6],
    [8, None, 14, 17, 7, None, 13, 16, None, 9, 12, 15, None, 8, 11, None, 17, 7, 10, None],
    [15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, None, 18, 8, 11, None, 17, 7]
]

Q = [(i, a) for i in range(12) for a in range(20) if cost[i][a] is not None]

m = gp.Model("audit_assignment")
m.Params.OutputFlag = 0

x = {}
for (i, a) in Q:
    x[i, a] = m.addVar(vtype=GRB.BINARY, name=f"x_{inspectors[i]}_{audits[a]}")

y = {}
for i in range(12):
    y[i] = m.addVar(vtype=GRB.BINARY, name=f"y_{inspectors[i]}")

m.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in range(12)) +
    gp.quicksum(cost[i][a] * x[i, a] for (i, a) in Q),
    GRB.MINIMIZE
)

# Copertura audit
for a in range(20):
    m.addConstr(
        gp.quicksum(x[i, a] for i in range(12) if (i, a) in Q) == required[a],
        name=f"copertura_{a}"
    )

# Almeno un senior sugli audit ad alto rischio
for a in high_risk:
    m.addConstr(
        gp.quicksum(x[i, a] for i in senior if (i, a) in Q) >= 1,
        name=f"senior_{a}"
    )

# Attivazione ispettori
for i in range(12):
    for a in range(20):
        if (i, a) in Q:
            m.addConstr(x[i, a] <= y[i], name=f"att_{i}_{a}")
    m.addConstr(
        y[i] <= gp.quicksum(x[i, a] for a in range(20) if (i, a) in Q),
        name=f"def_{i}"
    )

# Capacità ore e numero audit
for i in range(12):
    m.addConstr(
        gp.quicksum(duration[a] * x[i, a] for a in range(20) if (i, a) in Q) <= hours_max[i],
        name=f"ore_{i}"
    )
    m.addConstr(
        gp.quicksum(x[i, a] for a in range(20) if (i, a) in Q) <= audit_max[i],
        name=f"maxaudit_{i}"
    )

# Incompatibilità per ispettore
incompat_pairs = [(0, 1), (5, 6), (10, 11), (16, 17)]
for i in range(12):
    for a, b in incompat_pairs:
        if (i, a) in Q and (i, b) in Q:
            m.addConstr(x[i, a] + x[i, b] <= 1, name=f"incomp_{i}_{a}_{b}")

# Limite ispettori attivati
m.addConstr(gp.quicksum(y[i] for i in range(12)) <= 10, name="max_ispettori")

m.optimize()

solution_vars = {}
if m.Status == GRB.OPTIMAL:
    for i in range(12):
        solution_vars[f"y_{inspectors[i]}"] = y[i].X
        for a in range(20):
            if (i, a) in Q:
                solution_vars[f"x_{inspectors[i]}_{audits[a]}"] = x[i, a].X

    output = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": solution_vars
    }
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.INTERRUPTED: "INTERRUPTED"
    }
    output = {
        "status": status_map.get(m.Status, "UNKNOWN"),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(output))
