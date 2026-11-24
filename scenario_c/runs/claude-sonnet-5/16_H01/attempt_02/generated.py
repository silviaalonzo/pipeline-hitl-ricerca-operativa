"""H01 · Rete capacitada di centri distributivi (MILP) — correzione dell'esperto."""

import gurobipy as gp
from gurobipy import GRB


SITI = ["A", "B", "C", "D", "E", "F"]
ZONE = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8"]

d = {"Z1": 30, "Z2": 25, "Z3": 35, "Z4": 20, "Z5": 28, "Z6": 32, "Z7": 24, "Z8": 26}
CF = {"A": 110, "B": 95, "C": 120, "D": 90, "E": 105, "F": 100}
CAPACITA = {"A": 90, "B": 80, "C": 110, "D": 75, "E": 95, "F": 85}

_costi = {
    "Z1": {"A": 4, "B": 7, "C": 6, "D": 10, "E": 9, "F": 11},
    "Z2": {"A": 5, "B": 4, "C": 8, "D": 9, "E": 7, "F": 10},
    "Z3": {"A": 7, "B": 5, "C": 4, "D": 8, "E": 9, "F": 7},
    "Z4": {"A": 9, "B": 8, "C": 7, "D": 4, "E": 5, "F": 6},
    "Z5": {"A": 8, "B": 9, "C": 6, "D": 5, "E": 4, "F": 7},
    "Z6": {"A": 10, "B": 8, "C": 7, "D": 6, "E": 5, "F": 4},
    "Z7": {"A": 6, "B": 7, "C": 5, "D": 8, "E": 6, "F": 7},
    "Z8": {"A": 7, "B": 6, "C": 8, "D": 5, "E": 7, "F": 4},
}
CV = {(i, j): _costi[j][i] for i in SITI for j in ZONE}

_emis = {
    "Z1": {"A": 1, "B": 2, "C": 2, "D": 4, "E": 3, "F": 4},
    "Z2": {"A": 2, "B": 1, "C": 3, "D": 3, "E": 2, "F": 4},
    "Z3": {"A": 3, "B": 2, "C": 1, "D": 3, "E": 4, "F": 3},
    "Z4": {"A": 4, "B": 3, "C": 3, "D": 1, "E": 2, "F": 2},
    "Z5": {"A": 3, "B": 4, "C": 2, "D": 2, "E": 1, "F": 3},
    "Z6": {"A": 4, "B": 3, "C": 3, "D": 2, "E": 2, "F": 1},
    "Z7": {"A": 2, "B": 3, "C": 1, "D": 3, "E": 2, "F": 3},
    "Z8": {"A": 3, "B": 2, "C": 3, "D": 1, "E": 3, "F": 1},
}
EM = {(i, j): _emis[j][i] for i in SITI for j in ZONE}

NORD = ["A", "B", "C"]
SUD = ["D", "E", "F"]

m = gp.Model("H01")

x = m.addVars(SITI, vtype=GRB.BINARY, name="x")
y = m.addVars(SITI, ZONE, vtype=GRB.INTEGER, name="y")

m.setObjective(
    gp.quicksum(CF[i] * x[i] for i in SITI)
    + gp.quicksum(CV[i, j] * y[i, j] for i in SITI for j in ZONE),
    GRB.MINIMIZE,
)

m.addConstrs(
    (gp.quicksum(y[i, j] for i in SITI) == d[j] for j in ZONE),
    name="domanda",
)
m.addConstr(gp.quicksum(x[i] for i in SITI) >= 3, name="min_centri")
m.addConstr(gp.quicksum(x[i] for i in SITI) <= 4, name="max_centri")
m.addConstr(gp.quicksum(x[i] for i in NORD) >= 1, name="nord")
m.addConstr(gp.quicksum(x[i] for i in SUD) >= 1, name="sud")

m.addConstrs(
    (gp.quicksum(y[i, j] for j in ZONE) >= 20 * x[i] for i in SITI),
    name="movim_min",
)
m.addConstrs(
    (
        gp.quicksum(y[i, j] for j in ZONE) <= CAPACITA[i] * x[i]
        for i in SITI
    ),
    name="capacita",
)

m.addConstr(
    gp.quicksum(EM[i, j] * y[i, j] for i in SITI for j in ZONE) <= 470,
    name="emissioni",
)

m.write("modello.lp")
m.optimize()

print()
print("=" * 70)
print(f"Stato finale Gurobi : {m.Status}")
print(f"Runtime Gurobi      : {m.Runtime:.4f} s")
print(f"Variabili           : {m.NumVars}")
print(f"Vincoli             : {m.NumConstrs}")

if m.Status == GRB.OPTIMAL:
    print(f"Valore obiettivo    : {m.ObjVal:.6g}")
    m.write("H01.sol")
    print()
    print("Siti aperti:")
    for i in SITI:
        if x[i].X > 0.5:
            inviato = sum(y[i, j].X for j in ZONE)
            print(f"  {i}  (capacità {CAPACITA[i]}, movimentate {inviato:.0f} unità)")
    print()
    print("Assegnazioni non nulle (centro -> zona : quantità):")
    for i in SITI:
        for j in ZONE:
            if y[i, j].X > 1e-6:
                print(f"  {i} -> {j} : {y[i, j].X:.0f}")
    emissioni = sum(EM[i, j] * y[i, j].X for i in SITI for j in ZONE)
    print()
    print(f"Emissioni complessive : {emissioni:.0f} / 470")
print("=" * 70)
