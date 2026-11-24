#!/usr/bin/env python3
"""Costruisce il dataset definitivo ad alta complessità per lo studio H5.

Le cinque istanze sono generate e risolte prima di qualsiasi chiamata API. Ogni
problema trasferisce uno dei cinque principi della memoria di DeepSeek a un
contesto nuovo, con più variabili e famiglie di vincoli rispetto al set di
calibrazione. Le tracce restano complete e prive di ambiguità intenzionali.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import gurobipy as gp
from gurobipy import GRB


HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "prompts"
DATASET_VERSION = "definitivo_v2"

REQUEST = [
    "Definire con precisione insiemi, parametri e variabili decisionali.",
    "Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.",
    "Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.",
    "Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.",
]


@dataclass
class LinearProblem:
    metadata: dict[str, Any]
    variables: list[dict[str, Any]] = field(default_factory=list)
    constraints: list[dict[str, Any]] = field(default_factory=list)
    objective_coefficients: dict[str, float] = field(default_factory=dict)
    objective_sense: str = "min"
    objective_label: str = "Costo totale"

    def add_var(
        self,
        name: str,
        vartype: str,
        *,
        lb: float = 0.0,
        ub: float | None = None,
        description: str = "",
    ) -> None:
        self.variables.append(
            {
                "name": name,
                "vartype": vartype,
                "lb": float(lb),
                "ub": None if ub is None else float(ub),
                "description": description,
            }
        )

    def add_con(
        self,
        name: str,
        coeffs: dict[str, float],
        sense: str,
        rhs: float,
        description: str = "",
    ) -> None:
        if sense not in {"<=", ">=", "="}:
            raise ValueError(sense)
        self.constraints.append(
            {
                "name": name,
                "coeffs": {key: float(value) for key, value in coeffs.items() if value},
                "sense": sense,
                "rhs": float(rhs),
                "description": description,
            }
        )

    def set_objective(
        self,
        coefficients: dict[str, float],
        *,
        sense: str = "min",
        label: str = "Costo totale",
    ) -> None:
        self.objective_coefficients = {
            key: float(value) for key, value in coefficients.items() if value
        }
        self.objective_sense = sense
        self.objective_label = label

    def solve(self) -> dict[str, Any]:
        model = gp.Model(self.metadata["id"])
        model.Params.OutputFlag = 0
        model.Params.Seed = 0
        model.Params.MIPGap = 0.0
        model.Params.MIPGapAbs = 0.0
        vars_by_name: dict[str, gp.Var] = {}
        type_map = {"B": GRB.BINARY, "I": GRB.INTEGER, "C": GRB.CONTINUOUS}
        for spec in self.variables:
            vars_by_name[spec["name"]] = model.addVar(
                lb=spec["lb"],
                ub=GRB.INFINITY if spec["ub"] is None else spec["ub"],
                vtype=type_map[spec["vartype"]],
                name=spec["name"],
            )
        model.update()
        model.setObjective(
            gp.quicksum(
                coefficient * vars_by_name[name]
                for name, coefficient in self.objective_coefficients.items()
            ),
            GRB.MINIMIZE if self.objective_sense == "min" else GRB.MAXIMIZE,
        )
        for con in self.constraints:
            lhs = gp.quicksum(
                coefficient * vars_by_name[name]
                for name, coefficient in con["coeffs"].items()
            )
            if con["sense"] == "<=":
                model.addConstr(lhs <= con["rhs"], name=con["name"])
            elif con["sense"] == ">=":
                model.addConstr(lhs >= con["rhs"], name=con["name"])
            else:
                model.addConstr(lhs == con["rhs"], name=con["name"])
        model.optimize()
        if model.Status != GRB.OPTIMAL:
            raise RuntimeError(
                f"{self.metadata['id']} non certificato: stato Gurobi {model.Status}"
            )
        values = {name: float(var.X) for name, var in vars_by_name.items()}
        return {
            "status": "OPTIMAL",
            "objective": float(model.ObjVal),
            "variables": values,
            "nonzero_variables": {
                name: value for name, value in values.items() if abs(value) > 1e-8
            },
            "runtime_seconds": float(model.Runtime),
            "mip_gap": float(model.MIPGap),
            "solver": (
                f"Gurobi {gp.gurobi.version()[0]}."
                f"{gp.gurobi.version()[1]}.{gp.gurobi.version()[2]}"
            ),
        }

    def record(self) -> dict[str, Any]:
        solution = self.solve()
        return {
            **self.metadata,
            "request": REQUEST,
            "objective": {
                "sense": self.objective_sense,
                "label": self.objective_label,
                "coefficients": self.objective_coefficients,
            },
            "variables": self.variables,
            "constraints": self.constraints,
            "solution": solution,
            "dimensions": {
                "variables": len(self.variables),
                "binary_variables": sum(v["vartype"] == "B" for v in self.variables),
                "integer_variables": sum(v["vartype"] == "I" for v in self.variables),
                "continuous_variables": sum(v["vartype"] == "C" for v in self.variables),
                "constraints": len(self.constraints),
            },
        }


def base_metadata(
    problem_id: str,
    title: str,
    domain: str,
    model_class: str,
    source_problem: str,
    principle_id: str,
    principle: str,
    intro: list[str],
    tables: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": problem_id,
        "dataset_version": DATASET_VERSION,
        "title": title,
        "domain": domain,
        "difficulty": "Elevata",
        "model_class": model_class,
        "source": "Istanza sintetica controllata del dataset definitivo per H5",
        "source_problem": source_problem,
        "target_principle_id": principle_id,
        "target_principle": principle,
        "intro": intro,
        "tables": tables,
    }


def problem_l01() -> LinearProblem:
    vehicles = ["E1", "E2", "E3", "D1", "D2", "D3", "D4", "D5"]
    routes = [f"R{i:02d}" for i in range(1, 17)]
    electric = ["E1", "E2", "E3"]
    diesel = ["D1", "D2", "D3", "D4", "D5"]
    loads = dict(zip(routes, [5, 7, 4, 8, 6, 9, 5, 7, 8, 6, 9, 7, 10, 6, 8, 5]))
    distances = dict(
        zip(routes, [18, 28, 16, 34, 22, 51, 26, 20, 48, 31, 55, 24, 52, 29, 47, 45])
    )
    capacity = {
        "E1": 30,
        "E2": 32,
        "E3": 28,
        "D1": 38,
        "D2": 40,
        "D3": 36,
        "D4": 42,
        "D5": 35,
    }
    max_routes = {vehicle: (3 if vehicle in electric else 4) for vehicle in vehicles}
    fixed = {
        "E1": 62,
        "E2": 58,
        "E3": 55,
        "D1": 46,
        "D2": 44,
        "D3": 41,
        "D4": 49,
        "D5": 43,
    }
    emission_factor = {
        vehicle: (0 if vehicle in electric else 2 + (idx % 2))
        for idx, vehicle in enumerate(vehicles)
    }
    long_routes = ["R06", "R09", "R11", "R13", "R15", "R16"]
    center_routes = ["R01", "R03", "R05", "R08", "R12"]
    costs: dict[tuple[str, str], int] = {}
    for vi, vehicle in enumerate(vehicles):
        for ri, route in enumerate(routes):
            value = 9 + ((vi * 7 + ri * 3) % 13)
            if vehicle in electric and route in long_routes:
                value = max(3, value - 8 - vi)
            if vehicle == "E1" and route in long_routes:
                value = max(2, value - 2)
            costs[vehicle, route] = value

    p = LinearProblem(
        base_metadata(
            "L01",
            "Assegnazione di consegne a una flotta con limiti individuali",
            "Distribuzione urbana",
            "IP binaria",
            "H03",
            "S-001",
            "Quando un requisito si applica individualmente a più soggetti, formulare un vincolo separato per ciascun soggetto anziché aggregarli in un unico limite complessivo.",
            [
                "Un operatore deve assegnare sedici rotte a otto veicoli. Ogni rotta deve essere affidata a un solo veicolo. Un veicolo può essere usato soltanto se attivato e deve rispettare sia la capacità complessiva di carico sia il numero massimo di rotte riportati in tabella.",
                "Devono essere attivati al massimo sette veicoli e almeno due dei tre elettrici. Le rotte R06, R09, R11, R13, R15 e R16 sono lunghe: ciascun veicolo elettrico può servirne al massimo una. Inoltre, ciascun diesel può effettuare al massimo due delle rotte di centro R01, R03, R05, R08 e R12. Le emissioni complessive, calcolate come distanza per fattore del veicolo, non possono superare 1.050. Minimizzare costi fissi e di assegnazione.",
            ],
            [
                {
                    "title": "Veicoli",
                    "headers": [
                        "Veicolo",
                        "Tipo",
                        "Costo fisso",
                        "Capacità",
                        "Rotte max",
                        "Fattore emissione",
                    ],
                    "rows": [
                        [
                            v,
                            "Elettrico" if v in electric else "Diesel",
                            fixed[v],
                            capacity[v],
                            max_routes[v],
                            emission_factor[v],
                        ]
                        for v in vehicles
                    ],
                },
                {
                    "title": "Rotte",
                    "headers": ["Rotta", *routes],
                    "rows": [
                        ["Carico", *[loads[r] for r in routes]],
                        ["Distanza", *[distances[r] for r in routes]],
                    ],
                },
                {
                    "title": "Costi di assegnazione",
                    "headers": ["Veicolo", *routes],
                    "rows": [[v, *[costs[v, r] for r in routes]] for v in vehicles],
                },
            ],
        )
    )
    objective: dict[str, float] = {}
    for vehicle in vehicles:
        p.add_var(f"y_{vehicle}", "B", description=f"1 se {vehicle} è attivato")
        objective[f"y_{vehicle}"] = fixed[vehicle]
        for route in routes:
            p.add_var(
                f"x_{vehicle}_{route}",
                "B",
                description=f"1 se {route} è assegnata a {vehicle}",
            )
            objective[f"x_{vehicle}_{route}"] = costs[vehicle, route]
    p.set_objective(objective)
    for route in routes:
        p.add_con(
            f"cover_{route}",
            {f"x_{vehicle}_{route}": 1 for vehicle in vehicles},
            "=",
            1,
        )
    for vehicle in vehicles:
        p.add_con(
            f"load_{vehicle}",
            {
                **{f"x_{vehicle}_{route}": loads[route] for route in routes},
                f"y_{vehicle}": -capacity[vehicle],
            },
            "<=",
            0,
        )
        p.add_con(
            f"max_routes_{vehicle}",
            {
                **{f"x_{vehicle}_{route}": 1 for route in routes},
                f"y_{vehicle}": -max_routes[vehicle],
            },
            "<=",
            0,
        )
    p.add_con("max_active", {f"y_{v}": 1 for v in vehicles}, "<=", 7)
    p.add_con("min_electric", {f"y_{v}": 1 for v in electric}, ">=", 2)
    for vehicle in electric:
        p.add_con(
            f"long_limit_{vehicle}",
            {f"x_{vehicle}_{route}": 1 for route in long_routes},
            "<=",
            1,
        )
    for vehicle in diesel:
        p.add_con(
            f"center_limit_{vehicle}",
            {f"x_{vehicle}_{route}": 1 for route in center_routes},
            "<=",
            2,
        )
    p.add_con(
        "emission_budget",
        {
            f"x_{vehicle}_{route}": emission_factor[vehicle] * distances[route]
            for vehicle in vehicles
            for route in routes
        },
        "<=",
        1050,
    )
    return p


def problem_l02() -> LinearProblem:
    products = ["P1", "P2", "P3"]
    periods = [f"T{i}" for i in range(1, 9)]
    demand = {
        "P1": [34, 48, 42, 55, 38, 50, 46, 40],
        "P2": [28, 32, 45, 36, 50, 34, 42, 39],
        "P3": [40, 35, 38, 44, 36, 48, 41, 45],
    }
    initial = {"P1": 22, "P2": 18, "P3": 25}
    final_min = {"P1": 18, "P2": 15, "P3": 20}
    hours = {"P1": 2, "P2": 3, "P3": 1}
    min_lot = {"P1": 24, "P2": 20, "P3": 28}
    max_lot = {"P1": 82, "P2": 70, "P3": 90}
    holding = {"P1": 1.2, "P2": 1.6, "P3": 0.9}
    setup = {"P1": 52, "P2": 60, "P3": 45}
    capacity = dict(zip(periods, [250, 245, 235, 260, 240, 255, 245, 265]))
    production_cost = {
        product: [5 + ((pi * 2 + ti * 3) % 6) for ti in range(len(periods))]
        for pi, product in enumerate(products)
    }

    p = LinearProblem(
        base_metadata(
            "L02",
            "Pianificazione multi-prodotto di un reparto di confezionamento",
            "Produzione e scorte",
            "MILP intera",
            "H02",
            "S-002",
            "Nei problemi di produzione multi-periodo, indicizzare esplicitamente anche la scorta iniziale e collegare periodi consecutivi mediante il bilancio produzione più scorta precedente uguale domanda più scorta finale; completare poi il collegamento tra produzione e setup con limiti minimo e massimo di lotto.",
            [
                "Un reparto pianifica tre prodotti per otto periodi. Le scorte iniziali e le giacenze finali minime sono specifiche per prodotto; ogni scorta di fine periodo è intera, non negativa e non può superare 75 unità. La giacenza complessiva dei tre prodotti non può superare 150 unità in alcun periodo.",
                "La capacità produttiva è condivisa e dipende dalle ore richieste per unità. Produrre un articolo in un periodo richiede il relativo setup: quando il setup è attivo devono essere rispettati sia il lotto minimo sia quello massimo. Sono ammessi al massimo diciotto setup complessivi e, nei periodi T3 e T6, possono essere predisposti al massimo due prodotti. Minimizzare costi di produzione, setup e scorta.",
            ],
            [
                {
                    "title": "Parametri dei prodotti",
                    "headers": [
                        "Prodotto",
                        "Scorta iniziale",
                        "Scorta finale minima",
                        "Ore/unità",
                        "Lotto minimo",
                        "Lotto massimo",
                        "Costo setup",
                        "Costo scorta",
                    ],
                    "rows": [
                        [
                            product,
                            initial[product],
                            final_min[product],
                            hours[product],
                            min_lot[product],
                            max_lot[product],
                            setup[product],
                            holding[product],
                        ]
                        for product in products
                    ],
                },
                {
                    "title": "Domanda",
                    "headers": ["Prodotto", *periods],
                    "rows": [[product, *demand[product]] for product in products],
                },
                {
                    "title": "Costo unitario di produzione",
                    "headers": ["Prodotto", *periods],
                    "rows": [[product, *production_cost[product]] for product in products],
                },
                {
                    "title": "Capacità condivisa",
                    "headers": ["Periodo", *periods],
                    "rows": [["Ore disponibili", *[capacity[t] for t in periods]]],
                },
            ],
        )
    )
    objective: dict[str, float] = {}
    for product in products:
        for ti, period in enumerate(periods):
            p.add_var(f"x_{product}_{period}", "I", description=f"produzione {product} in {period}")
            p.add_var(
                f"I_{product}_{period}",
                "I",
                ub=75,
                description=f"scorta {product} a fine {period}",
            )
            p.add_var(f"y_{product}_{period}", "B", description=f"setup {product} in {period}")
            objective[f"x_{product}_{period}"] = production_cost[product][ti]
            objective[f"I_{product}_{period}"] = holding[product]
            objective[f"y_{product}_{period}"] = setup[product]
    p.set_objective(objective)
    for product in products:
        for ti, period in enumerate(periods):
            coeffs = {f"x_{product}_{period}": 1, f"I_{product}_{period}": -1}
            rhs = demand[product][ti] - initial[product] if ti == 0 else demand[product][ti]
            if ti > 0:
                coeffs[f"I_{product}_{periods[ti - 1]}"] = 1
            p.add_con(f"balance_{product}_{period}", coeffs, "=", rhs)
            p.add_con(
                f"max_lot_{product}_{period}",
                {
                    f"x_{product}_{period}": 1,
                    f"y_{product}_{period}": -max_lot[product],
                },
                "<=",
                0,
            )
            p.add_con(
                f"min_lot_{product}_{period}",
                {
                    f"x_{product}_{period}": 1,
                    f"y_{product}_{period}": -min_lot[product],
                },
                ">=",
                0,
            )
        p.add_con(
            f"final_{product}",
            {f"I_{product}_T8": 1},
            ">=",
            final_min[product],
        )
    for period in periods:
        p.add_con(
            f"capacity_{period}",
            {f"x_{product}_{period}": hours[product] for product in products},
            "<=",
            capacity[period],
        )
        p.add_con(
            f"warehouse_{period}",
            {f"I_{product}_{period}": 1 for product in products},
            "<=",
            150,
        )
    p.add_con(
        "max_setups_total",
        {
            f"y_{product}_{period}": 1
            for product in products
            for period in periods
        },
        "<=",
        18,
    )
    for period in ["T3", "T6"]:
        p.add_con(
            f"max_two_setups_{period}",
            {f"y_{product}_{period}": 1 for product in products},
            "<=",
            2,
        )
    return p


def problem_l03() -> LinearProblem:
    suppliers = [f"S{i}" for i in range(1, 9)]
    components = [f"C{i}" for i in range(1, 7)]
    demand = dict(zip(components, [90, 80, 75, 70, 65, 60]))
    capacity = dict(zip(suppliers, [125, 115, 110, 105, 120, 100, 95, 115]))
    fixed = dict(zip(suppliers, [165, 150, 170, 145, 155, 140, 160, 148]))
    risk = dict(zip(suppliers, [2, 3, 1, 4, 2, 3, 1, 4]))
    available_by_supplier = {
        "S1": ["C1", "C2", "C3", "C5"],
        "S2": ["C1", "C2", "C4", "C6"],
        "S3": ["C1", "C3", "C4", "C5", "C6"],
        "S4": ["C2", "C3", "C4", "C6"],
        "S5": ["C1", "C2", "C5", "C6"],
        "S6": ["C2", "C3", "C4", "C5"],
        "S7": ["C1", "C3", "C5", "C6"],
        "S8": ["C2", "C4", "C5", "C6"],
    }
    available = [
        (supplier, component)
        for supplier in suppliers
        for component in available_by_supplier[supplier]
    ]
    preferred = {
        "C1": "S1",
        "C2": "S2",
        "C3": "S3",
        "C4": "S4",
        "C5": "S5",
        "C6": "S7",
    }
    min_lot = dict(zip(components, [14, 12, 12, 10, 11, 10]))
    unit_cost: dict[tuple[str, str], int] = {}
    quality: dict[tuple[str, str], int] = {}
    for si, supplier in enumerate(suppliers):
        for ci, component in enumerate(components):
            if (supplier, component) not in available:
                continue
            unit_cost[supplier, component] = (
                3
                if preferred[component] == supplier
                else 9 + ((si * 3 + ci * 2) % 5)
            )
            quality[supplier, component] = (
                98
                if preferred[component] == supplier
                else 92 + ((si * 2 + ci * 3) % 7)
            )

    p = LinearProblem(
        base_metadata(
            "L03",
            "Approvvigionamento multi-componente da fornitori qualificati",
            "Procurement",
            "MILP intera",
            "H07",
            "S-003",
            "Nei problemi con coppie non disponibili, creare variabili soltanto per le coppie ammesse e collegare esplicitamente quantità, uso della coppia e attivazione della risorsa.",
            [
                "Un’impresa deve acquistare sei componenti da otto fornitori. Ogni domanda deve essere soddisfatta esattamente e ogni componente deve provenire da almeno due e da non più di tre fornitori qualificati. Quando una coppia fornitore–componente viene utilizzata, deve rispettare il lotto minimo specifico del componente.",
                "La capacità di ciascun fornitore è condivisa tra tutti i componenti e può essere utilizzata soltanto se il fornitore è attivato. Possono essere attivati al massimo sei fornitori e almeno uno tra S1 e S2. Per ogni componente la qualità media ponderata deve essere almeno 95; il rischio ponderato complessivo non può superare 1.300. Le celle «—» sono combinazioni non disponibili. Minimizzare costi fissi e di acquisto.",
            ],
            [
                {
                    "title": "Fornitori",
                    "headers": [
                        "Fornitore",
                        "Costo fisso",
                        "Capacità",
                        "Rischio unitario",
                    ],
                    "rows": [
                        [supplier, fixed[supplier], capacity[supplier], risk[supplier]]
                        for supplier in suppliers
                    ],
                },
                {
                    "title": "Domanda e lotto minimo",
                    "headers": ["Componente", *components],
                    "rows": [
                        ["Domanda", *[demand[c] for c in components]],
                        ["Lotto minimo", *[min_lot[c] for c in components]],
                    ],
                },
                {
                    "title": "Costi unitari e disponibilità",
                    "headers": ["Fornitore", *components],
                    "rows": [
                        [supplier, *[unit_cost.get((supplier, c), "—") for c in components]]
                        for supplier in suppliers
                    ],
                },
                {
                    "title": "Qualità delle coppie disponibili",
                    "headers": ["Fornitore", *components],
                    "rows": [
                        [supplier, *[quality.get((supplier, c), "—") for c in components]]
                        for supplier in suppliers
                    ],
                },
            ],
        )
    )
    objective: dict[str, float] = {}
    for supplier in suppliers:
        p.add_var(f"y_{supplier}", "B", description=f"1 se {supplier} è attivato")
        objective[f"y_{supplier}"] = fixed[supplier]
    for supplier, component in available:
        p.add_var(
            f"x_{supplier}_{component}",
            "I",
            description=f"quantità di {component} acquistata da {supplier}",
        )
        p.add_var(
            f"z_{supplier}_{component}",
            "B",
            description=f"1 se la coppia {supplier}-{component} è usata",
        )
        objective[f"x_{supplier}_{component}"] = unit_cost[supplier, component]
    p.set_objective(objective)
    for component in components:
        eligible = [
            supplier for supplier in suppliers if (supplier, component) in available
        ]
        p.add_con(
            f"demand_{component}",
            {f"x_{supplier}_{component}": 1 for supplier in eligible},
            "=",
            demand[component],
        )
        p.add_con(
            f"min_sources_{component}",
            {f"z_{supplier}_{component}": 1 for supplier in eligible},
            ">=",
            2,
        )
        p.add_con(
            f"max_sources_{component}",
            {f"z_{supplier}_{component}": 1 for supplier in eligible},
            "<=",
            3,
        )
        p.add_con(
            f"quality_{component}",
            {
                f"x_{supplier}_{component}": quality[supplier, component]
                for supplier in eligible
            },
            ">=",
            95 * demand[component],
        )
    for supplier in suppliers:
        p.add_con(
            f"capacity_{supplier}",
            {
                **{
                    f"x_{supplier}_{component}": 1
                    for component in components
                    if (supplier, component) in available
                },
                f"y_{supplier}": -capacity[supplier],
            },
            "<=",
            0,
        )
    p.add_con("max_active", {f"y_{supplier}": 1 for supplier in suppliers}, "<=", 6)
    p.add_con("at_least_one_S1_S2", {"y_S1": 1, "y_S2": 1}, ">=", 1)
    p.add_con(
        "risk_budget",
        {f"x_{supplier}_{component}": risk[supplier] for supplier, component in available},
        "<=",
        1300,
    )
    for supplier, component in available:
        p.add_con(
            f"upper_link_{supplier}_{component}",
            {
                f"x_{supplier}_{component}": 1,
                f"z_{supplier}_{component}": -demand[component],
            },
            "<=",
            0,
        )
        p.add_con(
            f"lower_link_{supplier}_{component}",
            {
                f"x_{supplier}_{component}": 1,
                f"z_{supplier}_{component}": -min_lot[component],
            },
            ">=",
            0,
        )
        p.add_con(
            f"activation_{supplier}_{component}",
            {f"z_{supplier}_{component}": 1, f"y_{supplier}": -1},
            "<=",
            0,
        )
    return p


def problem_l04() -> LinearProblem:
    products = ["A", "B", "C", "D", "E"]
    periods = [f"T{i}" for i in range(1, 7)]
    demand = {
        "A": [38, 42, 35, 50, 45, 40],
        "B": [32, 36, 44, 38, 46, 34],
        "C": [25, 30, 28, 35, 30, 32],
        "D": [40, 35, 45, 42, 38, 48],
        "E": [20, 24, 22, 28, 26, 25],
    }
    initial = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
    final_min = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
    hours = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
    min_lot = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
    max_lot = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
    setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
    holding_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}
    regular_capacity = dict(zip(periods, [350, 360, 345, 370, 355, 380]))
    overtime_max = dict(zip(periods, [85, 80, 90, 75, 85, 80]))
    overtime_unit_cost = dict(zip(periods, [7, 8, 7, 9, 8, 7]))
    production_cost = {
        product: [4 + ((pi * 3 + ti * 2) % 7) for ti in range(len(periods))]
        for pi, product in enumerate(products)
    }

    p = LinearProblem(
        base_metadata(
            "L04",
            "Produzione multi-prodotto con straordinario attivabile",
            "Produzione multi-prodotto",
            "MILP intera",
            "H09",
            "S-004",
            "Nei modelli multi-prodotto e multi-periodo, collegare ogni periodo mediante il bilancio delle scorte e rappresentare lo straordinario come capacità aggiuntiva limitata e costosa; i setup devono attivare la produzione attraverso limiti minimo e massimo di lotto.",
            [
                "Un impianto pianifica cinque prodotti per sei periodi. Per ogni prodotto sono note scorta iniziale, scorta finale minima, ore per unità e limiti di lotto. La scorta di ciascun prodotto non può superare 75 unità e la giacenza complessiva a fine periodo non può superare 210 unità.",
                "La capacità ordinaria è condivisa. Lo straordinario è capacità aggiuntiva: in ogni periodo richiede un’attivazione dal costo fisso di 25, può essere acquistato soltanto in quantità comprese tra 10 ore e il massimo indicato e ha il costo unitario riportato in tabella. La produzione richiede un setup e deve rispettare lotto minimo e massimo. Sono consentiti al massimo ventisei setup complessivi e non più di quattro per periodo. Minimizzare produzione, setup, scorte e straordinario.",
            ],
            [
                {
                    "title": "Parametri dei prodotti",
                    "headers": [
                        "Prodotto",
                        "Scorta iniziale",
                        "Scorta finale minima",
                        "Ore/unità",
                        "Lotto minimo",
                        "Lotto massimo",
                        "Costo setup",
                        "Costo scorta",
                    ],
                    "rows": [
                        [
                            product,
                            initial[product],
                            final_min[product],
                            hours[product],
                            min_lot[product],
                            max_lot[product],
                            setup_cost[product],
                            holding_cost[product],
                        ]
                        for product in products
                    ],
                },
                {
                    "title": "Domanda",
                    "headers": ["Prodotto", *periods],
                    "rows": [[product, *demand[product]] for product in products],
                },
                {
                    "title": "Costi unitari di produzione",
                    "headers": ["Prodotto", *periods],
                    "rows": [[product, *production_cost[product]] for product in products],
                },
                {
                    "title": "Capacità e straordinario",
                    "headers": ["Voce", *periods],
                    "rows": [
                        ["Capacità ordinaria", *[regular_capacity[t] for t in periods]],
                        ["Straordinario massimo", *[overtime_max[t] for t in periods]],
                        [
                            "Costo unitario straordinario",
                            *[overtime_unit_cost[t] for t in periods],
                        ],
                    ],
                },
            ],
        )
    )
    objective: dict[str, float] = {}
    for period in periods:
        p.add_var(
            f"o_{period}",
            "I",
            ub=overtime_max[period],
            description=f"ore straordinarie in {period}",
        )
        p.add_var(f"u_{period}", "B", description=f"1 se lo straordinario è attivato in {period}")
        objective[f"o_{period}"] = overtime_unit_cost[period]
        objective[f"u_{period}"] = 25
    for product in products:
        for ti, period in enumerate(periods):
            p.add_var(f"x_{product}_{period}", "I", description=f"produzione {product} in {period}")
            p.add_var(
                f"I_{product}_{period}",
                "I",
                ub=75,
                description=f"scorta {product} a fine {period}",
            )
            p.add_var(f"y_{product}_{period}", "B", description=f"setup {product} in {period}")
            objective[f"x_{product}_{period}"] = production_cost[product][ti]
            objective[f"I_{product}_{period}"] = holding_cost[product]
            objective[f"y_{product}_{period}"] = setup_cost[product]
    p.set_objective(objective)
    for product in products:
        for ti, period in enumerate(periods):
            coeffs = {f"x_{product}_{period}": 1, f"I_{product}_{period}": -1}
            rhs = demand[product][ti] - initial[product] if ti == 0 else demand[product][ti]
            if ti > 0:
                coeffs[f"I_{product}_{periods[ti - 1]}"] = 1
            p.add_con(f"balance_{product}_{period}", coeffs, "=", rhs)
            p.add_con(
                f"max_lot_{product}_{period}",
                {
                    f"x_{product}_{period}": 1,
                    f"y_{product}_{period}": -max_lot[product],
                },
                "<=",
                0,
            )
            p.add_con(
                f"min_lot_{product}_{period}",
                {
                    f"x_{product}_{period}": 1,
                    f"y_{product}_{period}": -min_lot[product],
                },
                ">=",
                0,
            )
        p.add_con(
            f"final_{product}",
            {f"I_{product}_T6": 1},
            ">=",
            final_min[product],
        )
    for period in periods:
        p.add_con(
            f"capacity_{period}",
            {
                **{f"x_{product}_{period}": hours[product] for product in products},
                f"o_{period}": -1,
            },
            "<=",
            regular_capacity[period],
        )
        p.add_con(
            f"overtime_upper_{period}",
            {f"o_{period}": 1, f"u_{period}": -overtime_max[period]},
            "<=",
            0,
        )
        p.add_con(
            f"overtime_lower_{period}",
            {f"o_{period}": 1, f"u_{period}": -10},
            ">=",
            0,
        )
        p.add_con(
            f"warehouse_{period}",
            {f"I_{product}_{period}": 1 for product in products},
            "<=",
            210,
        )
        p.add_con(
            f"max_setups_{period}",
            {f"y_{product}_{period}": 1 for product in products},
            "<=",
            4,
        )
    p.add_con(
        "max_setups_total",
        {
            f"y_{product}_{period}": 1
            for product in products
            for period in periods
        },
        "<=",
        26,
    )
    return p


def problem_l05() -> LinearProblem:
    inspectors = [f"I{i}" for i in range(1, 13)]
    audits = [f"A{i:02d}" for i in range(1, 21)]
    senior = ["I1", "I2", "I3", "I4"]
    high_risk = ["A04", "A08", "A12", "A16", "A20"]
    durations = dict(
        zip(audits, [3, 4, 2, 6, 5, 3, 4, 7, 2, 5, 3, 6, 4, 2, 5, 7, 3, 4, 5, 6])
    )
    fixed = {
        inspector: 18 + ((index * 5) % 11)
        for index, inspector in enumerate(inspectors)
    }
    hour_capacity = {
        inspector: 13 + (index % 5)
        for index, inspector in enumerate(inspectors)
    }
    max_audits = {
        inspector: (3 if inspector in senior else 4) for inspector in inspectors
    }
    eligible: dict[tuple[str, str], int] = {}
    for inspector_index, inspector in enumerate(inspectors, 1):
        for audit_index, audit in enumerate(audits, 1):
            allowed = ((inspector_index * 3 + audit_index * 5) % 7) not in {0, 1}
            if audit in high_risk and inspector in senior:
                allowed = True
            if allowed:
                eligible[inspector, audit] = 6 + (
                    (inspector_index * 7 + audit_index * 3) % 13
                )
    conflict_pairs = [
        ("A01", "A02"),
        ("A06", "A07"),
        ("A11", "A12"),
        ("A17", "A18"),
    ]

    p = LinearProblem(
        base_metadata(
            "L05",
            "Assegnazione di ispettori a un portafoglio di audit",
            "Assegnazione e qualificazione",
            "IP binaria",
            "M03",
            "S-005",
            "Nei problemi di assegnazione con coppie non disponibili, creare variabili soltanto per le coppie ammesse oppure imporre esplicitamente a zero le combinazioni vietate; la copertura deve essere imposta separatamente su ciascuna attività.",
            [
                "Un portafoglio di venti audit deve essere assegnato a dodici ispettori. Gli audit ordinari richiedono esattamente un ispettore; quelli ad alto rischio A04, A08, A12, A16 e A20 richiedono esattamente due ispettori distinti, dei quali almeno uno senior. Le celle «—» indicano una qualificazione assente e la combinazione non può essere utilizzata.",
                "Ogni ispettore attivato deve rispettare sia il monte ore sia il numero massimo di audit riportati in tabella. Per ciascun ispettore, le coppie A01–A02, A06–A07, A11–A12 e A17–A18 sono incompatibili: non possono essere assegnati entrambi gli audit della stessa coppia. Possono essere attivati al massimo dieci ispettori. Minimizzare costi fissi e costi di assegnazione.",
            ],
            [
                {
                    "title": "Ispettori",
                    "headers": [
                        "Ispettore",
                        "Livello",
                        "Costo fisso",
                        "Ore max",
                        "Audit max",
                    ],
                    "rows": [
                        [
                            inspector,
                            "Senior" if inspector in senior else "Standard",
                            fixed[inspector],
                            hour_capacity[inspector],
                            max_audits[inspector],
                        ]
                        for inspector in inspectors
                    ],
                },
                {
                    "title": "Audit",
                    "headers": ["Audit", *audits],
                    "rows": [
                        ["Durata", *[durations[audit] for audit in audits]],
                        [
                            "Ispettori richiesti",
                            *[2 if audit in high_risk else 1 for audit in audits],
                        ],
                    ],
                },
                {
                    "title": "Costi e qualificazioni",
                    "headers": ["Ispettore", *audits],
                    "rows": [
                        [
                            inspector,
                            *[
                                eligible.get((inspector, audit), "—")
                                for audit in audits
                            ],
                        ]
                        for inspector in inspectors
                    ],
                },
            ],
        )
    )
    objective: dict[str, float] = {}
    for inspector in inspectors:
        p.add_var(
            f"y_{inspector}", "B", description=f"1 se {inspector} è attivato"
        )
        objective[f"y_{inspector}"] = fixed[inspector]
    for inspector, audit in eligible:
        p.add_var(
            f"x_{inspector}_{audit}",
            "B",
            description=f"1 se {audit} è assegnato a {inspector}",
        )
        objective[f"x_{inspector}_{audit}"] = eligible[inspector, audit]
    p.set_objective(objective)
    for audit in audits:
        qualified = [
            inspector
            for inspector in inspectors
            if (inspector, audit) in eligible
        ]
        required = 2 if audit in high_risk else 1
        p.add_con(
            f"cover_{audit}",
            {f"x_{inspector}_{audit}": 1 for inspector in qualified},
            "=",
            required,
        )
        if audit in high_risk:
            p.add_con(
                f"senior_{audit}",
                {
                    f"x_{inspector}_{audit}": 1
                    for inspector in senior
                    if (inspector, audit) in eligible
                },
                ">=",
                1,
            )
    for inspector in inspectors:
        qualified = [
            audit for audit in audits if (inspector, audit) in eligible
        ]
        p.add_con(
            f"hours_{inspector}",
            {
                **{
                    f"x_{inspector}_{audit}": durations[audit]
                    for audit in qualified
                },
                f"y_{inspector}": -hour_capacity[inspector],
            },
            "<=",
            0,
        )
        p.add_con(
            f"count_{inspector}",
            {
                **{f"x_{inspector}_{audit}": 1 for audit in qualified},
                f"y_{inspector}": -max_audits[inspector],
            },
            "<=",
            0,
        )
        p.add_con(
            f"activation_{inspector}",
            {
                **{f"x_{inspector}_{audit}": 1 for audit in qualified},
                f"y_{inspector}": -1,
            },
            ">=",
            0,
        )
        for first, second in conflict_pairs:
            coeffs = {
                f"x_{inspector}_{audit}": 1
                for audit in (first, second)
                if (inspector, audit) in eligible
            }
            if len(coeffs) == 2:
                p.add_con(
                    f"conflict_{inspector}_{first}_{second}",
                    coeffs,
                    "<=",
                    1,
                )
    p.add_con(
        "max_active",
        {f"y_{inspector}": 1 for inspector in inspectors},
        "<=",
        10,
    )
    return p


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in [
            "id",
            "dataset_version",
            "title",
            "domain",
            "difficulty",
            "model_class",
            "source",
            "source_problem",
            "target_principle_id",
            "target_principle",
            "intro",
            "tables",
            "request",
        ]
    }


def render_prompt(record: dict[str, Any]) -> str:
    lines = [
        f"# {record['id']} — {record['title']}",
        "",
        f"Difficoltà: {record['difficulty']}",
        f"Classe: {record['model_class']}",
        "",
    ]
    for paragraph in record["intro"]:
        lines.extend([paragraph, ""])
    for table in record["tables"]:
        lines.extend([f"## {table['title']}", ""])
        headers = [str(value) for value in table["headers"]]
        lines.append(" | ".join(headers))
        lines.append(" | ".join(["---"] * len(headers)))
        for row in table["rows"]:
            lines.append(" | ".join(str(value) for value in row))
        lines.append("")
    lines.extend(["## Consegna", ""])
    for index, item in enumerate(record["request"], 1):
        lines.append(f"{index}. {item}")
    return "\n".join(lines) + "\n"


def main() -> None:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    problems = [
        problem_l01(),
        problem_l02(),
        problem_l03(),
        problem_l04(),
        problem_l05(),
    ]
    records = [problem.record() for problem in problems]

    (HERE / "ground_truth.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    public = [public_record(record) for record in records]
    (HERE / "problems.jsonl").write_text(
        "".join(
            json.dumps(record, ensure_ascii=False) + "\n" for record in public
        ),
        encoding="utf-8",
    )
    for record in records:
        (PROMPTS / f"{record['id']}.md").write_text(
            render_prompt(record), encoding="utf-8"
        )

    with (HERE / "solutions_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "dataset_version",
                "title",
                "domain",
                "model_class",
                "source_problem",
                "target_principle_id",
                "objective",
                "variables",
                "constraints",
                "runtime_seconds",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "id": record["id"],
                    "dataset_version": record["dataset_version"],
                    "title": record["title"],
                    "domain": record["domain"],
                    "model_class": record["model_class"],
                    "source_problem": record["source_problem"],
                    "target_principle_id": record["target_principle_id"],
                    "objective": record["solution"]["objective"],
                    "variables": record["dimensions"]["variables"],
                    "constraints": record["dimensions"]["constraints"],
                    "runtime_seconds": record["solution"]["runtime_seconds"],
                }
            )

    report = {
        "certified": True,
        "dataset_version": DATASET_VERSION,
        "solver": records[0]["solution"]["solver"],
        "problem_count": len(records),
        "problems": [
            {
                "id": record["id"],
                "status": record["solution"]["status"],
                "objective": record["solution"]["objective"],
                "mip_gap": record["solution"]["mip_gap"],
                "variables": record["dimensions"]["variables"],
                "constraints": record["dimensions"]["constraints"],
            }
            for record in records
        ],
    }
    (HERE / "verification_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
