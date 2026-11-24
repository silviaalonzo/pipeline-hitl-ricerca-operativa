import json
import gurobipy as gp

prodotti = ["A", "B", "C", "D", "E"]
periodi = range(6)

S0 = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
SF = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
h = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
Lmin = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
Lmax = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
costo_setup = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
costo_scorta = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

domanda = {
    "A": [38, 42, 35, 50, 45, 40],
    "B": [32, 36, 44, 38, 46, 34],
    "C": [25, 30, 28, 35, 30, 32],
    "D": [40, 35, 45, 42, 38, 48],
    "E": [20, 24, 22, 28, 26, 25],
}

costo_prod = {
    "A": [4, 6, 8, 10, 5, 7],
    "B": [7, 9, 4, 6, 8, 10],
    "C": [10, 5, 7, 9, 4, 6],
    "D": [6, 8, 10, 5, 7, 9],
    "E": [9, 4, 6, 8, 10, 5],
}

cap_ord = [350, 360, 345, 370, 355, 380]
max_straord = [85, 80, 90, 75, 85, 80]
costo_straord = [7, 8, 7, 9, 8, 7]
costo_fisso_straord = 25

m = gp.Model("L04_produzione")
m.Params.OutputFlag = 0

x = m.addVars(prodotti, periodi, vtype=gp.GRB.INTEGER, name="x")
I = m.addVars(prodotti, periodi, vtype=gp.GRB.INTEGER, name="I")
y = m.addVars(prodotti, periodi, vtype=gp.GRB.BINARY, name="setup")
R = m.addVars(periodi, vtype=gp.GRB.CONTINUOUS, name="straordinario")
A = m.addVars(periodi, vtype=gp.GRB.BINARY, name="attiva_straordinario")

# Bilancio di scorta
for p in prodotti:
    m.addConstr(I[p, 0] == S0[p] + x[p, 0] - domanda[p][0], name=f"bilancio_{p}_1")
    for t in range(1, 6):
        m.addConstr(I[p, t] == I[p, t-1] + x[p, t] - domanda[p][t], name=f"bilancio_{p}_{t+1}")

# Scorta finale minima e limiti di giacenza
for p in prodotti:
    m.addConstr(I[p, 5] >= SF[p], name=f"finale_{p}")
    for t in periodi:
        m.addConstr(I[p, t] <= 75, name=f"stock_max_{p}_{t}")

for t in periodi:
    m.addConstr(gp.quicksum(I[p, t] for p in prodotti) <= 210, name=f"stock_tot_{t}")

# Lotto minimo/massimo e setup
for p in prodotti:
    for t in periodi:
        m.addConstr(x[p, t] >= Lmin[p] * y[p, t], name=f"lotto_min_{p}_{t}")
        m.addConstr(x[p, t] <= Lmax[p] * y[p, t], name=f"lotto_max_{p}_{t}")

# Capacità ordinaria e straordinario
for t in periodi:
    m.addConstr(gp.quicksum(h[p] * x[p, t] for p in prodotti) <= cap_ord[t] + R[t], name=f"capacity_{t}")
    m.addConstr(R[t] <= max_straord[t] * A[t], name=f"ot_max_{t}")
    m.addConstr(R[t] >= 10 * A[t], name=f"ot_min_{t}")

# Limiti sui setup
m.addConstr(y.sum() <= 26, name="setup_total")
for t in periodi:
    m.addConstr(gp.quicksum(y[p, t] for p in prodotti) <= 4, name=f"setup_per_{t}")

# Funzione obiettivo
obj = (
    gp.quicksum(costo_prod[p][t] * x[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_setup[p] * y[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_scorta[p] * I[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_fisso_straord * A[t] + costo_straord[t] * R[t] for t in periodi)
)
m.setObjective(obj, gp.GRB.MINIMIZE)

m.optimize()

if m.Status == gp.GRB.OPTIMAL:
    sol = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": {v.VarName: v.X for v in m.getVars()},
    }
else:
    status = {
        gp.GRB.INFEASIBLE: "INFEASIBLE",
        gp.GRB.UNBOUNDED: "UNBOUNDED",
        gp.GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }.get(m.Status, f"STATUS_{m.Status}")
    sol = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(sol, separators=(",", ":")))
