"""
H08 · Rete di emergenza capacitada con backup (IP binaria) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Variabili della formulazione: x_ij = 1 se la zona j è assegnata alla stazione i,
  definita solo per i ∈ R_j (stazioni raggiungibili dalla zona j); y_i = 1 se la
  stazione i è aperta.
* Il backup delle zone critiche è scritto dall'esperto come tre vincoli espliciti
  sulle stazioni raggiungibili da Z3, Z8 e Z11:
  y_B + y_C + y_D ≥ 2,  y_D + y_G + y_H ≥ 2,  y_A + y_E + y_H ≥ 2.
* Il numero di stazioni aperte è fissato con l'uguaglianza Σ_i y_i = 4, come
  richiesto dal testo («aprire esattamente quattro stazioni»).
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
STAZIONI = ["A", "B", "C", "D", "E", "F", "G", "H"]

#          costo fisso  capacità
_staz = {
    "A": (35, 42),
    "B": (32, 44),
    "C": (40, 46),
    "D": (30, 40),
    "E": (38, 45),
    "F": (33, 43),
    "G": (36, 44),
    "H": (31, 42),
}

COSTO_FISSO = {i: _staz[i][0] for i in STAZIONI}
CAPACITA = {i: _staz[i][1] for i in STAZIONI}

ZONE = [f"Z{k}" for k in range(1, 13)]

DOMANDA = {
    "Z1": 8, "Z2": 7, "Z3": 10, "Z4": 6, "Z5": 9, "Z6": 8,
    "Z7": 7, "Z8": 11, "Z9": 6, "Z10": 9, "Z11": 8, "Z12": 7,
}

# R_j = stazioni raggiungibili dalla zona j, con il tempo di percorrenza
RAGGIUNGIBILI = {
    "Z1": {"A": 3, "B": 5},
    "Z2": {"A": 6, "B": 8, "C": 10},
    "Z3": {"B": 11, "C": 4, "D": 6},
    "Z4": {"C": 7, "D": 9},
    "Z5": {"A": 6, "D": 3, "E": 5},
    "Z6": {"B": 11, "E": 8, "F": 10},
    "Z7": {"C": 7, "F": 4, "G": 6, "H": 8},
    "Z8": {"D": 3, "G": 9, "H": 11},
    "Z9": {"E": 8, "F": 10, "H": 5},
    "Z10": {"F": 4, "G": 6, "H": 8},
    "Z11": {"A": 6, "E": 5, "H": 11},
    "Z12": {"B": 11, "G": 3, "H": 5},
}

COPPIE = [(i, j) for j in ZONE for i in RAGGIUNGIBILI[j]]

# ------------------------------------------------------------------------ modello
m = gp.Model("H08")

x = m.addVars(COPPIE, vtype=GRB.BINARY, name="x")   # zona assegnata a stazione
y = m.addVars(STAZIONI, vtype=GRB.BINARY, name="y")  # stazione aperta

# min  Σ_i CF_i·y_i + Σ_j Σ_{i∈R_j} DOMANDA_j·TEMPO_ij·x_ij
m.setObjective(
    gp.quicksum(COSTO_FISSO[i] * y[i] for i in STAZIONI)
    + gp.quicksum(DOMANDA[j] * RAGGIUNGIBILI[j][i] * x[i, j] for (i, j) in COPPIE),
    GRB.MINIMIZE,
)

# Σ_{i∈R_j} x_ij = 1   ∀j   (a ogni zona deve essere assegnata una stazione)
m.addConstrs(
    (gp.quicksum(x[i, j] for i in RAGGIUNGIBILI[j]) == 1 for j in ZONE),
    name="assegnazione",
)

# x_ij ≤ y_i   ∀j, ∀i∈R_j   (zona assegnabile a stazioni aperte)
m.addConstrs((x[i, j] <= y[i] for (i, j) in COPPIE), name="solo_aperte")

# Σ_{j: i∈R_j} DOMANDA_j·x_ij ≤ CAPACITA_i·y_i   ∀i
m.addConstrs(
    (
        gp.quicksum(DOMANDA[j] * x[i, j] for j in ZONE if i in RAGGIUNGIBILI[j])
        <= CAPACITA[i] * y[i]
        for i in STAZIONI
    ),
    name="capacita",
)

# Σ_i y_i = 4
m.addConstr(gp.quicksum(y[i] for i in STAZIONI) == 4, name="quattro_stazioni")

# y_A + y_B + y_C + y_D ≥ 1   (gruppo Ovest)
m.addConstr(y["A"] + y["B"] + y["C"] + y["D"] >= 1, name="ovest")
# y_E + y_F + y_G + y_H ≥ 1   (gruppo Est)
m.addConstr(y["E"] + y["F"] + y["G"] + y["H"] >= 1, name="est")

# Backup delle zone critiche Z3, Z8, Z11
m.addConstr(y["B"] + y["C"] + y["D"] >= 2, name="backup_Z3")
m.addConstr(y["D"] + y["G"] + y["H"] >= 2, name="backup_Z8")
m.addConstr(y["A"] + y["E"] + y["H"] >= 2, name="backup_Z11")

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
    m.write("H08.sol")
    aperte = [i for i in STAZIONI if y[i].X > 0.5]
    print()
    print(f"Stazioni aperte ({len(aperte)}): {', '.join(aperte)}"
          f"  — costi fissi {sum(COSTO_FISSO[i] for i in aperte)}")
    print()
    print("Assegnazione delle zone:")
    costo_percorrenza = 0
    for j in ZONE:
        for i in RAGGIUNGIBILI[j]:
            if x[i, j].X > 0.5:
                c = DOMANDA[j] * RAGGIUNGIBILI[j][i]
                costo_percorrenza += c
                print(f"  {j:<4} → {i}   domanda {DOMANDA[j]:>2}"
                      f" × tempo {RAGGIUNGIBILI[j][i]:>2} = {c:>4}")
    print()
    print(f"Costo di percorrenza totale : {costo_percorrenza}")
    print()
    print("Carico delle stazioni aperte:")
    for i in aperte:
        carico = sum(DOMANDA[j] * x[i, j].X for j in ZONE if i in RAGGIUNGIBILI[j])
        print(f"  {i}: {carico:>5.0f} / {CAPACITA[i]}")
print("=" * 70)
