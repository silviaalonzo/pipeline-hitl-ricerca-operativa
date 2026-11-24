import gurobipy as gp
from gurobipy import GRB
import json

# --- Dati ---
jobs = ["J1","J2","J3","J4","J5","J6","J7"]
machines = ["A","B"]

# tempi di lavorazione (None = incompatibile)
p = {
    ("J1","A"):7, ("J1","B"):9,
    ("J2","A"):6, ("J2","B"):5,
    ("J3","A"):8, ("J3","B"):7,
    ("J4","A"):5, ("J4","B"):8,
    ("J5","A"):9, ("J5","B"):6,
    ("J6","A"):4, ("J6","B"):7,
    ("J7","B"):5   # J7 incompatibile con A
}

# coppie compatibili
pairs = list(p.keys())

# --- Modello ---
m = gp.Model("bilanciamento_2_macchine")

x = m.addVars(pairs, vtype=GRB.BINARY, name="x")
Cmax = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Cmax")

# Obiettivo: minimizzare il makespan
m.setObjective(Cmax, GRB.MINIMIZE)

# Vincolo: ogni lavoro assegnato a esattamente una macchina compatibile
for j in jobs:
    compatible_m = [mm for (jj, mm) in pairs if jj == j]
    m.addConstr(gp.quicksum(x[j, mm] for mm in compatible_m) == 1, name=f"assign_{j}")

# Vincolo: carico di ciascuna macchina <= Cmax
for mm in machines:
    jobs_on_m = [jj for (jj, mmm) in pairs if mmm == mm]
    m.addConstr(
        gp.quicksum(p[(jj, mm)] * x[jj, mm] for jj in jobs_on_m) <= Cmax,
        name=f"load_{mm}"
    )

m.optimize()

# --- Output ---
status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED"
}
status = status_map.get(m.status, str(m.status))

if m.status == GRB.OPTIMAL:
    variables = {}
    for (j, mm) in pairs:
        variables[f"x_{j}_{mm}"] = round(x[j, mm].X, 4)
    variables["Cmax"] = round(Cmax.X, 4)
    objective = round(m.ObjVal, 4)

    # Stampa dettagli leggibili
    print("Stato solver:", status)
    print("Makespan ottimo:", objective)
    for mm in machines:
        assigned = [j for (jj, mmm) in pairs if mmm == mm and jj == jj
                    for j in [jj] if x[j, mm].X > 0.5]
        load = sum(p[(j, mm)] for j in assigned)
        print(f"Macchina {mm}: lavori {assigned}, carico = {load}")

    result = {"status": status, "objective": objective, "variables": variables}
else:
    result = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(result))
