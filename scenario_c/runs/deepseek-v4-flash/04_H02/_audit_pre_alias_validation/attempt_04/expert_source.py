"""
H02 · Produzione multi-periodo con setup e scorte (MILP intera) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* `x_ij ∈ Z ≥ 0` e `y_ij ∈ Z ≥ 0` sono scritti esplicitamente con il segno nella
  formulazione: `vtype=GRB.INTEGER` con lower bound 0 (default).
* Il parametro `M_ij` del vincolo `LOTTOMIN_i·δ_ij ≤ x_ij ≤ M_ij·δ_ij` non è definito
  nella formulazione manoscritta. Valore chiarito dall'autrice il 2026-08-17:
  **M_ij = ⌊CAPACITÀ_j / ORE_i⌋**, cioè il massimo producibile dell'articolo i nel
  periodo j date le ore disponibili in quel periodo.
* Le scorte di apertura sono scritte dall'esperto come tre vincoli espliciti
  (`y_A0 = 0`, `y_B0 = 0`, `y_C0 = 6`): `y` è quindi indicizzata su j = 0…4 e i tre
  fissaggi sono riprodotti come vincoli, non incorporati nei dati.
* Il doppio vincolo `LOTTOMIN_i·δ_ij ≤ x_ij ≤ M_ij·δ_ij` è reso come due vincoli
  distinti, come da scrittura.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
PRODOTTI = ["A", "B", "C"]
PERIODI = [1, 2, 3, 4]

# Domande per periodo
_domanda = {
    "A": {1: 8, 2: 12, 3: 10, 4: 14},
    "B": {1: 10, 2: 8, 3: 14, 4: 12},
    "C": {1: 6, 2: 9, 3: 7, 4: 11},
}
d = {(i, j): _domanda[i][j] for i in PRODOTTI for j in PERIODI}

# Costi unitari di produzione
_cp = {
    "A": {1: 9, 2: 11, 3: 10, 4: 12},
    "B": {1: 8, 2: 9, 3: 11, 4: 10},
    "C": {1: 13, 2: 12, 3: 14, 4: 11},
}
CP = {(i, j): _cp[i][j] for i in PRODOTTI for j in PERIODI}

# Parametri per prodotto
SETUP = {"A": 45, "B": 40, "C": 50}
HOLDING = {"A": 2, "B": 3, "C": 2}
ORE = {"A": 2, "B": 3, "C": 4}
LOTTOMIN = {"A": 4, "B": 4, "C": 3}

# Capacità in ore per periodo
CAPACITA = {1: 90, 2: 95, 3: 90, 4: 100}

# Big-M chiarito dall'autrice: massimo producibile date le ore del periodo
M = {(i, j): CAPACITA[j] // ORE[i] for i in PRODOTTI for j in PERIODI}

# ------------------------------------------------------------------------ modello
m = gp.Model("H02")

# x_ij = quantità prodotta di articolo i nel periodo j,  x_ij ∈ Z ≥ 0
x = m.addVars(PRODOTTI, PERIODI, vtype=GRB.INTEGER, name="x")

# y_ij = quantità a magazzino di articolo i a fine periodo j,  y_ij ∈ Z ≥ 0
# indicizzata su j = 0…4 perché la formulazione fissa esplicitamente y_i0
y = m.addVars(PRODOTTI, [0] + PERIODI, vtype=GRB.INTEGER, name="y")

# δ_ij = 1 se l'articolo i è prodotto nel periodo j, 0 altrimenti
delta = m.addVars(PRODOTTI, PERIODI, vtype=GRB.BINARY, name="delta")

# min  Σ_i Σ_j (CP_ij·x_ij + SETUP_i·δ_ij + HOLDING_i·y_ij)
m.setObjective(
    gp.quicksum(
        CP[i, j] * x[i, j] + SETUP[i] * delta[i, j] + HOLDING[i] * y[i, j]
        for i in PRODOTTI
        for j in PERIODI
    ),
    GRB.MINIMIZE,
)

# x_ij + y_i,j-1 = d_ij + y_ij   ∀i ∀j
m.addConstrs(
    (x[i, j] + y[i, j - 1] == d[i, j] + y[i, j] for i in PRODOTTI for j in PERIODI),
    name="bilancio",
)

# Σ_i y_ij ≤ 20   ∀j
m.addConstrs(
    (gp.quicksum(y[i, j] for i in PRODOTTI) <= 20 for j in PERIODI), name="scorta_max"
)

# y_A0 = 0,  y_B0 = 0,  y_C0 = 6
m.addConstr(y["A", 0] == 0, name="scorta_iniz_A")
m.addConstr(y["B", 0] == 0, name="scorta_iniz_B")
m.addConstr(y["C", 0] == 6, name="scorta_iniz_C")

# Σ_i δ_ij ≤ 2   ∀j
m.addConstrs(
    (gp.quicksum(delta[i, j] for i in PRODOTTI) <= 2 for j in PERIODI),
    name="max_due_setup",
)

# y_A4 = 0,  y_B4 = 0,  y_C4 = 0
m.addConstr(y["A", 4] == 0, name="scorta_fin_A")
m.addConstr(y["B", 4] == 0, name="scorta_fin_B")
m.addConstr(y["C", 4] == 0, name="scorta_fin_C")

# Σ_i ORE_i·x_ij ≤ CAPACITÀ_j   ∀j
m.addConstrs(
    (gp.quicksum(ORE[i] * x[i, j] for i in PRODOTTI) <= CAPACITA[j] for j in PERIODI),
    name="capacita",
)

# LOTTOMIN_i·δ_ij ≤ x_ij ≤ M_ij·δ_ij   ∀i ∀j
m.addConstrs(
    (x[i, j] >= LOTTOMIN[i] * delta[i, j] for i in PRODOTTI for j in PERIODI),
    name="lotto_min",
)
m.addConstrs(
    (x[i, j] <= M[i, j] * delta[i, j] for i in PRODOTTI for j in PERIODI),
    name="lotto_max",
)

# ---------------------------------------------------------------------- soluzione
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
    m.write("H02.sol")
    print()
    print("Piano di produzione (prodotto × periodo):")
    print("           T1     T2     T3     T4")
    for i in PRODOTTI:
        celle = []
        for j in PERIODI:
            prod = x[i, j].X
            marker = "*" if delta[i, j].X > 0.5 else " "
            celle.append(f"{prod:5.0f}{marker}")
        print(f"  {i}     " + " ".join(celle))
    print("  (* = setup attivo nel periodo)")
    print()
    print("Scorte di fine periodo:")
    print("     T0     T1     T2     T3     T4")
    for i in PRODOTTI:
        celle = [f"{y[i, j].X:5.0f}" for j in [0] + PERIODI]
        print(f"  {i} " + " ".join(celle))
    print()
    print("Ore impiegate per periodo:")
    for j in PERIODI:
        ore = sum(ORE[i] * x[i, j].X for i in PRODOTTI)
        setup = sum(1 for i in PRODOTTI if delta[i, j].X > 0.5)
        print(f"  T{j} : {ore:.0f} / {CAPACITA[j]} ore, {setup} setup attivi")
    costo_prod = sum(CP[i, j] * x[i, j].X for i in PRODOTTI for j in PERIODI)
    costo_setup = sum(SETUP[i] * delta[i, j].X for i in PRODOTTI for j in PERIODI)
    costo_hold = sum(HOLDING[i] * y[i, j].X for i in PRODOTTI for j in PERIODI)
    print()
    print(f"Costo di produzione   : {costo_prod:.0f}")
    print(f"Costo di setup        : {costo_setup:.0f}")
    print(f"Costo di mantenimento : {costo_hold:.0f}")
elif m.Status == GRB.INFEASIBLE:
    print("Modello INFEASIBLE: nessuna soluzione ammissibile.")
    m.computeIIS()
    m.write("modello.ilp")
    print("Vincoli appartenenti all'IIS:")
    for cs in m.getConstrs():
        if cs.IISConstr:
            print(f"  {cs.ConstrName}")
print("=" * 70)
