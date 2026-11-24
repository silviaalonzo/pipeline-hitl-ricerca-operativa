import gurobipy as gp
from gurobipy import GRB
import json

# Insiemi
days = ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"]
employees = ["E1","E2","E3","E4","E5","E6","E7","E8"]

S = ["E1","E2","E3"]      # senior
P = ["E7","E8"]           # specialisti
W = ["E1","E2"]           # limite weekend
WE = ["Sab","Dom"]        # giorni weekend

# Domanda giornaliera
demand = {"Lun":4, "Mar":3, "Mer":4, "Gio":4, "Ven":5, "Sab":3, "Dom":3}

# Costi (None = indisponibile)
cost = {
    "E1": {"Lun":9,  "Mar":9,  "Mer":10, "Gio":9,  "Ven":11, "Sab":14, "Dom":None},
    "E2": {"Lun":10, "Mar":9,  "Mer":9,  "Gio":10, "Ven":10, "Sab":None,"Dom":14},
    "E3": {"Lun":9,  "Mar":10, "Mer":9,  "Gio":9,  "Ven":12, "Sab":12, "Dom":13},
    "E4": {"Lun":7,  "Mar":None,"Mer":7, "Gio":8,  "Ven":8,  "Sab":11, "Dom":11},
    "E5": {"Lun":8,  "Mar":7,  "Mer":8,  "Gio":None,"Ven":9, "Sab":10, "Dom":12},
    "E6": {"Lun":None,"Mar":8, "Mer":8,  "Gio":7,  "Ven":8,  "Sab":12, "Dom":10},
    "E7": {"Lun":8,  "Mar":8,  "Mer":7,  "Gio":9,  "Ven":7,  "Sab":11, "Dom":None},
    "E8": {"Lun":9,  "Mar":7,  "Mer":8,  "Gio":8,  "Ven":7,  "Sab":10, "Dom":11},
}

L_min, L_max = 3, 5
K = 4  # max giorni consecutivi lavorabili

model = gp.Model("H03_turnazione")
model.Params.OutputFlag = 0

# Variabili
x = {}
for e in employees:
    for d in days:
        x[e,d] = model.addVar(vtype=GRB.BINARY, name=f"x_{e}_{d}")

# Disponibilità
for e in employees:
    for d in days:
        if cost[e][d] is None:
            model.addConstr(x[e,d] == 0, name=f"avail_{e}_{d}")

# Domanda minima giornaliera
for d in days:
    model.addConstr(gp.quicksum(x[e,d] for e in employees) >= demand[d], name=f"demand_{d}")

# Almeno un senior al giorno
for d in days:
    model.addConstr(gp.quicksum(x[e,d] for e in S) >= 1, name=f"senior_{d}")

# Giorni lavorati per dipendente
for e in employees:
    tot = gp.quicksum(x[e,d] for d in days)
    model.addConstr(tot >= L_min, name=f"min_days_{e}")
    model.addConstr(tot <= L_max, name=f"max_days_{e}")

# Nessuna sequenza di 4 giorni consecutivi (finestre senza wrap)
n = len(days)
for e in employees:
    for start in range(0, n - K + 1):
        window = days[start:start+K]
        model.addConstr(gp.quicksum(x[e,d] for d in window) <= K-1,
                         name=f"noconsec_{e}_{start}")

# Specialisti presenti giovedì e venerdì
model.addConstr(gp.quicksum(x[e,"Gio"] for e in P) >= 1, name="spec_gio")
model.addConstr(gp.quicksum(x[e,"Ven"] for e in P) >= 1, name="spec_ven")

# Limite weekend per E1 ed E2
for e in W:
    model.addConstr(gp.quicksum(x[e,d] for d in WE) <= 1, name=f"weekend_{e}")

# Obiettivo
obj = gp.quicksum(cost[e][d] * x[e,d] for e in employees for d in days if cost[e][d] is not None)
model.setObjective(obj, GRB.MINIMIZE)

model.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status = status_map.get(model.Status, str(model.Status))

result = {"status": status, "objective": None, "variables": {}}

if model.Status == GRB.OPTIMAL:
    variables = {}
    for e in employees:
        for d in days:
            variables[f"x_{e}_{d}"] = round(x[e,d].X, 2)
    result["objective"] = round(model.ObjVal, 2)
    result["variables"] = variables

    # Stampa leggibile delle decisioni non nulle
    print("Stato:", status)
    print("Costo ottimo:", model.ObjVal)
    print("Decisioni non nulle:")
    for e in employees:
        for d in days:
            if x[e,d].X > 0.5:
                print(f"  {e} lavora {d} (costo {cost[e][d]})")

print("SOLUTION_JSON=" + json.dumps(result))
