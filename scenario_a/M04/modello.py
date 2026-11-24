#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M04 - Composizione di una flotta giornaliera
Scenario A (esperto umano senza assistenza LLM) - Tesi MSc Silvia Alonzo

Traduzione 1:1 in gurobipy della formulazione manoscritta dell'esperto.
La modellazione NON e' stata modificata in alcun modo: variabili, funzione
obiettivo e vincoli sono esattamente quelli scritti nella formulazione.

Formulazione di riferimento:
    x_i = n. di veicoli di tipo i impiegati              i = 1..5

    min  sum_i COSTO_i x_i
    s.t. sum_i VOLUME_i x_i    >= 180
         sum_i PORTATA_i x_i   >= 95
         sum_i EMISSIONI_i x_i <= 145
         0 <= x1 <= 8
         0 <= x2 <= 6
         1 <= x3 <= 4
         1 <= x4 <= 5
         0 <= x5 <= 3
         x_i in Z

Nota di traduzione: l'ordine degli indici 1..5 segue la tabella del testo
(1 Van, 2 Autocarro, 3 Refrigerato, 4 Elettrico, 5 Bilico); i lower bound
unitari su x3 e x4 sono quelli scritti nella formulazione.
"""

from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

QUI = Path(__file__).resolve().parent

# --------------------------------------------------------------------- DATI
TIPI = [1, 2, 3, 4, 5]
NOME = {1: "Van", 2: "Autocarro", 3: "Refrigerato", 4: "Elettrico", 5: "Bilico"}

VOLUME = {1: 18, 2: 30, 3: 20, 4: 16, 5: 42}
PORTATA = {1: 8, 2: 18, 3: 10, 4: 7, 5: 28}
COSTO = {1: 120, 2: 180, 3: 210, 4: 150, 5: 260}
EMISSIONI = {1: 12, 2: 22, 3: 15, 4: 4, 5: 32}

# Bound come scritti nella formulazione
LB = {1: 0, 2: 0, 3: 1, 4: 1, 5: 0}
UB = {1: 8, 2: 6, 3: 4, 4: 5, 5: 3}

VOLUME_RICHIESTO = 180
PORTATA_RICHIESTA = 95
EMISSIONI_MASSIME = 145

# ------------------------------------------------------------------ MODELLO
m = gp.Model("M04_composizione_flotta")

# Variabili decisionali
x = m.addVars(
    TIPI,
    vtype=GRB.INTEGER,
    lb=[LB[i] for i in TIPI],
    ub=[UB[i] for i in TIPI],
    name="x",
)

# Funzione obiettivo: min sum_i COSTO_i x_i
m.setObjective(gp.quicksum(COSTO[i] * x[i] for i in TIPI), GRB.MINIMIZE)

# sum_i VOLUME_i x_i >= 180
m.addConstr(gp.quicksum(VOLUME[i] * x[i] for i in TIPI) >= VOLUME_RICHIESTO, name="volume")

# sum_i PORTATA_i x_i >= 95
m.addConstr(
    gp.quicksum(PORTATA[i] * x[i] for i in TIPI) >= PORTATA_RICHIESTA, name="portata"
)

# sum_i EMISSIONI_i x_i <= 145
m.addConstr(
    gp.quicksum(EMISSIONI[i] * x[i] for i in TIPI) <= EMISSIONI_MASSIME, name="emissioni"
)

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
print("RISULTATO M04 - Composizione di una flotta giornaliera")
print("=" * 70)
print(f"Stato finale Gurobi      : {STATI.get(m.Status, m.Status)} (codice {m.Status})")
print(f"Tempo di esecuzione Gurobi: {m.Runtime:.4f} s")

if m.SolCount > 0:
    print(f"Valore funzione obiettivo : {m.ObjVal:.6g}")
    print()
    print("Decisioni non nulle:")
    for i in TIPI:
        if abs(x[i].X) > 1e-6:
            print(f"    x[{i}] ({NOME[i]}) = {x[i].X:g}   (costo unitario {COSTO[i]})")
    print()
    print("Verifica requisiti:")
    vol = sum(VOLUME[i] * x[i].X for i in TIPI)
    por = sum(PORTATA[i] * x[i].X for i in TIPI)
    emi = sum(EMISSIONI[i] * x[i].X for i in TIPI)
    print(f"    volume offerto   = {vol:g} (richiesto >= {VOLUME_RICHIESTO})")
    print(f"    portata offerta  = {por:g} (richiesta >= {PORTATA_RICHIESTA})")
    print(f"    emissioni totali = {emi:g} (ammesse <= {EMISSIONI_MASSIME})")
    m.write(str(QUI / "M04.sol"))
    print()
    print(f"File soluzione scritto: {QUI / 'M04.sol'}")
else:
    print("Nessuna soluzione disponibile: file .sol non prodotto.")

print("=" * 70)
