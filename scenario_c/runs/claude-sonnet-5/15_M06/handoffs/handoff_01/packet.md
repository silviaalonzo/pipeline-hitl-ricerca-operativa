# Handoff 1 — M06 / claude-sonnet-5

- **Stadio:** 4
- **Categoria:** validazione_indipendente_fallita
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** sono presenti variabili operative non riconosciute
- **Cicli automatici già usati:** 0
- **Ground truth mostrata:** no

## Diagnosi automatica

Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. Esaminare le violazioni e il codice riportati nel pacchetto.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | stop | 4741 | 5322 | sì | validazione_indipendente_fallita |

## Traccia

# M06 — Bilanciamento di lavori su due macchine

Difficoltà: Media
Classe: MILP intera

Sette lavori indipendenti devono essere assegnati a due macchine parallele. Ogni lavoro va eseguito interamente su una sola macchina; i tempi dipendono dalla macchina scelta.
J7 non è compatibile con la macchina A. Tutti i lavori sono disponibili all’inizio e ogni macchina esegue i lavori assegnati in sequenza. Minimizzare il makespan, cioè il maggiore tra i carichi delle due macchine.

## Tempi di lavorazione

Lavoro | Macchina A | Macchina B
--- | --- | ---
J1 | 7 | 9
J2 | 6 | 5
J3 | 8 | 7
J4 | 5 | 8
J5 | 9 | 6
J6 | 4 | 7
J7 | — | 5

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "M06",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": true,
  "gap_within_tolerance": true,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 0.0,
  "constraint_violations": [],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "Load_A",
    "Load_B"
  ],
  "missing_variables_assumed_zero": [
    "x_J7_A"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB

# Dati
jobs = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
machines = ["A", "B"]

# tempi di lavorazione: solo le coppie ammesse
p = {
    ("J1", "A"): 7, ("J1", "B"): 9,
    ("J2", "A"): 6, ("J2", "B"): 5,
    ("J3", "A"): 8, ("J3", "B"): 7,
    ("J4", "A"): 5, ("J4", "B"): 8,
    ("J5", "A"): 9, ("J5", "B"): 6,
    ("J6", "A"): 4, ("J6", "B"): 7,
    ("J7", "B"): 5,  # J7 non compatibile con A
}

allowed_pairs = list(p.keys())

# Machine ammesse per ciascun lavoro
machines_for_job = {j: [m for (jj, m) in allowed_pairs if jj == j] for j in jobs}

model = gp.Model("Bilanciamento_2_macchine")

# Variabili decisionali
x = model.addVars(allowed_pairs, vtype=GRB.BINARY, name="x")
Load = model.addVars(machines, vtype=GRB.CONTINUOUS, lb=0.0, name="Load")
Cmax = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="Cmax")

# Vincolo: ogni lavoro assegnato a esattamente una macchina ammessa
for j in jobs:
    model.addConstr(
        gp.quicksum(x[j, m] for m in machines_for_job[j]) == 1,
        name=f"assign_{j}"
    )

# Vincolo: definizione del carico di ciascuna macchina
for m in machines:
    model.addConstr(
        Load[m] == gp.quicksum(p[j, m] * x[j, m] for j in jobs if (j, m) in p),
        name=f"load_{m}"
    )

# Vincolo: makespan >= carico di ogni macchina
for m in machines:
    model.addConstr(Cmax >= Load[m], name=f"makespan_{m}")

# Funzione obiettivo
model.setObjective(Cmax, GRB.MINIMIZE)

model.optimize()

import json

status = model.Status
if status == GRB.OPTIMAL:
    variables = {}
    for (j, m) in allowed_pairs:
        variables[f"x_{j}_{m}"] = round(x[j, m].X, 4)
    for m in machines:
        variables[f"Load_{m}"] = round(Load[m].X, 4)
    variables["Cmax"] = round(Cmax.X, 4)
    objective = round(model.ObjVal, 4)
    print(f"SOLUTION_JSON={json.dumps({'status': 'OPTIMAL', 'objective': objective, 'variables': variables})}")
else:
    status_name = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }.get(status, "NOT_OPTIMAL")
    print(f"SOLUTION_JSON={json.dumps({'status': status_name, 'objective': None, 'variables': {}})}")
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
