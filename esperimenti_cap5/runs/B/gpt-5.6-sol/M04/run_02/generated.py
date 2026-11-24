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

model = gp.Model("composizione_flotta_giornaliera")
model.Params.OutputFlag = 0

x = {
    i: model.addVar(
        lb=0,
        ub=disponibilita[i],
        vtype=GRB.INTEGER,
        name=f"x_{i}"
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

model.addConstr(x["Refrigerato"] >= 1, name="almeno_un_refrigerato")
model.addConstr(x["Elettrico"] >= 1, name="almeno_un_elettrico")

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
    result = {
        "status": status,
        "objective": float(model.ObjVal),
        "variables": {
            x[i].VarName: float(round(x[i].X))
            for i in tipi
        }
    }
else:
    result = {
        "status": status,
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":"), ensure_ascii=False))
