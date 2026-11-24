import json
import gurobipy as gp
from gurobipy import GRB

P = ["A", "B", "C", "D", "E"]
T = [1, 2, 3, 4, 5, 6]

init = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
final = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
hours = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
lot_min = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
lot_max = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
hold_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

demand = {
    "A": {1: 38, 2: 42, 3: 35, 4: 50, 5: 45, 6: 40},
    "B": {1: 32, 2: 36, 3: 44, 4: 38, 5: 46, 6: 34},
    "C": {1: 25, 2: 30, 3: 28, 4: 35, 5: 30, 6: 32},
    "D": {1: 40, 2: 35, 3: 45, 4: 42, 5: 38, 6: 48},
    "E": {1: 20, 2: 24, 3: 22, 4: 28, 5: 26, 6: 25},
}

prod_cost = {
    "A": {1: 4, 2: 6, 3: 8, 4: 10, 5: 5, 6: 7},
    "B": {1: 7, 2: 9, 3: 4, 4: 6, 5: 8, 6: 10},
    "C": {1: 10, 2: 5, 3: 7, 4: 9, 5: 4, 6: 6},
    "D": {1: 6, 2: 8, 3: 10, 4: 5, 5: 7, 6: 9},
    "E": {1: 9, 2: 4, 3: 6, 4: 8, 5: 10, 6: 5},
}

regular_cap = {1: 350, 2: 360, 3: 345, 4: 370, 5: 355, 6: 380}
ot_max = {1: 85, 2: 80, 3: 90, 4: 75, 5: 85, 6: 80}
ot_cost = {1: 7, 2: 8, 3: 7, 4: 9, 5: 8, 6: 7}

FIXED_OT = 25
MAX_INV = 75
MAX_TOT_INV = 210
MAX_TOT_SETUPS = 26
MAX_SETUPS_PER_PERIOD = 4

m = gp.Model("L04_produzione_straordinario")

x = m.addVars(P, T, vtype=GRB.INTEGER, name="x")
y = m.addVars(P, T, vtype=GRB.BINARY, name="y")
I = m.addVars(P, T, vtype=GRB.INTEGER, name="I")
z = m.addVars(T, vtype=GRB.BINARY, name="z")
o = m.addVars(T, vtype=GRB.INTEGER, name="o")

# Bilanci di magazzino
for i in P:
    for t in T:
        if t == 1:
            m.addConstr(I[i, t] == init[i] + x[i, t] - demand[i][t], name=f"balance_{i}_{t}")
        else:
            m.addConstr(I[i, t] == I[i, t - 1] + x[i, t] - demand[i][t], name=f"balance_{i}_{t}")

# Scorta finale minima
for i in P:
    m.addConstr(I[i, 6] >= final[i], name=f"final_{i}")

# Limiti di scorta
for i in P:
    for t in T:
        m.addConstr(I[i, t] <= MAX_INV, name=f"inv_ub_{i}_{t}")

for t in T:
    m.addConstr(gp.quicksum(I[i, t] for i in P) <= MAX_TOT_INV, name=f"tot_inv_{t}")

# Setup e limiti di lotto
for i in P:
    for t in T:
        m.addConstr(x[i, t] >= lot_min[i] * y[i, t], name=f"lot_lb_{i}_{t}")
        m.addConstr(x[i, t] <= lot_max[i] * y[i, t], name=f"lot_ub_{i}_{t}")

# Capacità ordinaria + straordinario
for t in T:
    m.addConstr(
        gp.quicksum(hours[i] * x[i, t] for i in P) <= regular_cap[t] + o[t],
        name=f"capacity_{t}"
    )

# Attivazione e quantità minima/massima di straordinario
for t in T:
    m.addConstr(o[t] >= 10 * z[t], name=f"ot_lb_{t}")
    m.addConstr(o[t] <= ot_max[t] * z[t], name=f"ot_ub_{t}")

# Limiti sui setup
for t in T:
    m.addConstr(
        gp.quicksum(y[i, t] for i in P) <= MAX_SETUPS_PER_PERIOD,
        name=f"setup_period_{t}"
    )

m.addConstr(
    gp.quicksum(y[i, t] for i in P for t in T) <= MAX_TOT_SETUPS,
    name="setup_total"
)

# Funzione obiettivo
obj = (
    gp.quicksum(
        prod_cost[i][t] * x[i, t]
        + setup_cost[i] * y[i, t]
        + hold_cost[i] * I[i, t]
        for i in P for t in T
    )
    + gp.quicksum(ot_cost[t] * o[t] + FIXED_OT * z[t] for t in T)
)

m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

if m.Status == GRB.OPTIMAL:
    var_values = {}

    for i in P:
        for t in T:
            var_values[f"x_{i}_{t}"] = x[i, t].X
            var_values[f"y_{i}_{t}"] = y[i, t].X
            var_values[f"I_{i}_{t}"] = I[i, t].X

    for t in T:
        var_values[f"o_{t}"] = o[t].X
        var_values[f"z_{t}"] = z[t].X

    print("SOLUTION_JSON=" + json.dumps({
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": var_values
    }))
else:
    print("SOLUTION_JSON=" + json.dumps({
        "status": f"NOT_OPTIMAL_{m.Status}",
        "objective": None,
        "variables": {}
    }))
