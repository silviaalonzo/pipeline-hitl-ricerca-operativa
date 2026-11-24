import gurobipy as gp
from gurobipy import GRB
import json

tipi = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {
    "Van": 18,
    "Autocarro": 30,
    "Refrigerato": 20,
    "Elettrico": 16,
    "Bilico": 42
}

portata = {
    "Van": 8,
    "Autocarro": 18,
    "Refrigerato": 10,
    "Elettrico": 7,
    "Bilico": 28
}

costo = {
    "Van": 120,
    "Autocarro": 180,
    "Refrigerato": 210,
    "Elettrico": 150,
    "Bilico": 260
}

emissioni = {
    "Van": 12,
    "Autocarro": 22,
    "Refrigerato": 15,
    "Elettrico": 4,
    "Bilico": 32
}

disponibilita = {
    "Van": 8,
    "Autocarro": 6,
    "Refrigerato": 4,
    "Elettrico": 5,
    "Bilico": 3
}

volume_minimo = 180
portata_minima = 95
emissioni_massime = 145

env = gp.Env(empty=True)
env.setParam("OutputFlag", 0)
env.start()

model = gp.Model("composizione_flotta_giornaliera", env=env)
model.Params.MIPGap = 0.0

x = {
    i: model.addVar(
        lb=0,
        ub=disponibilita[i],
        vtype=GRB.INTEGER,
        name="x_" + i
    )
    for i in tipi
}

model.setObjective(
    gp.quicksum(costo[i] * x[i] for i in tipi),
    GRB.MINIMIZE
)

model.addConstr(
    gp.quicksum(volume[i] * x[i] for i in tipi) >= volume_minimo,
    name="volume_minimo"
)

model.addConstr(
    gp.quicksum(portata[i] * x[i] for i in tipi) >= portata_minima,
    name="portata_minima"
)

model.addConstr(
    gp.quicksum(emissioni[i] * x[i] for i in tipi) <= emissioni_massime,
    name="emissioni_massime"
)

model.addConstr(
    x["Refrigerato"] >= 1,
    name="almeno_un_refrigerato"
)

model.addConstr(
    x["Elettrico"] >= 1,
    name="almeno_un_elettrico"
)

model.optimize()

status_labels = [
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT",
    "SOLUTION_LIMIT", "INTERRUPTED", "NUMERIC", "SUBOPTIMAL",
    "INPROGRESS", "USER_OBJ_LIMIT", "WORK_LIMIT", "MEM_LIMIT"
]

status = "STATUS_" + str(model.Status)
for label in status_labels:
    if getattr(GRB, label, None) == model.Status:
        status = label
        break

if model.Status == GRB.OPTIMAL:
    risultato = {
        "status": "OPTIMAL",
        "objective": float(round(model.ObjVal, 10)),
        "variables": {
            "x_" + i: float(round(x[i].X, 10))
            for i in tipi
        }
    }
else:
    risultato = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(risultato, separators=(",", ":")))
