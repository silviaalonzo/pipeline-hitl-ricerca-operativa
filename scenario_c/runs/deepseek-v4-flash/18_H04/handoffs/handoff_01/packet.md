# Handoff 1 — H04 / deepseek-v4-flash

- **Stadio:** 4
- **Categoria:** validazione_indipendente_fallita
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** sono presenti variabili operative non riconosciute
- **Cicli automatici già usati:** 1
- **Ground truth mostrata:** no

## Diagnosi automatica

Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. Esaminare le violazioni e il codice riportati nel pacchetto.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 2556 | 14766 | sì | validazione_indipendente_fallita |

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
  "feasible_in_original_problem": true,
  "gap_within_tolerance": true,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 4.0,
  "constraint_violations": [
    {
      "constraint": "linkmax_R1_Medio",
      "lhs": 3.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 3.0
    },
    {
      "constraint": "linkmax_R2_Medio",
      "lhs": 4.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 4.0
    },
    {
      "constraint": "linkmax_R3_Grande",
      "lhs": 2.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 2.0
    },
    {
      "constraint": "linkmax_R4_Medio",
      "lhs": 2.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 2.0
    },
    {
      "constraint": "linkmax_R4_Grande",
      "lhs": 2.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 2.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "z_R1_Medio",
    "z_R2_Medio",
    "z_R3_Grande",
    "z_R4_Medio",
    "z_R4_Grande"
  ],
  "missing_variables_assumed_zero": [
    "y_R1_Grande",
    "y_R1_Medio",
    "y_R1_Piccolo",
    "y_R2_Grande",
    "y_R2_Medio",
    "y_R2_Piccolo",
    "y_R3_Grande",
    "y_R3_Medio",
    "y_R3_Piccolo",
    "y_R4_Grande",
    "y_R4_Medio",
    "y_R4_Piccolo"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB
import json

rotte = ["R1", "R2", "R3", "R4"]
tipi = ["Piccolo", "Medio", "Grande"]

domanda = {"R1": 42, "R2": 55, "R3": 38, "R4": 64}
capacita = {"Piccolo": 8, "Medio": 14, "Grande": 20}
disponibilita = {"Piccolo": 10, "Medio": 9, "Grande": 6}
emissioni = {"Piccolo": 5, "Medio": 8, "Grande": 11}

costo = {
    ("R1", "Piccolo"): 45, ("R1", "Medio"): 62, ("R1", "Grande"): 82,
    ("R2", "Piccolo"): 52, ("R2", "Medio"): 68, ("R2", "Grande"): 88,
    ("R3", "Piccolo"): 40, ("R3", "Medio"): 58, ("R3", "Grande"): 79,
    ("R4", "Piccolo"): 60, ("R4", "Medio"): 77, ("R4", "Grande"): 96,
}

m = gp.Model("allocazione_flotta")
m.setParam("OutputFlag", 0)

x = {}
z = {}

for r in rotte:
    for t in tipi:
        x[r, t] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{r}_{t}")
        z[r, t] = m.addVar(vtype=GRB.BINARY, name=f"z_{r}_{t}")

m.setObjective(
    gp.quicksum(costo[r, t] * x[r, t] for r in rotte for t in tipi),
    GRB.MINIMIZE,
)

for r in rotte:
    m.addConstr(
        gp.quicksum(capacita[t] * x[r, t] for t in tipi) >= domanda[r],
        name=f"domanda_{r}",
    )
    m.addConstr(
        gp.quicksum(z[r, t] for t in tipi) <= 2,
        name=f"max_tipi_{r}",
    )
    for t in tipi:
        m.addConstr(x[r, t] <= disponibilita[t] * z[r, t], name=f"link_{r}_{t}")
        m.addConstr(x[r, t] >= z[r, t], name=f"uso_{r}_{t}")

for t in tipi:
    m.addConstr(
        gp.quicksum(x[r, t] for r in rotte) <= disponibilita[t],
        name=f"disponibilita_{t}",
    )

m.addConstr(
    gp.quicksum(emissioni[t] * x[r, t] for r in rotte for t in tipi) <= 145,
    name="limite_emissioni",
)

m.addConstr(x["R4", "Grande"] >= 1, name="r4_almeno_un_grande")

m.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.NUMERIC: "NUMERIC",
}

if m.Status == GRB.OPTIMAL:
    variabili = {v.VarName: float(v.X) for v in m.getVars()}
    result = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": variabili,
    }
else:
    result = {
        "status": status_names.get(m.Status, f"STATUS_{m.Status}"),
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
