import gurobipy as gp
from gurobipy import GRB
import json

zone = ["Z1","Z2","Z3","Z4","Z5","Z6","Z7","Z8","Z9","Z10","Z11","Z12"]
station = ["A","B","C","D","E","F","G","H"]

costo_fisso = {
    "A": 35, "B": 32, "C": 40, "D": 30,
    "E": 38, "F": 33, "G": 36, "H": 31
}

capacita = {
    "A": 42, "B": 44, "C": 46, "D": 40,
    "E": 45, "F": 43, "G": 44, "H": 42
}

domanda = {
    "Z1": 8, "Z2": 7, "Z3": 10, "Z4": 6,
    "Z5": 9, "Z6": 8, "Z7": 7, "Z8": 11,
    "Z9": 6, "Z10": 9, "Z11": 8, "Z12": 7
}

tempo = {
    "Z1": {"A": 3, "B": 5},
    "Z2": {"A": 6, "B": 8, "C": 10},
    "Z3": {"B": 11, "C": 4, "D": 6},
    "Z4": {"C": 7, "D": 9},
    "Z5": {"A": 6, "D": 3, "E": 5},
    "Z6": {"B": 11, "E": 8, "F": 10},
    "Z7": {"C": 7, "F": 4, "G": 6, "H": 8},
    "Z8": {"D": 3, "G": 9, "H": 11},
    "Z9": {"E": 8, "F": 10, "H": 5},
    "Z10": {"F": 4, "G": 6, "H": 8},
    "Z11": {"A": 6, "E": 5, "H": 11},
    "Z12": {"B": 11, "G": 3, "H": 5}
}

ovest = ["A","B","C","D"]
est = ["E","F","G","H"]
critiche = ["Z3","Z8","Z11"]

m = gp.Model("Rete_emergenza")
m.setParam("OutputFlag", 0)

y = m.addVars(station, vtype=GRB.BINARY, name="y")

x = {}
for i in zone:
    for j in tempo[i]:
        x[i, j] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

m.setObjective(
    gp.quicksum(costo_fisso[j] * y[j] for j in station)
    + gp.quicksum(domanda[i] * tempo[i][j] * x[i, j]
                  for i in zone for j in tempo[i]),
    GRB.MINIMIZE
)

m.addConstr(gp.quicksum(y[j] for j in station) == 4, "quattro_stazioni")
m.addConstr(gp.quicksum(y[j] for j in ovest) >= 1, "almeno_ovest")
m.addConstr(gp.quicksum(y[j] for j in est) >= 1, "almeno_est")

for i in zone:
    m.addConstr(
        gp.quicksum(x[i, j] for j in tempo[i]) == 1,
        f"assegnazione_{i}"
    )

for i in zone:
    for j in tempo[i]:
        m.addConstr(x[i, j] <= y[j], f"apertura_{i}_{j}")

for j in station:
    m.addConstr(
        gp.quicksum(domanda[i] * x[i, j] for i in zone if j in tempo[i])
        <= capacita[j] * y[j],
        f"capacita_{j}"
    )

for i in critiche:
    m.addConstr(
        gp.quicksum(y[j] for j in tempo[i]) >= 2,
        f"backup_{i}"
    )

m.optimize()

if m.Status == GRB.OPTIMAL:
    variables = {}
    for j in station:
        variables[f"y_{j}"] = y[j].X
    for (i, j), var in x.items():
        variables[f"x_{i}_{j}"] = var.X

    solution = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variables
    }
else:
    solution = {
        "status": str(m.Status),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(solution, ensure_ascii=False))
