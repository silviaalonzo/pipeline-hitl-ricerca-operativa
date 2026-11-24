#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M01 - Localizzazione di centri di assistenza
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione in gurobipy della formulazione dell'esperto.

Formulazione di riferimento:
    x_i = 1 se il sito i e' aperto, 0 altrimenti          i = A, B, C, D
    y_ij = 1 se la zona j e' assegnata al sito i, 0 altr. i = A..D ; j = 1..6

    min  sum_i CF_i x_i + sum_i sum_j CA_ij y_ij
    s.t. sum_i x_i = 2
         sum_i y_ij = 1                 per ogni j   (ogni zona a un solo centro)
         sum_j y_ij <= CAPACITA_i       per ogni i
         y_ij <= x_i                    per ogni i, j (solo verso centri aperti)
         x_i in {0,1}                   per ogni i
         y_ij in {0,1}                  per ogni i, j
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
SITI = ["A", "B", "C", "D"]
ZONE = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]

# Costo fisso di apertura (migliaia di euro)
CF = {"A": 38, "B": 42, "C": 35, "D": 46}

# Capacita': numero massimo di zone assegnabili al sito
CAPACITA = {"A": 2, "B": 3, "C": 2, "D": 3}

# Costo di assegnazione CA[i][j]: sito i, zona j (migliaia di euro)
CA = {
    "A": {"Z1": 8, "Z2": 10, "Z3": 12, "Z4": 15, "Z5": 9, "Z6": 14},
    "B": {"Z1": 14, "Z2": 9, "Z3": 8, "Z4": 11, "Z5": 13, "Z6": 10},
    "C": {"Z1": 11, "Z2": 13, "Z3": 14, "Z4": 9, "Z5": 8, "Z6": 7},
    "D": {"Z1": 17, "Z2": 15, "Z3": 10, "Z4": 7, "Z5": 14, "Z6": 9},
}

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M01_localizzazione_centri_assistenza")

# Variabili decisionali
x = m.addVars(SITI, vtype=GRB.BINARY, name="x")
y = m.addVars(SITI, ZONE, vtype=GRB.BINARY, name="y")

# Funzione obiettivo: min sum_i CF_i x_i + sum_i sum_j CA_ij y_ij
m.setObjective(
    gp.quicksum(CF[i] * x[i] for i in SITI)
    + gp.quicksum(CA[i][j] * y[i, j] for i in SITI for j in ZONE),
    GRB.MINIMIZE,
)

# sum_i x_i = 2
m.addConstr(gp.quicksum(x[i] for i in SITI) == 2, name="aperture")

# sum_i y_ij = 1  per ogni j
m.addConstrs(
    (gp.quicksum(y[i, j] for i in SITI) == 1 for j in ZONE), name="assegnazione"
)

# sum_j y_ij <= CAPACITA_i  per ogni i
m.addConstrs(
    (gp.quicksum(y[i, j] for j in ZONE) <= CAPACITA[i] for i in SITI), name="capacita"
)

# y_ij <= x_i  per ogni i, j : una zona puo' essere servita solo da un centro aperto
m.addConstrs((y[i, j] <= x[i] for i in SITI for j in ZONE), name="collegamento")

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
print("RISULTATO M01 - Localizzazione di centri di assistenza")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle:")
    print("  Siti aperti (x_i = 1):")
    for i in SITI:
        if x[i].X > 0.5:
            print(f"    x[{i}] = 1   (costo fisso {CF[i]})")
    print("  Assegnazioni zona-sito (y_ij = 1):")
    for i in SITI:
        for j in ZONE:
            if y[i, j].X > 0.5:
                print(f"    y[{i},{j}] = 1   (costo assegnazione {CA[i][j]})")
    print()
    print("Utilizzo delle capacita':")
    for i in SITI:
        if x[i].X > 0.5:
            usate = sum(y[i, j].X for j in ZONE)
            print(f"    sito {i}: {usate:g} zone su {CAPACITA[i]} disponibili")
    m.write(str(QUI / "M01.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M01.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
