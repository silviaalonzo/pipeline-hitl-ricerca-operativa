#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M10 - Progettazione di una rete distributiva
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_ij = flusso sull'arco (i,j)
    y_ij = 1 se l'arco (i,j) e' attivato, 0 altrimenti

    min  sum_{(i,j)} ( CF_ij y_ij + CV_ij x_ij )
    s.t. x_ij <= CAPACITA_ij y_ij                per ogni arco (i,j)
         x_SA + x_SB = 40
         x_SA = x_AB + x_AC
         x_SB + x_AB = x_BC + x_BT
         x_AC + x_BC = x_CT
         x_BT + x_CT = 40
         x_ij in Z                               per ogni arco
         y_ij in {0,1}                           per ogni arco

Nota di traduzione: la formulazione scrive "x_ij in Z". L'autrice ha precisato
(16 agosto 2026) che con Z intende gli interi NON NEGATIVI, quindi le variabili
di flusso sono dichiarate intere con il lower bound di default 0. E' questo a
escludere i flussi negativi: il vincolo x_ij <= CAPACITA_ij y_ij impone solo il
limite superiore.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
ARCHI = [("S", "A"), ("S", "B"), ("A", "B"), ("A", "C"), ("B", "C"), ("B", "T"),
         ("C", "T")]

CF = {("S", "A"): 40, ("S", "B"): 35, ("A", "B"): 15, ("A", "C"): 30,
      ("B", "C"): 18, ("B", "T"): 45, ("C", "T"): 38}
CV = {("S", "A"): 2, ("S", "B"): 3, ("A", "B"): 1, ("A", "C"): 2,
      ("B", "C"): 2, ("B", "T"): 4, ("C", "T"): 2}
CAPACITA = {("S", "A"): 30, ("S", "B"): 35, ("A", "B"): 15, ("A", "C"): 25,
            ("B", "C"): 20, ("B", "T"): 25, ("C", "T"): 35}

DOMANDA = 40

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M10_rete_distributiva")

# Variabili decisionali
x = m.addVars(ARCHI, vtype=GRB.INTEGER, name="x")
y = m.addVars(ARCHI, vtype=GRB.BINARY, name="y")

# Funzione obiettivo: min sum ( CF_ij y_ij + CV_ij x_ij )
m.setObjective(
    gp.quicksum(CF[a] * y[a] + CV[a] * x[a] for a in ARCHI), GRB.MINIMIZE
)

# x_ij <= CAPACITA_ij y_ij   per ogni arco
m.addConstrs((x[a] <= CAPACITA[a] * y[a] for a in ARCHI), name="attivazione")

# Conservazione del flusso, nodo per nodo, come scritta nella formulazione
m.addConstr(x["S", "A"] + x["S", "B"] == DOMANDA, name="uscita_S")
m.addConstr(x["S", "A"] == x["A", "B"] + x["A", "C"], name="nodo_A")
m.addConstr(x["S", "B"] + x["A", "B"] == x["B", "C"] + x["B", "T"], name="nodo_B")
m.addConstr(x["A", "C"] + x["B", "C"] == x["C", "T"], name="nodo_C")
m.addConstr(x["B", "T"] + x["C", "T"] == DOMANDA, name="ingresso_T")

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
print("RISULTATO M10 - Progettazione di una rete distributiva")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Archi e decisioni:")
    print(f"    {'arco':<8}{'flusso x':>10}{'attivo y':>10}{'capacita':>10}"
          f"{'CF':>6}{'CV':>5}")
    for a in ARCHI:
        etichetta = f"{a[0]}->{a[1]}"
        print(f"    {etichetta:<8}{x[a].X:>10g}{y[a].X:>10g}{CAPACITA[a]:>10}"
              f"{CF[a]:>6}{CV[a]:>5}")
    print()
    print("Composizione del costo:")
    fisso = sum(CF[a] * y[a].X for a in ARCHI)
    variabile = sum(CV[a] * x[a].X for a in ARCHI)
    print(f"    costi di attivazione = {fisso:g}")
    print(f"    costi di trasporto   = {variabile:g}")
    m.write(str(QUI / "M10.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M10.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
