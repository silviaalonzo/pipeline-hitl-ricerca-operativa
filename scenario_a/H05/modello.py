"""
H05 · Portafoglio pluriennale con sinergie (IP binaria) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* I progetti sono indicizzati con le lettere A…L usate dalla formulazione e dal testo.
* Le due sinergie sono modellate esplicitamente, come richiesto dal testo, con le
  variabili ausiliarie z_AC e z_EK e la linearizzazione canonica del prodotto
  logico (z ≤ x_1, z ≤ x_2, z ≥ x_1 + x_2 − 1) scritta per esteso dall'esperto.
* Nella formulazione i prerequisiti sono scritti `x_G ≤ x_B`, `x_J ≤ x_E`,
  `x_K ≤ x_C`, coerentemente con «G richiede B, J richiede E e K richiede C».
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
PROGETTI = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

#              VAN  A1  A2  A3  Personale  Rischio
_dati = {
    "A": (42, 18, 12, 10, 4, 5),
    "B": (35, 20, 18, 14, 4, 4),
    "C": (48, 25, 20, 18, 5, 6),
    "D": (31, 15, 14, 12, 3, 3),
    "E": (40, 22, 16, 15, 4, 4),
    "F": (28, 14, 12, 10, 3, 2),
    "G": (55, 30, 25, 22, 6, 7),
    "H": (37, 20, 18, 16, 4, 5),
    "I": (33, 17, 15, 12, 3, 3),
    "J": (50, 27, 21, 18, 5, 6),
    "K": (46, 24, 19, 17, 5, 5),
    "L": (29, 16, 13, 11, 3, 3),
}

VAN = {i: _dati[i][0] for i in PROGETTI}
COSTO_A1 = {i: _dati[i][1] for i in PROGETTI}
COSTO_A2 = {i: _dati[i][2] for i in PROGETTI}
COSTO_A3 = {i: _dati[i][3] for i in PROGETTI}
PERSONALE = {i: _dati[i][4] for i in PROGETTI}
RISCHIO = {i: _dati[i][5] for i in PROGETTI}

# ------------------------------------------------------------------------ modello
m = gp.Model("H05")

# x_i = 1 se il progetto i è scelto, 0 altrimenti
x = m.addVars(PROGETTI, vtype=GRB.BINARY, name="x")

# z_AC = 1 se A e C sono entrambi scelti;  z_EK = 1 se E e K sono entrambi scelti
z_AC = m.addVar(vtype=GRB.BINARY, name="z_AC")
z_EK = m.addVar(vtype=GRB.BINARY, name="z_EK")

# max  Σ_i VAN_i·x_i + 12·z_AC + 10·z_EK
m.setObjective(
    gp.quicksum(VAN[i] * x[i] for i in PROGETTI) + 12 * z_AC + 10 * z_EK,
    GRB.MAXIMIZE,
)

# Σ_i COSTO_A1_i·x_i ≤ 110
m.addConstr(gp.quicksum(COSTO_A1[i] * x[i] for i in PROGETTI) <= 110, name="budget_A1")
# Σ_i COSTO_A2_i·x_i ≤ 100
m.addConstr(gp.quicksum(COSTO_A2[i] * x[i] for i in PROGETTI) <= 100, name="budget_A2")
# Σ_i COSTO_A3_i·x_i ≤ 90
m.addConstr(gp.quicksum(COSTO_A3[i] * x[i] for i in PROGETTI) <= 90, name="budget_A3")

# Σ_i PERSONALE_i·x_i ≤ 28
m.addConstr(gp.quicksum(PERSONALE[i] * x[i] for i in PROGETTI) <= 28, name="personale")
# Σ_i RISCHIO_i·x_i ≤ 32
m.addConstr(gp.quicksum(RISCHIO[i] * x[i] for i in PROGETTI) <= 32, name="rischio")

# Prerequisiti
m.addConstr(x["G"] <= x["B"], name="prereq_G_B")
m.addConstr(x["J"] <= x["E"], name="prereq_J_E")
m.addConstr(x["K"] <= x["C"], name="prereq_K_C")

# Incompatibilità
m.addConstr(x["D"] + x["H"] <= 1, name="incomp_D_H")
m.addConstr(x["F"] + x["L"] <= 1, name="incomp_F_L")

# Almeno due progetti digitali tra A, C, G, J
m.addConstr(x["A"] + x["C"] + x["G"] + x["J"] >= 2, name="digitali")
# Almeno un progetto sostenibile tra E, H, K
m.addConstr(x["E"] + x["H"] + x["K"] >= 1, name="sostenibili")

# Σ_i x_i ≤ 8
m.addConstr(gp.quicksum(x[i] for i in PROGETTI) <= 8, name="max_progetti")

# Linearizzazione delle sinergie
m.addConstr(z_AC <= x["A"], name="sin_AC_1")
m.addConstr(z_AC <= x["C"], name="sin_AC_2")
m.addConstr(z_AC >= x["A"] + x["C"] - 1, name="sin_AC_3")
m.addConstr(z_EK <= x["E"], name="sin_EK_1")
m.addConstr(z_EK <= x["K"], name="sin_EK_2")
m.addConstr(z_EK >= x["E"] + x["K"] - 1, name="sin_EK_3")

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
    m.write("H05.sol")
    scelti = [i for i in PROGETTI if x[i].X > 0.5]
    print()
    print(f"Progetti scelti ({len(scelti)}): {', '.join(scelti)}")
    print(f"VAN dei progetti      : {sum(VAN[i] for i in scelti)}")
    print(f"Sinergia A-C attiva   : {'sì' if z_AC.X > 0.5 else 'no'}  (+12 se attiva)")
    print(f"Sinergia E-K attiva   : {'sì' if z_EK.X > 0.5 else 'no'}  (+10 se attiva)")
    print()
    print("Consumo delle risorse:")
    print(f"  Budget A1 : {sum(COSTO_A1[i] for i in scelti)} / 110")
    print(f"  Budget A2 : {sum(COSTO_A2[i] for i in scelti)} / 100")
    print(f"  Budget A3 : {sum(COSTO_A3[i] for i in scelti)} / 90")
    print(f"  Personale : {sum(PERSONALE[i] for i in scelti)} / 28")
    print(f"  Rischio   : {sum(RISCHIO[i] for i in scelti)} / 32")
print("=" * 70)
