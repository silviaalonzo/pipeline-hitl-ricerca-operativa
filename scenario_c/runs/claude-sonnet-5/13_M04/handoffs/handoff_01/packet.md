# Handoff 1 — M04 / claude-sonnet-5

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
| 0 | INITIAL | stop | 4428 | 214 | sì | validazione_indipendente_fallita |

## Traccia

# M04 — Composizione di una flotta giornaliera

Difficoltà: Media
Classe: IP intera

Un operatore deve scegliere quanti veicoli di ciascun tipo impiegare in una giornata. La flotta deve offrire almeno 180 unità di volume e 95 unità di portata, utilizzando almeno un mezzo refrigerato e un mezzo elettrico.
Le emissioni complessive non possono superare 145 unità. Minimizzare il costo giornaliero.

## Caratteristiche dei veicoli

Tipo | Volume | Portata | Costo | Emissioni | Disponibilità
--- | --- | --- | --- | --- | ---
Van | 18 | 8 | 120 | 12 | 8
Autocarro | 30 | 18 | 180 | 22 | 6
Refrigerato | 20 | 10 | 210 | 15 | 4
Elettrico | 16 | 7 | 150 | 4 | 5
Bilico | 42 | 28 | 260 | 32 | 3

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "M04",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 180.0,
  "constraint_violations": [
    {
      "constraint": "volume",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 180.0,
      "violation": 180.0
    },
    {
      "constraint": "peso",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 95.0,
      "violation": 95.0
    },
    {
      "constraint": "refrigerato",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 1.0,
      "violation": 1.0
    },
    {
      "constraint": "elettrico",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 1.0,
      "violation": 1.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "Autocarro",
    "Refrigerato",
    "Elettrico",
    "Bilico"
  ],
  "missing_variables_assumed_zero": [
    "x_Autocarro",
    "x_Bilico",
    "x_Elettrico",
    "x_Refrigerato",
    "x_Van"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB

# Dati
types = ["Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"]

volume = {"Van": 18, "Autocarro": 30, "Refrigerato": 20, "Elettrico": 16, "Bilico": 42}
portata = {"Van": 8, "Autocarro": 18, "Refrigerato": 10, "Elettrico": 7, "Bilico": 28}
costo = {"Van": 120, "Autocarro": 180, "Refrigerato": 210, "Elettrico": 150, "Bilico": 260}
emissioni = {"Van": 12, "Autocarro": 22, "Refrigerato": 15, "Elettrico": 4, "Bilico": 32}
disponibilita = {"Van": 8, "Autocarro": 6, "Refrigerato": 4, "Elettrico": 5, "Bilico": 3}

# Modello
m = gp.Model("composizione_flotta")

x = m.addVars(types, vtype=GRB.INTEGER, lb=0, name="x")

# Vincoli di disponibilità
for t in types:
    x[t].ub = disponibilita[t]

# Vincoli di volume e portata
m.addConstr(gp.quicksum(volume[t] * x[t] for t in types) >= 180, name="volume_min")
m.addConstr(gp.quicksum(portata[t] * x[t] for t in types) >= 95, name="portata_min")

# Almeno un refrigerato e un elettrico
m.addConstr(x["Refrigerato"] >= 1, name="min_refrigerato")
m.addConstr(x["Elettrico"] >= 1, name="min_elettrico")

# Vincolo di emissioni
m.addConstr(gp.quicksum(emissioni[t] * x[t] for t in types) <= 145, name="emissioni_max")

# Obiettivo: minimizzare il costo totale
m.setObjective(gp.quicksum(costo[t] * x[t] for t in types), GRB.MINIMIZE)

m.optimize()

status = m.Status
if status == GRB.OPTIMAL:
    obj_val = m.ObjVal
    variables = {t: x[t].X for t in types}
    import json
    print("SOLUTION_JSON=" + json.dumps({
        "status": "OPTIMAL",
        "objective": obj_val,
        "variables": variables
    }))
else:
    import json
    status_map = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }
    status_str = status_map.get(status, str(status))
    print("SOLUTION_JSON=" + json.dumps({
        "status": status_str,
        "objective": None,
        "variables": {}
    }))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
