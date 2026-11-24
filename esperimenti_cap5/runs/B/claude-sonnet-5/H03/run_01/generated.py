import gurobipy as gp
from gurobipy import GRB
import json

# ---------------- Dati ----------------
days = ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"]
employees = ["E1","E2","E3","E4","E5","E6","E7","E8"]

demand = {1:4, 2:3, 3:4, 4:4, 5:5, 6:3, 7:3}  # 1..7 -> Lun..Dom

# Costi: None indica indisponibilità ("—")
cost = {
    "E1": [9, 9, 10, 9, 11, 14, None],
    "E2": [10, 9, 9, 10, 10, None, 14],
    "E3": [9, 10, 9, 9, 12, 12, 13],
    "E4": [7, None, 7, 8, 8, 11, 11],
    "E5": [8, 7, 8, None, 9, 10, 12],
    "E6": [None, 8, 8, 7, 8, 12, 10],
    "E7": [8, 8, 7, 9, 7, 11, None],
    "E8": [9, 7, 8, 8, 7, 10, 11],
}

senior = ["E1", "E2", "E3"]
specialist = ["E7", "E8"]
weekend_days = [6, 7]  # Sab, Dom

D = list(range(1, 8))

# ---------------- Modello ----------------
m = gp.Model("H03_turnazione")

x = {}
for e in employees:
    for d in D:
        c = cost[e][d - 1]
        avail = c is not None
        ub = 1 if avail else 0
        obj_c = c if avail else 0
        x[e, d] = m.addVar(vtype=GRB.BINARY, ub=ub, obj=obj_c, name=f"x_{e}_{d}")

m.modelSense = GRB.MINIMIZE
m.update()

# 1. Copertura minima giornaliera
for d in D:
    m.addConstr(gp.quicksum(x[e, d] for e in employees) >= demand[d], name=f"coverage_{d}")

# 2. Almeno un senior al giorno
for d in D:
    m.addConstr(gp.quicksum(x[e, d] for e in senior) >= 1, name=f"senior_{d}")

# 3. Giorni lavorati per dipendente: 3 <= ... <= 5
for e in employees:
    tot = gp.quicksum(x[e, d] for d in D)
    m.addConstr(tot >= 3, name=f"min_days_{e}")
    m.addConstr(tot <= 5, name=f"max_days_{e}")

# 4. No 4 giorni consecutivi
for e in employees:
    for w in range(1, 5):  # finestre: 1-4,2-5,3-6,4-7
        m.addConstr(gp.quicksum(x[e, d] for d in range(w, w + 4)) <= 3,
                    name=f"no4cons_{e}_{w}")

# 5. Specialisti presenti Gio (4) e Ven (5)
m.addConstr(gp.quicksum(x[e, 4] for e in specialist) >= 1, name="specialist_thu")
m.addConstr(gp.quicksum(x[e, 5] for e in specialist) >= 1, name="specialist_fri")

# 6. E1, E2: massimo un giorno di weekend
for e in ["E1", "E2"]:
    m.addConstr(gp.quicksum(x[e, d] for d in weekend_days) <= 1, name=f"weekend_{e}")

m.optimize()

# ---------------- Output ----------------
result = {"status": None, "objective": None, "variables": {}}

if m.status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.objVal, 2)
    for e in employees:
        for d in D:
            result["variables"][f"x_{e}_{d}"] = round(x[e, d].X, 2)
else:
    result["status"] = str(m.status)
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
