"""
H06 · Sequenziamento con ritardi pesati (MILP intera) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Variabili della formulazione: S_i istante di inizio, C_i istante di fine,
  T_i ritardo del lavoro i; y_ij = 1 se i è eseguito prima di j, definita per i < j.
* La costante big-M è quella calcolata esplicitamente dall'esperto:
  M = max(disponibilità) + Σ durate = 6 + 38 = 44.
* Le precedenze sono scritte nella formulazione come C1 ≤ S2 e C3 ≤ S5.
* Il ritardo è linearizzato con la coppia T_i ≥ C_i − scadenza_i e T_i ≥ 0,
  quest'ultima già implicata dal dominio Z≥0 ma scritta per esteso dall'esperto.
* `S_i, C_i, T_i ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower bound 0,
  secondo la convenzione fissata dall'autrice per il simbolo Z.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
LAVORI = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]

#         durata  disponibilità  scadenza  peso
_dati = {
    "J1": (5, 0, 9, 4),
    "J2": (7, 0, 17, 3),
    "J3": (4, 2, 12, 5),
    "J4": (6, 3, 22, 2),
    "J5": (3, 5, 15, 6),
    "J6": (8, 0, 28, 2),
    "J7": (5, 6, 25, 4),
}

DURATA = {i: _dati[i][0] for i in LAVORI}
DISPONIBILITA = {i: _dati[i][1] for i in LAVORI}
SCADENZA = {i: _dati[i][2] for i in LAVORI}
PESO = {i: _dati[i][3] for i in LAVORI}

# M = max disponibilità + Σ durate = 6 + 38 = 44   (calcolo dell'esperto)
M = max(DISPONIBILITA.values()) + sum(DURATA.values())

COPPIE = [(i, j) for a, i in enumerate(LAVORI) for j in LAVORI[a + 1:]]

# ------------------------------------------------------------------------ modello
m = gp.Model("H06")

# S_i = istante di inizio, C_i = istante di fine, T_i = ritardo del lavoro i
S = m.addVars(LAVORI, vtype=GRB.INTEGER, name="S")
C = m.addVars(LAVORI, vtype=GRB.INTEGER, name="C")
T = m.addVars(LAVORI, vtype=GRB.INTEGER, name="T")

# y_ij = 1 se i è eseguito prima di j, per i < j
y = m.addVars(COPPIE, vtype=GRB.BINARY, name="y")

# min  Σ_i PESO_i·T_i
m.setObjective(gp.quicksum(PESO[i] * T[i] for i in LAVORI), GRB.MINIMIZE)

# C_i = S_i + DURATA_i   ∀i
m.addConstrs((C[i] == S[i] + DURATA[i] for i in LAVORI), name="fine")

# S_i ≥ DISPONIBILITA_i   ∀i
m.addConstrs((S[i] >= DISPONIBILITA[i] for i in LAVORI), name="disponibilita")

# S_i + DURATA_i ≤ S_j + M(1 − y_ij)   ∀ i < j
m.addConstrs(
    (S[i] + DURATA[i] <= S[j] + M * (1 - y[i, j]) for (i, j) in COPPIE),
    name="nosovr_1",
)
# S_j + DURATA_j ≤ S_i + M·y_ij   ∀ i < j
m.addConstrs(
    (S[j] + DURATA[j] <= S[i] + M * y[i, j] for (i, j) in COPPIE),
    name="nosovr_2",
)

# C1 ≤ S2   e   C3 ≤ S5
m.addConstr(C["J1"] <= S["J2"], name="prec_J1_J2")
m.addConstr(C["J3"] <= S["J5"], name="prec_J3_J5")

# T_i ≥ C_i − SCADENZA_i   e   T_i ≥ 0   ∀i
m.addConstrs((T[i] >= C[i] - SCADENZA[i] for i in LAVORI), name="ritardo")
m.addConstrs((T[i] >= 0 for i in LAVORI), name="ritardo_nonneg")

# ---------------------------------------------------------------------- soluzione
m.write("modello.lp")
m.optimize()

print()
print("=" * 70)
print(f"Stato finale Gurobi : {m.Status}")
print(f"Runtime Gurobi      : {m.Runtime:.4f} s")
print(f"Variabili           : {m.NumVars}")
print(f"Vincoli             : {m.NumConstrs}")
print(f"Big-M usato         : {M}")

if m.Status == GRB.OPTIMAL:
    print(f"Valore obiettivo    : {m.ObjVal:.6g}")
    m.write("H06.sol")
    print()
    print("Sequenza dei lavori (per istante di inizio):")
    print(f"  {'Lavoro':<8}{'Inizio':>8}{'Fine':>8}{'Scadenza':>10}"
          f"{'Ritardo':>9}{'Peso':>6}{'Costo':>8}")
    for i in sorted(LAVORI, key=lambda k: S[k].X):
        print(f"  {i:<8}{S[i].X:>8.0f}{C[i].X:>8.0f}{SCADENZA[i]:>10}"
              f"{T[i].X:>9.0f}{PESO[i]:>6}{PESO[i] * T[i].X:>8.0f}")
    print()
    print(f"Somma dei ritardi pesati : {sum(PESO[i] * T[i].X for i in LAVORI):.0f}")
print("=" * 70)
