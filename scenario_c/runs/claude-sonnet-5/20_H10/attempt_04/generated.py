"""
H10 · Rete multi-prodotto con capacità condivise (MILP intera) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Insiemi della formulazione: N = {S, A, B, C, D, T}, K = {K1, K2},
  A = {SA, SB, AB, AC, BC, BD, CD, CT, DT}; q_K1 = 28, q_K2 = 22.
* Variabili: x_ijk flusso intero del prodotto k sull'arco (i,j),
  y_ij = 1 se l'arco (i,j) è attivo.
* La conservazione del flusso è scritta dall'esperto nodo per nodo, con le due
  uguaglianze di origine sugli archi uscenti da S e le due di destinazione sugli
  archi entranti in T.
* La capacità è condivisa fra i due prodotti: x_ij,K1 + x_ij,K2 ≤ CAPACITÀ_ij·y_ij.
* `x_ijk ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower bound 0, secondo la
  convenzione fissata dall'autrice per il simbolo Z.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
PRODOTTI = ["K1", "K2"]
DOMANDA = {"K1": 28, "K2": 22}

ARCHI = ["SA", "SB", "AB", "AC", "BC", "BD", "CD", "CT", "DT"]

#          costo fisso  capacità
_archi = {
    "SA": (55, 35),
    "SB": (50, 35),
    "AB": (18, 15),
    "AC": (38, 30),
    "BC": (22, 25),
    "BD": (35, 25),
    "CD": (20, 20),
    "CT": (48, 35),
    "DT": (44, 35),
}

COSTO_FISSO = {a: _archi[a][0] for a in ARCHI}
CAPACITA = {a: _archi[a][1] for a in ARCHI}

# costi unitari per prodotto
COSTO_UNIT = {
    ("SA", "K1"): 2, ("SA", "K2"): 3,
    ("SB", "K1"): 3, ("SB", "K2"): 2,
    ("AB", "K1"): 1, ("AB", "K2"): 2,
    ("AC", "K1"): 2, ("AC", "K2"): 3,
    ("BC", "K1"): 2, ("BC", "K2"): 1,
    ("BD", "K1"): 3, ("BD", "K2"): 2,
    ("CD", "K1"): 1, ("CD", "K2"): 2,
    ("CT", "K1"): 3, ("CT", "K2"): 2,
    ("DT", "K1"): 2, ("DT", "K2"): 3,
}

# ------------------------------------------------------------------------ modello
m = gp.Model("H10")

x = m.addVars(ARCHI, PRODOTTI, vtype=GRB.INTEGER, name="x")  # flusso
y = m.addVars(ARCHI, vtype=GRB.BINARY, name="y")             # arco attivo

# min  Σ_ij CF_ij·y_ij + Σ_k Σ_ij c_ijk·x_ijk
m.setObjective(
    gp.quicksum(COSTO_FISSO[a] * y[a] for a in ARCHI)
    + gp.quicksum(COSTO_UNIT[a, k] * x[a, k] for a in ARCHI for k in PRODOTTI),
    GRB.MINIMIZE,
)

# Origine:  x_SA,K1 + x_SB,K1 = 28   e   x_SA,K2 + x_SB,K2 = 22
m.addConstrs(
    (x["SA", k] + x["SB", k] == DOMANDA[k] for k in PRODOTTI),
    name="origine",
)

# Conservazione nei nodi intermedi, ∀k
# A:  x_SAk = x_ABk + x_ACk
m.addConstrs((x["SA", k] == x["AB", k] + x["AC", k] for k in PRODOTTI), name="nodo_A")
# B:  x_SBk + x_ABk = x_BCk + x_BDk
m.addConstrs(
    (x["SB", k] + x["AB", k] == x["BC", k] + x["BD", k] for k in PRODOTTI),
    name="nodo_B",
)
# C:  x_ACk + x_BCk = x_CDk + x_CTk
m.addConstrs(
    (x["AC", k] + x["BC", k] == x["CD", k] + x["CT", k] for k in PRODOTTI),
    name="nodo_C",
)
# D:  x_BDk + x_CDk = x_DTk
m.addConstrs(
    (x["BD", k] + x["CD", k] == x["DT", k] for k in PRODOTTI),
    name="nodo_D",
)

# Destinazione:  x_CT,K1 + x_DT,K1 = 28   e   x_CT,K2 + x_DT,K2 = 22
m.addConstrs(
    (x["CT", k] + x["DT", k] == DOMANDA[k] for k in PRODOTTI),
    name="destinazione",
)

# Capacità condivisa fra i due prodotti:  x_ij,K1 + x_ij,K2 ≤ CAPACITA_ij·y_ij
m.addConstrs(
    (
        x[a, "K1"] + x[a, "K2"] <= CAPACITA[a] * y[a]
        for a in ARCHI
    ),
    name="capacita",
)

# Resilienza:  y_SA = 1,  y_SB = 1
m.addConstr(y["SA"] == 1, name="resilienza_SA")
m.addConstr(y["SB"] == 1, name="resilienza_SB")

# Σ_ij y_ij ≤ 7
m.addConstr(gp.quicksum(y[a] for a in ARCHI) <= 7, name="max_archi")

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
    m.write("H10.sol")
    attivi = [a for a in ARCHI if y[a].X > 0.5]
    print()
    print(f"Archi attivati ({len(attivi)}): {', '.join(attivi)}"
          f"  — costi fissi {sum(COSTO_FISSO[a] for a in attivi)}")
    print()
    print("Flussi sugli archi attivi:")
    print(f"  {'Arco':<6}{'K1':>6}{'K2':>6}{'Totale':>9}{'Capacità':>10}{'Costo var.':>12}")
    costo_var = 0
    for a in ARCHI:
        f1, f2 = x[a, "K1"].X, x[a, "K2"].X
        if f1 + f2 > 0.5 or y[a].X > 0.5:
            c = COSTO_UNIT[a, "K1"] * f1 + COSTO_UNIT[a, "K2"] * f2
            costo_var += c
            print(f"  {a:<6}{f1:>6.0f}{f2:>6.0f}{f1 + f2:>9.0f}"
                  f"{CAPACITA[a]:>10}{c:>12.0f}")
    print()
    print(f"Costo variabile totale : {costo_var:.0f}")
print("=" * 70)
