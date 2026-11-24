# Handoff 1 — L02 / deepseek-v4-flash

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
| 0 | INITIAL | stop | 5285 | 51276 | sì | validazione_indipendente_fallita |

## Traccia

# L02 — Pianificazione multi-prodotto di un reparto di confezionamento

Difficoltà: Elevata
Classe: MILP intera

Un reparto pianifica tre prodotti per otto periodi. Le scorte iniziali e le giacenze finali minime sono specifiche per prodotto; ogni scorta di fine periodo è intera, non negativa e non può superare 75 unità. La giacenza complessiva dei tre prodotti non può superare 150 unità in alcun periodo.

La capacità produttiva è condivisa e dipende dalle ore richieste per unità. Produrre un articolo in un periodo richiede il relativo setup: quando il setup è attivo devono essere rispettati sia il lotto minimo sia quello massimo. Sono ammessi al massimo diciotto setup complessivi e, nei periodi T3 e T6, possono essere predisposti al massimo due prodotti. Minimizzare costi di produzione, setup e scorta.

## Parametri dei prodotti

Prodotto | Scorta iniziale | Scorta finale minima | Ore/unità | Lotto minimo | Lotto massimo | Costo setup | Costo scorta
--- | --- | --- | --- | --- | --- | --- | ---
P1 | 22 | 18 | 2 | 24 | 82 | 52 | 1.2
P2 | 18 | 15 | 3 | 20 | 70 | 60 | 1.6
P3 | 25 | 20 | 1 | 28 | 90 | 45 | 0.9

## Domanda

Prodotto | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8
--- | --- | --- | --- | --- | --- | --- | --- | ---
P1 | 34 | 48 | 42 | 55 | 38 | 50 | 46 | 40
P2 | 28 | 32 | 45 | 36 | 50 | 34 | 42 | 39
P3 | 40 | 35 | 38 | 44 | 36 | 48 | 41 | 45

## Costo unitario di produzione

Prodotto | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8
--- | --- | --- | --- | --- | --- | --- | --- | ---
P1 | 5 | 8 | 5 | 8 | 5 | 8 | 5 | 8
P2 | 7 | 10 | 7 | 10 | 7 | 10 | 7 | 10
P3 | 9 | 6 | 9 | 6 | 9 | 6 | 9 | 6

## Capacità condivisa

Periodo | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8
--- | --- | --- | --- | --- | --- | --- | --- | ---
Ore disponibili | 250 | 245 | 235 | 260 | 240 | 255 | 245 | 265

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "L02",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 55.0,
  "constraint_violations": [
    {
      "constraint": "balance_P1_T1",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 12.0,
      "violation": 12.0
    },
    {
      "constraint": "balance_P1_T2",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 48.0,
      "violation": 48.0
    },
    {
      "constraint": "balance_P1_T3",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 42.0,
      "violation": 42.0
    },
    {
      "constraint": "balance_P1_T4",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 55.0,
      "violation": 55.0
    },
    {
      "constraint": "balance_P1_T5",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 38.0
    },
    {
      "constraint": "balance_P1_T6",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 50.0,
      "violation": 50.0
    },
    {
      "constraint": "balance_P1_T7",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 46.0,
      "violation": 46.0
    },
    {
      "constraint": "balance_P1_T8",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 40.0,
      "violation": 40.0
    },
    {
      "constraint": "final_P1",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 18.0,
      "violation": 18.0
    },
    {
      "constraint": "balance_P2_T1",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 10.0,
      "violation": 10.0
    },
    {
      "constraint": "balance_P2_T2",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 32.0,
      "violation": 32.0
    },
    {
      "constraint": "balance_P2_T3",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 45.0,
      "violation": 45.0
    },
    {
      "constraint": "balance_P2_T4",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 36.0,
      "violation": 36.0
    },
    {
      "constraint": "balance_P2_T5",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 50.0,
      "violation": 50.0
    },
    {
      "constraint": "balance_P2_T6",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 34.0,
      "violation": 34.0
    },
    {
      "constraint": "balance_P2_T7",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 42.0,
      "violation": 42.0
    },
    {
      "constraint": "balance_P2_T8",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 39.0,
      "violation": 39.0
    },
    {
      "constraint": "final_P2",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 15.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_P3_T1",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 15.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_P3_T2",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 35.0
    },
    {
      "constraint": "balance_P3_T3",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 38.0
    },
    {
      "constraint": "balance_P3_T4",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 44.0,
      "violation": 44.0
    },
    {
      "constraint": "balance_P3_T5",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 36.0,
      "violation": 36.0
    },
    {
      "constraint": "balance_P3_T6",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 48.0,
      "violation": 48.0
    },
    {
      "constraint": "balance_P3_T7",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 41.0,
      "violation": 41.0
    },
    {
      "constraint": "balance_P3_T8",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 45.0,
      "violation": 45.0
    },
    {
      "constraint": "final_P3",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 20.0,
      "violation": 20.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "x_0_0",
    "x_0_2",
    "x_0_4",
    "x_0_6",
    "x_0_7",
    "x_1_0",
    "x_1_1",
    "x_1_2",
    "x_1_3",
    "x_1_4",
    "x_1_5",
    "x_1_6",
    "x_1_7",
    "x_2_0",
    "x_2_1",
    "x_2_3",
    "x_2_5",
    "x_2_7",
    "y_0_0",
    "y_0_2",
    "y_0_4",
    "y_0_6",
    "y_0_7",
    "y_1_0",
    "y_1_1",
    "y_1_2",
    "y_1_3",
    "y_1_4",
    "y_1_5",
    "y_1_6",
    "y_1_7",
    "y_2_0",
    "y_2_1",
    "y_2_3",
    "y_2_5",
    "y_2_7",
    "s_0_0",
    "s_0_1",
    "s_0_2",
    "s_0_3",
    "s_0_4",
    "s_0_6",
    "s_0_7",
    "s_1_0",
    "s_1_1",
    "s_1_2",
    "s_1_3",
    "s_1_5",
    "s_1_6",
    "s_1_7",
    "s_2_0",
    "s_2_1",
    "s_2_3",
    "s_2_5",
    "s_2_7"
  ],
  "missing_variables_assumed_zero": [
    "I_P1_T1",
    "I_P1_T2",
    "I_P1_T3",
    "I_P1_T4",
    "I_P1_T5",
    "I_P1_T6",
    "I_P1_T7",
    "I_P1_T8",
    "I_P2_T1",
    "I_P2_T2",
    "I_P2_T3",
    "I_P2_T4",
    "I_P2_T5",
    "I_P2_T6",
    "I_P2_T7",
    "I_P2_T8",
    "I_P3_T1",
    "I_P3_T2",
    "I_P3_T3",
    "I_P3_T4",
    "I_P3_T5",
    "I_P3_T6",
    "I_P3_T7",
    "I_P3_T8",
    "x_P1_T1",
    "x_P1_T2",
    "x_P1_T3",
    "x_P1_T4",
    "x_P1_T5",
    "x_P1_T6",
    "x_P1_T7",
    "x_P1_T8",
    "x_P2_T1",
    "x_P2_T2",
    "x_P2_T3",
    "x_P2_T4",
    "x_P2_T5",
    "x_P2_T6",
    "x_P2_T7",
    "x_P2_T8",
    "x_P3_T1",
    "x_P3_T2",
    "x_P3_T3",
    "x_P3_T4",
    "x_P3_T5",
    "x_P3_T6",
    "x_P3_T7",
    "x_P3_T8",
    "y_P1_T1",
    "y_P1_T2",
    "y_P1_T3",
    "y_P1_T4",
    "y_P1_T5",
    "y_P1_T6",
    "y_P1_T7",
    "y_P1_T8",
    "y_P2_T1",
    "y_P2_T2",
    "y_P2_T3",
    "y_P2_T4",
    "y_P2_T5",
    "y_P2_T6",
    "y_P2_T7",
    "y_P2_T8",
    "y_P3_T1",
    "y_P3_T2",
    "y_P3_T3",
    "y_P3_T4",
    "y_P3_T5",
    "y_P3_T6",
    "y_P3_T7",
    "y_P3_T8"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB
import json

# Dati dalla traccia
I = [0, 1, 2]
T = list(range(8))

s0 = {0: 22, 1: 18, 2: 25}
fmin = {0: 18, 1: 15, 2: 20}
a = {0: 2, 1: 3, 2: 1}
Lmin = {0: 24, 1: 20, 2: 28}
Lmax = {0: 82, 1: 70, 2: 90}
sc = {0: 52, 1: 60, 2: 45}
h = {0: 1.2, 1: 1.6, 2: 0.9}

d = {
    0: [34, 48, 42, 55, 38, 50, 46, 40],
    1: [28, 32, 45, 36, 50, 34, 42, 39],
    2: [40, 35, 38, 44, 36, 48, 41, 45],
}

pc = {
    0: [5, 8, 5, 8, 5, 8, 5, 8],
    1: [7, 10, 7, 10, 7, 10, 7, 10],
    2: [9, 6, 9, 6, 9, 6, 9, 6],
}

C = [250, 245, 235, 260, 240, 255, 245, 265]

m = gp.Model("L02")
m.setParam("OutputFlag", 0)

# Variabili
x = m.addVars(I, T, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(I, T, vtype=GRB.BINARY, name="y")
s = m.addVars(I, T, vtype=GRB.INTEGER, lb=0, ub=75, name="s")

# Funzione obiettivo
m.setObjective(
    gp.quicksum(pc[i][t] * x[i, t] + sc[i] * y[i, t] + h[i] * s[i, t]
                for i in I for t in T),
    GRB.MINIMIZE
)

# Bilancio di scorta
m.addConstrs((s0[i] + x[i, 0] == d[i][0] + s[i, 0] for i in I), name="bal0")
m.addConstrs((s[i, t - 1] + x[i, t] == d[i][t] + s[i, t]
              for i in I for t in range(1, 8)), name="bal")

# Scorta finale minima
m.addConstrs((s[i, 7] >= fmin[i] for i in I), name="final_inv")

# Capacità condivisa
m.addConstrs((gp.quicksum(a[i] * x[i, t] for i in I) <= C[t] for t in T),
             name="capacity")

# Vincoli di setup e lotto minimo/massimo
m.addConstrs((x[i, t] >= Lmin[i] * y[i, t] for i in I for t in T), name="lot_min")
m.addConstrs((x[i, t] <= Lmax[i] * y[i, t] for i in I for t in T), name="lot_max")

# Limite complessivo ai setup
m.addConstr(gp.quicksum(y[i, t] for i in I for t in T) <= 18, name="max_setups")

# Limite T3 e T6: al massimo due prodotti in setup
m.addConstrs((gp.quicksum(y[i, t] for i in I) <= 2 for t in [2, 5]),
             name="max_two_T3_T6")

# Giacenza complessiva massima
m.addConstrs((gp.quicksum(s[i, t] for i in I) <= 150 for t in T),
             name="total_inventory")

m.optimize()

# Stampa finale richiesta
if m.Status == GRB.OPTIMAL:
    sol_status = "OPTIMAL"
    objective = m.ObjVal
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
    }
    sol_status = status_map.get(m.Status, "UNKNOWN")
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": sol_status,
    "objective": objective,
    "variables": variables
}))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
