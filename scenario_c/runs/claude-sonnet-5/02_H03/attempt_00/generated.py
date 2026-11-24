import gurobipy as gp
from gurobipy import GRB

# --- Dati ---
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]

demand = {"Lun": 4, "Mar": 3, "Mer": 4, "Gio": 4, "Ven": 5, "Sab": 3, "Dom": 3}

# Costi; None indica indisponibilità ("—")
cost = {
    "E1": {"Lun": 9,  "Mar": 9,  "Mer": 10, "Gio": 9,  "Ven": 11, "Sab": 14, "Dom": None},
    "E2": {"Lun": 10, "Mar": 9,  "Mer": 9,  "Gio": 10, "Ven": 10, "Sab": None, "Dom": 14},
    "E3": {"Lun": 9,  "Mar": 10, "Mer": 9,  "Gio": 9,  "Ven": 12, "Sab": 12, "Dom": 13},
    "E4": {"Lun": 7,  "Mar": None, "Mer": 7, "Gio": 8, "Ven": 8,  "Sab": 11, "Dom": 11},
    "E5": {"Lun": 8,  "Mar": 7,  "Mer": 8,  "Gio": None, "Ven": 9, "Sab": 10, "Dom": 12},
    "E6": {"Lun": None, "Mar": 8, "Mer": 8, "Gio": 7,  "Ven": 8,  "Sab": 12, "Dom": 10},
    "E7": {"Lun": 8,  "Mar": 8,  "Mer": 7,  "Gio": 9,  "Ven": 7,  "Sab": 11, "Dom": None},
    "E8": {"Lun": 9,  "Mar": 7,  "Mer": 8,  "Gio": 8,  "Ven": 7,  "Sab": 10, "Dom": 11},
}

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]
weekend_limited = ["E1", "E2"]
weekend_days = ["Sab", "Dom"]

# Insieme A: coppie disponibili
A = [(e, d) for e in employees for d in days if cost[e][d] is not None]

# --- Modello ---
m = gp.Model("H03_turnazione")

x = m.addVars(A, vtype=GRB.BINARY, name="x")

def xv(e, d):
    """Restituisce la variabile x[e,d] se disponibile, altrimenti 0."""
    return x[e, d] if (e, d) in x else 0.0

# Obiettivo: minimizzare il costo totale
m.setObjective(gp.quicksum(cost[e][d] * x[e, d] for (e, d) in A), GRB.MINIMIZE)

# 1. Copertura domanda giornaliera
for d in days:
    m.addConstr(gp.quicksum(xv(e, d) for e in employees) >= demand[d], name=f"demand_{d}")

# 2. Presenza senior ogni giorno
for d in days:
    m.addConstr(gp.quicksum(xv(e, d) for e in seniors) >= 1, name=f"senior_{d}")

# 3. Giorni lavorati per dipendente (3-5)
for e in employees:
    tot = gp.quicksum(xv(e, d) for d in days)
    m.addConstr(tot >= 3, name=f"minwork_{e}")
    m.addConstr(tot <= 5, name=f"maxwork_{e}")

# 4. No 4 giorni consecutivi (finestre mobili t=0..3, 0-indexed)
for e in employees:
    for t in range(0, 4):  # finestre: (t,t+1,t+2,t+3) con t=0,1,2,3 -> giorni indice 0..6
        window_days = days[t:t+4]
        m.addConstr(gp.quicksum(xv(e, d) for d in window_days) <= 3,
                    name=f"noconsec_{e}_{t}")

# 5. Specialisti E7/E8 presenti Gio e Ven
for d in ["Gio", "Ven"]:
    m.addConstr(gp.quicksum(xv(e, d) for e in specialists) >= 1, name=f"specialist_{d}")

# 6. E1, E2 max 1 giorno di weekend
for e in weekend_limited:
    m.addConstr(gp.quicksum(xv(e, d) for d in weekend_days) <= 1, name=f"weekend_{e}")

# --- Risoluzione ---
m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
}
status_str = status_map.get(m.status, str(m.status))

variables = {}
objective = None

if m.status == GRB.OPTIMAL:
    objective = m.objVal
    for (e, d) in A:
        variables[f"x_{e}_{d}"] = x[e, d].X
    # Includi anche le variabili "non esistenti" (indisponibili) con valore 0
    for e in employees:
        for d in days:
            if (e, d) not in x:
                variables[f"x_{e}_{d}"] = 0.0

import json
print("SOLUTION_JSON=" + json.dumps({
    "status": status_str,
    "objective": objective,
    "variables": variables
}))
