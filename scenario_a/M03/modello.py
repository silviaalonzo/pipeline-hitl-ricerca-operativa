#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M03 - Assegnazione del personale ai turni
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_ij = 1 se il dipendente i e' assegnato al turno j, 0 altrimenti
           i = Ana..Fabio ; j = M1, M2, P1, P2, N1, N2

    min  sum_i sum_j COSTO_ij x_ij
    s.t. sum_j x_ij <= 2                    per ogni i
         sum_{j = N1..N2} x_ij <= 1         per ogni i
         sum_i x_ij = 1                     per ogni j
         8 vincoli di indisponibilita'      (celle "-" della tabella)
         x_ij in {0,1}

Nota di traduzione: gli "8 vincoli di indisponibilita'" sono resi come otto
vincoli espliciti x_ij = 0 sulle otto celle marcate "-". Per tali celle il costo
non e' definito nel testo; poiche' le variabili sono forzate a zero, il
coefficiente in funzione obiettivo e' irrilevante ed e' posto a 0.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
DIPENDENTI = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
TURNI = ["M1", "M2", "P1", "P2", "N1", "N2"]
TURNI_NOTTURNI = ["N1", "N2"]

# Costi e disponibilita': None = cella "-" (indisponibilita')
COSTO = {
    "Ana": {"M1": 8, "M2": 7, "P1": 9, "P2": 8, "N1": None, "N2": None},
    "Bruno": {"M1": 7, "M2": 8, "P1": 8, "P2": 9, "N1": None, "N2": None},
    "Carla": {"M1": None, "M2": 9, "P1": 8, "P2": 8, "N1": 11, "N2": 12},
    "Diego": {"M1": 10, "M2": None, "P1": 9, "P2": 8, "N1": 10, "N2": 11},
    "Elena": {"M1": 8, "M2": 10, "P1": 9, "P2": 9, "N1": 12, "N2": 10},
    "Fabio": {"M1": 9, "M2": 8, "P1": 10, "P2": 7, "N1": None, "N2": None},
}

# Le otto celle "-" della tabella
INDISPONIBILITA = [
    (i, j) for i in DIPENDENTI for j in TURNI if COSTO[i][j] is None
]

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M03_assegnazione_personale_turni")

# Variabili decisionali
x = m.addVars(DIPENDENTI, TURNI, vtype=GRB.BINARY, name="x")

# Funzione obiettivo: min sum_i sum_j COSTO_ij x_ij
m.setObjective(
    gp.quicksum(
        (COSTO[i][j] if COSTO[i][j] is not None else 0) * x[i, j]
        for i in DIPENDENTI
        for j in TURNI
    ),
    GRB.MINIMIZE,
)

# sum_j x_ij <= 2  per ogni i
m.addConstrs(
    (gp.quicksum(x[i, j] for j in TURNI) <= 2 for i in DIPENDENTI), name="max_due_turni"
)

# sum_{j in notturni} x_ij <= 1  per ogni i
m.addConstrs(
    (gp.quicksum(x[i, j] for j in TURNI_NOTTURNI) <= 1 for i in DIPENDENTI),
    name="max_un_notturno",
)

# sum_i x_ij = 1  per ogni j
m.addConstrs(
    (gp.quicksum(x[i, j] for i in DIPENDENTI) == 1 for j in TURNI), name="copertura"
)

# 8 vincoli di indisponibilita'
for i, j in INDISPONIBILITA:
    m.addConstr(x[i, j] == 0, name=f"indisponibilita_{i}_{j}")

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
print("RISULTATO M03 - Assegnazione del personale ai turni")
print("=" * 70)
print(f"Numero di vincoli di indisponibilita' inseriti: {len(INDISPONIBILITA)}")
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle (x_ij = 1):")
    for j in TURNI:
        for i in DIPENDENTI:
            if x[i, j].X > 0.5:
                print(f"    x[{i},{j}] = 1   (costo {COSTO[i][j]})")
    m.write(str(QUI / "M03.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M03.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
