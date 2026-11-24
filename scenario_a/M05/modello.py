#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M05 - Selezione di un portafoglio progetti
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_i = 1 se il progetto i viene scelto nel portafoglio, 0 altrimenti
          i = 1..8

    max  sum_i VALORE_i x_i
    s.t. sum_i BUDGET_i x_i    <= 100
         sum_i PERSONALE_i x_i <= 18
         x5 <= x2                       (P5 => P2)
         x7 <= x3                       (P7 => P3)
         x4 + x6 <= 1
         x1 + x3 + x7 >= 1
         sum_i x_i >= 3
         x_i in {0,1}

NOTA - refuso di trascrizione, chiarito dall'autrice della formulazione:
nel manoscritto il penultimo vincolo e' trascritto come "x1 + x3 + x9 >= 1".
L'indice 9 non esiste (i progetti sono 8) ed e' stato letto come x7, unico
indice compatibile sia con l'insieme delle variabili sia con il testo del
problema ("almeno un progetto digitale tra P1, P3 e P7"). L'autrice ha
confermato che l'indice inteso era x7. Nessun'altra modifica e' stata
apportata alla formulazione.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
PROGETTI = [1, 2, 3, 4, 5, 6, 7, 8]

VALORE = {1: 30, 2: 24, 3: 35, 4: 28, 5: 33, 6: 26, 7: 38, 8: 21}
BUDGET = {1: 20, 2: 18, 3: 27, 4: 24, 5: 22, 6: 19, 7: 30, 8: 15}
PERSONALE = {1: 4, 2: 3, 3: 5, 4: 4, 5: 4, 6: 3, 7: 5, 8: 2}

BUDGET_DISPONIBILE = 100
PERSONALE_DISPONIBILE = 18

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M05_selezione_portafoglio_progetti")

# Variabili decisionali
x = m.addVars(PROGETTI, vtype=GRB.BINARY, name="x")

# Funzione obiettivo: max sum_i VALORE_i x_i
m.setObjective(gp.quicksum(VALORE[i] * x[i] for i in PROGETTI), GRB.MAXIMIZE)

# sum_i BUDGET_i x_i <= 100
m.addConstr(
    gp.quicksum(BUDGET[i] * x[i] for i in PROGETTI) <= BUDGET_DISPONIBILE, name="budget"
)

# sum_i PERSONALE_i x_i <= 18
m.addConstr(
    gp.quicksum(PERSONALE[i] * x[i] for i in PROGETTI) <= PERSONALE_DISPONIBILE,
    name="personale",
)

# x5 <= x2
m.addConstr(x[5] <= x[2], name="P5_richiede_P2")

# x7 <= x3
m.addConstr(x[7] <= x[3], name="P7_richiede_P3")

# x4 + x6 <= 1
m.addConstr(x[4] + x[6] <= 1, name="P4_P6_incompatibili")

# x1 + x3 + x7 >= 1   (nel manoscritto: "x1 + x3 + x9 >= 1", cfr. nota in testa)
m.addConstr(x[1] + x[3] + x[7] >= 1, name="almeno_un_digitale")

# sum_i x_i >= 3
m.addConstr(gp.quicksum(x[i] for i in PROGETTI) >= 3, name="almeno_tre_progetti")

m.write(str(QUI / "modello.lp"))

# ---------------------------------------------------------------- SOLUZIONE
m.optimize()

STATI = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

print()
print("=" * 70)
print("RISULTATO M05 - Selezione di un portafoglio progetti")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle (x_i = 1):")
    for i in PROGETTI:
        if x[i].X > 0.5:
            print(
                f"    x[{i}] = 1   (P{i}: valore {VALORE[i]}, "
                f"budget {BUDGET[i]}, personale {PERSONALE[i]})"
            )
    print()
    print("Verifica risorse:")
    bud = sum(BUDGET[i] * x[i].X for i in PROGETTI)
    per = sum(PERSONALE[i] * x[i].X for i in PROGETTI)
    print(f"    budget impiegato    = {bud:g} / {BUDGET_DISPONIBILE}")
    print(f"    personale impiegato = {per:g} / {PERSONALE_DISPONIBILE}")
    m.write(str(QUI / "M05.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M05.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
