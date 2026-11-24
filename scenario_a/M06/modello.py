#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M06 - Bilanciamento di lavori su due macchine
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_ij = 1 se il lavoro i e' assegnato alla macchina j, 0 altrimenti
           i = 1..7 ; j = A, B
    Cmax = massimo tra i due carichi

    min  Cmax
    s.t. sum_{j=A,B} x_ij = 1              per ogni i  (un lavoro su una sola macchina)
         Cmax >= sum_{i=1}^{7} T_iA x_iA
         Cmax >= sum_{i=1}^{7} T_iB x_iB
         x_7B = 1                          (J7 non e' compatibile con la macchina A)
         x_ij in {0,1}                     per ogni i, j

Note di traduzione:
- la formulazione esclude J7 dalla macchina A scrivendo x_7B = 1 (e non
  x_7A = 0): il vincolo e' riportato nella forma scritta dall'esperto;
- la cella "-" della tabella dei tempi (J7 su macchina A) non ha un valore
  numerico; il coefficiente e' posto a 0, scelta ininfluente perche' x_7A e'
  forzata a zero da x_7B = 1 insieme al vincolo di assegnazione unica;
- Cmax non ha un dominio dichiarato nella formulazione ed e' quindi
  introdotta come variabile continua non negativa.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
LAVORI = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
MACCHINE = ["A", "B"]

# Tempi di lavorazione: None = lavorazione non ammessa (cella "-" della tabella)
TEMPO = {
    "J1": {"A": 7, "B": 9},
    "J2": {"A": 6, "B": 5},
    "J3": {"A": 8, "B": 7},
    "J4": {"A": 5, "B": 8},
    "J5": {"A": 9, "B": 6},
    "J6": {"A": 4, "B": 7},
    "J7": {"A": None, "B": 5},
}

# Coefficiente usato nei vincoli su Cmax (0 dove il tempo non e' definito)
T = {i: {j: (TEMPO[i][j] or 0) for j in MACCHINE} for i in LAVORI}

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M06_bilanciamento_due_macchine")

# Variabili decisionali
x = m.addVars(LAVORI, MACCHINE, vtype=GRB.BINARY, name="x")
cmax = m.addVar(name="Cmax")

# Funzione obiettivo: min Cmax
m.setObjective(cmax, GRB.MINIMIZE)

# sum_j x_ij = 1  per ogni i
m.addConstrs(
    (gp.quicksum(x[i, j] for j in MACCHINE) == 1 for i in LAVORI), name="assegnazione"
)

# Cmax >= carico della macchina A  e  Cmax >= carico della macchina B
m.addConstr(cmax >= gp.quicksum(T[i]["A"] * x[i, "A"] for i in LAVORI), name="carico_A")
m.addConstr(cmax >= gp.quicksum(T[i]["B"] * x[i, "B"] for i in LAVORI), name="carico_B")

# x_7B = 1 : J7 non e' compatibile con la macchina A
m.addConstr(x["J7", "B"] == 1, name="incompatibilita_J7A")

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
print("RISULTATO M06 - Bilanciamento di lavori su due macchine")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle (x_ij = 1):")
    for i in LAVORI:
        for j in MACCHINE:
            if x[i, j].X > 0.5:
                print(f"    x[{i},{j}] = 1   (tempo {T[i][j]})")
    print()
    print("Carichi delle macchine:")
    for j in MACCHINE:
        carico = sum(T[i][j] * x[i, j].X for i in LAVORI)
        lavori_j = [i for i in LAVORI if x[i, j].X > 0.5]
        print(f"    macchina {j}: carico {carico:g}   lavori {', '.join(lavori_j)}")
    print(f"    makespan (Cmax) = {cmax.X:g}")
    m.write(str(QUI / "M06.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M06.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
