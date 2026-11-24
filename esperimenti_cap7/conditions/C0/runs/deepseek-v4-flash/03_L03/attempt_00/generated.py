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

available = [(s, c) for s in suppliers for c in components if cost[s][c] is not None]

m = gp.Model("L03_approvvigionamento")
m.setParam("OutputFlag", 0)

y = m.addVars(suppliers, vtype=GRB.BINARY, name="y")
x = m.addVars(available, vtype=GRB.INTEGER, name="x")
z = m.addVars(available, vtype=GRB.BINARY, name="z")

# Domanda esatta e numero fornitori per componente
for c in components:
    m.addConstr(
        gp.quicksum(x[s, c] for s in suppliers if (s, c) in available) == demand[c],
        name=f"domanda_{c}"
    )
    m.addConstr(
        gp.quicksum(z[s, c] for s in suppliers if (s, c) in available) >= 2,
        name=f"min_forn_{c}"
    )
    m.addConstr(
        gp.quicksum(z[s, c] for s in suppliers if (s, c) in available) <= 3,
        name=f"max_forn_{c}"
    )
    m.addConstr(
        gp.quicksum(quality[s][c] * x[s, c] for s in suppliers if (s, c) in available) >= 95 * demand[c],
        name=f"qualita_{c}"
    )

# Capacità e attivazione fornitori
for s in suppliers:
    m.addConstr(
        gp.quicksum(x[s, c] for c in components if (s, c) in available) <= capacity[s] * y[s],
        name=f"capacita_{s}"
    )

# Lotto minimo e uso della coppia
for (s, c) in available:
    m.addConstr(x[s, c] >= min_lot[c] * z[s, c], name=f"lotto_{s}_{c}")
    m.addConstr(x[s, c] <= min(demand[c], capacity[s]) * z[s, c], name=f"link_{s}_{c}")
    m.addConstr(z[s, c] <= y[s], name=f"attivazione_{s}_{c}")

# Rischio complessivo
m.addConstr(
    gp.quicksum(risk[s] * x[s, c] for (s, c) in available) <= 1300,
    name="rischio"
)

# Limiti sul numero di fornitori attivi
m.addConstr(gp.quicksum(y[s] for s in suppliers) <= 6, name="max_attivi")
m.addConstr(y["S1"] + y["S2"] >= 1, name="almeno_S1_S2")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(fixed_cost[s] * y[s] for s in suppliers) +
    gp.quicksum(cost[s][c] * x[s, c] for (s, c) in available),
    GRB.MINIMIZE
)

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = m.ObjVal
    variables_out = {}

    for s in suppliers:
        variables_out[f"y_{s}"] = y[s].X

    for (s, c) in available:
        variables_out[f"x_{s}_{c}"] = x[s, c].X
        variables_out[f"z_{s}_{c}"] = z[s, c].X
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    status = status_map.get(m.status, f"STATUS_{m.status}")
    objective = None
    variables_out = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables_out
}))
