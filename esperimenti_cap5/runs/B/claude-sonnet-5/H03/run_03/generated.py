import gurobipy as gp
from gurobipy import GRB
import json

# ---- Dati ----
days = ['Lun','Mar','Mer','Gio','Ven','Sab','Dom']
employees = ['E1','E2','E3','E4','E5','E6','E7','E8']

demand = {'Lun':4,'Mar':3,'Mer':4,'Gio':4,'Ven':5,'Sab':3,'Dom':3}

# Costi: None = indisponibile
cost = {
    'E1': {'Lun':9,'Mar':9,'Mer':10,'Gio':9,'Ven':11,'Sab':14,'Dom':None},
    'E2': {'Lun':10,'Mar':9,'Mer':9,'Gio':10,'Ven':10,'Sab':None,'Dom':14},
    'E3': {'Lun':9,'Mar':10,'Mer':9,'Gio':9,'Ven':12,'Sab':12,'Dom':13},
    'E4': {'Lun':7,'Mar':None,'Mer':7,'Gio':8,'Ven':8,'Sab':11,'Dom':11},
    'E5': {'Lun':8,'Mar':7,'Mer':8,'Gio':None,'Ven':9,'Sab':10,'Dom':12},
    'E6': {'Lun':None,'Mar':8,'Mer':8,'Gio':7,'Ven':8,'Sab':12,'Dom':10},
    'E7': {'Lun':8,'Mar':8,'Mer':7,'Gio':9,'Ven':7,'Sab':11,'Dom':None},
    'E8': {'Lun':9,'Mar':7,'Mer':8,'Gio':8,'Ven':7,'Sab':10,'Dom':11},
}

seniors = ['E1','E2','E3']
specialists = ['E7','E8']
minD, maxD = 3, 5

model = gp.Model("turnazione_H03")
model.Params.OutputFlag = 0

# ---- Variabili ----
x = {}
for e in employees:
    for d in days:
        available = cost[e][d] is not None
        c = cost[e][d] if available else 0.0
        ub = 1 if available else 0
        x[e, d] = model.addVar(vtype=GRB.BINARY, ub=ub, obj=c, name=f"x_{e}_{d}")

model.ModelSense = GRB.MINIMIZE

# ---- Vincoli ----
# Copertura domanda
for d in days:
    model.addConstr(gp.quicksum(x[e, d] for e in employees) >= demand[d], name=f"dom_{d}")

# Almeno un senior al giorno
for d in days:
    model.addConstr(gp.quicksum(x[e, d] for e in seniors) >= 1, name=f"senior_{d}")

# Giorni lavorati per dipendente (min/max)
for e in employees:
    tot = gp.quicksum(x[e, d] for d in days)
    model.addConstr(tot >= minD, name=f"minD_{e}")
    model.addConstr(tot <= maxD, name=f"maxD_{e}")

# Nessun dipendente lavora 4 giorni consecutivi
for e in employees:
    for start in range(0, 4):  # windows: 0-3,1-4,2-5,3-6
        window = days[start:start+4]
        model.addConstr(gp.quicksum(x[e, d] for d in window) <= 3,
                         name=f"cons_{e}_{start}")

# Specialisti presenti giovedì e venerdì
model.addConstr(gp.quicksum(x[e, 'Gio'] for e in specialists) >= 1, name="spec_Gio")
model.addConstr(gp.quicksum(x[e, 'Ven'] for e in specialists) >= 1, name="spec_Ven")

# E1, E2: massimo un giorno di weekend
model.addConstr(x['E1', 'Sab'] + x['E1', 'Dom'] <= 1, name="we_E1")
model.addConstr(x['E2', 'Sab'] + x['E2', 'Dom'] <= 1, name="we_E2")

# ---- Risoluzione ----
model.optimize()

status = model.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(model.ObjVal, 4)
    variables = {}
    for e in employees:
        for d in days:
            variables[f"x_{e}_{d}"] = round(x[e, d].X, 4)
    result["variables"] = variables

    # Stampa riepilogo leggibile
    print("Stato solver:", result["status"])
    print("Costo ottimo:", result["objective"])
    print("Decisioni non nulle (x_e_d = 1):")
    for e in employees:
        for d in days:
            if x[e, d].X > 0.5:
                print(f"  {e} lavora {d} (costo {cost[e][d]})")
else:
    if status == GRB.INFEASIBLE:
        result["status"] = "INFEASIBLE"
    elif status == GRB.UNBOUNDED:
        result["status"] = "UNBOUNDED"
    else:
        result["status"] = str(status)
    result["objective"] = None
    result["variables"] = {}
    print("Stato solver:", result["status"])

print("SOLUTION_JSON=" + json.dumps(result))
