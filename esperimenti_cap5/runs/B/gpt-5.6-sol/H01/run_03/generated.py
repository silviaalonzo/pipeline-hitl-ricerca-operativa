import gurobipy as gp
from gurobipy import GRB
import json

I = ["A", "B", "C", "D", "E", "F"]
J = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8"]
NORD = ["A", "B", "C"]
SUD = ["D", "E", "F"]

domanda = {
    "Z1": 30, "Z2": 25, "Z3": 35, "Z4": 20,
    "Z5": 28, "Z6": 32, "Z7": 24, "Z8": 26
}

costo_fisso = {
    "A": 110, "B": 95, "C": 120,
    "D": 90, "E": 105, "F": 100
}

capacita = {
    "A": 90, "B": 80, "C": 110,
    "D": 75, "E": 95, "F": 85
}

costo = {
    "Z1": {"A": 4, "B": 7, "C": 6, "D": 10, "E": 9, "F": 11},
    "Z2": {"A": 5, "B": 4, "C": 8, "D": 9, "E": 7, "F": 10},
    "Z3": {"A": 7, "B": 5, "C": 4, "D": 8, "E": 9, "F": 7},
    "Z4": {"A": 9, "B": 8, "C": 7, "D": 4, "E": 5, "F": 6},
    "Z5": {"A": 8, "B": 9, "C": 6, "D": 5, "E": 4, "F": 7},
    "Z6": {"A": 10, "B": 8, "C": 7, "D": 6, "E": 5, "F": 4},
    "Z7": {"A": 6, "B": 7, "C": 5, "D": 8, "E": 6, "F": 7},
    "Z8": {"A": 7, "B": 6, "C": 8, "D": 5, "E": 7, "F": 4}
}

emissione = {
    "Z1": {"A": 1, "B": 2, "C": 2, "D": 4, "E": 3, "F": 4},
    "Z2": {"A": 2, "B": 1, "C": 3, "D": 3, "E": 2, "F": 4},
    "Z3": {"A": 3, "B": 2, "C": 1, "D": 3, "E": 4, "F": 3},
    "Z4": {"A": 4, "B": 3, "C": 3, "D": 1, "E": 2, "F": 2},
    "Z5": {"A": 3, "B": 4, "C": 2, "D": 2, "E": 1, "F": 3},
    "Z6": {"A": 4, "B": 3, "C": 3, "D": 2, "E": 2, "F": 1},
    "Z7": {"A": 2, "B": 3, "C": 1, "D": 3, "E": 2, "F": 3},
    "Z8": {"A": 3, "B": 2, "C": 3, "D": 1, "E": 3, "F": 1}
}

L = 20
E_MAX = 470
K_MIN = 3
K_MAX = 4

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H01_rete_capacitata", env=env)

y = model.addVars(I, vtype=GRB.BINARY, name="y")
x = model.addVars(I, J, lb=0.0, vtype=GRB.CONTINUOUS, name="x")

model.setObjective(
    gp.quicksum(costo_fisso[i] * y[i] for i in I)
    + gp.quicksum(costo[j][i] * x[i, j] for i in I for j in J),
    GRB.MINIMIZE
)

model.addConstrs(
    (gp.quicksum(x[i, j] for i in I) == domanda[j] for j in J),
    name="domanda"
)

model.addConstrs(
    (gp.quicksum(x[i, j] for j in J) <= capacita[i] * y[i] for i in I),
    name="capacita_massima"
)

model.addConstrs(
    (gp.quicksum(x[i, j] for j in J) >= L * y[i] for i in I),
    name="movimentazione_minima"
)

model.addConstr(
    gp.quicksum(y[i] for i in I) >= K_MIN,
    name="numero_minimo_centri"
)

model.addConstr(
    gp.quicksum(y[i] for i in I) <= K_MAX,
    name="numero_massimo_centri"
)

model.addConstr(
    gp.quicksum(y[i] for i in NORD) >= 1,
    name="resilienza_nord"
)

model.addConstr(
    gp.quicksum(y[i] for i in SUD) >= 1,
    name="resilienza_sud"
)

model.addConstr(
    gp.quicksum(emissione[j][i] * x[i, j] for i in I for j in J) <= E_MAX,
    name="limite_emissioni"
)

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
    def clean(value):
        value = float(value)
        if abs(value) < 1e-9:
            return 0.0
        return float(round(value, 10))

    variables = {}
    for variable in model.getVars():
        variables[variable.VarName] = clean(variable.X)

    payload = {
        "status": "OPTIMAL",
        "objective": clean(model.ObjVal),
        "variables": variables
    }
else:
    payload = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":"), allow_nan=False))
