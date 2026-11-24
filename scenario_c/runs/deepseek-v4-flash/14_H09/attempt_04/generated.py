"""
H09 · Produzione e scorte multi-prodotto con straordinario (MILP) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Variabili della formulazione: x_it quantità prodotta, s_it scorta di fine
  periodo, y_it = 1 se si attiva la produzione del prodotto i in t, o_t ore di
  straordinario nel periodo t.
* Le scorte iniziali s_A0 = s_B0 = s_C0 = 0 sono costanti, non variabili: entrano
  come termine noto nel bilancio del primo periodo.
* Il big-M del vincolo di lotto è quello calcolato dall'esperto:
  M_it = ⌊(CAPACITÀ_t + 20) / ORE_i⌋.
* «0 ≤ o_t ≤ 20» è tradotto con i bound della variabile continua o_t.
* `x_it, s_it ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower bound 0, secondo
  la convenzione fissata dall'autrice per il simbolo Z; o_t resta continua.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
PRODOTTI = ["A", "B", "C"]
PERIODI = [1, 2, 3, 4, 5, 6]

DOMANDA = {
    "A": {1: 12, 2: 18, 3: 14, 4: 20, 5: 16, 6: 19},
    "B": {1: 10, 2: 9, 3: 15, 4: 12, 5: 17, 6: 14},
    "C": {1: 8, 2: 11, 3: 10, 4: 13, 5: 9, 6: 15},
}

COSTO_UNIT = {
    "A": {1: 7, 2: 8, 3: 9, 4: 7, 5: 10, 6: 8},
    "B": {1: 9, 2: 8, 3: 8, 4: 10, 5: 7, 6: 9},
    "C": {1: 11, 2: 10, 3: 12, 4: 9, 5: 11, 6: 8},
}

#          setup  holding  ore/unità  lotto minimo
_prod = {
    "A": (35, 2, 2, 5),
    "B": (40, 2, 3, 4),
    "C": (45, 3, 4, 3),
}

SETUP = {i: _prod[i][0] for i in PRODOTTI}
HOLDING = {i: _prod[i][1] for i in PRODOTTI}
ORE = {i: _prod[i][2] for i in PRODOTTI}
LOTTO_MIN = {i: _prod[i][3] for i in PRODOTTI}

CAPACITA = {1: 120, 2: 115, 3: 125, 4: 110, 5: 120, 6: 115}

COSTO_STRAORDINARIO = 18
MAX_STRAORDINARIO = 20

# M_it = ⌊(CAPACITÀ_t + 20) / ORE_i⌋   (calcolo dell'esperto)
M = {
    (i, t): (CAPACITA[t] + MAX_STRAORDINARIO) // ORE[i]
    for i in PRODOTTI for t in PERIODI
}

# ------------------------------------------------------------------------ modello
m = gp.Model("H09")

x = m.addVars(PRODOTTI, PERIODI, vtype=GRB.INTEGER, name="x")   # produzione
s = m.addVars(PRODOTTI, PERIODI, vtype=GRB.INTEGER, name="s")   # scorta di fine periodo
y = m.addVars(PRODOTTI, PERIODI, vtype=GRB.BINARY, name="y")    # setup
# 0 ≤ o_t ≤ 20,  o_t ∈ R≥0
o = m.addVars(PERIODI, vtype=GRB.CONTINUOUS, lb=0.0, ub=MAX_STRAORDINARIO, name="o")

# min  Σ_i Σ_t (cu_it·x_it + SETUP_i·y_it + HOLDING_i·s_it) + 18·Σ_t o_t
m.setObjective(
    gp.quicksum(
        COSTO_UNIT[i][t] * x[i, t] + SETUP[i] * y[i, t] + HOLDING[i] * s[i, t]
        for i in PRODOTTI for t in PERIODI
    )
    + COSTO_STRAORDINARIO * gp.quicksum(o[t] for t in PERIODI),
    GRB.MINIMIZE,
)

# x_it + s_{i,t−1} = d_it + s_it   ∀i, ∀t   con   s_A0 = s_B0 = s_C0 = 0
m.addConstrs(
    (
        x[i, t] + (s[i, t - 1] if t > 1 else 0) == DOMANDA[i][t] + s[i, t]
        for i in PRODOTTI for t in PERIODI
    ),
    name="bilancio",
)

# Σ_i ORE_i·x_it ≤ CAPACITA_t + o_t   ∀t
m.addConstrs(
    (
        gp.quicksum(ORE[i] * x[i, t] for i in PRODOTTI) <= CAPACITA[t] + o[t]
        for t in PERIODI
    ),
    name="capacita",
)

# LOTTO_MIN_i·y_it ≤ x_it ≤ M_it·y_it   ∀i, ∀t
m.addConstrs(
    (LOTTO_MIN[i] * y[i, t] <= x[i, t] for i in PRODOTTI for t in PERIODI),
    name="lotto_min",
)
m.addConstrs(
    (x[i, t] <= M[i, t] * y[i, t] for i in PRODOTTI for t in PERIODI),
    name="lotto_max",
)

# y_A1 + y_B1 + y_C1 ≤ 3   (nel primo periodo si possono attivare tutti e tre)
m.addConstr(gp.quicksum(y[i, 1] for i in PRODOTTI) <= 3, name="attivazioni_t1")
# y_At + y_Bt + y_Ct ≤ 2   per t = 2, …, 6
m.addConstrs(
    (gp.quicksum(y[i, t] for i in PRODOTTI) <= 2 for t in PERIODI[1:]),
    name="attivazioni",
)

# Σ_i s_it ≤ 40   ∀t
m.addConstrs(
    (gp.quicksum(s[i, t] for i in PRODOTTI) <= 40 for t in PERIODI),
    name="scorta_totale",
)

# s_A6 ≥ 2,  s_B6 ≥ 2,  s_C6 ≥ 2
m.addConstrs((s[i, 6] >= 2 for i in PRODOTTI), name="scorta_finale")

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
    m.write("H09.sol")
    print()
    print("Piano di produzione (produzione / scorta di fine periodo):")
    print(f"  {'':<4}" + "".join(f"{'T' + str(t):>14}" for t in PERIODI))
    for i in PRODOTTI:
        riga = "".join(f"{x[i, t].X:>7.0f}/{s[i, t].X:<6.0f}" for t in PERIODI)
        print(f"  {i:<4}" + riga)
    print()
    print("Setup attivati:")
    for t in PERIODI:
        attivi = [i for i in PRODOTTI if y[i, t].X > 0.5]
        print(f"  T{t}: {', '.join(attivi) if attivi else '—':<10}"
              f" ({len(attivi)} attivazioni)")
    print()
    print("Ore, capacità e straordinario:")
    for t in PERIODI:
        ore_usate = sum(ORE[i] * x[i, t].X for i in PRODOTTI)
        print(f"  T{t}: ore usate {ore_usate:>6.1f}  capacità {CAPACITA[t]:>4}"
              f"  straordinario {o[t].X:>5.2f} / {MAX_STRAORDINARIO}")
    print()
    costo_prod = sum(COSTO_UNIT[i][t] * x[i, t].X for i in PRODOTTI for t in PERIODI)
    costo_setup = sum(SETUP[i] * y[i, t].X for i in PRODOTTI for t in PERIODI)
    costo_hold = sum(HOLDING[i] * s[i, t].X for i in PRODOTTI for t in PERIODI)
    costo_stra = COSTO_STRAORDINARIO * sum(o[t].X for t in PERIODI)
    print(f"  Costo di produzione   : {costo_prod:>8.1f}")
    print(f"  Costo di setup        : {costo_setup:>8.1f}")
    print(f"  Costo di giacenza     : {costo_hold:>8.1f}")
    print(f"  Costo di straordinario: {costo_stra:>8.1f}")
    print(f"  Totale                : "
          f"{costo_prod + costo_setup + costo_hold + costo_stra:>8.1f}")
print("=" * 70)
