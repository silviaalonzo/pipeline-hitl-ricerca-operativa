import json
import gurobipy as gp
from gurobipy import GRB

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

lot = {"C1": 14, "C2": 12, "C3": 12, "C4": 10, "C5": 11, "C6": 10}

cost = {
    ("S1", "C1"): 3, ("S1", "C2"): 11, ("S1", "C3"): 13, ("S1", "C5"): 12,
    ("S2", "C1"): 12, ("S2", "C2"): 3, ("S2", "C4"): 13, ("S2", "C6"): 12,
    ("S3", "C1"): 10, ("S3", "C3"): 3, ("S3", "C4"): 11, ("S3", "C5"): 13, ("S3", "C6"): 10,
    ("S4", "C2"): 10, ("S4", "C3"): 12, ("S4", "C4"): 3, ("S4", "C6"): 13,
    ("S5", "C1"): 11, ("S5", "C2"): 13, ("S5", "C5"): 3, ("S5", "C6"): 11,
    ("S6", "C2"): 11, ("S6", "C3"): 13, ("S6", "C4"): 10, ("S6", "C5"): 12,
    ("S7", "C1"): 12, ("S7", "C3"): 11, ("S7", "C5"): 10, ("S7", "C6"): 3,
    ("S8", "C2"): 12, ("S8", "C4"): 11, ("S8", "C5"): 13, ("S8", "C6"): 10
}

quality = {
    ("S1", "C1"): 98, ("S1", "C2"): 95, ("S1", "C3"): 98, ("S1", "C5"): 97,
    ("S2", "C1"): 94, ("S2", "C2"): 98, ("S2", "C4"): 96, ("S2", "C6"): 95,
    ("S3", "C1"): 96, ("S3", "C3"): 98, ("S3", "C4"): 98, ("S3", "C5"): 94, ("S3", "C6"): 97,
    ("S4", "C2"): 94, ("S4", "C3"): 97, ("S4", "C4"): 98, ("S4", "C6"): 92,
    ("S5", "C1"): 93, ("S5", "C2"): 96, ("S5", "C5"): 98, ("S5", "C6"): 94,
    ("S6", "C2"): 98, ("S6", "C3"): 94, ("S6", "C4"): 97, ("S6", "C5"): 93,
    ("S7", "C1"): 97, ("S7", "C3"): 96, ("S7", "C5"): 95, ("S7", "C6"): 98,
    ("S8", "C2"): 95, ("S8", "C4"): 94, ("S8", "C5"): 97, ("S8", "C6"): 93
}

A = set(cost.keys())
available = sorted(A)

model = gp.Model("approvvigionamento")
model.Params.OutputFlag = 0

z = {}
for i in suppliers:
    z[i] = model.addVar(vtype=GRB.BINARY, name=f"z_{i}")

y = {}
x = {}
for (i, j) in available:
    M = min(capacity[i], demand[j])
    y[i, j] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j}")
    x[i, j] = model.addVar(vtype=GRB.INTEGER, lb=0, ub=M, name=f"x_{i}_{j}")

# Domanda esatta e numero di fornitori per componente
for j in components:
    model.addConstr(
        gp.quicksum(x[i, j] for i in suppliers if (i, j) in A) == demand[j],
        name=f"domanda_{j}"
    )
    model.addConstr(
        gp.quicksum(y[i, j] for i in suppliers if (i, j) in A) >= 2,
        name=f"fornitori_min_{j}"
    )
    model.addConstr(
        gp.quicksum(y[i, j] for i in suppliers if (i, j) in A) <= 3,
        name=f"fornitori_max_{j}"
    )

# Legami quantità-uso-attivazione e lotto minimo
for (i, j) in available:
    M = min(capacity[i], demand[j])
    model.addConstr(y[i, j] <= z[i], name=f"attivazione_{i}_{j}")
    model.addConstr(x[i, j] >= lot[j] * y[i, j], name=f"lotto_{i}_{j}")
    model.addConstr(x[i, j] <= M * y[i, j], name=f"uso_{i}_{j}")

# Capacità condivisa
for i in suppliers:
    model.addConstr(
        gp.quicksum(x[i, j] for j in components if (i, j) in A) <= capacity[i] * z[i],
        name=f"capacita_{i}"
    )

# Qualità media ponderata per componente
for j in components:
    model.addConstr(
        gp.quicksum(quality[i, j] * x[i, j] for i in suppliers if (i, j) in A) >= 95 * demand[j],
        name=f"qualita_{j}"
    )

# Rischio complessivo
model.addConstr(
    gp.quicksum(risk[i] * x[i, j] for (i, j) in available) <= 1300,
    name="rischio"
)

# Attivazione fornitori
model.addConstr(gp.quicksum(z[i] for i in suppliers) <= 6, name="max_attivazioni")
model.addConstr(z["S1"] + z["S2"] >= 1, name="almeno_S1_S2")

# Funzione obiettivo
obj = (
    gp.quicksum(fixed_cost[i] * z[i] for i in suppliers)
    + gp.quicksum(cost[i, j] * x[i, j] for (i, j) in available)
)
model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

if model.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = model.ObjVal
    variables = {}

    for i in suppliers:
        variables[f"z_{i}"] = z[i].X

    for (i, j) in available:
        variables[f"y_{i}_{j}"] = y[i, j].X
        variables[f"x_{i}_{j}"] = x[i, j].X
else:
    status = {GRB.INFEASIBLE: "INFEASIBLE", GRB.UNBOUNDED: "UNBOUNDED"}.get(model.status, "UNKNOWN")
    objective = None
    variables = {}

result = {
    "status": status,
    "objective": objective,
    "variables": variables
}

print("SOLUTION_JSON=" + json.dumps(result))
