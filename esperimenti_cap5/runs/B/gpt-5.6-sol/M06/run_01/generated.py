import json
import gurobipy as gp
from gurobipy import GRB

# Insiemi
J = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
M = ["A", "B"]

# Tempi di lavorazione per le sole coppie compatibili
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5
}

K = list(p.keys())
a = {(j, m): 1 if (j, m) in p else 0 for j in J for m in M}

# Ambiente silenzioso, per produrre solamente la riga JSON finale
env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M06_bilanciamento", env=env)

# Variabili decisionali
x = {
    (j, m): model.addVar(vtype=GRB.BINARY, name=f"x_{j}_{m}")
    for j in J for m in M
}
Cmax = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Cmax")

# Ogni lavoro deve essere assegnato esattamente a una macchina
for j in J:
    model.addConstr(
        gp.quicksum(x[j, m] for m in M) == 1,
        name=f"assegnazione_{j}"
    )

# Vincoli di compatibilità
for j in J:
    for m in M:
        model.addConstr(
            x[j, m] <= a[j, m],
            name=f"compatibilita_{j}_{m}"
        )

# Il makespan deve dominare il carico di ogni macchina
for m in M:
    model.addConstr(
        gp.quicksum(
            p[j, m] * x[j, m]
            for j in J if (j, m) in p
        ) <= Cmax,
        name=f"carico_{m}"
    )

# Funzione obiettivo
model.setObjective(Cmax, GRB.MINIMIZE)
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

status_code = model.Status
status_text = status_names.get(status_code, f"STATUS_{status_code}")

def clean_value(value):
    if abs(value) <= 1e-9:
        return 0.0
    if abs(value - round(value)) <= 1e-9:
        return float(round(value))
    return float(value)

if status_code == GRB.OPTIMAL:
    variables = {}
    for j in J:
        for m in M:
            variables[f"x_{j}_{m}"] = clean_value(x[j, m].X)
    variables["Cmax"] = clean_value(Cmax.X)

    result = {
        "status": "OPTIMAL",
        "objective": clean_value(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status_text,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
