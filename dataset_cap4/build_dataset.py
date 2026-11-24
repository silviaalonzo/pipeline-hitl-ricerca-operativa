#!/usr/bin/env python3
"""Costruisce e certifica il dataset sperimentale del Capitolo 4.

Il file genera 20 problemi IP/MILP (10 medi e 10 elevati), li risolve con
HiGHS e produce:

* problems.jsonl: input da somministrare a esperto e LLM;
* ground_truth.json: modello lineare completo e soluzione certificata;
* solutions_summary.csv: riepilogo degli ottimi;
* verify_with_gurobi.py: risolutore/verificatore generico per Gurobi.

Le istanze sono deterministiche e non dipendono da numeri casuali.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import highspy


ROOT = Path(__file__).resolve().parent


@dataclass
class Variable:
    name: str
    vartype: str  # B, I, C
    lb: float = 0.0
    ub: float | None = None
    description: str = ""


@dataclass
class Constraint:
    name: str
    coeffs: Dict[str, float]
    sense: str  # <=, >=, =
    rhs: float
    description: str = ""


@dataclass
class Problem:
    id: str
    pair: int
    title: str
    domain: str
    difficulty: str
    model_class: str
    source: str
    intro: List[str]
    tables: List[dict]
    request: List[str]
    variables: List[Variable]
    objective_sense: str
    objective: Dict[str, float]
    constraints: List[Constraint]
    objective_label: str
    notes: List[str] = field(default_factory=list)
    difficulty_rationale: str = ""


def v(name: str, vartype: str, lb: float = 0, ub: float | None = None, description: str = "") -> Variable:
    return Variable(name, vartype, lb, ub, description)


def c(name: str, coeffs: Dict[str, float], sense: str, rhs: float, description: str = "") -> Constraint:
    coeffs = {k: float(val) for k, val in coeffs.items() if abs(val) > 1e-12}
    return Constraint(name, coeffs, sense, float(rhs), description)


def add_term(coeffs: Dict[str, float], name: str, value: float) -> None:
    coeffs[name] = coeffs.get(name, 0.0) + float(value)


def solve_problem(problem: Problem) -> dict:
    h = highspy.Highs()
    h.silent()
    handles = {}
    for var in problem.variables:
        ub = highspy.kHighsInf if var.ub is None else var.ub
        if var.vartype == "B":
            handles[var.name] = h.addBinary(obj=problem.objective.get(var.name, 0.0), name=var.name)
        elif var.vartype == "I":
            handles[var.name] = h.addIntegral(
                lb=var.lb, ub=ub, obj=problem.objective.get(var.name, 0.0), name=var.name
            )
        elif var.vartype == "C":
            handles[var.name] = h.addVariable(
                lb=var.lb, ub=ub, obj=problem.objective.get(var.name, 0.0), name=var.name
            )
        else:
            raise ValueError(f"Tipo variabile non riconosciuto: {var.vartype}")

    for con in problem.constraints:
        expr = h.expr()
        for name, coef in con.coeffs.items():
            expr += coef * handles[name]
        if con.sense == "<=":
            h.addConstr(expr <= con.rhs, name=con.name)
        elif con.sense == ">=":
            h.addConstr(expr >= con.rhs, name=con.name)
        elif con.sense == "=":
            h.addConstr(expr == con.rhs, name=con.name)
        else:
            raise ValueError(f"Senso non riconosciuto: {con.sense}")

    if problem.objective_sense == "min":
        h.setMinimize()
    else:
        h.setMaximize()
    h.run()
    status = h.modelStatusToString(h.getModelStatus())
    if status != "Optimal":
        raise RuntimeError(f"{problem.id}: soluzione non ottima ({status})")

    values = {name: float(h.val(handle)) for name, handle in handles.items()}
    for var in problem.variables:
        if var.vartype in {"B", "I"}:
            values[var.name] = float(round(values[var.name]))
        elif abs(values[var.name]) < 1e-9:
            values[var.name] = 0.0

    objective = sum(problem.objective.get(name, 0.0) * value for name, value in values.items())
    max_violation = 0.0
    for con in problem.constraints:
        lhs = sum(coef * values[name] for name, coef in con.coeffs.items())
        if con.sense == "<=":
            violation = max(0.0, lhs - con.rhs)
        elif con.sense == ">=":
            violation = max(0.0, con.rhs - lhs)
        else:
            violation = abs(lhs - con.rhs)
        max_violation = max(max_violation, violation)

    return {
        "status": status,
        "objective": round(objective, 6),
        "values": {k: round(val, 6) for k, val in values.items()},
        "nonzero_values": {k: round(val, 6) for k, val in values.items() if abs(val) > 1e-8},
        "max_constraint_violation": max_violation,
    }


def common_request() -> List[str]:
    return [
        "Definire con precisione insiemi, parametri e variabili decisionali.",
        "Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.",
        "Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.",
        "Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.",
    ]


def facility_medium() -> Problem:
    sites = ["A", "B", "C", "D"]
    zones = [f"Z{i}" for i in range(1, 7)]
    fixed = dict(zip(sites, [38, 42, 35, 46]))
    cap = dict(zip(sites, [2, 3, 2, 3]))
    cost_rows = {
        "Z1": [8, 14, 11, 17], "Z2": [10, 9, 13, 15], "Z3": [12, 8, 14, 10],
        "Z4": [15, 11, 9, 7], "Z5": [9, 13, 8, 14], "Z6": [14, 10, 7, 9],
    }
    variables = [v(f"y_{j}", "B", description=f"1 se si apre il centro {j}") for j in sites]
    variables += [v(f"x_{i}_{j}", "B", description=f"1 se {i} è assegnata a {j}") for i in zones for j in sites]
    obj = {f"y_{j}": fixed[j] for j in sites}
    for i in zones:
        for j, val in zip(sites, cost_rows[i]):
            obj[f"x_{i}_{j}"] = val
    cons = []
    for i in zones:
        cons.append(c(f"assegna_{i}", {f"x_{i}_{j}": 1 for j in sites}, "=", 1))
        for j in sites:
            cons.append(c(f"link_{i}_{j}", {f"x_{i}_{j}": 1, f"y_{j}": -1}, "<=", 0))
    for j in sites:
        coeff = {f"x_{i}_{j}": 1 for i in zones}; coeff[f"y_{j}"] = -cap[j]
        cons.append(c(f"cap_{j}", coeff, "<=", 0))
    cons.append(c("due_centri", {f"y_{j}": 1 for j in sites}, "=", 2))
    return Problem(
        "M01", 1, "Localizzazione di centri di assistenza", "Localizzazione e assegnazione",
        "Media", "IP binaria", "Istanza sintetica controllata",
        [
            "Un’impresa deve servire sei zone commerciali aprendo esattamente due centri di assistenza tra quattro siti candidati. Ogni zona deve essere assegnata a un solo centro aperto.",
            "I costi fissi e i costi di servizio sono espressi in migliaia di euro. La capacità indica il numero massimo di zone assegnabili al sito.",
        ],
        [
            {"title": "Siti candidati", "headers": ["Sito", "Costo fisso", "Capacità (zone)"], "rows": [[j, fixed[j], cap[j]] for j in sites]},
            {"title": "Costo di assegnazione", "headers": ["Zona"] + sites, "rows": [[i] + cost_rows[i] for i in zones]},
        ], common_request(), variables, "min", obj, cons, "Costo totale (migliaia di euro)",
        difficulty_rationale="Decisioni binarie di apertura e assegnazione, capacità e collegamento logico; 28 variabili binarie.")


def facility_high() -> Problem:
    sites = ["A", "B", "C", "D", "E", "F"]
    zones = [f"Z{i}" for i in range(1, 9)]
    demand = dict(zip(zones, [30, 25, 35, 20, 28, 32, 24, 26]))
    fixed = dict(zip(sites, [110, 95, 120, 90, 105, 100]))
    cap = dict(zip(sites, [90, 80, 110, 75, 95, 85]))
    costs = {
        "Z1": [4, 7, 6, 10, 9, 11], "Z2": [5, 4, 8, 9, 7, 10],
        "Z3": [7, 5, 4, 8, 9, 7], "Z4": [9, 8, 7, 4, 5, 6],
        "Z5": [8, 9, 6, 5, 4, 7], "Z6": [10, 8, 7, 6, 5, 4],
        "Z7": [6, 7, 5, 8, 6, 7], "Z8": [7, 6, 8, 5, 7, 4],
    }
    emissions = {
        "Z1": [1, 2, 2, 4, 3, 4], "Z2": [2, 1, 3, 3, 2, 4],
        "Z3": [3, 2, 1, 3, 4, 3], "Z4": [4, 3, 3, 1, 2, 2],
        "Z5": [3, 4, 2, 2, 1, 3], "Z6": [4, 3, 3, 2, 2, 1],
        "Z7": [2, 3, 1, 3, 2, 3], "Z8": [3, 2, 3, 1, 3, 1],
    }
    variables = [v(f"y_{j}", "B") for j in sites]
    variables += [v(f"x_{i}_{j}", "C", 0, demand[i]) for i in zones for j in sites]
    obj = {f"y_{j}": fixed[j] for j in sites}
    for i in zones:
        for j, val in zip(sites, costs[i]): obj[f"x_{i}_{j}"] = val
    cons = []
    for i in zones:
        cons.append(c(f"domanda_{i}", {f"x_{i}_{j}": 1 for j in sites}, "=", demand[i]))
    for j in sites:
        coeff = {f"x_{i}_{j}": 1 for i in zones}; coeff[f"y_{j}"] = -cap[j]
        cons.append(c(f"capacita_{j}", coeff, "<=", 0))
        coeff2 = {f"x_{i}_{j}": 1 for i in zones}; coeff2[f"y_{j}"] = -20
        cons.append(c(f"minimo_{j}", coeff2, ">=", 0))
    cons += [
        c("min_centri", {f"y_{j}": 1 for j in sites}, ">=", 3),
        c("max_centri", {f"y_{j}": 1 for j in sites}, "<=", 4),
        c("presidio_nord", {f"y_{j}": 1 for j in ["A", "B", "C"]}, ">=", 1),
        c("presidio_sud", {f"y_{j}": 1 for j in ["D", "E", "F"]}, ">=", 1),
    ]
    eco = {}
    for i in zones:
        for j, val in zip(sites, emissions[i]): eco[f"x_{i}_{j}"] = val
    cons.append(c("emissioni", eco, "<=", 470))
    return Problem(
        "H01", 1, "Rete capacitada di centri distributivi", "Localizzazione e distribuzione",
        "Elevata", "MILP", "Istanza sintetica controllata",
        [
            "Un’azienda deve soddisfare integralmente la domanda di otto zone aprendo da tre a quattro centri tra sei siti candidati. La domanda di una zona può essere ripartita tra più centri.",
            "Ogni centro aperto deve movimentare almeno 20 unità e non può superare la propria capacità. Per resilienza deve essere aperto almeno un sito nel gruppo Nord (A–C) e almeno uno nel gruppo Sud (D–F).",
            "Il costo è dato dai costi fissi più il costo unitario di distribuzione. Le emissioni complessive, calcolate mediante i coefficienti della seconda matrice, non possono superare 470 unità.",
        ],
        [
            {"title": "Domanda", "headers": ["Zona"] + zones, "rows": [["Unità"] + [demand[i] for i in zones]]},
            {"title": "Siti", "headers": ["Sito", "Costo fisso", "Capacità"], "rows": [[j, fixed[j], cap[j]] for j in sites]},
            {"title": "Costi unitari", "headers": ["Zona"] + sites, "rows": [[i] + costs[i] for i in zones]},
            {"title": "Coefficienti di emissione", "headers": ["Zona"] + sites, "rows": [[i] + emissions[i] for i in zones]},
        ], common_request(), variables, "min", obj, cons, "Costo totale",
        difficulty_rationale="Localizzazione binaria e flussi continui, soglie minime, vincoli geografici ed emissioni; 54 variabili e relazioni dense.")


def production_medium() -> Problem:
    products = ["A", "B", "C", "D"]
    profit = dict(zip(products, [42, 36, 50, 31])); setup = dict(zip(products, [80, 65, 90, 50]))
    machine = dict(zip(products, [3, 2, 4, 1])); labor = dict(zip(products, [2, 3, 2, 2]))
    minb = dict(zip(products, [4, 5, 3, 6])); maxd = dict(zip(products, [20, 25, 16, 30]))
    variables = [v(f"x_{p}", "I", 0, maxd[p]) for p in products] + [v(f"y_{p}", "B") for p in products]
    obj = {f"x_{p}": profit[p] for p in products} | {f"y_{p}": -setup[p] for p in products}
    cons = [
        c("ore_macchina", {f"x_{p}": machine[p] for p in products}, "<=", 90),
        c("ore_lavoro", {f"x_{p}": labor[p] for p in products}, "<=", 100),
        c("almeno_due", {f"y_{p}": 1 for p in products}, ">=", 2),
    ]
    for p in products:
        cons.append(c(f"max_{p}", {f"x_{p}": 1, f"y_{p}": -maxd[p]}, "<=", 0))
        cons.append(c(f"min_{p}", {f"x_{p}": 1, f"y_{p}": -minb[p]}, ">=", 0))
    return Problem(
        "M02", 2, "Piano di produzione con costi di setup", "Produzione",
        "Media", "MILP intera", "Istanza sintetica controllata",
        [
            "Un’azienda produce quattro articoli in lotti interi. Avviare un articolo comporta un costo fisso di setup; se viene prodotto, occorre rispettare un lotto minimo e la domanda massima.",
            "Sono disponibili 90 ore-macchina e 100 ore di lavoro. Per ragioni commerciali devono essere prodotti almeno due articoli diversi. Massimizzare il margine totale al netto dei setup.",
        ],
        [{"title": "Dati di produzione", "headers": ["Prodotto", "Margine/unità", "Setup", "Ore macchina", "Ore lavoro", "Lotto min.", "Domanda max"],
          "rows": [[p, profit[p], setup[p], machine[p], labor[p], minb[p], maxd[p]] for p in products]}],
        common_request(), variables, "max", obj, cons, "Margine netto",
        difficulty_rationale="Quantità intere collegate a variabili binarie di setup, due risorse condivise e lotti minimi.")


def production_high() -> Problem:
    products = ["A", "B", "C"]; periods = [1, 2, 3, 4]
    demand = {"A": [8, 12, 10, 14], "B": [10, 8, 14, 12], "C": [6, 9, 7, 11]}
    initial = {"A": 0, "B": 0, "C": 6}
    prod_cost = {"A": [9, 11, 10, 12], "B": [8, 9, 11, 10], "C": [13, 12, 14, 11]}
    setup = {"A": 45, "B": 40, "C": 50}; hold = {"A": 2, "B": 3, "C": 2}
    resource = {"A": 2, "B": 3, "C": 4}; cap = [90, 95, 90, 100]; minb = {"A": 4, "B": 4, "C": 3}
    max_prod = {p: [cap[t-1] // resource[p] for t in periods] for p in products}
    variables = []
    for p in products:
        for t in periods:
            variables += [v(f"x_{p}_{t}", "I", 0, max_prod[p][t-1]), v(f"I_{p}_{t}", "I", 0, 20), v(f"y_{p}_{t}", "B")]
    obj = {}
    for p in products:
        for t in periods:
            obj[f"x_{p}_{t}"] = prod_cost[p][t-1]; obj[f"I_{p}_{t}"] = hold[p]; obj[f"y_{p}_{t}"] = setup[p]
    cons = []
    for p in products:
        for t in periods:
            coeff = {f"x_{p}_{t}": 1, f"I_{p}_{t}": -1}
            rhs = demand[p][t-1]
            if t > 1:
                coeff[f"I_{p}_{t-1}"] = 1
            else:
                rhs -= initial[p]
            cons.append(c(f"bilancio_{p}_{t}", coeff, "=", rhs))
            cons.append(c(f"maxprod_{p}_{t}", {f"x_{p}_{t}": 1, f"y_{p}_{t}": -max_prod[p][t-1]}, "<=", 0))
            cons.append(c(f"minlotto_{p}_{t}", {f"x_{p}_{t}": 1, f"y_{p}_{t}": -minb[p]}, ">=", 0))
        cons.append(c(f"finale_{p}", {f"I_{p}_4": 1}, "=", 0))
    for t in periods:
        cons.append(c(f"capacita_{t}", {f"x_{p}_{t}": resource[p] for p in products}, "<=", cap[t-1]))
        cons.append(c(f"setup_{t}", {f"y_{p}_{t}": 1 for p in products}, "<=", 2))
        cons.append(c(f"magazzino_{t}", {f"I_{p}_{t}": 1 for p in products}, "<=", 20))
    return Problem(
        "H02", 2, "Produzione multi-periodo con setup e scorte", "Produzione e scorte",
        "Elevata", "MILP intera", "Istanza sintetica controllata",
        [
            "Un impianto pianifica la produzione di tre articoli per quattro periodi. La domanda deve essere soddisfatta senza arretrati mediante produzione corrente e scorte provenienti dal periodo precedente. Le scorte iniziali sono 0 unità di A, 0 di B e 6 di C.",
            "L’avvio di un articolo in un periodo comporta un setup. Si possono attivare al massimo due articoli per periodo, la scorta totale non può superare 20 unità e tutte le scorte finali devono essere nulle.",
            "La capacità è espressa in ore. Produzione e scorte sono quantità intere. Minimizzare costi di produzione, setup e mantenimento.",
        ],
        [
            {"title": "Domande per periodo", "headers": ["Prodotto", "T1", "T2", "T3", "T4"], "rows": [[p] + demand[p] for p in products]},
            {"title": "Costi unitari di produzione", "headers": ["Prodotto", "T1", "T2", "T3", "T4"], "rows": [[p] + prod_cost[p] for p in products]},
            {"title": "Parametri per prodotto", "headers": ["Prodotto", "Setup", "Holding", "Ore/unità", "Lotto min."], "rows": [[p, setup[p], hold[p], resource[p], minb[p]] for p in products]},
            {"title": "Capacità", "headers": ["Periodo", "T1", "T2", "T3", "T4"], "rows": [["Ore"] + cap]},
        ], common_request(), variables, "min", obj, cons, "Costo totale",
        difficulty_rationale="36 variabili intere/binarie, bilanci intertemporali, setup condivisi, capacità e magazzino multi-periodo.")


def workforce_medium() -> Problem:
    workers = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
    shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]
    costs = {
        "Ana": [8, 7, 9, 8, 15, 15], "Bruno": [7, 8, 8, 9, 15, 15],
        "Carla": [9, 9, 8, 8, 11, 12], "Diego": [10, 9, 9, 8, 10, 11],
        "Elena": [8, 10, 9, 9, 12, 10], "Fabio": [9, 8, 10, 7, 15, 15],
    }
    unavailable = {("Ana", "N1"), ("Ana", "N2"), ("Bruno", "N1"), ("Bruno", "N2"), ("Fabio", "N1"), ("Fabio", "N2"), ("Carla", "M1"), ("Diego", "M2")}
    variables = [v(f"x_{w}_{s}", "B") for w in workers for s in shifts]
    obj = {f"x_{w}_{s}": costs[w][shifts.index(s)] for w in workers for s in shifts}
    cons = []
    for s in shifts: cons.append(c(f"copertura_{s}", {f"x_{w}_{s}": 1 for w in workers}, "=", 1))
    for w in workers:
        cons.append(c(f"carico_{w}", {f"x_{w}_{s}": 1 for s in shifts}, "<=", 2))
        cons.append(c(f"notti_{w}", {f"x_{w}_{s}": 1 for s in ["N1", "N2"]}, "<=", 1))
    for w, s in unavailable: cons.append(c(f"indisp_{w}_{s}", {f"x_{w}_{s}": 1}, "=", 0))
    return Problem(
        "M03", 3, "Assegnazione del personale ai turni", "Workforce scheduling",
        "Media", "IP binaria", "Istanza sintetica controllata",
        [
            "Un centro operativo deve coprire sei turni con sei dipendenti. Ogni turno richiede esattamente una persona; ogni dipendente può lavorare al massimo due turni e non più di un turno notturno.",
            "Le celle indicate con “—” rappresentano indisponibilità. Minimizzare il costo complessivo dei turni.",
        ],
        [{"title": "Costi e disponibilità", "headers": ["Dipendente"] + shifts,
          "rows": [[w] + [("—" if (w, s) in unavailable else costs[w][shifts.index(s)]) for s in shifts] for w in workers]}],
        common_request(), variables, "min", obj, cons, "Costo dei turni",
        difficulty_rationale="36 variabili binarie, copertura esatta, indisponibilità e limiti individuali su carico e notti.")


def workforce_high() -> Problem:
    employees = [f"E{i}" for i in range(1, 9)]; days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    demand = dict(zip(days, [4, 3, 4, 4, 5, 3, 3])); seniors = {"E1", "E2", "E3"}
    costs = {
        "E1": [9, 9, 10, 9, 11, 14, 15], "E2": [10, 9, 9, 10, 10, 13, 14],
        "E3": [9, 10, 9, 9, 12, 12, 13], "E4": [7, 8, 7, 8, 8, 11, 11],
        "E5": [8, 7, 8, 7, 9, 10, 12], "E6": [7, 8, 8, 7, 8, 12, 10],
        "E7": [8, 8, 7, 9, 7, 11, 10], "E8": [9, 7, 8, 8, 7, 10, 11],
    }
    unavailable = {("E1", "Dom"), ("E2", "Sab"), ("E4", "Mar"), ("E5", "Gio"), ("E6", "Lun"), ("E7", "Dom")}
    variables = [v(f"x_{e}_{d}", "B") for e in employees for d in days]
    obj = {f"x_{e}_{d}": costs[e][days.index(d)] for e in employees for d in days}
    cons = []
    for d in days:
        cons.append(c(f"domanda_{d}", {f"x_{e}_{d}": 1 for e in employees}, ">=", demand[d]))
        cons.append(c(f"senior_{d}", {f"x_{e}_{d}": 1 for e in seniors}, ">=", 1))
    for e in employees:
        cons.append(c(f"min_giorni_{e}", {f"x_{e}_{d}": 1 for d in days}, ">=", 3))
        cons.append(c(f"max_giorni_{e}", {f"x_{e}_{d}": 1 for d in days}, "<=", 5))
        for start in range(4):
            cons.append(c(f"consecutivi_{e}_{start}", {f"x_{e}_{days[k]}": 1 for k in range(start, start+4)}, "<=", 3))
    for e, d in unavailable: cons.append(c(f"indisp_{e}_{d}", {f"x_{e}_{d}": 1}, "=", 0))
    cons += [
        c("specialista_gio", {"x_E7_Gio": 1, "x_E8_Gio": 1}, ">=", 1),
        c("specialista_ven", {"x_E7_Ven": 1, "x_E8_Ven": 1}, ">=", 1),
        c("weekend_E1", {"x_E1_Sab": 1, "x_E1_Dom": 1}, "<=", 1),
        c("weekend_E2", {"x_E2_Sab": 1, "x_E2_Dom": 1}, "<=", 1),
    ]
    return Problem(
        "H03", 3, "Turnazione settimanale con competenze e riposi", "Workforce scheduling",
        "Elevata", "IP binaria", "Istanza sintetica controllata",
        [
            "Un servizio deve pianificare otto dipendenti su sette giorni. Ogni giorno deve essere coperta almeno la domanda indicata e deve essere presente almeno un senior tra E1, E2 ed E3.",
            "Ogni dipendente lavora da tre a cinque giorni e non può lavorare quattro giorni consecutivi. E7 ed E8 sono specialisti: almeno uno deve essere presente giovedì e venerdì. E1 ed E2 possono lavorare al massimo uno dei due giorni del fine settimana.",
            "Le indisponibilità sono indicate con “—”. Minimizzare il costo del piano settimanale.",
        ],
        [
            {"title": "Domanda giornaliera", "headers": ["Giorno"] + days, "rows": [["Addetti"] + [demand[d] for d in days]]},
            {"title": "Costi e disponibilità", "headers": ["Dipendente"] + days,
             "rows": [[e] + [("—" if (e, d) in unavailable else costs[e][days.index(d)]) for d in days] for e in employees]},
        ], common_request(), variables, "min", obj, cons, "Costo settimanale",
        difficulty_rationale="56 variabili binarie, coperture, competenze, indisponibilità e vincoli mobili sui giorni consecutivi.")


def fleet_medium() -> Problem:
    types = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]
    volume = dict(zip(types, [18, 30, 20, 16, 42])); weight = dict(zip(types, [8, 18, 10, 7, 28]))
    cost = dict(zip(types, [120, 180, 210, 150, 260])); avail = dict(zip(types, [8, 6, 4, 5, 3])); emission = dict(zip(types, [12, 22, 15, 4, 32]))
    variables = [v(f"x_{k}", "I", 0, avail[k]) for k in types]
    obj = {f"x_{k}": cost[k] for k in types}
    cons = [
        c("volume", {f"x_{k}": volume[k] for k in types}, ">=", 180),
        c("peso", {f"x_{k}": weight[k] for k in types}, ">=", 95),
        c("emissioni", {f"x_{k}": emission[k] for k in types}, "<=", 145),
        c("refrigerato", {"x_Refrigerato": 1}, ">=", 1),
        c("elettrico", {"x_Elettrico": 1}, ">=", 1),
        c("max_mezzi", {f"x_{k}": 1 for k in types}, "<=", 10),
    ]
    return Problem(
        "M04", 4, "Composizione di una flotta giornaliera", "Trasporto",
        "Media", "IP intera", "Istanza sintetica controllata",
        [
            "Un operatore deve scegliere quanti veicoli di ciascun tipo impiegare in una giornata. La flotta deve offrire almeno 180 unità di volume e 95 unità di portata, utilizzando almeno un mezzo refrigerato e un mezzo elettrico.",
            "Le emissioni complessive non possono superare 145 unità. Minimizzare il costo giornaliero.",
        ],
        [{"title": "Caratteristiche dei veicoli", "headers": ["Tipo", "Volume", "Portata", "Costo", "Emissioni", "Disponibilità"],
          "rows": [[k, volume[k], weight[k], cost[k], emission[k], avail[k]] for k in types]}],
        common_request(), variables, "min", obj, cons, "Costo giornaliero",
        difficulty_rationale="Cinque variabili intere con requisiti multidimensionali, disponibilità, emissioni, limite di flotta e obblighi tecnologici.")


def fleet_high() -> Problem:
    routes = ["R1", "R2", "R3", "R4"]; types = ["Piccolo", "Medio", "Grande"]
    demand = dict(zip(routes, [42, 55, 38, 64])); capacity = dict(zip(types, [8, 14, 20]))
    fleet = dict(zip(types, [10, 9, 6])); emissions = dict(zip(types, [5, 8, 11]))
    costs = {"R1": [45, 62, 82], "R2": [52, 68, 88], "R3": [40, 58, 79], "R4": [60, 77, 96]}
    variables = [v(f"x_{r}_{k}", "I", 0, fleet[k]) for r in routes for k in types]
    variables += [v(f"y_{r}_{k}", "B") for r in routes for k in types]
    obj = {f"x_{r}_{k}": costs[r][types.index(k)] for r in routes for k in types}
    cons = []
    for r in routes:
        cons.append(c(f"domanda_{r}", {f"x_{r}_{k}": capacity[k] for k in types}, ">=", demand[r]))
        cons.append(c(f"max_tipi_{r}", {f"y_{r}_{k}": 1 for k in types}, "<=", 2))
        for k in types:
            cons.append(c(f"linkmax_{r}_{k}", {f"x_{r}_{k}": 1, f"y_{r}_{k}": -fleet[k]}, "<=", 0))
            cons.append(c(f"linkmin_{r}_{k}", {f"x_{r}_{k}": 1, f"y_{r}_{k}": -1}, ">=", 0))
    for k in types: cons.append(c(f"flotta_{k}", {f"x_{r}_{k}": 1 for r in routes}, "<=", fleet[k]))
    cons += [
        c("grande_R4", {"x_R4_Grande": 1}, ">=", 1),
        c("emissioni", {f"x_{r}_{k}": emissions[k] for r in routes for k in types}, "<=", 145),
    ]
    return Problem(
        "H04", 4, "Allocazione della flotta su più rotte", "Trasporto",
        "Elevata", "MILP intera", "Istanza sintetica controllata",
        [
            "Un’impresa deve assegnare viaggi di tre tipi di veicolo a quattro rotte. La capacità complessiva assegnata a ogni rotta deve coprirne la domanda. La disponibilità di ciascun tipo è condivisa tra tutte le rotte.",
            "Per contenere la complessità operativa, su ogni rotta possono essere usati al massimo due tipi di veicolo. Sulla rotta R4 deve essere impiegato almeno un veicolo grande. Le emissioni totali non possono superare 145 unità.",
            "Minimizzare il costo totale dei viaggi.",
        ],
        [
            {"title": "Domanda per rotta", "headers": ["Rotta"] + routes, "rows": [["Domanda"] + [demand[r] for r in routes]]},
            {"title": "Flotta", "headers": ["Tipo", "Capacità/viaggio", "Disponibilità", "Emissioni/viaggio"], "rows": [[k, capacity[k], fleet[k], emissions[k]] for k in types]},
            {"title": "Costo di un viaggio", "headers": ["Rotta"] + types, "rows": [[r] + costs[r] for r in routes]},
        ], common_request(), variables, "min", obj, cons, "Costo totale",
        difficulty_rationale="Viaggi interi e attivazioni binarie su quattro rotte, flotta condivisa, emissioni e vincoli logici per rotta.")


def portfolio_medium() -> Problem:
    projects = [f"P{i}" for i in range(1, 9)]
    value = dict(zip(projects, [30, 24, 35, 28, 33, 26, 38, 21])); budget = dict(zip(projects, [20, 18, 27, 24, 22, 19, 30, 15]))
    staff = dict(zip(projects, [4, 3, 5, 4, 4, 3, 5, 2]))
    variables = [v(f"x_{p}", "B") for p in projects]
    obj = {f"x_{p}": value[p] for p in projects}
    cons = [
        c("budget", {f"x_{p}": budget[p] for p in projects}, "<=", 100),
        c("personale", {f"x_{p}": staff[p] for p in projects}, "<=", 18),
        c("dipendenza_P5", {"x_P5": 1, "x_P2": -1}, "<=", 0),
        c("dipendenza_P7", {"x_P7": 1, "x_P3": -1}, "<=", 0),
        c("esclusione", {"x_P4": 1, "x_P6": 1}, "<=", 1),
        c("digitale", {"x_P1": 1, "x_P3": 1, "x_P7": 1}, ">=", 1),
        c("min_progetti", {f"x_{p}": 1 for p in projects}, ">=", 3),
    ]
    return Problem(
        "M05", 5, "Selezione di un portafoglio progetti", "Project portfolio",
        "Media", "IP binaria", "Istanza sintetica controllata",
        [
            "Un’impresa deve selezionare un portafoglio tra otto progetti, massimizzandone il valore complessivo entro un budget di 100 e 18 unità di personale.",
            "P5 richiede P2; P7 richiede P3; P4 e P6 sono incompatibili. Deve essere scelto almeno un progetto digitale tra P1, P3 e P7 e almeno tre progetti complessivi.",
        ],
        [{"title": "Progetti", "headers": ["Progetto", "Valore", "Budget", "Personale"], "rows": [[p, value[p], budget[p], staff[p]] for p in projects]}],
        common_request(), variables, "max", obj, cons, "Valore del portafoglio",
        difficulty_rationale="Otto scelte binarie con due risorse, dipendenze, incompatibilità e requisiti di composizione.")


def portfolio_high() -> Problem:
    projects = list("ABCDEFGHIJKL")
    npv = dict(zip(projects, [42, 35, 48, 31, 40, 28, 55, 37, 33, 50, 46, 29]))
    c1 = dict(zip(projects, [18, 20, 25, 15, 22, 14, 30, 20, 17, 27, 24, 16]))
    c2 = dict(zip(projects, [12, 18, 20, 14, 16, 12, 25, 18, 15, 21, 19, 13]))
    c3 = dict(zip(projects, [10, 14, 18, 12, 15, 10, 22, 16, 12, 18, 17, 11]))
    staff = dict(zip(projects, [4, 4, 5, 3, 4, 3, 6, 4, 3, 5, 5, 3]))
    risk = dict(zip(projects, [5, 4, 6, 3, 4, 2, 7, 5, 3, 6, 5, 3]))
    variables = [v(f"x_{p}", "B") for p in projects] + [v("z_AC", "B"), v("z_EK", "B")]
    obj = {f"x_{p}": npv[p] for p in projects} | {"z_AC": 12, "z_EK": 10}
    cons = [
        c("budget1", {f"x_{p}": c1[p] for p in projects}, "<=", 110),
        c("budget2", {f"x_{p}": c2[p] for p in projects}, "<=", 100),
        c("budget3", {f"x_{p}": c3[p] for p in projects}, "<=", 90),
        c("personale", {f"x_{p}": staff[p] for p in projects}, "<=", 28),
        c("rischio", {f"x_{p}": risk[p] for p in projects}, "<=", 32),
        c("dep_G_B", {"x_G": 1, "x_B": -1}, "<=", 0),
        c("dep_J_E", {"x_J": 1, "x_E": -1}, "<=", 0),
        c("dep_K_C", {"x_K": 1, "x_C": -1}, "<=", 0),
        c("ex_D_H", {"x_D": 1, "x_H": 1}, "<=", 1),
        c("ex_F_L", {"x_F": 1, "x_L": 1}, "<=", 1),
        c("digitale", {f"x_{p}": 1 for p in ["A", "C", "G", "J"]}, ">=", 2),
        c("sostenibile", {f"x_{p}": 1 for p in ["E", "H", "K"]}, ">=", 1),
        c("max_progetti", {f"x_{p}": 1 for p in projects}, "<=", 8),
        c("zac1", {"z_AC": 1, "x_A": -1}, "<=", 0), c("zac2", {"z_AC": 1, "x_C": -1}, "<=", 0),
        c("zac3", {"z_AC": 1, "x_A": -1, "x_C": -1}, ">=", -1),
        c("zek1", {"z_EK": 1, "x_E": -1}, "<=", 0), c("zek2", {"z_EK": 1, "x_K": -1}, "<=", 0),
        c("zek3", {"z_EK": 1, "x_E": -1, "x_K": -1}, ">=", -1),
    ]
    return Problem(
        "H05", 5, "Portafoglio pluriennale con sinergie", "Project portfolio",
        "Elevata", "IP binaria", "Istanza sintetica controllata",
        [
            "Un’impresa seleziona progetti su un orizzonte triennale. Deve massimizzare il VAN complessivo rispettando budget annuali pari a 110, 100 e 90, un limite di 28 unità di personale e un rischio complessivo non superiore a 32.",
            "G richiede B, J richiede E e K richiede C. Le coppie D–H e F–L sono incompatibili. Servono almeno due progetti digitali tra A, C, G e J e almeno un progetto sostenibile tra E, H e K; si possono scegliere al massimo otto progetti.",
            "Se A e C sono entrambi scelti si ottiene una sinergia di 12; se E e K sono entrambi scelti la sinergia è 10. Le sinergie devono essere modellate esplicitamente.",
        ],
        [{"title": "Dati dei progetti", "headers": ["Prog.", "VAN", "Costo A1", "Costo A2", "Costo A3", "Personale", "Rischio"],
          "rows": [[p, npv[p], c1[p], c2[p], c3[p], staff[p], risk[p]] for p in projects]}],
        common_request(), variables, "max", obj, cons, "VAN comprensivo delle sinergie",
        difficulty_rationale="Portafoglio binario con tre budget, rischio, dipendenze, esclusioni e linearizzazione di due sinergie.")


def scheduling_medium() -> Problem:
    jobs = [f"J{i}" for i in range(1, 8)]; machines = ["A", "B"]
    times = {"J1": [7, 9], "J2": [6, 5], "J3": [8, 7], "J4": [5, 8], "J5": [9, 6], "J6": [4, 7], "J7": [99, 5]}
    variables = [v(f"x_{j}_{m}", "B") for j in jobs for m in machines] + [v("Cmax", "I", 0, 100)]
    obj = {"Cmax": 1}
    cons = []
    for j in jobs:
        cons.append(c(f"assegna_{j}", {f"x_{j}_{m}": 1 for m in machines}, "=", 1))
    for m in machines:
        coeff = {f"x_{j}_{m}": times[j][machines.index(m)] for j in jobs}; coeff["Cmax"] = -1
        cons.append(c(f"carico_{m}", coeff, "<=", 0))
    cons.append(c("compat_J7", {"x_J7_A": 1}, "=", 0))
    return Problem(
        "M06", 6, "Bilanciamento di lavori su due macchine", "Scheduling",
        "Media", "MILP intera", "Istanza sintetica controllata",
        [
            "Sette lavori indipendenti devono essere assegnati a due macchine parallele. Ogni lavoro va eseguito interamente su una sola macchina; i tempi dipendono dalla macchina scelta.",
            "J7 non è compatibile con la macchina A. Tutti i lavori sono disponibili all’inizio e ogni macchina esegue i lavori assegnati in sequenza. Minimizzare il makespan, cioè il maggiore tra i carichi delle due macchine.",
        ],
        [{"title": "Tempi di lavorazione", "headers": ["Lavoro", "Macchina A", "Macchina B"],
          "rows": [[j, ("—" if j == "J7" else times[j][0]), times[j][1]] for j in jobs]}],
        common_request(), variables, "min", obj, cons, "Makespan",
        notes=["Sono ammesse più assegnazioni ottime con lo stesso makespan."],
        difficulty_rationale="Assegnazione binaria con tempi dipendenti dalla macchina e minimizzazione del massimo carico.")


def scheduling_high() -> Problem:
    jobs = [f"J{i}" for i in range(1, 8)]
    p = dict(zip(jobs, [5, 7, 4, 6, 3, 8, 5])); due = dict(zip(jobs, [9, 17, 12, 22, 15, 28, 25]))
    release = dict(zip(jobs, [0, 0, 2, 3, 5, 0, 6])); weight = dict(zip(jobs, [4, 3, 5, 2, 6, 2, 4]))
    horizon = sum(p.values()) + max(release.values())
    variables = []
    for j in jobs: variables += [v(f"S_{j}", "I", release[j], horizon), v(f"C_{j}", "I", 0, horizon+10), v(f"T_{j}", "I", 0, horizon+10)]
    pairs = [(jobs[i], jobs[k]) for i in range(len(jobs)) for k in range(i+1, len(jobs))]
    variables += [v(f"o_{i}_{j}", "B") for i, j in pairs]
    obj = {f"T_{j}": weight[j] for j in jobs}
    cons = []
    for j in jobs:
        cons.append(c(f"completion_{j}", {f"C_{j}": 1, f"S_{j}": -1}, "=", p[j]))
        cons.append(c(f"tardiness_{j}", {f"T_{j}": 1, f"C_{j}": -1}, ">=", -due[j]))
    for i, j in pairs:
        o = f"o_{i}_{j}"
        cons.append(c(f"ordine1_{i}_{j}", {f"S_{j}": 1, f"S_{i}": -1, o: -horizon}, ">=", p[i]-horizon))
        cons.append(c(f"ordine2_{i}_{j}", {f"S_{i}": 1, f"S_{j}": -1, o: horizon}, ">=", p[j]))
    cons += [
        c("precedenza_J1_J2", {"S_J2": 1, "C_J1": -1}, ">=", 0),
        c("precedenza_J3_J5", {"S_J5": 1, "C_J3": -1}, ">=", 0),
    ]
    return Problem(
        "H06", 6, "Sequenziamento con ritardi pesati", "Scheduling",
        "Elevata", "MILP intera", "Istanza sintetica controllata",
        [
            "Sette lavori devono essere sequenziati senza sovrapposizioni su una sola macchina. Ogni lavoro ha durata, data di disponibilità, scadenza e peso di priorità.",
            "J1 deve terminare prima dell’inizio di J2; J3 deve terminare prima dell’inizio di J5. Il ritardo di un lavoro è max(0, completamento − scadenza).",
            "Minimizzare la somma dei ritardi moltiplicati per i rispettivi pesi. Modellare la non sovrapposizione mediante variabili binarie di ordinamento e una costante big-M giustificata.",
        ],
        [{"title": "Dati dei lavori", "headers": ["Lavoro", "Durata", "Disponibilità", "Scadenza", "Peso"],
          "rows": [[j, p[j], release[j], due[j], weight[j]] for j in jobs]}],
        common_request(), variables, "min", obj, cons, "Ritardo pesato totale",
        difficulty_rationale="21 variabili di ordinamento, tempi interi, disgiunzioni big-M, release date, scadenze e precedenze.")


def suppliers_medium() -> Problem:
    suppliers = ["A", "B", "C", "D"]
    unit = dict(zip(suppliers, [11, 10, 12, 9])); fixed = dict(zip(suppliers, [80, 95, 60, 120]))
    cap = dict(zip(suppliers, [80, 100, 70, 90])); minimum = dict(zip(suppliers, [20, 25, 15, 20]))
    quality = dict(zip(suppliers, [96, 90, 98, 88])); emission = dict(zip(suppliers, [3, 4, 2, 5]))
    variables = [v(f"x_{s}", "I", 0, cap[s]) for s in suppliers] + [v(f"y_{s}", "B") for s in suppliers]
    obj = {f"x_{s}": unit[s] for s in suppliers} | {f"y_{s}": fixed[s] for s in suppliers}
    cons = [
        c("domanda", {f"x_{s}": 1 for s in suppliers}, "=", 180),
        c("qualita", {f"x_{s}": quality[s] - 92 for s in suppliers}, ">=", 0),
        c("emissioni", {f"x_{s}": emission[s] for s in suppliers}, "<=", 650),
        c("almeno_due", {f"y_{s}": 1 for s in suppliers}, ">=", 2),
    ]
    for s in suppliers:
        cons.append(c(f"max_{s}", {f"x_{s}": 1, f"y_{s}": -cap[s]}, "<=", 0))
        cons.append(c(f"min_{s}", {f"x_{s}": 1, f"y_{s}": -minimum[s]}, ">=", 0))
    return Problem(
        "M07", 7, "Selezione dei fornitori con qualità minima", "Procurement",
        "Media", "MILP intera", "Istanza sintetica controllata",
        [
            "Un’impresa deve acquistare esattamente 180 unità da almeno due fornitori. Attivare un fornitore comporta un costo fisso e, se attivato, richiede un ordine minimo.",
            "La qualità media ponderata deve essere almeno 92 e le emissioni totali non possono superare 650. Minimizzare costi variabili e fissi.",
        ],
        [{"title": "Fornitori", "headers": ["Fornitore", "Costo/unità", "Costo fisso", "Capacità", "Ordine min.", "Qualità", "Emissioni/unità"],
          "rows": [[s, unit[s], fixed[s], cap[s], minimum[s], quality[s], emission[s]] for s in suppliers]}],
        common_request(), variables, "min", obj, cons, "Costo di approvvigionamento",
        difficulty_rationale="Quantità intere, attivazioni binarie, qualità media, emissioni, capacità e ordini minimi.")


def suppliers_high() -> Problem:
    suppliers = list("ABCDEF"); comps = ["C1", "C2", "C3"]
    demand = {"C1": 80, "C2": 70, "C3": 60}; total_cap = dict(zip(suppliers, [100, 110, 90, 120, 80, 95]))
    fixed = dict(zip(suppliers, [120, 140, 100, 150, 90, 110]))
    costs = {"A": [9, 12, 11], "B": [10, 9, 12], "C": [11, 10, 9], "D": [8, 11, 10], "E": [12, 8, 11], "F": [10, 12, 8]}
    quality = {"A": [96, 94, 95], "B": [93, 97, 92], "C": [98, 95, 96], "D": [91, 94, 93], "E": [97, 98, 94], "F": [94, 92, 98]}
    risk = dict(zip(suppliers, [2, 3, 1, 4, 2, 3])); unavailable = {("D", "C1"), ("E", "C3"), ("F", "C2")}
    variables = [v(f"y_{s}", "B") for s in suppliers]
    variables += [v(f"x_{s}_{k}", "I", 0, demand[k]) for s in suppliers for k in comps]
    variables += [v(f"z_{s}_{k}", "B") for s in suppliers for k in comps]
    obj = {f"y_{s}": fixed[s] for s in suppliers}
    for s in suppliers:
        for k in comps: obj[f"x_{s}_{k}"] = costs[s][comps.index(k)]
    cons = []
    for k in comps:
        cons.append(c(f"domanda_{k}", {f"x_{s}_{k}": 1 for s in suppliers}, "=", demand[k]))
        threshold = {"C1": 95, "C2": 95, "C3": 95}[k]
        cons.append(c(f"qualita_{k}", {f"x_{s}_{k}": quality[s][comps.index(k)]-threshold for s in suppliers}, ">=", 0))
        cons.append(c(f"multisource_{k}", {f"z_{s}_{k}": 1 for s in suppliers}, ">=", 2))
    for s in suppliers:
        coeff = {f"x_{s}_{k}": 1 for k in comps}; coeff[f"y_{s}"] = -total_cap[s]
        cons.append(c(f"capacita_{s}", coeff, "<=", 0))
        cons.append(c(f"uso_{s}", {f"z_{s}_{k}": 1 for k in comps} | {f"y_{s}": -3}, "<=", 0))
        for k in comps:
            cons.append(c(f"zmax_{s}_{k}", {f"x_{s}_{k}": 1, f"z_{s}_{k}": -demand[k]}, "<=", 0))
            cons.append(c(f"zmin_{s}_{k}", {f"x_{s}_{k}": 1, f"z_{s}_{k}": -10}, ">=", 0))
            cons.append(c(f"zy_{s}_{k}", {f"z_{s}_{k}": 1, f"y_{s}": -1}, "<=", 0))
    for s, k in unavailable:
        cons.append(c(f"indisp_{s}_{k}", {f"x_{s}_{k}": 1}, "=", 0)); cons.append(c(f"indispz_{s}_{k}", {f"z_{s}_{k}": 1}, "=", 0))
    cons += [
        c("max_fornitori", {f"y_{s}": 1 for s in suppliers}, "<=", 4),
        c("locale", {"y_A": 1, "y_B": 1}, ">=", 1),
        c("rischio", {f"x_{s}_{k}": risk[s] for s in suppliers for k in comps}, "<=", 580),
    ]
    return Problem(
        "H07", 7, "Sourcing multi-componente con rischio e multisourcing", "Procurement",
        "Elevata", "MILP intera", "Istanza sintetica controllata",
        [
            "Un produttore deve acquistare esattamente 80 unità di C1, 70 di C2 e 60 di C3. Ogni componente deve provenire da almeno due fornitori, con almeno 10 unità per ogni combinazione fornitore–componente utilizzata.",
            "La capacità indicata è complessiva sui tre componenti. La qualità media di ciascun componente deve essere almeno 95. Si possono attivare al massimo quattro fornitori e almeno uno tra A e B. Il rischio totale, pari a quantità per coefficiente del fornitore, non può superare 580.",
            "Le celle “—” indicano componenti non fornibili. Minimizzare costi d’acquisto e attivazione.",
        ],
        [
            {"title": "Fornitori", "headers": ["Fornitore", "Costo fisso", "Capacità totale", "Rischio"], "rows": [[s, fixed[s], total_cap[s], risk[s]] for s in suppliers]},
            {"title": "Costi unitari", "headers": ["Fornitore"] + comps, "rows": [[s] + [("—" if (s,k) in unavailable else costs[s][comps.index(k)]) for k in comps] for s in suppliers]},
            {"title": "Qualità", "headers": ["Fornitore"] + comps, "rows": [[s] + [("—" if (s,k) in unavailable else quality[s][comps.index(k)]) for k in comps] for s in suppliers]},
        ], common_request(), variables, "min", obj, cons, "Costo di sourcing",
        difficulty_rationale="42 variabili intere/binarie, tre qualità medie, multisourcing, capacità condivise, rischio e disponibilità selettive.")


def coverage_medium() -> Problem:
    sites = list("ABCDEFGH"); zones = [f"Z{i}" for i in range(1, 11)]
    cost = dict(zip(sites, [24, 20, 27, 22, 25, 19, 23, 21]))
    coverage = {
        "A": [1,2,3], "B": [2,3,4,5], "C": [1,5,6], "D": [3,6,7],
        "E": [4,7,8], "F": [5,8,9], "G": [6,9,10], "H": [7,8,10],
    }
    variables = [v(f"y_{s}", "B") for s in sites]
    obj = {f"y_{s}": cost[s] for s in sites}
    cons = []
    for znum in range(1,11):
        covering = [s for s in sites if znum in coverage[s]]
        cons.append(c(f"copertura_Z{znum}", {f"y_{s}": 1 for s in covering}, ">=", 2 if znum in {3,7} else 1))
    cons.append(c("max_centri", {f"y_{s}": 1 for s in sites}, "<=", 5))
    return Problem(
        "M08", 8, "Copertura di zone con centri di servizio", "Set covering",
        "Media", "IP binaria", "Istanza sintetica controllata",
        [
            "Un ente deve aprire centri di servizio per coprire dieci zone. Una zona è coperta se almeno uno dei centri indicati nella matrice è aperto.",
            "Le zone Z3 e Z7 sono critiche e richiedono doppia copertura. Possono essere aperti al massimo cinque centri. Minimizzare il costo di apertura.",
        ],
        [
            {"title": "Centri e costi", "headers": ["Centro", "Costo", "Zone coperte"], "rows": [[s, cost[s], ", ".join(f"Z{i}" for i in coverage[s])] for s in sites]},
        ], common_request(), variables, "min", obj, cons, "Costo di apertura",
        difficulty_rationale="Set covering binario con copertura singola/doppia e limite sul numero di centri.")


def coverage_high() -> Problem:
    sites = list("ABCDEFGH"); zones = [f"Z{i}" for i in range(1,13)]
    demand = dict(zip(zones, [8,7,10,6,9,8,7,11,6,9,8,7])); fixed = dict(zip(sites, [35,32,40,30,38,33,36,31]))
    cap = dict(zip(sites, [42,44,46,40,45,43,44,42]))
    reachable = {
        "Z1": ["A","B"], "Z2": ["A","B","C"], "Z3": ["B","C","D"], "Z4": ["C","D"],
        "Z5": ["A","D","E"], "Z6": ["B","E","F"], "Z7": ["C","F","G","H"], "Z8": ["D","G","H"],
        "Z9": ["E","F","H"], "Z10": ["F","G","H"], "Z11": ["A","E","H"], "Z12": ["B","G","H"],
    }
    travel = {}
    for zi,z in enumerate(zones):
        travel[z] = {s: 3 + ((zi*3 + sites.index(s)*2) % 9) for s in reachable[z]}
    variables = [v(f"y_{s}", "B") for s in sites]
    variables += [v(f"x_{z}_{s}", "B") for z in zones for s in reachable[z]]
    obj = {f"y_{s}": fixed[s] for s in sites}
    for z in zones:
        for s in reachable[z]: obj[f"x_{z}_{s}"] = demand[z]*travel[z][s]
    cons = [c("quattro_stazioni", {f"y_{s}": 1 for s in sites}, "=", 4),
            c("ovest", {f"y_{s}": 1 for s in ["A","B","C","D"]}, ">=", 1),
            c("est", {f"y_{s}": 1 for s in ["E","F","G","H"]}, ">=", 1)]
    for z in zones:
        cons.append(c(f"assegna_{z}", {f"x_{z}_{s}": 1 for s in reachable[z]}, "=", 1))
        for s in reachable[z]: cons.append(c(f"link_{z}_{s}", {f"x_{z}_{s}": 1, f"y_{s}": -1}, "<=", 0))
    for s in sites:
        coeff = {f"x_{z}_{s}": demand[z] for z in zones if s in reachable[z]}; coeff[f"y_{s}"] = -cap[s]
        cons.append(c(f"capacita_{s}", coeff, "<=", 0))
    for z in ["Z3","Z8","Z11"]:
        cons.append(c(f"backup_{z}", {f"y_{s}": 1 for s in reachable[z]}, ">=", 2))
    return Problem(
        "H08", 8, "Rete di emergenza capacitada con backup", "Localizzazione e copertura",
        "Elevata", "IP binaria", "Istanza sintetica controllata",
        [
            "Un’amministrazione deve aprire esattamente quattro stazioni di emergenza e assegnare ciascuna delle dodici zone a una stazione raggiungibile. La domanda della zona consuma capacità della stazione assegnata.",
            "Deve essere aperta almeno una stazione nel gruppo Ovest (A–D) e una nel gruppo Est (E–H). Per le zone critiche Z3, Z8 e Z11 devono risultare aperte almeno due stazioni raggiungibili, così da garantire un backup anche se la zona viene assegnata a una sola.",
            "Minimizzare costi fissi più domanda moltiplicata per il tempo di percorrenza.",
        ],
        [
            {"title": "Stazioni", "headers": ["Stazione", "Costo fisso", "Capacità"], "rows": [[s,fixed[s],cap[s]] for s in sites]},
            {"title": "Zone, domanda e tempi delle stazioni raggiungibili", "headers": ["Zona", "Domanda", "Stazioni (tempo)"],
             "rows": [[z,demand[z],", ".join(f"{s} ({travel[z][s]})" for s in reachable[z])] for z in zones]},
        ], common_request(), variables, "min", obj, cons, "Costo totale di rete",
        difficulty_rationale="Localizzazione e assegnazione capacitada, matrice sparsa di raggiungibilità, backup critico e vincoli geografici.")


def inventory_medium() -> Problem:
    periods = list(range(1,7)); demand = [20,30,15,35,25,20]; purchase = [9,8,11,7,10,9]
    setup = [40]*6; cap = [50,50,45,55,45,50]; minq = 10; hold = 2; initial = 10
    variables = []
    for t in periods: variables += [v(f"q_{t}", "I", 0, cap[t-1]), v(f"I_{t}", "I", 0, 60), v(f"y_{t}", "B")]
    obj = {}
    for t in periods: obj[f"q_{t}"] = purchase[t-1]; obj[f"I_{t}"] = hold; obj[f"y_{t}"] = setup[t-1]
    cons = []
    for t in periods:
        coeff = {f"q_{t}": 1, f"I_{t}": -1}
        rhs = demand[t-1]
        if t == 1: rhs -= initial
        else: coeff[f"I_{t-1}"] = 1
        cons.append(c(f"bilancio_{t}", coeff, "=", rhs))
        cons.append(c(f"max_{t}", {f"q_{t}": 1, f"y_{t}": -cap[t-1]}, "<=", 0))
        cons.append(c(f"min_{t}", {f"q_{t}": 1, f"y_{t}": -minq}, ">=", 0))
    cons.append(c("scorta_finale", {"I_6": 1}, ">=", 5))
    return Problem(
        "M09", 9, "Piano di riordino con costi fissi", "Inventory management",
        "Media", "MILP intera", "Istanza sintetica controllata",
        [
            "Un’impresa pianifica gli ordini di un prodotto per sei periodi. La scorta iniziale è 10, non sono ammessi arretrati e la scorta finale deve essere almeno 5.",
            "Un ordine attivato deve essere di almeno 10 unità e non può superare la capacità del periodo. Ogni ordine comporta un costo fisso di 40; il costo di mantenimento è 2 per unità rimasta a fine periodo.",
            "Ordini e scorte sono interi. Minimizzare il costo complessivo.",
        ],
        [{"title": "Dati per periodo", "headers": ["Periodo", "Domanda", "Costo acquisto", "Capacità ordine"],
          "rows": [[t,demand[t-1],purchase[t-1],cap[t-1]] for t in periods]}],
        common_request(), variables, "min", obj, cons, "Costo totale di approvvigionamento",
        difficulty_rationale="Lotti interi e setup binari collegati da bilanci temporali, capacità e scorta finale.")


def inventory_high() -> Problem:
    products = ["A","B","C"]; periods = list(range(1,7))
    demand = {"A":[12,18,14,20,16,19], "B":[10,9,15,12,17,14], "C":[8,11,10,13,9,15]}
    prod_cost = {"A":[7,8,9,7,10,8], "B":[9,8,8,10,7,9], "C":[11,10,12,9,11,8]}
    setup = {"A":35,"B":40,"C":45}; hold={"A":2,"B":2,"C":3}; hours={"A":2,"B":3,"C":4}
    minb={"A":5,"B":4,"C":3}; basecap=[120,115,125,110,120,115]; overtime_cost=18
    variables=[]
    for p in products:
        for t in periods: variables += [v(f"x_{p}_{t}","I",0,50),v(f"I_{p}_{t}","I",0,45),v(f"y_{p}_{t}","B")]
    variables += [v(f"o_{t}","C",0,20) for t in periods]
    obj={}
    for p in products:
        for t in periods:
            obj[f"x_{p}_{t}"]=prod_cost[p][t-1]; obj[f"I_{p}_{t}"]=hold[p]; obj[f"y_{p}_{t}"]=setup[p]
    for t in periods: obj[f"o_{t}"]=overtime_cost
    cons=[]
    for p in products:
        for t in periods:
            coeff={f"x_{p}_{t}":1,f"I_{p}_{t}":-1}
            if t>1: coeff[f"I_{p}_{t-1}"]=1
            cons.append(c(f"bilancio_{p}_{t}",coeff,"=",demand[p][t-1]))
            cons.append(c(f"max_{p}_{t}",{f"x_{p}_{t}":1,f"y_{p}_{t}":-50},"<=",0))
            cons.append(c(f"min_{p}_{t}",{f"x_{p}_{t}":1,f"y_{p}_{t}":-minb[p]},">=",0))
        cons.append(c(f"finale_{p}",{f"I_{p}_6":1},">=",2))
    for t in periods:
        coeff={f"x_{p}_{t}":hours[p] for p in products}; coeff[f"o_{t}"]=-1
        cons.append(c(f"capacita_{t}",coeff,"<=",basecap[t-1]))
        cons.append(c(f"setup_{t}",{f"y_{p}_{t}":1 for p in products},"<=",3 if t == 1 else 2))
        cons.append(c(f"magazzino_{t}",{f"I_{p}_{t}":1 for p in products},"<=",40))
    return Problem(
        "H09",9,"Produzione e scorte multi-prodotto con straordinario","Production-inventory",
        "Elevata","MILP","Istanza sintetica controllata",
        [
            "Un impianto pianifica tre prodotti per sei periodi. La domanda deve essere soddisfatta senza arretrati; le scorte iniziali sono nulle e a fine orizzonte devono restare almeno 2 unità di ciascun prodotto.",
            "Ogni prodotto richiede un setup nel periodo in cui viene prodotto e un lotto minimo. Nel primo periodo possono essere attivati tutti e tre i prodotti; nei periodi successivi se ne possono attivare al massimo due. La capacità base può essere aumentata con al massimo 20 ore di straordinario al costo di 18 per ora.",
            "La scorta totale a fine periodo non può superare 40. Produzione e scorte sono intere; lo straordinario è continuo. Minimizzare tutti i costi.",
        ],
        [
            {"title":"Domanda","headers":["Prodotto"]+[f"T{t}" for t in periods],"rows":[[p]+demand[p] for p in products]},
            {"title":"Costo unitario di produzione","headers":["Prodotto"]+[f"T{t}" for t in periods],"rows":[[p]+prod_cost[p] for p in products]},
            {"title":"Parametri di prodotto","headers":["Prodotto","Setup","Holding","Ore/unità","Lotto min."],"rows":[[p,setup[p],hold[p],hours[p],minb[p]] for p in products]},
            {"title":"Capacità base","headers":["Periodo"]+[f"T{t}" for t in periods],"rows":[["Ore"]+basecap]},
        ],common_request(),variables,"min",obj,cons,"Costo totale",
        difficulty_rationale="60 variabili miste, bilanci su sei periodi, setup condivisi, capacità aumentabile, scorte e vincoli finali.")


def network_medium() -> Problem:
    nodes=["S","A","B","C","T"]
    arcs=[("S","A"),("S","B"),("A","B"),("A","C"),("B","C"),("B","T"),("C","T")]
    fixed=[40,35,15,30,18,45,38]; unit=[2,3,1,2,2,4,2]; cap=[30,35,15,25,20,25,35]
    variables=[]; obj={}
    for idx,(i,j) in enumerate(arcs):
        name=f"{i}_{j}"; variables += [v(f"f_{name}","I",0,cap[idx]),v(f"y_{name}","B")]
        obj[f"f_{name}"]=unit[idx]; obj[f"y_{name}"]=fixed[idx]
    cons=[]
    for n in nodes:
        coeff={}
        for idx,(i,j) in enumerate(arcs):
            name=f"{i}_{j}"
            if i==n:add_term(coeff,f"f_{name}",1)
            if j==n:add_term(coeff,f"f_{name}",-1)
        rhs=40 if n=="S" else (-40 if n=="T" else 0)
        cons.append(c(f"flusso_{n}",coeff,"=",rhs))
    for idx,(i,j) in enumerate(arcs): cons.append(c(f"cap_{i}_{j}",{f"f_{i}_{j}":1,f"y_{i}_{j}":-cap[idx]},"<=",0))
    return Problem(
        "M10",10,"Progettazione di una rete distributiva","Network design",
        "Media","MILP intera","Istanza sintetica controllata",
        [
            "Una rete deve inviare 40 unità dal nodo S al nodo T. È possibile attivare gli archi indicati; ogni arco ha un costo fisso, un costo per unità e una capacità.",
            "Il flusso è intero e può attraversare i nodi intermedi A, B e C. Minimizzare costi di attivazione e trasporto rispettando la conservazione del flusso.",
        ],
        [{"title":"Archi","headers":["Arco","Costo fisso","Costo/unità","Capacità"],"rows":[[f"{i}→{j}",fixed[k],unit[k],cap[k]] for k,(i,j) in enumerate(arcs)]}],
        common_request(),variables,"min",obj,cons,"Costo totale di rete",
        difficulty_rationale="Attivazioni binarie e flussi interi collegati da capacità e conservazione su una rete diretta.")


def network_high() -> Problem:
    nodes=["S","A","B","C","D","T"]
    arcs=[("S","A"),("S","B"),("A","B"),("A","C"),("B","C"),("B","D"),("C","D"),("C","T"),("D","T")]
    commodities=["K1","K2"]; demand={"K1":28,"K2":22}
    fixed=[55,50,18,38,22,35,20,48,44]; cap=[35,35,15,30,25,25,20,35,35]
    unit={"K1":[2,3,1,2,2,3,1,3,2],"K2":[3,2,2,3,1,2,2,2,3]}
    variables=[v(f"y_{i}_{j}","B") for i,j in arcs]
    variables += [v(f"f_{k}_{i}_{j}","I",0,cap[a]) for k in commodities for a,(i,j) in enumerate(arcs)]
    obj={f"y_{i}_{j}":fixed[a] for a,(i,j) in enumerate(arcs)}
    for k in commodities:
        for a,(i,j) in enumerate(arcs):obj[f"f_{k}_{i}_{j}"]=unit[k][a]
    cons=[]
    for k in commodities:
        for n in nodes:
            coeff={}
            for i,j in arcs:
                if i==n:add_term(coeff,f"f_{k}_{i}_{j}",1)
                if j==n:add_term(coeff,f"f_{k}_{i}_{j}",-1)
            rhs=demand[k] if n=="S" else (-demand[k] if n=="T" else 0)
            cons.append(c(f"flusso_{k}_{n}",coeff,"=",rhs))
    for a,(i,j) in enumerate(arcs):
        coeff={f"f_{k}_{i}_{j}":1 for k in commodities}; coeff[f"y_{i}_{j}"]=-cap[a]
        cons.append(c(f"capacita_{i}_{j}",coeff,"<=",0))
    cons += [
        c("ridondanza_S",{"y_S_A":1,"y_S_B":1},"=",2),
        c("limite_archi",{f"y_{i}_{j}":1 for i,j in arcs},"<=",7),
    ]
    return Problem(
        "H10",10,"Rete multi-prodotto con capacità condivise","Network design",
        "Elevata","MILP intera","Istanza sintetica controllata",
        [
            "Una rete deve trasportare due prodotti K1 e K2 da S a T, rispettivamente per 28 e 22 unità. Gli archi attivati condividono la capacità tra i due prodotti.",
            "Per resilienza devono essere attivati entrambi gli archi in uscita da S. Per limiti gestionali possono essere attivati al massimo sette archi complessivi. I costi unitari dipendono dal prodotto.",
            "I flussi sono interi. Minimizzare costi fissi e costi di flusso rispettando conservazione e capacità condivise.",
        ],
        [
            {"title":"Archi e costi fissi","headers":["Arco","Costo fisso","Capacità"],"rows":[[f"{i}→{j}",fixed[a],cap[a]] for a,(i,j) in enumerate(arcs)]},
            {"title":"Costi unitari per prodotto","headers":["Arco","K1","K2"],"rows":[[f"{i}→{j}",unit["K1"][a],unit["K2"][a]] for a,(i,j) in enumerate(arcs)]},
        ],common_request(),variables,"min",obj,cons,"Costo totale multi-prodotto",
        difficulty_rationale="27 variabili intere/binarie, due flussi accoppiati da capacità condivise, ridondanza e limite di attivazione.")


def all_problems() -> List[Problem]:
    return [
        facility_medium(), production_medium(), workforce_medium(), fleet_medium(), portfolio_medium(),
        scheduling_medium(), suppliers_medium(), coverage_medium(), inventory_medium(), network_medium(),
        facility_high(), production_high(), workforce_high(), fleet_high(), portfolio_high(),
        scheduling_high(), suppliers_high(), coverage_high(), inventory_high(), network_high(),
    ]


def public_record(p: Problem) -> dict:
    return {
        "id": p.id, "pair": p.pair, "title": p.title, "domain": p.domain,
        "difficulty": p.difficulty, "model_class": p.model_class, "source": p.source,
        "intro": p.intro, "tables": p.tables, "request": p.request,
    }


def truth_record(p: Problem, solution: dict) -> dict:
    return {
        **public_record(p),
        "objective": {"sense": p.objective_sense, "label": p.objective_label, "coefficients": p.objective},
        "variables": [vars(x) for x in p.variables],
        "constraints": [vars(x) for x in p.constraints],
        "solution": solution,
        "notes": p.notes,
        "difficulty_rationale": p.difficulty_rationale,
        "structural_size": {
            "variables": len(p.variables),
            "binary": sum(x.vartype == "B" for x in p.variables),
            "integer": sum(x.vartype == "I" for x in p.variables),
            "continuous": sum(x.vartype == "C" for x in p.variables),
            "constraints": len(p.constraints),
        },
    }


GUROBI_SCRIPT = r'''#!/usr/bin/env python3
"""Risolutore generico Gurobi per il ground truth del dataset Cap. 4."""
import argparse
import json
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB

HERE = Path(__file__).resolve().parent

def solve(record):
    model = gp.Model(record["id"])
    model.Params.OutputFlag = 0
    vars_ = {}
    types = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
    for spec in record["variables"]:
        ub = GRB.INFINITY if spec["ub"] is None else spec["ub"]
        vars_[spec["name"]] = model.addVar(lb=spec["lb"], ub=ub, vtype=types[spec["vartype"]], name=spec["name"])
    model.update()
    obj = gp.quicksum(coef * vars_[name] for name, coef in record["objective"]["coefficients"].items())
    model.setObjective(obj, GRB.MINIMIZE if record["objective"]["sense"] == "min" else GRB.MAXIMIZE)
    for con in record["constraints"]:
        lhs = gp.quicksum(coef * vars_[name] for name, coef in con["coeffs"].items())
        if con["sense"] == "<=": model.addConstr(lhs <= con["rhs"], name=con["name"])
        elif con["sense"] == ">=": model.addConstr(lhs >= con["rhs"], name=con["name"])
        else: model.addConstr(lhs == con["rhs"], name=con["name"])
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"{record['id']}: status Gurobi {model.Status}")
    expected = record["solution"]["objective"]
    if abs(model.ObjVal - expected) > 1e-5:
        raise RuntimeError(f"{record['id']}: ottimo Gurobi {model.ObjVal} diverso dal ground truth {expected}")
    values = {name: var.X for name, var in vars_.items() if abs(var.X) > 1e-8}
    return model.ObjVal, values

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="es. M01; se omesso risolve tutto")
    args = ap.parse_args()
    records = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    for rec in records:
        if args.id and rec["id"] != args.id: continue
        obj, values = solve(rec)
        print(rec["id"], "objective=", round(obj, 6))
        print(values)
'''


def write_outputs() -> None:
    problems = all_problems()
    ids = [p.id for p in problems]
    if len(problems) != 20 or len(set(ids)) != 20:
        raise AssertionError("Il dataset deve contenere 20 ID unici")
    if sum(p.difficulty == "Media" for p in problems) != 10 or sum(p.difficulty == "Elevata" for p in problems) != 10:
        raise AssertionError("Devono esserci 10 problemi medi e 10 elevati")

    truth = []
    for p in problems:
        solution = solve_problem(p)
        if solution["max_constraint_violation"] > 1e-6:
            raise AssertionError(f"{p.id}: violazione {solution['max_constraint_violation']}")
        truth.append(truth_record(p, solution))

    with (ROOT / "problems.jsonl").open("w", encoding="utf-8") as f:
        for p in problems:
            f.write(json.dumps(public_record(p), ensure_ascii=False) + "\n")
    (ROOT / "ground_truth.json").write_text(json.dumps(truth, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "verify_with_gurobi.py").write_text(GUROBI_SCRIPT, encoding="utf-8")

    with (ROOT / "solutions_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "difficolta", "dominio", "classe", "n_variabili", "n_vincoli", "ottimo", "violazione_max"])
        for rec in truth:
            writer.writerow([
                rec["id"], rec["difficulty"], rec["domain"], rec["model_class"],
                rec["structural_size"]["variables"], rec["structural_size"]["constraints"],
                rec["solution"]["objective"], rec["solution"]["max_constraint_violation"],
            ])

    print("Dataset generato e certificato:")
    for rec in truth:
        s = rec["structural_size"]
        print(f"{rec['id']} {rec['difficulty']:<7} obj={rec['solution']['objective']:<10} vars={s['variables']:<3} cons={s['constraints']:<3}")


if __name__ == "__main__":
    write_outputs()
