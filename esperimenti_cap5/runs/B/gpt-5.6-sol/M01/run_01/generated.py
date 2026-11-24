import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
I = ["A", "B", "C", "D"]
Z = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]

# Parametri
f = {
    "A": 38,
    "B": 42,
    "C": 35,
    "D": 46
}

q = {
    "A": 2,
    "B": 3,
    "C": 2,
    "D": 3
}

c = {
    ("Z1", "A"): 8,  ("Z1", "B"): 14, ("Z1", "C"): 11, ("Z1", "D"): 17,
    ("Z2", "A"): 10, ("Z2", "B"): 9,  ("Z2", "C"): 13, ("Z2", "D"): 15,
    ("Z3", "A"): 12, ("Z3", "B"): 8,  ("Z3", "C"): 14, ("Z3", "D"): 10,
    ("Z4", "A"): 15, ("Z4", "B"): 11, ("Z4", "C"): 9,  ("Z4", "D"): 7,
    ("Z5", "A"): 9,  ("Z5", "B"): 13, ("Z5", "C"): 8,  ("Z5", "D"): 14,
    ("Z6", "A"): 14, ("Z6", "B"): 10, ("Z6", "C"): 7,  ("Z6", "D"): 9
}

p = 2

# Ambiente Gurobi senza output aggiuntivo
env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

# Modello
model = gp.Model("M01_localizzazione_centri", env=env)

# Variabili decisionali
y = model.addVars(I, vtype=GRB.BINARY, name="y")
x = model.addVars(Z, I, vtype=GRB.BINARY, name="x")

# Funzione obiettivo
model.setObjective(
    gp.quicksum(f[i] * y[i] for i in I) +
    gp.quicksum(c[z, i] * x[z, i] for z in Z for i in I),
    GRB.MINIMIZE
)

# Apertura di esattamente due centri
model.addConstr(
    gp.quicksum(y[i] for i in I) == p,
    name="numero_centri"
)

# Ogni zona è assegnata esattamente a un centro
model.addConstrs(
    (gp.quicksum(x[z, i] for i in I) == 1 for z in Z),
    name="assegnazione"
)

# Capacità e divieto di assegnazione a siti chiusi
model.addConstrs(
    (gp.quicksum(x[z, i] for z in Z) <= q[i] * y[i] for i in I),
    name="capacita"
)

# Risoluzione
model.optimize()

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

status = status_names.get(model.Status, "STATUS_" + str(model.Status))

if model.Status == GRB.OPTIMAL:
    variables = {}
    for i in I:
        value = float(round(y[i].X))
        variables[y[i].VarName] = value
    for z in Z:
        for i in I:
            value = float(round(x[z, i].X))
            variables[x[z, i].VarName] = value

    result = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
