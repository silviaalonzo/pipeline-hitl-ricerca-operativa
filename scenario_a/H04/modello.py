"""
H04 · Allocazione della flotta su più rotte (MILP intera) — Scenario A

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
Nessuna correzione, nessun miglioramento: variabili, funzione obiettivo e vincoli
corrispondono uno a uno a quanto scritto nella formulazione, con la sola eccezione
del refuso di trascrizione chiarito dall'autrice e documentata qui sotto.

Refuso di trascrizione chiarito dall'autrice (2026-08-17)
---------------------------------------------------------
Il manoscritto riporta il vincolo di copertura come `Σ_i x_ij ≥ DOMANDA_j`, dove
`x_ij` è il **numero di viaggi**: la domanda risulta così confrontata con un
conteggio di viaggi anziché con la capacità trasportata, e il modello è
`INFEASIBLE` (servirebbero 199 viaggi contro una disponibilità di 25).
L'autrice ha confermato che si tratta di un errore di scrittura nella trascrizione
e che il vincolo inteso è

    Σ_i CAPACITÀ_i · x_ij ≥ DOMANDA_j        ∀j

coerentemente con il testo del problema: «la capacità complessiva assegnata a ogni
rotta deve coprirne la domanda». La traduzione recepisce l'intenzione dichiarata.
La prima esecuzione, con il vincolo nella forma letterale, è documentata in
`output_terminale_esecuzione_1.txt` e in `modello.ilp`.

Note di traduzione
------------------
* `x_ij ∈ Z ≥ 0` è scritto esplicitamente con il segno nella formulazione:
  `vtype=GRB.INTEGER` con lower bound 0 (default).
* `y_GRANDE,4 = 1` è reso come fissaggio della binaria del tipo «Grande» sulla
  rotta R4, coerentemente con «sulla rotta R4 deve essere impiegato almeno un
  veicolo grande».
* Il doppio vincolo `y_ij ≤ x_ij ≤ DISPONIBILITÀ_i·y_ij` è reso come due vincoli
  distinti, come da scrittura.
* Il vincolo sulle emissioni è scritto `Σ_i EMISSIONI_i·(Σ_j x_ij) ≤ 145`.
"""

import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------------------------- dati
TIPI = ["Piccolo", "Medio", "Grande"]
ROTTE = ["R1", "R2", "R3", "R4"]

# Domanda per rotta
DOMANDA = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}

# Flotta
CAPACITA = {"Piccolo": 8, "Medio": 14, "Grande": 20}
DISPONIBILITA = {"Piccolo": 10, "Medio": 9, "Grande": 6}
EMISSIONI = {"Piccolo": 5, "Medio": 8, "Grande": 11}

# Costo di un viaggio COSTO[i][j]
_costi = {
    "R1": {"Piccolo": 45, "Medio": 62, "Grande": 82},
    "R2": {"Piccolo": 52, "Medio": 68, "Grande": 88},
    "R3": {"Piccolo": 40, "Medio": 58, "Grande": 79},
    "R4": {"Piccolo": 60, "Medio": 77, "Grande": 96},
}
COSTO = {(i, j): _costi[j][i] for i in TIPI for j in ROTTE}

# ------------------------------------------------------------------------ modello
m = gp.Model("H04")

# x_ij = numero di viaggi del veicolo i sulla rotta j,  x_ij ∈ Z ≥ 0
x = m.addVars(TIPI, ROTTE, vtype=GRB.INTEGER, name="x")

# y_ij = 1 se il veicolo i viene usato sulla rotta j, 0 altrimenti
y = m.addVars(TIPI, ROTTE, vtype=GRB.BINARY, name="y")

# min  Σ_i Σ_j COSTO_ij·x_ij
m.setObjective(
    gp.quicksum(COSTO[i, j] * x[i, j] for i in TIPI for j in ROTTE), GRB.MINIMIZE
)

# Σ_i CAPACITÀ_i·x_ij ≥ DOMANDA_j   ∀j
# (refuso di trascrizione chiarito dall'autrice: vedi intestazione del file)
m.addConstrs(
    (gp.quicksum(CAPACITA[i] * x[i, j] for i in TIPI) >= DOMANDA[j] for j in ROTTE),
    name="domanda",
)

# Σ_i y_ij ≤ 2   ∀j
m.addConstrs(
    (gp.quicksum(y[i, j] for i in TIPI) <= 2 for j in ROTTE), name="max_due_tipi"
)

# y_GRANDE,4 = 1
m.addConstr(y["Grande", "R4"] == 1, name="grande_su_R4")

# Σ_j x_ij ≤ DISPONIBILITÀ_i   ∀i
m.addConstrs(
    (gp.quicksum(x[i, j] for j in ROTTE) <= DISPONIBILITA[i] for i in TIPI),
    name="disponibilita",
)

# Σ_i EMISSIONI_i·(Σ_j x_ij) ≤ 145
m.addConstr(
    gp.quicksum(EMISSIONI[i] * gp.quicksum(x[i, j] for j in ROTTE) for i in TIPI) <= 145,
    name="emissioni",
)

# y_ij ≤ x_ij ≤ DISPONIBILITÀ_i·y_ij   ∀i ∀j
m.addConstrs((y[i, j] <= x[i, j] for i in TIPI for j in ROTTE), name="link_inf")
m.addConstrs(
    (x[i, j] <= DISPONIBILITA[i] * y[i, j] for i in TIPI for j in ROTTE),
    name="link_sup",
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
    m.write("H04.sol")
    print()
    print("Viaggi assegnati (tipo -> rotta : numero):")
    for i in TIPI:
        for j in ROTTE:
            if x[i, j].X > 1e-6:
                print(f"  {i} -> {j} : {x[i, j].X:.0f}")
    print()
    print("Capacità offerta per rotta:")
    for j in ROTTE:
        offerta = sum(CAPACITA[i] * x[i, j].X for i in TIPI)
        viaggi = sum(x[i, j].X for i in TIPI)
        print(f"  {j} : {offerta:.0f} unità di capacità, "
              f"{viaggi:.0f} viaggi (domanda {DOMANDA[j]})")
    emissioni = sum(EMISSIONI[i] * x[i, j].X for i in TIPI for j in ROTTE)
    print()
    print(f"Emissioni totali : {emissioni:.0f} / 145")
elif m.Status == GRB.INFEASIBLE:
    print("Modello INFEASIBLE: nessuna soluzione ammissibile.")
    print("Calcolo dell'Irreducible Infeasible Subsystem (IIS)…")
    m.computeIIS()
    m.write("modello.ilp")
    print()
    print("Vincoli appartenenti all'IIS:")
    for cs in m.getConstrs():
        if cs.IISConstr:
            print(f"  {cs.ConstrName}")
    print()
    print("Bound appartenenti all'IIS:")
    for v in m.getVars():
        if v.IISLB:
            print(f"  lower bound di {v.VarName}")
        if v.IISUB:
            print(f"  upper bound di {v.VarName}")
print("=" * 70)
