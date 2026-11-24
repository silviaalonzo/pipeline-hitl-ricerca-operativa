#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M09 - Piano di riordino con costi fissi
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_i     = quantita' ordinata nel periodo i               i = 1..6
    y_i     = quantita' a magazzino a fine periodo i         i = 1..6
    delta_i = 1 se nel periodo i si ordina, 0 altrimenti

    min  sum_i CACQ_i x_i + sum_i 40 delta_i + sum_i 2 y_i
    s.t. x_i + y_{i-1} = DOMANDA_i + y_i        per ogni i
         x_i <= CAPACITA_i delta_i              per ogni i
         x_i >= 10 delta_i                      per ogni i
         y_0 = 10
         y_6 >= 5
         x_i in Z                               per ogni i
         y_i in Z                               per ogni i
         delta_i in {0,1}                       per ogni i

Note di traduzione:
- y_0 non compare fra le variabili dichiarate (y_i e' definita per i = 1..6):
  "y_0 = 10" e' quindi la scorta iniziale, usata come costante nel bilancio
  del primo periodo e non come variabile con un proprio vincolo;
- la formulazione scrive "x_i in Z" e "y_i in Z": l'autrice ha precisato
  (16 agosto 2026) che con Z intende gli interi NON NEGATIVI, quindi entrambe
  le famiglie sono dichiarate intere con il lower bound di default 0. Per y_i
  questo e' l'unico elemento che esprime il divieto di arretrati posto dal
  testo, dato che nessun altro vincolo della formulazione lo implica.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
PERIODI = [1, 2, 3, 4, 5, 6]

DOMANDA = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
CACQ = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
CAPACITA = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}

SCORTA_INIZIALE = 10          # y_0 = 10
SCORTA_FINALE_MINIMA = 5      # y_6 >= 5
COSTO_FISSO = 40
COSTO_MANTENIMENTO = 2
ORDINE_MINIMO = 10

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M09_piano_riordino")

# Variabili decisionali
x = m.addVars(PERIODI, vtype=GRB.INTEGER, name="x")
y = m.addVars(PERIODI, vtype=GRB.INTEGER, name="y")
delta = m.addVars(PERIODI, vtype=GRB.BINARY, name="delta")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(CACQ[i] * x[i] for i in PERIODI)
    + gp.quicksum(COSTO_FISSO * delta[i] for i in PERIODI)
    + gp.quicksum(COSTO_MANTENIMENTO * y[i] for i in PERIODI),
    GRB.MINIMIZE,
)

# x_i + y_{i-1} = DOMANDA_i + y_i   per ogni i   (y_0 = scorta iniziale)
for i in PERIODI:
    precedente = SCORTA_INIZIALE if i == 1 else y[i - 1]
    m.addConstr(x[i] + precedente == DOMANDA[i] + y[i], name=f"bilancio_{i}")

# x_i <= CAPACITA_i delta_i   per ogni i
m.addConstrs((x[i] <= CAPACITA[i] * delta[i] for i in PERIODI), name="capacita")

# x_i >= 10 delta_i   per ogni i
m.addConstrs((x[i] >= ORDINE_MINIMO * delta[i] for i in PERIODI), name="ordine_minimo")

# y_6 >= 5
m.addConstr(y[6] >= SCORTA_FINALE_MINIMA, name="scorta_finale")

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
print("RISULTATO M09 - Piano di riordino con costi fissi")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Piano ottenuto:")
    print(f"    {'per.':>5}{'domanda':>10}{'ordine x':>10}{'delta':>8}"
          f"{'scorta y':>10}{'capacita':>10}")
    for i in PERIODI:
        print(f"    {i:>5}{DOMANDA[i]:>10}{x[i].X:>10g}{delta[i].X:>8g}"
              f"{y[i].X:>10g}{CAPACITA[i]:>10}")
    print()
    print("Composizione del costo:")
    acq = sum(CACQ[i] * x[i].X for i in PERIODI)
    fis = sum(COSTO_FISSO * delta[i].X for i in PERIODI)
    man = sum(COSTO_MANTENIMENTO * y[i].X for i in PERIODI)
    print(f"    costo di acquisto     = {acq:g}")
    print(f"    costi fissi di ordine = {fis:g}"
          f"  ({sum(delta[i].X for i in PERIODI):g} ordini)")
    print(f"    costo di mantenimento = {man:g}")
    m.write(str(QUI / "M09.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M09.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
