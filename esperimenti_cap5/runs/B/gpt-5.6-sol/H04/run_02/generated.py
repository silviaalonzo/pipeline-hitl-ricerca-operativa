import gurobipy as gp
from gurobipy import GRB
import json

veicoli = ["Piccolo", "Medio", "Grande"]
rotte = ["R1", "R2", "R3", "R4"]

domanda = {
    "R1": 42,
    "R2": 55,
    "R3": 38,
    "R4": 64
}

capacita = {
    "Piccolo": 8,
    "Medio": 14,
    "Grande": 20
}

disponibilita = {
    "Piccolo": 10,
    "Medio": 9,
    "Grande": 6
}

emissioni = {
    "Piccolo": 5,
    "Medio": 8,
    "Grande": 11
}

costi = {
    ("Piccolo", "R1"): 45,
    ("Piccolo", "R2"): 52,
    ("Piccolo", "R3"): 40,
    ("Piccolo", "R4"): 60,
    ("Medio", "R1"): 62,
    ("Medio", "R2"): 68,
    ("Medio", "R3"): 58,
    ("Medio", "R4"): 77,
    ("Grande", "R1"): 82,
    ("Grande", "R2"): 88,
    ("Grande", "R3"): 79,
    ("Grande", "R4"): 96
}

limite_emissioni = 145

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("H04_allocazione_flotta", env=env)
model.Params.MIPGap = 0.0

x = model.addVars(
    veicoli,
    rotte,
    vtype=GRB.INTEGER,
    lb=0,
    name="x"
)

y = model.addVars(
    veicoli,
    rotte,
    vtype=GRB.BINARY,
    name="y"
)

model.setObjective(
    gp.quicksum(costi[v, r] * x[v, r] for v in veicoli for r in rotte),
    GRB.MINIMIZE
)

for r in rotte:
    model.addConstr(
        gp.quicksum(capacita[v] * x[v, r] for v in veicoli) >= domanda[r],
        name="domanda_" + r
    )

for v in veicoli:
    model.addConstr(
        gp.quicksum(x[v, r] for r in rotte) <= disponibilita[v],
        name="disponibilita_" + v
    )

for v in veicoli:
    for r in rotte:
        model.addConstr(
            x[v, r] <= disponibilita[v] * y[v, r],
            name="link_superiore_" + v + "_" + r
        )
        model.addConstr(
            x[v, r] >= y[v, r],
            name="link_inferiore_" + v + "_" + r
        )

for r in rotte:
    model.addConstr(
        gp.quicksum(y[v, r] for v in veicoli) <= 2,
        name="massimo_due_tipi_" + r
    )

model.addConstr(
    x["Grande", "R4"] >= 1,
    name="grande_obbligatorio_R4"
)

model.addConstr(
    gp.quicksum(
        emissioni[v] * x[v, r]
        for v in veicoli
        for r in rotte
    ) <= limite_emissioni,
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
    valori = {}
    for v in veicoli:
        for r in rotte:
            valori[x[v, r].VarName] = float(round(x[v, r].X))
    for v in veicoli:
        for r in rotte:
            valori[y[v, r].VarName] = float(round(y[v, r].X))

    risultato = {
        "status": status,
        "objective": float(round(model.ObjVal, 10)),
        "variables": valori
    }
else:
    risultato = {
        "status": status,
        "objective": None,
        "variables": {}
    }

model.dispose()
env.dispose()

print("SOLUTION_JSON=" + json.dumps(risultato, separators=(",", ":")))
