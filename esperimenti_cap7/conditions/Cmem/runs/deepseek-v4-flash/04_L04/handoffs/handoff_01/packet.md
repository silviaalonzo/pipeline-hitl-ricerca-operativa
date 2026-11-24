# Handoff 1 — L04 / deepseek-v4-flash

- **Stadio:** 4
- **Categoria:** validazione_indipendente_fallita
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** la soluzione viola almeno un requisito del problema originale; il gap supera la soglia dello 0,1%; sono presenti variabili operative non riconosciute
- **Cicli automatici già usati:** 0
- **Ground truth mostrata:** no

## Diagnosi automatica

Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. Esaminare le violazioni e il codice riportati nel pacchetto.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | stop | 8018 | 25489 | sì | validazione_indipendente_fallita |

## Traccia

# L04 — Produzione multi-prodotto con straordinario attivabile

Difficoltà: Elevata
Classe: MILP intera

Un impianto pianifica cinque prodotti per sei periodi. Per ogni prodotto sono note scorta iniziale, scorta finale minima, ore per unità e limiti di lotto. La scorta di ciascun prodotto non può superare 75 unità e la giacenza complessiva a fine periodo non può superare 210 unità.

La capacità ordinaria è condivisa. Lo straordinario è capacità aggiuntiva: in ogni periodo richiede un’attivazione dal costo fisso di 25, può essere acquistato soltanto in quantità comprese tra 10 ore e il massimo indicato e ha il costo unitario riportato in tabella. La produzione richiede un setup e deve rispettare lotto minimo e massimo. Sono consentiti al massimo ventisei setup complessivi e non più di quattro per periodo. Minimizzare produzione, setup, scorte e straordinario.

## Parametri dei prodotti

Prodotto | Scorta iniziale | Scorta finale minima | Ore/unità | Lotto minimo | Lotto massimo | Costo setup | Costo scorta
--- | --- | --- | --- | --- | --- | --- | ---
A | 20 | 15 | 2 | 22 | 85 | 48 | 1.1
B | 15 | 10 | 3 | 18 | 75 | 55 | 1.4
C | 10 | 8 | 1 | 25 | 90 | 40 | 0.8
D | 18 | 12 | 2 | 20 | 80 | 52 | 1.2
E | 25 | 5 | 4 | 15 | 65 | 45 | 1.5

## Domanda

Prodotto | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
A | 38 | 42 | 35 | 50 | 45 | 40
B | 32 | 36 | 44 | 38 | 46 | 34
C | 25 | 30 | 28 | 35 | 30 | 32
D | 40 | 35 | 45 | 42 | 38 | 48
E | 20 | 24 | 22 | 28 | 26 | 25

## Costi unitari di produzione

Prodotto | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
A | 4 | 6 | 8 | 10 | 5 | 7
B | 7 | 9 | 4 | 6 | 8 | 10
C | 10 | 5 | 7 | 9 | 4 | 6
D | 6 | 8 | 10 | 5 | 7 | 9
E | 9 | 4 | 6 | 8 | 10 | 5

## Capacità e straordinario

Voce | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
Capacità ordinaria | 350 | 360 | 345 | 370 | 355 | 380
Straordinario massimo | 85 | 80 | 90 | 75 | 85 | 80
Costo unitario straordinario | 7 | 8 | 7 | 9 | 8 | 7

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "L04",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 84.0,
  "constraint_violations": [
    {
      "constraint": "overtime_upper_T1",
      "lhs": 84.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 84.0
    },
    {
      "constraint": "overtime_upper_T3",
      "lhs": 83.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 83.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "z_T1",
    "z_T3"
  ],
  "missing_variables_assumed_zero": [
    "u_T1",
    "u_T2",
    "u_T3",
    "u_T4",
    "u_T5",
    "u_T6"
  ]
}
```

## Codice da esaminare

```python
import json
import gurobipy as gp
from gurobipy import GRB

products = ["A", "B", "C", "D", "E"]
periods = ["T1", "T2", "T3", "T4", "T5", "T6"]

initial_stock = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
final_min = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
hours = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
lot_min = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
lot_max = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
holding_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

demand_data = {
    "A": [38, 42, 35, 50, 45, 40],
    "B": [32, 36, 44, 38, 46, 34],
    "C": [25, 30, 28, 35, 30, 32],
    "D": [40, 35, 45, 42, 38, 48],
    "E": [20, 24, 22, 28, 26, 25]
}
demand = {p: {periods[i]: v for i, v in enumerate(vals)} for p, vals in demand_data.items()}

production_cost_data = {
    "A": [4, 6, 8, 10, 5, 7],
    "B": [7, 9, 4, 6, 8, 10],
    "C": [10, 5, 7, 9, 4, 6],
    "D": [6, 8, 10, 5, 7, 9],
    "E": [9, 4, 6, 8, 10, 5]
}
production_cost = {p: {periods[i]: v for i, v in enumerate(vals)} for p, vals in production_cost_data.items()}

capacity = {"T1": 350, "T2": 360, "T3": 345, "T4": 370, "T5": 355, "T6": 380}
ot_max = {"T1": 85, "T2": 80, "T3": 90, "T4": 75, "T5": 85, "T6": 80}
ot_cost = {"T1": 7, "T2": 8, "T3": 7, "T4": 9, "T5": 8, "T6": 7}

fixed_ot = 25
stock_max = 75
total_stock_max = 210
max_total_setups = 26
max_period_setups = 4

m = gp.Model("L04")
m.Params.OutputFlag = 0

x = m.addVars(products, periods, lb=0, vtype=GRB.INTEGER, name="x")
s = m.addVars(products, periods, lb=0, vtype=GRB.INTEGER, name="s")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")
o = m.addVars(periods, lb=0, vtype=GRB.INTEGER, name="o")
z = m.addVars(periods, vtype=GRB.BINARY, name="z")

# Bilanci di scorta
for p in products:
    for idx, t in enumerate(periods):
        if idx == 0:
            m.addConstr(s[p, t] == initial_stock[p] + x[p, t] - demand[p][t], name=f"balance_{p}_{t}")
        else:
            prev = periods[idx - 1]
            m.addConstr(s[p, t] == s[p, prev] + x[p, t] - demand[p][t], name=f"balance_{p}_{t}")

# Setup e limiti di lotto
for p in products:
    for t in periods:
        m.addConstr(x[p, t] >= lot_min[p] * y[p, t], name=f"lotmin_{p}_{t}")
        m.addConstr(x[p, t] <= lot_max[p] * y[p, t], name=f"lotmax_{p}_{t}")

# Limiti di scorta
for p in products:
    for t in periods:
        m.addConstr(s[p, t] <= stock_max, name=f"stockmax_{p}_{t}")

for t in periods:
    m.addConstr(gp.quicksum(s[p, t] for p in products) <= total_stock_max, name=f"totalstock_{t}")

# Scorta finale minima
for p in products:
    m.addConstr(s[p, "T6"] >= final_min[p], name=f"final_{p}")

# Capacità ordinaria e straordinario
for t in periods:
    m.addConstr(gp.quicksum(hours[p] * x[p, t] for p in products) <= capacity[t] + o[t], name=f"capacity_{t}")

for t in periods:
    m.addConstr(o[t] >= 10 * z[t], name=f"otmin_{t}")
    m.addConstr(o[t] <= ot_max[t] * z[t], name=f"otmax_{t}")

# Limiti sui setup
m.addConstr(gp.quicksum(y[p, t] for p in products for t in periods) <= max_total_setups, name="total_setups")

for t in periods:
    m.addConstr(gp.quicksum(y[p, t] for p in products) <= max_period_setups, name=f"setups_{t}")

# Funzione obiettivo
obj = gp.quicksum(production_cost[p][t] * x[p, t] for p in products for t in periods)
obj += gp.quicksum(setup_cost[p] * y[p, t] for p in products for t in periods)
obj += gp.quicksum(holding_cost[p] * s[p, t] for p in products for t in periods)
obj += fixed_ot * gp.quicksum(z[t] for t in periods)
obj += gp.quicksum(ot_cost[t] * o[t] for t in periods)

m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

if m.status == GRB.OPTIMAL:
    variables = {}
    for p in products:
        for t in periods:
            variables[f"x_{p}_{t}"] = x[p, t].X
            variables[f"s_{p}_{t}"] = s[p, t].X
            variables[f"y_{p}_{t}"] = y[p, t].X
    for t in periods:
        variables[f"o_{t}"] = o[t].X
        variables[f"z_{t}"] = z[t].X

    solution = {
        "status": "OPTIMAL",
        "objective": m.ObjVal,
        "variables": variables
    }
else:
    status_names = {
        1: "LOADED", 2: "OPTIMAL", 3: "INFEASIBLE",
        4: "INF_OR_UNBD", 5: "UNBOUNDED", 6: "CUTOFF",
        7: "ITERATION_LIMIT", 8: "NODE_LIMIT", 9: "TIME_LIMIT",
        10: "SOLUTION_LIMIT", 11: "INTERRUPTED", 12: "NUMERIC",
        13: "SUBOPTIMAL", 14: "INPROGRESS", 15: "USER_OBJ_LIMIT"
    }
    solution = {
        "status": status_names.get(m.status, str(m.status)),
        "objective": None,
        "variables": {}
    }

print("SOLUTION_JSON=" + json.dumps(solution))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
