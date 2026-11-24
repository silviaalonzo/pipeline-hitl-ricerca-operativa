#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M08 - Copertura di zone con centri di servizio
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    y_i = 1 se il centro i e' aperto, 0 altrimenti     i = A..H

    min  sum_{i=A}^{H} COSTO_i y_i
    s.t. yA + yC           >= 1     (Z1)
         yA + yB           >= 1     (Z2)
         yA + yB + yD      >= 2     (Z3, doppia copertura)
         yB + yE           >= 1     (Z4)
         yB + yC + yF      >= 1     (Z5)
         yC + yD + yG      >= 1     (Z6)
         yD + yE + yH      >= 2     (Z7, doppia copertura)
         yE + yF + yH      >= 1     (Z8)
         yF + yG           >= 1     (Z9)
         yG + yH           >= 1     (Z10)
         sum_{i=A}^{H} y_i <= 5
         y_i in {0,1}                per ogni i

Nota di traduzione: i vincoli di copertura sono riportati esattamente come
elencati nella formulazione; l'elenco dei centri che compaiono in ciascuna
riga coincide con la colonna "Zone coperte" della tabella del testo.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
CENTRI = ["A", "B", "C", "D", "E", "F", "G", "H"]

COSTO = {"A": 24, "B": 20, "C": 27, "D": 22, "E": 25, "F": 19, "G": 23, "H": 21}

# Vincoli di copertura come scritti nella formulazione: (zona, centri, rhs)
COPERTURA = [
    ("Z1", ["A", "C"], 1),
    ("Z2", ["A", "B"], 1),
    ("Z3", ["A", "B", "D"], 2),
    ("Z4", ["B", "E"], 1),
    ("Z5", ["B", "C", "F"], 1),
    ("Z6", ["C", "D", "G"], 1),
    ("Z7", ["D", "E", "H"], 2),
    ("Z8", ["E", "F", "H"], 1),
    ("Z9", ["F", "G"], 1),
    ("Z10", ["G", "H"], 1),
]

CENTRI_MASSIMI = 5

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M08_copertura_zone")

# Variabili decisionali
y = m.addVars(CENTRI, vtype=GRB.BINARY, name="y")

# Funzione obiettivo: min sum_i COSTO_i y_i
m.setObjective(gp.quicksum(COSTO[i] * y[i] for i in CENTRI), GRB.MINIMIZE)

# Vincoli di copertura, uno per zona
for zona, centri, rhs in COPERTURA:
    m.addConstr(gp.quicksum(y[i] for i in centri) >= rhs, name=f"copertura_{zona}")

# sum_i y_i <= 5
m.addConstr(gp.quicksum(y[i] for i in CENTRI) <= CENTRI_MASSIMI, name="numero_centri")

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
print("RISULTATO M08 - Copertura di zone con centri di servizio")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle (y_i = 1):")
    for i in CENTRI:
        if y[i].X > 0.5:
            print(f"    y[{i}] = 1   (costo {COSTO[i]})")
    print()
    print(f"Centri aperti: {sum(y[i].X for i in CENTRI):g} (ammessi <= {CENTRI_MASSIMI})")
    print()
    print("Copertura ottenuta:")
    for zona, centri, rhs in COPERTURA:
        aperti = [i for i in centri if y[i].X > 0.5]
        print(f"    {zona:<4}: {len(aperti)} copertura/e (richieste {rhs})"
              f"   centri {', '.join(aperti) if aperti else '-'}")
    m.write(str(QUI / "M08.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M08.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
