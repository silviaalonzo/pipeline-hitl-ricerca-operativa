#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M02 - Piano di produzione con costi di setup
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_i     = n. di lotti prodotti di articolo i          i = A, B, C, D
    delta_i = 1 se l'articolo i e' avviato, 0 altrimenti

    max  sum_i MARGINE_i x_i - sum_i SETUP_i delta_i
    s.t. sum_i OREMACCHINA_i x_i <= 90
         sum_i OREUOMO_i x_i     <= 100
         x_i >= LOTTOMIN_i * delta_i        per ogni i
         x_i <= DOMMAX_i  * delta_i         per ogni i
         sum_i delta_i >= 2
         x_i in Z
         delta_i in {0,1}

Nota di traduzione: la formulazione scrive "x_i in Z". L'autrice ha precisato
(16 agosto 2026) che con Z intende gli interi NON NEGATIVI; le variabili x sono
quindi dichiarate intere con il lower bound di default 0. La convenzione e'
applicata in modo uniforme a tutti i problemi in cui la formulazione scrive "in Z".
Su questo problema la scelta e' ininfluente: la non negativita' era gia' implicata
da x_i <= DOMMAX_i delta_i con delta_i = 0.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
ARTICOLI = ["A", "B", "C", "D"]

MARGINE = {"A": 42, "B": 36, "C": 50, "D": 31}
SETUP = {"A": 80, "B": 65, "C": 90, "D": 50}
OREMACCHINA = {"A": 3, "B": 2, "C": 4, "D": 1}
OREUOMO = {"A": 2, "B": 3, "C": 2, "D": 2}
LOTTOMIN = {"A": 4, "B": 5, "C": 3, "D": 6}
DOMMAX = {"A": 20, "B": 25, "C": 16, "D": 30}

ORE_MACCHINA_DISPONIBILI = 90
ORE_LAVORO_DISPONIBILI = 100

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M02_piano_produzione_setup")

# Variabili decisionali
x = m.addVars(ARTICOLI, vtype=GRB.INTEGER, name="x")
delta = m.addVars(ARTICOLI, vtype=GRB.BINARY, name="delta")

# Funzione obiettivo: max sum_i MARGINE_i x_i - sum_i SETUP_i delta_i
m.setObjective(
    gp.quicksum(MARGINE[i] * x[i] for i in ARTICOLI)
    - gp.quicksum(SETUP[i] * delta[i] for i in ARTICOLI),
    GRB.MAXIMIZE,
)

# sum_i OREMACCHINA_i x_i <= 90
m.addConstr(
    gp.quicksum(OREMACCHINA[i] * x[i] for i in ARTICOLI) <= ORE_MACCHINA_DISPONIBILI,
    name="ore_macchina",
)

# sum_i OREUOMO_i x_i <= 100
m.addConstr(
    gp.quicksum(OREUOMO[i] * x[i] for i in ARTICOLI) <= ORE_LAVORO_DISPONIBILI,
    name="ore_lavoro",
)

# x_i >= LOTTOMIN_i * delta_i  per ogni i
m.addConstrs((x[i] >= LOTTOMIN[i] * delta[i] for i in ARTICOLI), name="lotto_minimo")

# x_i <= DOMMAX_i * delta_i  per ogni i
m.addConstrs((x[i] <= DOMMAX[i] * delta[i] for i in ARTICOLI), name="domanda_massima")

# sum_i delta_i >= 2
m.addConstr(gp.quicksum(delta[i] for i in ARTICOLI) >= 2, name="almeno_due_articoli")

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
print("RISULTATO M02 - Piano di produzione con costi di setup")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle:")
    for i in ARTICOLI:
        if abs(x[i].X) > 1e-6:
            print(f"    x[{i}] = {x[i].X:g}   (margine unitario {MARGINE[i]})")
    for i in ARTICOLI:
        if delta[i].X > 0.5:
            print(f"    delta[{i}] = 1   (setup {SETUP[i]})")
    print()
    print("Verifica risorse:")
    ore_m = sum(OREMACCHINA[i] * x[i].X for i in ARTICOLI)
    ore_l = sum(OREUOMO[i] * x[i].X for i in ARTICOLI)
    print(f"    ore macchina impiegate = {ore_m:g} / {ORE_MACCHINA_DISPONIBILI}")
    print(f"    ore lavoro impiegate   = {ore_l:g} / {ORE_LAVORO_DISPONIBILI}")
    m.write(str(QUI / "M02.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M02.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
