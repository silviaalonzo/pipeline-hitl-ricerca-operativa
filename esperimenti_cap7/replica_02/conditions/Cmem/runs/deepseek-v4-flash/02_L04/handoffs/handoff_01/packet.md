# Handoff 1 — L04 / deepseek-v4-flash

- **Stadio:** 4
- **Categoria:** validazione_indipendente_fallita
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** la soluzione viola almeno un requisito del problema originale; il gap supera la soglia dello 0,1%; sono presenti variabili operative non riconosciute
- **Cicli automatici già usati:** 1
- **Ground truth mostrata:** no

## Diagnosi automatica

Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. Esaminare le violazioni e il codice riportati nel pacchetto.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 64001 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 4458 | 32868 | sì | validazione_indipendente_fallita |

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
  "max_constraint_violation": 85.0,
  "constraint_violations": [
    {
      "constraint": "balance_A_T1",
      "lhs": -67.0,
      "sense": "=",
      "rhs": 18.0,
      "violation": 85.0
    },
    {
      "constraint": "min_lot_A_T1",
      "lhs": -22.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 22.0
    },
    {
      "constraint": "balance_A_T3",
      "lhs": -25.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 60.0
    },
    {
      "constraint": "min_lot_A_T3",
      "lhs": -22.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 22.0
    },
    {
      "constraint": "balance_A_T5",
      "lhs": -28.0,
      "sense": "=",
      "rhs": 45.0,
      "violation": 73.0
    },
    {
      "constraint": "min_lot_A_T5",
      "lhs": -22.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 22.0
    },
    {
      "constraint": "balance_A_T6",
      "lhs": 13.0,
      "sense": "=",
      "rhs": 40.0,
      "violation": 27.0
    },
    {
      "constraint": "min_lot_A_T6",
      "lhs": -22.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 22.0
    },
    {
      "constraint": "balance_B_T1",
      "lhs": -36.0,
      "sense": "=",
      "rhs": 17.0,
      "violation": 53.0
    },
    {
      "constraint": "min_lot_B_T1",
      "lhs": -18.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 18.0
    },
    {
      "constraint": "balance_B_T3",
      "lhs": -16.0,
      "sense": "=",
      "rhs": 44.0,
      "violation": 60.0
    },
    {
      "constraint": "min_lot_B_T3",
      "lhs": -18.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 18.0
    },
    {
      "constraint": "balance_B_T4",
      "lhs": -32.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 70.0
    },
    {
      "constraint": "min_lot_B_T4",
      "lhs": -18.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 18.0
    },
    {
      "constraint": "balance_B_T6",
      "lhs": -8.0,
      "sense": "=",
      "rhs": 34.0,
      "violation": 42.0
    },
    {
      "constraint": "min_lot_B_T6",
      "lhs": -18.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 18.0
    },
    {
      "constraint": "balance_C_T1",
      "lhs": -10.0,
      "sense": "=",
      "rhs": 15.0,
      "violation": 25.0
    },
    {
      "constraint": "min_lot_C_T1",
      "lhs": -25.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 25.0
    },
    {
      "constraint": "balance_C_T2",
      "lhs": -54.0,
      "sense": "=",
      "rhs": 30.0,
      "violation": 84.0
    },
    {
      "constraint": "min_lot_C_T2",
      "lhs": -25.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 25.0
    },
    {
      "constraint": "balance_C_T5",
      "lhs": -39.0,
      "sense": "=",
      "rhs": 30.0,
      "violation": 69.0
    },
    {
      "constraint": "min_lot_C_T5",
      "lhs": -25.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 25.0
    },
    {
      "constraint": "balance_D_T1",
      "lhs": -18.0,
      "sense": "=",
      "rhs": 22.0,
      "violation": 40.0
    },
    {
      "constraint": "min_lot_D_T1",
      "lhs": -20.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 20.0
    },
    {
      "constraint": "balance_D_T2",
      "lhs": -27.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 62.0
    },
    {
      "constraint": "min_lot_D_T2",
      "lhs": -20.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 20.0
    },
    {
      "constraint": "balance_D_T4",
      "lhs": -38.0,
      "sense": "=",
      "rhs": 42.0,
      "violation": 80.0
    },
    {
      "constraint": "min_lot_D_T4",
      "lhs": -20.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 20.0
    },
    {
      "constraint": "balance_D_T5",
      "lhs": 18.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 20.0
    },
    {
      "constraint": "min_lot_D_T5",
      "lhs": -20.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 20.0
    },
    {
      "constraint": "balance_D_T6",
      "lhs": 8.0,
      "sense": "=",
      "rhs": 48.0,
      "violation": 40.0
    },
    {
      "constraint": "min_lot_D_T6",
      "lhs": -20.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 20.0
    },
    {
      "constraint": "balance_E_T2",
      "lhs": -14.0,
      "sense": "=",
      "rhs": 24.0,
      "violation": 38.0
    },
    {
      "constraint": "min_lot_E_T2",
      "lhs": -15.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_E_T3",
      "lhs": -10.0,
      "sense": "=",
      "rhs": 22.0,
      "violation": 32.0
    },
    {
      "constraint": "min_lot_E_T3",
      "lhs": -15.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_E_T5",
      "lhs": 1.0,
      "sense": "=",
      "rhs": 26.0,
      "violation": 25.0
    },
    {
      "constraint": "min_lot_E_T5",
      "lhs": -15.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_E_T6",
      "lhs": -5.0,
      "sense": "=",
      "rhs": 25.0,
      "violation": 30.0
    },
    {
      "constraint": "min_lot_E_T6",
      "lhs": -15.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 15.0
    },
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
    "OTact_1",
    "OTact_3",
    "Prod_A_1",
    "Prod_A_3",
    "Prod_A_5",
    "Prod_A_6",
    "Prod_B_1",
    "Prod_B_3",
    "Prod_B_4",
    "Prod_B_6",
    "Prod_C_1",
    "Prod_C_2",
    "Prod_C_5",
    "Prod_D_1",
    "Prod_D_2",
    "Prod_D_4",
    "Prod_D_5",
    "Prod_D_6",
    "Prod_E_2",
    "Prod_E_3",
    "Prod_E_5",
    "Prod_E_6"
  ],
  "missing_variables_assumed_zero": [
    "u_T1",
    "u_T2",
    "u_T3",
    "u_T4",
    "u_T5",
    "u_T6",
    "x_A_T1",
    "x_A_T2",
    "x_A_T3",
    "x_A_T4",
    "x_A_T5",
    "x_A_T6",
    "x_B_T1",
    "x_B_T2",
    "x_B_T3",
    "x_B_T4",
    "x_B_T5",
    "x_B_T6",
    "x_C_T1",
    "x_C_T2",
    "x_C_T3",
    "x_C_T4",
    "x_C_T5",
    "x_C_T6",
    "x_D_T1",
    "x_D_T2",
    "x_D_T3",
    "x_D_T4",
    "x_D_T5",
    "x_D_T6",
    "x_E_T1",
    "x_E_T2",
    "x_E_T3",
    "x_E_T4",
    "x_E_T5",
    "x_E_T6"
  ]
}
```

## Codice da esaminare

```python
import json
import gurobipy as gp
from gurobipy import GRB

products = ["A", "B", "C", "D", "E"]
periods = list(range(1, 7))

initial_stock = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
final_min_stock = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
hours_per_unit = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
lot_min = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
lot_max = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
setup_cost = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
holding_cost = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

demand = {
    ("A", 1): 38, ("A", 2): 42, ("A", 3): 35, ("A", 4): 50, ("A", 5): 45, ("A", 6): 40,
    ("B", 1): 32, ("B", 2): 36, ("B", 3): 44, ("B", 4): 38, ("B", 5): 46, ("B", 6): 34,
    ("C", 1): 25, ("C", 2): 30, ("C", 3): 28, ("C", 4): 35, ("C", 5): 30, ("C", 6): 32,
    ("D", 1): 40, ("D", 2): 35, ("D", 3): 45, ("D", 4): 42, ("D", 5): 38, ("D", 6): 48,
    ("E", 1): 20, ("E", 2): 24, ("E", 3): 22, ("E", 4): 28, ("E", 5): 26, ("E", 6): 25,
}

prod_cost = {
    ("A", 1): 4, ("A", 2): 6, ("A", 3): 8, ("A", 4): 10, ("A", 5): 5, ("A", 6): 7,
    ("B", 1): 7, ("B", 2): 9, ("B", 3): 4, ("B", 4): 6, ("B", 5): 8, ("B", 6): 10,
    ("C", 1): 10, ("C", 2): 5, ("C", 3): 7, ("C", 4): 9, ("C", 5): 4, ("C", 6): 6,
    ("D", 1): 6, ("D", 2): 8, ("D", 3): 10, ("D", 4): 5, ("D", 5): 7, ("D", 6): 9,
    ("E", 1): 9, ("E", 2): 4, ("E", 3): 6, ("E", 4): 8, ("E", 5): 10, ("E", 6): 5,
}

cap_ord = {1: 350, 2: 360, 3: 345, 4: 370, 5: 355, 6: 380}
overtime_max = {1: 85, 2: 80, 3: 90, 4: 75, 5: 85, 6: 80}
overtime_cost = {1: 7, 2: 8, 3: 7, 4: 9, 5: 8, 6: 7}
fixed_overtime = 25
min_overtime = 10

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

m = gp.Model("L04")
m.Params.OutputFlag = 0
m.Params.MIPGap = 0

Prod = m.addVars(products, periods, name="Prod", lb=0, vtype=GRB.INTEGER)
Inv = m.addVars(products, periods, name="Inv", lb=0, vtype=GRB.INTEGER)
Setup = m.addVars(products, periods, name="Setup", vtype=GRB.BINARY)
OT = m.addVars(periods, name="OT", lb=0, vtype=GRB.CONTINUOUS)
OTact = m.addVars(periods, name="OTact", vtype=GRB.BINARY)

for i in products:
    for t in periods:
        prev = initial_stock[i] if t == 1 else Inv[i, t - 1]
        m.addConstr(Inv[i, t] == prev + Prod[i, t] - demand[i, t], name=f"Balance_{i}_{t}")

for i in products:
    for t in periods:
        m.addConstr(Inv[i, t] <= 75, name=f"InvUB_{i}_{t}")

for i in products:
    m.addConstr(Inv[i, 6] >= final_min_stock[i], name=f"FinalMin_{i}")

for t in periods:
    m.addConstr(gp.quicksum(Inv[i, t] for i in products) <= 210, name=f"TotalInv_{t}")

for i in products:
    for t in periods:
        m.addConstr(Prod[i, t] <= lot_max[i] * Setup[i, t], name=f"MaxLot_{i}_{t}")
        m.addConstr(Prod[i, t] >= lot_min[i] * Setup[i, t], name=f"MinLot_{i}_{t}")

for t in periods:
    m.addConstr(gp.quicksum(Setup[i, t] for i in products) <= 4, name=f"SetupPeriod_{t}")

m.addConstr(gp.quicksum(Setup[i, t] for i in products for t in periods) <= 26, name="SetupTotal")

for t in periods:
    m.addConstr(gp.quicksum(hours_per_unit[i] * Prod[i, t] for i in products) <= cap_ord[t] + OT[t], name=f"Capacity_{t}")
    m.addConstr(OT[t] >= min_overtime * OTact[t], name=f"OTmin_{t}")
    m.addConstr(OT[t] <= overtime_max[t] * OTact[t], name=f"OTmax_{t}")

objective = (
    gp.quicksum(prod_cost[i, t] * Prod[i, t] for i in products for t in periods)
    + gp.quicksum(setup_cost[i] * Setup[i, t] for i in products for t in periods)
    + gp.quicksum(holding_cost[i] * Inv[i, t] for i in products for t in periods)
    + gp.quicksum(overtime_cost[t] * OT[t] for t in periods)
    + fixed_overtime * gp.quicksum(OTact[t] for t in periods)
)

m.setObjective(objective, GRB.MINIMIZE)
m.optimize()

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective_value = float(m.ObjVal)
    variables = {
        v.VarName: float(v.X)
        for v in sorted(m.getVars(), key=lambda var: var.VarName)
    }
else:
    status = status_names.get(m.Status, str(m.Status))
    objective_value = 0.0
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective_value, "variables": variables},
    separators=(",", ":"),
    ensure_ascii=False,
))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
