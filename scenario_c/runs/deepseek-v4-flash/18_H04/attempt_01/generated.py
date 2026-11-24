import gurobipy as gp
from gurobipy import GRB
import json

rotte = ["R1", "R2", "R3", "R4"]
tipi = ["Piccolo", "Medio", "Grande"]

domanda = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}
capacita = {"Piccolo": 8, "Medio": 14, "Grande": 20}
disponibilita = {"Piccolo": 10, "Medio": 9, "Grande": 6}
emissioni = {"Piccolo": 5, "Medio": 8, "Grande": 11}

costo = {
    ("R1", "Piccolo"): 45, ("R1", "Medio"): 62, ("R1", "Grande"): 82,
    ("R2", "Piccolo"): 52, ("R2", "Medio"): 68, ("R2", "Grande"): 88,
    ("R3", "Piccolo"): 40, ("R3", "Medio"): 58, ("R3", "Grande"): 79,
    ("R4", "Piccolo"): 60, ("R4", "Medio"): 77, ("R4", "Grande"): 96,
}

m = gp.Model("allocazione_flotta")
m.setParam("OutputFlag", 0)

x = {}
z = {}

for r in rotte:
    for t in tipi:
        x[r, t] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{r}_{t}")
        z[r, t] = m.addVar(vtype=GRB.BINARY, name=f"z_{r}_{t}")

m.setObjective(
    gp.quicksum(costo[r, t] * x[r, t] for r in rotte for t in tipi),
    GRB.MINIMIZE,
)

for r in rotte:
    m.addConstr(
        gp.quicksum(capacita[t] * x[r, t] for t in tipi) >= domanda[r],
        name=f"domanda_{r}",
    )
    m.addConstr(
        gp.quicksum(z[r, t] for t in tipi) <= 2,
        name=f"max_tipi_{r}",
    )
    for t in tipi:
        m.addConstr(x[r, t] <= disponibilita[t] * z[r, t], name=f"link_{r}_{t}")
        m.addConstr(x[r, t] >= z[r, t], name=f"uso_{r}_{t}")

for t in tipi:
    m.addConstr(
        gp.quicksum(x[r, t] for r in rotte) <= disponibilita[t],
        name=f"disponibilita_{t}",
    )

m.addConstr(
    gp.quicksum(emissioni[t] * x[r, t] for r in rotte for t in tipi) <= 145,
    name="limite_emissioni",
)

m.addConstr(x["R4", "Grande"] >= 1, name="r4_almeno_un_grande")

m.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.NUMERIC: "NUMERIC",
}

if m.Status == GRB.OPTIMAL:
    variabili = {v.VarName: float(v.X) for v in m.getVars()}
    result = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": variabili,
    }
else:
    result = {
        "status": status_names.get(m.Status, f"STATUS_{m.Status}"),
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result))
