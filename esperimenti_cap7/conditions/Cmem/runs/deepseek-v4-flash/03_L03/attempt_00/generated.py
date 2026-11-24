import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
components = ["C1", "C2", "C3", "C4", "C5", "C6"]

fixed_cost = {
    "S1": 165, "S2": 150, "S3": 170, "S4": 145,
    "S5": 155, "S6": 140, "S7": 160, "S8": 148
}

capacity = {
    "S1": 125, "S2": 115, "S3": 110, "S4": 105,
    "S5": 120, "S6": 100, "S7": 95, "S8": 115
}

risk = {
    "S1": 2, "S2": 3, "S3": 1, "S4": 4,
    "S5": 2, "S6": 3, "S7": 1, "S8": 4
}

demand = {"C1": 90, "C2": 80, "C3": 75, "C4": 70, "C5": 65, "C6": 60}
min_lot = {"C1": 14, "C2": 12, "C3": 12, "C4": 10, "C5": 11, "C6": 10}

cost = {
    "S1": {"C1": 3, "C2": 11, "C3": 13, "C4": None, "C5": 12, "C6": None},
    "S2": {"C1": 12, "C2": 3, "C3": None, "C4": 13, "C5": None, "C6": 12},
    "S3": {"C1": 10, "C2": None, "C3": 3, "C4": 11, "C5": 13, "C6": 10},
    "S4": {"C1": None, "C2": 10, "C3": 12, "C4": 3, "C5": None, "C6": 13},
    "S5": {"C1": 11, "C2": 13, "C3": None, "C4": None, "C5": 3, "C6": 11},
    "S6": {"C1": None, "C2": 11, "C3": 13, "C4": 10, "C5": 12, "C6": None},
    "S7": {"C1": 12, "C2": None, "C3": 11, "C4": None, "C5": 10, "C6": 3},
    "S8": {"C1": None, "C2": 12, "C3": None, "C4": 11, "C5": 13, "C6": 10}
}

quality = {
    "S1": {"C1": 98, "C2": 95, "C3": 98, "C4": None, "C5": 97, "C6": None},
    "S2": {"C1": 94, "C2": 98, "C3": None, "C4": 96, "C5": None, "C6": 95},
    "S3": {"C1": 96, "C2": None, "C3": 98, "C4": 98, "C5": 94, "C6": 97},
    "S4": {"C1": None, "C2": 94, "C3": 97, "C4": 98, "C5": None, "C6": 92},
    "S5": {"C1": 93, "C2": 96, "C3": None, "C4": None, "C5": 98, "C6": 94},
    "S6": {"C1": None, "C2": 98, "C3": 94, "C4": 97, "C5": 93, "C6": None},
    "S7": {"C1": 97, "C2": None, "C3": 96, "C4": None, "C5": 95, "C6": 98},
    "S8": {"C1": None, "C2": 95, "C3": None, "C4": 94, "C5": 97, "C6": 93}
}

A = [(i, j) for i in suppliers for j in components if cost[i][j] is not None]

m = gp.Model("procurement_milp")
m.setParam("OutputFlag", 0)

x = {}
y = {}
for (i, j) in A:
    x[i, j] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{i}_{j}")
    y[i, j] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j}")

z = {i: m.addVar(vtype=GRB.BINARY, name=f"z_{i}") for i in suppliers}

m.setObjective(
    gp.quicksum(fixed_cost[i] * z[i] for i in suppliers)
    + gp.quicksum(cost[i][j] * x[i, j] for (i, j) in A),
    GRB.MINIMIZE
)

# Domanda esatta
for j in components:
    m.addConstr(
        gp.quicksum(x[i, cc] for (i, cc) in A if cc == j) == demand[j],
        name=f"demand_{j}"
    )

# Lotto minimo e legame quantità-uso
for (i, j) in A:
    m.addConstr(x[i, j] >= min_lot[j] * y[i, j], name=f"lot_{i}_{j}")
    m.addConstr(x[i, j] <= demand[j] * y[i, j], name=f"link_{i}_{j}")

# Capacità del fornitore attivato
for i in suppliers:
    m.addConstr(
        gp.quicksum(x[ii, cc] for (ii, cc) in A if ii == i) <= capacity[i] * z[i],
        name=f"cap_{i}"
    )

# Da 2 a 3 fornitori per componente
for j in components:
    m.addConstr(
        gp.quicksum(y[i, cc] for (i, cc) in A if cc == j) >= 2,
        name=f"min_suppliers_{j}"
    )
    m.addConstr(
        gp.quicksum(y[i, cc] for (i, cc) in A if cc == j) <= 3,
        name=f"max_suppliers_{j}"
    )

# Attivazione fornitori
m.addConstr(gp.quicksum(z[i] for i in suppliers) <= 6, name="max_active")
m.addConstr(z["S1"] + z["S2"] >= 1, name="at_least_s1_s2")

# Qualità media per componente
for j in components:
    m.addConstr(
        gp.quicksum(quality[i][cc] * x[i, cc] for (i, cc) in A if cc == j) >= 95 * demand[j],
        name=f"quality_{j}"
    )

# Rischio complessivo
m.addConstr(
    gp.quicksum(risk[i] * x[i, j] for (i, j) in A) <= 1300,
    name="risk"
)

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status = f"STATUS_{m.status}"
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({"status": status, "objective": objective, "variables": variables}))
