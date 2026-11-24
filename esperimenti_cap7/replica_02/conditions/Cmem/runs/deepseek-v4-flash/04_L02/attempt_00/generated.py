import gurobipy as gp
from gurobipy import GRB
import json

# Dati dalla traccia
I = [0, 1, 2]
T = list(range(8))

s0 = {0: 22, 1: 18, 2: 25}
fmin = {0: 18, 1: 15, 2: 20}
a = {0: 2, 1: 3, 2: 1}
Lmin = {0: 24, 1: 20, 2: 28}
Lmax = {0: 82, 1: 70, 2: 90}
sc = {0: 52, 1: 60, 2: 45}
h = {0: 1.2, 1: 1.6, 2: 0.9}

d = {
    0: [34, 48, 42, 55, 38, 50, 46, 40],
    1: [28, 32, 45, 36, 50, 34, 42, 39],
    2: [40, 35, 38, 44, 36, 48, 41, 45],
}

pc = {
    0: [5, 8, 5, 8, 5, 8, 5, 8],
    1: [7, 10, 7, 10, 7, 10, 7, 10],
    2: [9, 6, 9, 6, 9, 6, 9, 6],
}

C = [250, 245, 235, 260, 240, 255, 245, 265]

m = gp.Model("L02")
m.setParam("OutputFlag", 0)

# Variabili
x = m.addVars(I, T, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(I, T, vtype=GRB.BINARY, name="y")
s = m.addVars(I, T, vtype=GRB.INTEGER, lb=0, ub=75, name="s")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(pc[i][t] * x[i, t] + sc[i] * y[i, t] + h[i] * s[i, t]
                for i in I for t in T),
    GRB.MINIMIZE
)

# Bilancio di scorta
m.addConstrs((s0[i] + x[i, 0] == d[i][0] + s[i, 0] for i in I), name="bal0")
m.addConstrs((s[i, t - 1] + x[i, t] == d[i][t] + s[i, t]
              for i in I for t in range(1, 8)), name="bal")

# Scorta finale minima
m.addConstrs((s[i, 7] >= fmin[i] for i in I), name="final_inv")

# Capacità condivisa
m.addConstrs((gp.quicksum(a[i] * x[i, t] for i in I) <= C[t] for t in T),
             name="capacity")

# Vincoli di setup e lotto minimo/massimo
m.addConstrs((x[i, t] >= Lmin[i] * y[i, t] for i in I for t in T), name="lot_min")
m.addConstrs((x[i, t] <= Lmax[i] * y[i, t] for i in I for t in T), name="lot_max")

# Limite complessivo ai setup
m.addConstr(gp.quicksum(y[i, t] for i in I for t in T) <= 18, name="max_setups")

# Limite T3 e T6: al massimo due prodotti in setup
m.addConstrs((gp.quicksum(y[i, t] for i in I) <= 2 for t in [2, 5]),
             name="max_two_T3_T6")

# Giacenza complessiva massima
m.addConstrs((gp.quicksum(s[i, t] for i in I) <= 150 for t in T),
             name="total_inventory")

m.optimize()

# Stampa finale richiesta
if m.Status == GRB.OPTIMAL:
    sol_status = "OPTIMAL"
    objective = m.ObjVal
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
    }
    sol_status = status_map.get(m.Status, "UNKNOWN")
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": sol_status,
    "objective": objective,
    "variables": variables
}))
