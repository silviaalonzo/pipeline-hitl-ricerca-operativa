import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
J = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
M = ["A", "B"]

# Tempi definiti esclusivamente per le coppie compatibili
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5
}
E = list(p.keys())

# Ambiente silenzioso, per produrre soltanto la riga JSON finale
env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("M06_bilanciamento_due_macchine", env=env)
model.Params.OutputFlag = 0

# Variabili decisionali
x = model.addVars(E, vtype=GRB.BINARY, name="x")
C_max = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="C_max")

# Ogni lavoro deve essere assegnato a una sola macchina compatibile
for j in J:
    model.addConstr(
        gp.quicksum(x[j, m] for m in M if (j, m) in p) == 1,
        name=f"assegnazione_{j}"
    )

# Il makespan deve essere almeno pari al carico di ogni macchina
for m in M:
    model.addConstr(
        gp.quicksum(p[j, m] * x[j, m] for j in J if (j, m) in p) <= C_max,
        name=f"carico_{m}"
    )

# Funzione obiettivo
model.setObjective(C_max, GRB.MINIMIZE)

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
status = status_names.get(model.Status, str(model.Status))

if model.Status == GRB.OPTIMAL:
    variables = {"C_max": float(C_max.X)}
    for j, m in E:
        value = float(round(x[j, m].X))
        variables[f"x[{j},{m}]"] = value

    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": variables
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
