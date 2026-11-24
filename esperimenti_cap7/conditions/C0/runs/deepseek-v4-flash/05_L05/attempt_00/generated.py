import gurobipy as gp
from gurobipy import GRB
import json

audits = [
    "A01","A02","A03","A04","A05","A06","A07","A08","A09","A10",
    "A11","A12","A13","A14","A15","A16","A17","A18","A19","A20"
]
inspectors = ["I1","I2","I3","I4","I5","I6","I7","I8","I9","I10","I11","I12"]
senior = {"I1","I2","I3","I4"}

fixed_cost = {
    "I1":18, "I2":23, "I3":28, "I4":22,
    "I5":27, "I6":21, "I7":26, "I8":20,
    "I9":25, "I10":19, "I11":24, "I12":18
}
hours_max = {
    "I1":13, "I2":14, "I3":15, "I4":16,
    "I5":17, "I6":13, "I7":14, "I8":15,
    "I9":16, "I10":17, "I11":13, "I12":14
}
audit_max = {
    "I1":3, "I2":3, "I3":3, "I4":3,
    "I5":4, "I6":4, "I7":4, "I8":4,
    "I9":4, "I10":4, "I11":4, "I12":4
}
duration = {
    "A01":3,"A02":4,"A03":2,"A04":6,"A05":5,
    "A06":3,"A07":4,"A08":7,"A09":2,"A10":5,
    "A11":3,"A12":6,"A13":4,"A14":2,"A15":5,
    "A16":7,"A17":3,"A18":4,"A19":5,"A20":6
}
required = {
    "A01":1,"A02":1,"A03":1,"A04":2,"A05":1,
    "A06":1,"A07":1,"A08":2,"A09":1,"A10":1,
    "A11":1,"A12":2,"A13":1,"A14":1,"A15":1,
    "A16":2,"A17":1,"A18":1,"A19":1,"A20":2
}
high_risk = {"A04","A08","A12","A16","A20"}
incompatible_pairs = [
    ("A01","A02"), ("A06","A07"), ("A11","A12"), ("A17","A18")
]

cost_rows = {
    "I1":  ["—","6","9","12","—","18","8","11","14","17","7","10","13","16","—","9","12","15","—","8"],
    "I2":  ["10","13","—","6","9","—","15","18","8","—","14","17","—","10","13","16","—","9","12","15"],
    "I3":  ["—","7","10","13","16","6","9","12","15","18","—","11","14","17","—","10","13","—","6","9"],
    "I4":  ["11","—","17","7","10","—","16","6","—","12","15","18","—","11","14","17","7","10","13","16"],
    "I5":  ["18","8","11","—","17","7","—","13","16","6","—","12","15","—","8","11","14","—","7","10"],
    "I6":  ["12","—","18","8","—","14","17","7","—","13","16","—","9","12","15","—","8","11","—","17"],
    "I7":  ["6","9","—","15","18","8","—","14","17","—","10","13","16","—","9","12","—","18","8","11"],
    "I8":  ["—","16","6","9","—","15","18","—","11","14","17","—","10","13","—","6","9","12","—","18"],
    "I9":  ["7","10","—","16","6","—","12","15","18","—","11","14","—","7","10","13","—","6","9","—"],
    "I10": ["—","17","7","—","13","16","6","—","12","15","—","8","11","14","—","7","10","—","16","6"],
    "I11": ["8","—","14","17","7","—","13","16","—","9","12","15","—","8","11","—","17","7","10","—"],
    "I12": ["15","18","8","—","14","17","—","10","13","16","—","9","12","—","18","8","11","—","17","7"]
}

def parse_cost(v):
    return None if v == "—" else int(v)

cost_matrix = {
    i: {a: parse_cost(v) for a, v in zip(audits, row)}
    for i, row in cost_rows.items()
}

Q = [(i, a) for i in inspectors for a in audits if cost_matrix[i][a] is not None]

m = gp.Model("audit_ispettori")
m.Params.OutputFlag = 0

x = {}
for i, a in Q:
    x[i, a] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{a}")

y = {}
for i in inspectors:
    y[i] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}")

m.setObjective(
    gp.quicksum(fixed_cost[i] * y[i] for i in inspectors) +
    gp.quicksum(cost_matrix[i][a] * x[i, a] for i, a in Q),
    GRB.MINIMIZE
)

# Copertura audit
for a in audits:
    m.addConstr(
        gp.quicksum(x[i, a] for i in inspectors if (i, a) in Q) == required[a],
        name=f"copertura_{a}"
    )

# Almeno un senior negli audit ad alto rischio
for a in high_risk:
    m.addConstr(
        gp.quicksum(x[i, a] for i in inspectors if i in senior and (i, a) in Q) >= 1,
        name=f"senior_{a}"
    )

# Capacita' per ispettore
for i in inspectors:
    m.addConstr(
        gp.quicksum(x[i, a] for a in audits if (i, a) in Q) <= audit_max[i],
        name=f"auditmax_{i}"
    )
    m.addConstr(
        gp.quicksum(duration[a] * x[i, a] for a in audits if (i, a) in Q) <= hours_max[i],
        name=f"hours_{i}"
    )

# Attivazione
for i, a in Q:
    m.addConstr(x[i, a] <= y[i], name=f"attivazione_{i}_{a}")

for i in inspectors:
    m.addConstr(
        y[i] <= gp.quicksum(x[i, a] for a in audits if (i, a) in Q),
        name=f"attivazione_esatta_{i}"
    )

# Incompatibilita' tra coppie di audit
for i in inspectors:
    for a, b in incompatible_pairs:
        if (i, a) in Q and (i, b) in Q:
            m.addConstr(x[i, a] + x[i, b] <= 1, name=f"incompat_{i}_{a}_{b}")

# Massimo 10 ispettori attivati
m.addConstr(gp.quicksum(y[i] for i in inspectors) <= 10, name="max_attivati")

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL"
}

if m.Status == GRB.OPTIMAL:
    variables = {
        v.VarName: v.X
        for v in sorted(m.getVars(), key=lambda v: v.VarName)
    }
    solution = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variables
    }
else:
    solution = {
        "status": status_map.get(m.Status, str(m.Status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(solution, ensure_ascii=False))
