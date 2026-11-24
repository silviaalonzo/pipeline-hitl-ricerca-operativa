#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M07 - Selezione dei fornitori con qualita' minima
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione,
compresi quelli che si discostano dal testo del problema.

Formulazione di riferimento:
    x_i     = n. di unita' acquistate dal fornitore i        i = A, B, C, D
    delta_i = 1 se il fornitore i e' attivo, 0 altrimenti

    min  sum_i CV_i x_i + sum_i CF_i delta_i
    s.t. sum_i delta_i >= 2
         sum_i x_i = 180
         sum_i QUALITA_i delta_i >= 92
         sum_i EMISSIONI_i x_i <= 650
         ORDINEMIN_i delta_i <= x_i <= CAPACITA_i delta_i   per ogni i
         x_i in Z                                          per ogni i
         delta_i in {0,1}                                  per ogni i

Note di traduzione:
- il vincolo di qualita' e' scritto nella formulazione con le variabili
  binarie delta_i e non con le quantita' x_i: e' riportato cosi' com'e';
- la doppia disuguaglianza e' tradotta in due vincoli di riga per fornitore.
  Il manoscritto riporta a destra CAPACITA_i; l'autrice ha chiarito
  (16 agosto 2026) che si tratta di un refuso di trascrizione e che il limite
  superiore inteso e' CAPACITA_i delta_i, cioe' legato all'attivazione;
- la formulazione scrive "x_i in Z": l'autrice ha precisato (16 agosto 2026)
  che con Z intende gli interi NON NEGATIVI, quindi le variabili sono
  dichiarate intere con il lower bound di default 0.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
FORNITORI = ["A", "B", "C", "D"]

CV = {"A": 11, "B": 10, "C": 12, "D": 9}          # costo per unita'
CF = {"A": 80, "B": 95, "C": 60, "D": 120}        # costo fisso di attivazione
CAPACITA = {"A": 80, "B": 100, "C": 70, "D": 90}
ORDINEMIN = {"A": 20, "B": 25, "C": 15, "D": 20}
QUALITA = {"A": 96, "B": 90, "C": 98, "D": 88}
EMISSIONI = {"A": 3, "B": 4, "C": 2, "D": 5}

FABBISOGNO = 180
FORNITORI_MINIMI = 2
QUALITA_MINIMA = 92
EMISSIONI_MASSIME = 650

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M07_selezione_fornitori")

# Variabili decisionali
x = m.addVars(FORNITORI, vtype=GRB.INTEGER, name="x")
delta = m.addVars(FORNITORI, vtype=GRB.BINARY, name="delta")

# Funzione obiettivo: min sum_i CV_i x_i + sum_i CF_i delta_i
m.setObjective(
    gp.quicksum(CV[i] * x[i] for i in FORNITORI)
    + gp.quicksum(CF[i] * delta[i] for i in FORNITORI),
    GRB.MINIMIZE,
)

# sum_i delta_i >= 2
m.addConstr(
    gp.quicksum(delta[i] for i in FORNITORI) >= FORNITORI_MINIMI, name="fornitori_minimi"
)

# sum_i x_i = 180
m.addConstr(gp.quicksum(x[i] for i in FORNITORI) == FABBISOGNO, name="fabbisogno")

# sum_i QUALITA_i delta_i >= 92   (scritto sulle binarie nella formulazione)
m.addConstr(
    gp.quicksum(QUALITA[i] * delta[i] for i in FORNITORI) >= QUALITA_MINIMA,
    name="qualita",
)

# sum_i EMISSIONI_i x_i <= 650
m.addConstr(
    gp.quicksum(EMISSIONI[i] * x[i] for i in FORNITORI) <= EMISSIONI_MASSIME,
    name="emissioni",
)

# ORDINEMIN_i delta_i <= x_i <= CAPACITA_i delta_i   per ogni i
m.addConstrs((ORDINEMIN[i] * delta[i] <= x[i] for i in FORNITORI), name="ordine_minimo")
m.addConstrs((x[i] <= CAPACITA[i] * delta[i] for i in FORNITORI), name="capacita")

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
print("RISULTATO M07 - Selezione dei fornitori con qualita' minima")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle:")
    for i in FORNITORI:
        if abs(x[i].X) > 1e-6 or delta[i].X > 0.5:
            print(
                f"    fornitore {i}: x = {x[i].X:g}   delta = {delta[i].X:g}"
                f"   (CV {CV[i]}, CF {CF[i]}, ordine min. {ORDINEMIN[i]})"
            )
    print()
    print("Verifica requisiti:")
    tot = sum(x[i].X for i in FORNITORI)
    att = sum(delta[i].X for i in FORNITORI)
    emi = sum(EMISSIONI[i] * x[i].X for i in FORNITORI)
    qual_delta = sum(QUALITA[i] * delta[i].X for i in FORNITORI)
    print(f"    unita' acquistate  = {tot:g} (richieste {FABBISOGNO})")
    print(f"    fornitori attivati = {att:g} (richiesti >= {FORNITORI_MINIMI})")
    print(f"    emissioni totali   = {emi:g} (ammesse <= {EMISSIONI_MASSIME})")
    print(f"    qualita' come da formulazione (sulle delta) = {qual_delta:g}"
          f" (richiesta >= {QUALITA_MINIMA})")
    if abs(tot) > 1e-9:
        qual_media = sum(QUALITA[i] * x[i].X for i in FORNITORI) / tot
        print(f"    qualita' media ponderata sulle quantita'    = {qual_media:.4f}")
    m.write(str(QUI / "M07.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M07.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
