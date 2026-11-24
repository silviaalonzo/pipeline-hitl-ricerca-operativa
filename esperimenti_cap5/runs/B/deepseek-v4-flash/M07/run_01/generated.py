import gurobipy as gp
import json

fornitori = ["A", "B", "C", "D"]

costo = {"A": 11, "B": 10, "C": 12, "D": 9}
fisso = {"A": 80, "B": 95, "C": 60, "D": 120}
capacita = {"A": 80, "B": 100, "C": 70, "D": 90}
ordine_min = {"A": 20, "B": 25, "C": 15, "D": 20}
qualita = {"A": 96, "B": 90, "C": 98, "D": 88}
emissioni = {"A": 3, "B": 4, "C": 2, "D": 5}

m = gp.Model("M07")
m.Params.OutputFlag = 0

x = {i: m.addVar(vtype=gp.GRB.INTEGER, name=f"x_{i}") for i in fornitori}
y = {i: m.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}") for i in fornitori}

m.setObjective(
    gp.quicksum(costo[i] * x[i] + fisso[i] * y[i] for i in fornitori),
    gp.GRB.MINIMIZE,
)

m.addConstr(gp.quicksum(x[i] for i in fornitori) == 180, "totale")
m.addConstr(gp.quicksum(y[i] for i in fornitori) >= 2, "almeno_due")

for i in fornitori:
    m.addConstr(x[i] >= ordine_min[i] * y[i], name=f"minimo_{i}")
    m.addConstr(x[i] <= capacita[i] * y[i], name=f"capacita_{i}")

m.addConstr(gp.quicksum(qualita[i] * x[i] for i in fornitori) >= 92 * 180, "qualita")
m.addConstr(gp.quicksum(emissioni[i] * x[i] for i in fornitori) <= 650, "emissioni")

m.optimize()

if m.Status == gp.GRB.OPTIMAL:
    variabili = {}
    for i in fornitori:
        variabili[f"x_{i}"] = x[i].X
    for i in fornitori:
        variabili[f"y_{i}"] = y[i].X

    risultato = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variabili,
    }
else:
    status_map = {
        gp.GRB.INFEASIBLE: "INFEASIBLE",
        gp.GRB.UNBOUNDED: "UNBOUNDED",
        gp.GRB.INF_OR_UNBD: "INF_OR_UNBD",
        gp.GRB.NUMERIC: "NUMERIC",
        gp.GRB.SUBOPTIMAL: "SUBOPTIMAL",
        gp.GRB.TIME_LIMIT: "TIME_LIMIT",
        gp.GRB.NODE_LIMIT: "NODE_LIMIT",
        gp.GRB.INTERRUPTED: "INTERRUPTED",
    }
    stato = status_map.get(m.Status, "UNKNOWN")
    risultato = {"status": stato, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(risultato, separators=(",", ":")))
