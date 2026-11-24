"""
H03 · Turnazione settimanale con competenze e riposi (IP binaria) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Indici della formulazione: i = 1…8 (dipendenti E1…E8), j = 1…7 (Lun…Dom).
* Il vincolo di seniority è scritto `Σ_{i=1}^{3} x_ij ≥ 1 ∀j`: la somma sui primi
  tre dipendenti corrisponde ai senior E1, E2, E3 indicati dal testo.
* Il divieto di quattro giorni consecutivi è scritto dall'esperto come quattro
  famiglie esplicite di vincoli (finestre 1-4, 2-5, 3-6, 4-7), ciascuna `∀i`.
* Le indisponibilità («—» nella tabella dei costi) sono scritte dall'esperto come
  sei vincoli espliciti di fissaggio a zero, riprodotti qui uno per uno.
  Alle celle «—» non corrisponde un costo numerico: il coefficiente è posto a 0.
  La scelta è ininfluente perché le variabili corrispondenti sono fissate a zero.
* Il doppio vincolo `3 ≤ Σ_j x_ij ≤ 5` è reso come due vincoli distinti.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
DIPENDENTI = [1, 2, 3, 4, 5, 6, 7, 8]          # E1 … E8
GIORNI = [1, 2, 3, 4, 5, 6, 7]                  # Lun … Dom
NOMI_GIORNI = {1: "Lun", 2: "Mar", 3: "Mer", 4: "Gio", 5: "Ven", 6: "Sab", 7: "Dom"}

# Domanda giornaliera di addetti
d = {1: 4, 2: 3, 3: 4, 4: 4, 5: 5, 6: 3, 7: 3}

# Costi e disponibilità: None indica l'indisponibilità «—»
_tabella = {
    1: [9, 9, 10, 9, 11, 14, None],
    2: [10, 9, 9, 10, 10, None, 14],
    3: [9, 10, 9, 9, 12, 12, 13],
    4: [7, None, 7, 8, 8, 11, 11],
    5: [8, 7, 8, None, 9, 10, 12],
    6: [None, 8, 8, 7, 8, 12, 10],
    7: [8, 8, 7, 9, 7, 11, None],
    8: [9, 7, 8, 8, 7, 10, 11],
}
# Alle celle «—» corrisponde coefficiente 0 (variabile comunque fissata a zero)
c = {(i, j): (_tabella[i][j - 1] if _tabella[i][j - 1] is not None else 0)
     for i in DIPENDENTI for j in GIORNI}

# ------------------------------------------------------------------------ modello
m = gp.Model("H03")

# x_ij = 1 se il dipendente i lavora il giorno j, 0 altrimenti
x = m.addVars(DIPENDENTI, GIORNI, vtype=GRB.BINARY, name="x")

# min  Σ_i Σ_j c_ij·x_ij
m.setObjective(
    gp.quicksum(c[i, j] * x[i, j] for i in DIPENDENTI for j in GIORNI), GRB.MINIMIZE
)

# Σ_i x_ij ≥ d_j   ∀j
m.addConstrs(
    (gp.quicksum(x[i, j] for i in DIPENDENTI) >= d[j] for j in GIORNI), name="domanda"
)

# Σ_{i=1}^{3} x_ij ≥ 1   ∀j
m.addConstrs(
    (gp.quicksum(x[i, j] for i in [1, 2, 3]) >= 1 for j in GIORNI), name="senior"
)

# 3 ≤ Σ_j x_ij ≤ 5   ∀i
m.addConstrs(
    (gp.quicksum(x[i, j] for j in GIORNI) >= 3 for i in DIPENDENTI), name="min_giorni"
)
m.addConstrs(
    (gp.quicksum(x[i, j] for j in GIORNI) <= 5 for i in DIPENDENTI), name="max_giorni"
)

# x_i1 + x_i2 + x_i3 + x_i4 ≤ 3   ∀i
m.addConstrs(
    (x[i, 1] + x[i, 2] + x[i, 3] + x[i, 4] <= 3 for i in DIPENDENTI), name="consec_1"
)
# x_i2 + x_i3 + x_i4 + x_i5 ≤ 3   ∀i
m.addConstrs(
    (x[i, 2] + x[i, 3] + x[i, 4] + x[i, 5] <= 3 for i in DIPENDENTI), name="consec_2"
)
# x_i3 + x_i4 + x_i5 + x_i6 ≤ 3   ∀i
m.addConstrs(
    (x[i, 3] + x[i, 4] + x[i, 5] + x[i, 6] <= 3 for i in DIPENDENTI), name="consec_3"
)
# x_i4 + x_i5 + x_i6 + x_i7 ≤ 3   ∀i
m.addConstrs(
    (x[i, 4] + x[i, 5] + x[i, 6] + x[i, 7] <= 3 for i in DIPENDENTI), name="consec_4"
)

# x_7,4 + x_8,4 ≥ 1     (specialisti, giovedì)
m.addConstr(x[7, 4] + x[8, 4] >= 1, name="specialisti_gio")
# x_7,5 + x_8,5 ≥ 1     (specialisti, venerdì)
m.addConstr(x[7, 5] + x[8, 5] >= 1, name="specialisti_ven")

# x_1,6 + x_1,7 ≤ 1     (E1, al massimo un giorno del fine settimana)
m.addConstr(x[1, 6] + x[1, 7] <= 1, name="weekend_E1")
# x_2,6 + x_2,7 ≤ 1     (E2, al massimo un giorno del fine settimana)
m.addConstr(x[2, 6] + x[2, 7] <= 1, name="weekend_E2")

# Indisponibilità
m.addConstr(x[1, 7] == 0, name="indisp_E1_Dom")
m.addConstr(x[2, 6] == 0, name="indisp_E2_Sab")
m.addConstr(x[4, 2] == 0, name="indisp_E4_Mar")
m.addConstr(x[5, 4] == 0, name="indisp_E5_Gio")
m.addConstr(x[6, 1] == 0, name="indisp_E6_Lun")
m.addConstr(x[7, 7] == 0, name="indisp_E7_Dom")

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
    m.write("H03.sol")
    print()
    print("Piano settimanale (X = in servizio):")
    intestazione = "        " + "  ".join(f"{NOMI_GIORNI[j]:>3}" for j in GIORNI)
    print(intestazione)
    for i in DIPENDENTI:
        celle = []
        for j in GIORNI:
            celle.append("  X" if x[i, j].X > 0.5 else "  .")
        giorni_lav = sum(1 for j in GIORNI if x[i, j].X > 0.5)
        print(f"  E{i}    " + "  ".join(celle) + f"   ({giorni_lav} giorni)")
    print()
    print("Copertura giornaliera (assegnati / richiesti):")
    for j in GIORNI:
        assegnati = sum(1 for i in DIPENDENTI if x[i, j].X > 0.5)
        print(f"  {NOMI_GIORNI[j]} : {assegnati} / {d[j]}")
print("=" * 70)
