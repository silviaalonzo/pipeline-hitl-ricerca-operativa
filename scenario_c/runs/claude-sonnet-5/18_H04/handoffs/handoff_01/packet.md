# Handoff 1 — H04 / claude-sonnet-5

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
| 0 | INITIAL | stop | 5531 | 1524 | sì | validazione_indipendente_fallita |

## Traccia

# H04 — Allocazione della flotta su più rotte

Difficoltà: Elevata
Classe: MILP intera

Un’impresa deve assegnare viaggi di tre tipi di veicolo a quattro rotte. La capacità complessiva assegnata a ogni rotta deve coprirne la domanda. La disponibilità di ciascun tipo è condivisa tra tutte le rotte.
Per contenere la complessità operativa, su ogni rotta possono essere usati al massimo due tipi di veicolo. Sulla rotta R4 deve essere impiegato almeno un veicolo grande. Le emissioni totali non possono superare 145 unità.
Minimizzare il costo totale dei viaggi.

## Domanda per rotta

Rotta | R1 | R2 | R3 | R4
--- | --- | --- | --- | ---
Domanda | 42 | 55 | 38 | 64

## Flotta

Tipo | Capacità/viaggio | Disponibilità | Emissioni/viaggio
--- | --- | --- | ---
Piccolo | 8 | 10 | 5
Medio | 14 | 9 | 8
Grande | 20 | 6 | 11

## Costo di un viaggio

Rotta | Piccolo | Medio | Grande
--- | --- | --- | ---
R1 | 45 | 62 | 82
R2 | 52 | 68 | 88
R3 | 40 | 58 | 79
R4 | 60 | 77 | 96

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "H04",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 38.0,
  "constraint_violations": [
    {
      "constraint": "domanda_R3",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 38.0,
      "violation": 38.0
    },
    {
      "constraint": "linkmin_R3_Medio",
      "lhs": -1.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "domanda_R4",
      "lhs": 28.0,
      "sense": ">=",
      "rhs": 64.0,
      "violation": 36.0
    },
    {
      "constraint": "grande_R4",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 1.0,
      "violation": 1.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "x_R3_L",
    "x_R4_L",
    "y_R1_L",
    "y_R2_L",
    "y_R3_L",
    "y_R4_L"
  ],
  "missing_variables_assumed_zero": [
    "x_R1_Grande",
    "x_R1_Piccolo",
    "x_R2_Grande",
    "x_R2_Piccolo",
    "x_R3_Grande",
    "x_R3_Piccolo",
    "x_R4_Grande",
    "x_R4_Piccolo",
    "y_R1_Grande",
    "y_R1_Piccolo",
    "y_R2_Grande",
    "y_R2_Piccolo",
    "y_R3_Grande",
    "y_R3_Piccolo",
    "y_R4_Grande",
    "y_R4_Piccolo"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB

# ------------------- Dati -------------------
R = ["R1", "R2", "R3", "R4"]
T = ["S", "M", "L"]  # Piccolo, Medio, Grande

demand = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}

cap   = {"S": 8,  "M": 14, "L": 20}
avail = {"S": 10, "M": 9,  "L": 6}
emis  = {"S": 5,  "M": 8,  "L": 11}

cost = {
    ("R1", "S"): 45, ("R1", "M"): 62, ("R1", "L"): 82,
    ("R2", "S"): 52, ("R2", "M"): 68, ("R2", "L"): 88,
    ("R3", "S"): 40, ("R3", "M"): 58, ("R3", "L"): 79,
    ("R4", "S"): 60, ("R4", "M"): 77, ("R4", "L"): 96,
}

MAXTYPES = 2
EMIS_MAX = 145
BigM = avail  # limite superiore naturale per x[r,t]

# ------------------- Modello -------------------
m = gp.Model("H04_allocazione_flotta")

x = m.addVars(R, T, vtype=GRB.INTEGER, lb=0, name="x")
y = m.addVars(R, T, vtype=GRB.BINARY, name="y")

# Obiettivo: minimizzare il costo totale
m.setObjective(
    gp.quicksum(cost[r, t] * x[r, t] for r in R for t in T),
    GRB.MINIMIZE
)

# 1. Copertura della domanda
for r in R:
    m.addConstr(
        gp.quicksum(cap[t] * x[r, t] for t in T) >= demand[r],
        name=f"demand_{r}"
    )

# 2. Disponibilità totale per tipo
for t in T:
    m.addConstr(
        gp.quicksum(x[r, t] for r in R) <= avail[t],
        name=f"avail_{t}"
    )

# 3. Al massimo due tipi per rotta
for r in R:
    m.addConstr(
        gp.quicksum(y[r, t] for t in T) <= MAXTYPES,
        name=f"maxtypes_{r}"
    )

# 4. Collegamento x-y (big-M)
for r in R:
    for t in T:
        m.addConstr(
            x[r, t] <= BigM[t] * y[r, t],
            name=f"link_{r}_{t}"
        )

# 5. R4 almeno un veicolo grande
m.addConstr(x["R4", "L"] >= 1, name="R4_large_min")

# 6. Limite emissioni totali
m.addConstr(
    gp.quicksum(emis[t] * x[r, t] for r in R for t in T) <= EMIS_MAX,
    name="emissions_limit"
)

# ------------------- Risoluzione -------------------
m.optimize()

status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for r in R:
        for t in T:
            variables[f"x_{r}_{t}"] = round(x[r, t].X, 4)
    for r in R:
        for t in T:
            variables[f"y_{r}_{t}"] = round(y[r, t].X, 4)
    result["variables"] = variables
else:
    result["status"] = str(status)

import json
print(f"SOLUTION_JSON={json.dumps(result)}")
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
