"""
H07 · Sourcing multi-componente con rischio e multisourcing (MILP intera) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione.

Note di traduzione
------------------
* Variabili della formulazione: x_ij quantità del componente i acquistata dal
  fornitore j, z_ij = 1 se il componente i è acquistato da j, y_j = 1 se il
  fornitore j è usato. Le variabili sono definite su tutte le coppie (i, j).
* Le celle «—» della tabella dei costi sono tradotte dall'esperto con i tre
  azzeramenti espliciti x_C1,D = 0, x_C2,F = 0, x_C3,E = 0.
* Il vincolo di lotto minimo e capacità 10·z_ij ≤ x_ij ≤ U_ij·z_ij è scritto
  dall'esperto «∀ ij disponibile», quindi è imposto solo sulle quindici coppie
  fornibili, con U_ij = min{capacità_j, domanda_i} come indicato.
* `x_ij ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower bound 0, secondo la
  convenzione fissata dall'autrice per il simbolo Z.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
COMPONENTI = ["C1", "C2", "C3"]
FORNITORI = ["A", "B", "C", "D", "E", "F"]

DOMANDA = {"C1": 80, "C2": 70, "C3": 60}

#         costo fisso  capacità totale  rischio
_forn = {
    "A": (120, 100, 2),
    "B": (140, 110, 3),
    "C": (100, 90, 1),
    "D": (150, 120, 4),
    "E": (90, 80, 2),
    "F": (110, 95, 3),
}

COSTO_FISSO = {j: _forn[j][0] for j in FORNITORI}
CAPACITA = {j: _forn[j][1] for j in FORNITORI}
RISCHIO = {j: _forn[j][2] for j in FORNITORI}

# costi unitari; None = componente non fornibile (cella «—»)
COSTO_UNIT = {
    ("C1", "A"): 9, ("C2", "A"): 12, ("C3", "A"): 11,
    ("C1", "B"): 10, ("C2", "B"): 9, ("C3", "B"): 12,
    ("C1", "C"): 11, ("C2", "C"): 10, ("C3", "C"): 9,
    ("C1", "D"): None, ("C2", "D"): 11, ("C3", "D"): 10,
    ("C1", "E"): 12, ("C2", "E"): 8, ("C3", "E"): None,
    ("C1", "F"): 10, ("C2", "F"): None, ("C3", "F"): 8,
}

QUALITA = {
    ("C1", "A"): 96, ("C2", "A"): 94, ("C3", "A"): 95,
    ("C1", "B"): 93, ("C2", "B"): 97, ("C3", "B"): 92,
    ("C1", "C"): 98, ("C2", "C"): 95, ("C3", "C"): 96,
    ("C1", "D"): None, ("C2", "D"): 94, ("C3", "D"): 93,
    ("C1", "E"): 97, ("C2", "E"): 98, ("C3", "E"): None,
    ("C1", "F"): 94, ("C2", "F"): None, ("C3", "F"): 98,
}

COPPIE = [(i, j) for i in COMPONENTI for j in FORNITORI]
DISPONIBILI = [(i, j) for (i, j) in COPPIE if COSTO_UNIT[i, j] is not None]
NON_DISPONIBILI = [(i, j) for (i, j) in COPPIE if COSTO_UNIT[i, j] is None]

# U_ij = min{capacità_j, domanda_i}
U = {(i, j): min(CAPACITA[j], DOMANDA[i]) for (i, j) in DISPONIBILI}

# ------------------------------------------------------------------------ modello
m = gp.Model("H07")

x = m.addVars(COPPIE, vtype=GRB.INTEGER, name="x")   # quantità
z = m.addVars(COPPIE, vtype=GRB.BINARY, name="z")    # coppia componente-fornitore attiva
y = m.addVars(FORNITORI, vtype=GRB.BINARY, name="y")  # fornitore attivato

# min  Σ_j CF_j·y_j + Σ_i Σ_j cu_ij·x_ij
m.setObjective(
    gp.quicksum(COSTO_FISSO[j] * y[j] for j in FORNITORI)
    + gp.quicksum(COSTO_UNIT[i, j] * x[i, j] for (i, j) in DISPONIBILI),
    GRB.MINIMIZE,
)

# Σ_j x_ij = DOMANDA_i   (Σ_j x_C1,j = 80, Σ_j x_C2,j = 70, Σ_j x_C3,j = 60)
m.addConstrs(
    (gp.quicksum(x[i, j] for j in FORNITORI) == DOMANDA[i] for i in COMPONENTI),
    name="domanda",
)

# x_C1,D = 0 ; x_C2,F = 0 ; x_C3,E = 0
m.addConstrs((x[i, j] == 0 for (i, j) in NON_DISPONIBILI), name="non_fornibile")

# 10·z_ij ≤ x_ij ≤ U_ij·z_ij   ∀ ij disponibile
m.addConstrs((10 * z[i, j] <= x[i, j] for (i, j) in DISPONIBILI), name="lotto_min")
m.addConstrs((x[i, j] <= U[i, j] * z[i, j] for (i, j) in DISPONIBILI), name="lotto_max")

# Σ_j z_ij ≥ 2   ∀i   (multisourcing)
m.addConstrs(
    (gp.quicksum(z[i, j] for j in FORNITORI) >= 2 for i in COMPONENTI),
    name="multisourcing",
)

# z_ij ≤ y_j   ∀(i,j)
m.addConstrs((z[i, j] <= y[j] for (i, j) in COPPIE), name="attiva_fornitore")

# y_j ≤ Σ_i z_ij   ∀j
m.addConstrs(
    (y[j] <= gp.quicksum(z[i, j] for i in COMPONENTI) for j in FORNITORI),
    name="fornitore_usato",
)

# Σ_i x_ij ≤ Q_j·y_j   ∀j   (capacità complessiva sui tre componenti)
m.addConstrs(
    (gp.quicksum(x[i, j] for i in COMPONENTI) <= CAPACITA[j] * y[j] for j in FORNITORI),
    name="capacita",
)

# Σ_j y_j ≤ 4
m.addConstr(gp.quicksum(y[j] for j in FORNITORI) <= 4, name="max_fornitori")

# y_A + y_B ≥ 1
m.addConstr(y["A"] + y["B"] >= 1, name="almeno_A_o_B")

# Σ_j q_ij·x_ij ≥ 95·d_i   ∀i   (qualità media)
m.addConstrs(
    (
        gp.quicksum(QUALITA[i, j] * x[i, j] for j in FORNITORI
                    if QUALITA[i, j] is not None) >= 95 * DOMANDA[i]
        for i in COMPONENTI
    ),
    name="qualita",
)

# Σ_j Σ_i RISCHIO_j·x_ij ≤ 580
m.addConstr(
    gp.quicksum(RISCHIO[j] * x[i, j] for (i, j) in COPPIE) <= 580,
    name="rischio",
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
    m.write("H07.sol")
    attivi = [j for j in FORNITORI if y[j].X > 0.5]
    print()
    print(f"Fornitori attivati ({len(attivi)}): {', '.join(attivi)}"
          f"  — costi fissi {sum(COSTO_FISSO[j] for j in attivi)}")
    print()
    print("Acquisti non nulli:")
    for (i, j) in DISPONIBILI:
        if x[i, j].X > 0.5:
            print(f"  {i} da {j}: {x[i, j].X:>5.0f} unità"
                  f"  × costo {COSTO_UNIT[i, j]:>2} = {COSTO_UNIT[i, j] * x[i, j].X:>6.0f}"
                  f"  (qualità {QUALITA[i, j]}, rischio {RISCHIO[j]})")
    print()
    for i in COMPONENTI:
        q = sum(QUALITA[i, j] * x[i, j].X for j in FORNITORI
                if QUALITA[i, j] is not None)
        n_forn = sum(1 for j in FORNITORI if z[i, j].X > 0.5)
        print(f"  {i}: qualità media {q / DOMANDA[i]:.3f} (≥ 95),"
              f" fornitori attivi {n_forn} (≥ 2)")
    rischio_tot = sum(RISCHIO[j] * x[i, j].X for (i, j) in COPPIE)
    print(f"  Rischio totale: {rischio_tot:.0f} / 580")
print("=" * 70)
