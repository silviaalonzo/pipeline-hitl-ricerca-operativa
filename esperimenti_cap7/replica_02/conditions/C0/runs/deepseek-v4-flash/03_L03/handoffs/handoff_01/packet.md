# Handoff 1 — L03 / deepseek-v4-flash

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
| 0 | INITIAL | stop | 7221 | 48895 | sì | validazione_indipendente_fallita |

## Traccia

# L03 — Approvvigionamento multi-componente da fornitori qualificati

Difficoltà: Elevata
Classe: MILP intera

Un’impresa deve acquistare sei componenti da otto fornitori. Ogni domanda deve essere soddisfatta esattamente e ogni componente deve provenire da almeno due e da non più di tre fornitori qualificati. Quando una coppia fornitore–componente viene utilizzata, deve rispettare il lotto minimo specifico del componente.

La capacità di ciascun fornitore è condivisa tra tutti i componenti e può essere utilizzata soltanto se il fornitore è attivato. Possono essere attivati al massimo sei fornitori e almeno uno tra S1 e S2. Per ogni componente la qualità media ponderata deve essere almeno 95; il rischio ponderato complessivo non può superare 1.300. Le celle «—» sono combinazioni non disponibili. Minimizzare costi fissi e di acquisto.

## Fornitori

Fornitore | Costo fisso | Capacità | Rischio unitario
--- | --- | --- | ---
S1 | 165 | 125 | 2
S2 | 150 | 115 | 3
S3 | 170 | 110 | 1
S4 | 145 | 105 | 4
S5 | 155 | 120 | 2
S6 | 140 | 100 | 3
S7 | 160 | 95 | 1
S8 | 148 | 115 | 4

## Domanda e lotto minimo

Componente | C1 | C2 | C3 | C4 | C5 | C6
--- | --- | --- | --- | --- | --- | ---
Domanda | 90 | 80 | 75 | 70 | 65 | 60
Lotto minimo | 14 | 12 | 12 | 10 | 11 | 10

## Costi unitari e disponibilità

Fornitore | C1 | C2 | C3 | C4 | C5 | C6
--- | --- | --- | --- | --- | --- | ---
S1 | 3 | 11 | 13 | — | 12 | —
S2 | 12 | 3 | — | 13 | — | 12
S3 | 10 | — | 3 | 11 | 13 | 10
S4 | — | 10 | 12 | 3 | — | 13
S5 | 11 | 13 | — | — | 3 | 11
S6 | — | 11 | 13 | 10 | 12 | —
S7 | 12 | — | 11 | — | 10 | 3
S8 | — | 12 | — | 11 | 13 | 10

## Qualità delle coppie disponibili

Fornitore | C1 | C2 | C3 | C4 | C5 | C6
--- | --- | --- | --- | --- | --- | ---
S1 | 98 | 95 | 98 | — | 97 | —
S2 | 94 | 98 | — | 96 | — | 95
S3 | 96 | — | 98 | 98 | 94 | 97
S4 | — | 94 | 97 | 98 | — | 92
S5 | 93 | 96 | — | — | 98 | 94
S6 | — | 98 | 94 | 97 | 93 | —
S7 | 97 | — | 96 | — | 95 | 98
S8 | — | 95 | — | 94 | 97 | 93

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "L03",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 97.0,
  "constraint_violations": [
    {
      "constraint": "capacity_S1",
      "lhs": 76.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 76.0
    },
    {
      "constraint": "capacity_S2",
      "lhs": 68.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 68.0
    },
    {
      "constraint": "capacity_S3",
      "lhs": 97.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 97.0
    },
    {
      "constraint": "capacity_S4",
      "lhs": 72.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 72.0
    },
    {
      "constraint": "capacity_S5",
      "lhs": 54.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 54.0
    },
    {
      "constraint": "capacity_S7",
      "lhs": 73.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 73.0
    },
    {
      "constraint": "at_least_one_S1_S2",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 1.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S1_C1",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S2_C2",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S3_C1",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S3_C3",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S3_C4",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S3_C6",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S4_C2",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S4_C4",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S5_C5",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S7_C3",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S7_C5",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    },
    {
      "constraint": "activation_S7_C6",
      "lhs": 1.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 1.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "a_S1",
    "a_S2",
    "a_S3",
    "a_S4",
    "a_S5",
    "a_S7"
  ],
  "missing_variables_assumed_zero": [
    "y_S1",
    "y_S2",
    "y_S3",
    "y_S4",
    "y_S5",
    "y_S6",
    "y_S7",
    "y_S8"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB
import json

suppliers = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
components = ["C1", "C2", "C3", "C4", "C5", "C6"]

fixed_cost = {
    "S1": 165, "S2": 150, "S3": 170, "S4": 145,
    "S5": 155, "S6": 140, "S7": 160, "S8": 148
}
capacity = {
    "S1": 125, "S2": 115, "S3": 110, "S4": 105,
    "S5": 120, "S6": 100, "S7": 95, "S8": 115
}
risk = {
    "S1": 2, "S2": 3, "S3": 1, "S4": 4,
    "S5": 2, "S6": 3, "S7": 1, "S8": 4
}

demand = {"C1": 90, "C2": 80, "C3": 75, "C4": 70, "C5": 65, "C6": 60}
min_lot = {"C1": 14, "C2": 12, "C3": 12, "C4": 10, "C5": 11, "C6": 10}

cost = {
    "S1": {"C1": 3, "C2": 11, "C3": 13, "C4": None, "C5": 12, "C6": None},
    "S2": {"C1": 12, "C2": 3, "C3": None, "C4": 13, "C5": None, "C6": 12},
    "S3": {"C1": 10, "C2": None, "C3": 3, "C4": 11, "C5": 13, "C6": 10},
    "S4": {"C1": None, "C2": 10, "C3": 12, "C4": 3, "C5": None, "C6": 13},
    "S5": {"C1": 11, "C2": 13, "C3": None, "C4": None, "C5": 3, "C6": 11},
    "S6": {"C1": None, "C2": 11, "C3": 13, "C4": 10, "C5": 12, "C6": None},
    "S7": {"C1": 12, "C2": None, "C3": 11, "C4": None, "C5": 10, "C6": 3},
    "S8": {"C1": None, "C2": 12, "C3": None, "C4": 11, "C5": 13, "C6": 10}
}

quality = {
    "S1": {"C1": 98, "C2": 95, "C3": 98, "C4": None, "C5": 97, "C6": None},
    "S2": {"C1": 94, "C2": 98, "C3": None, "C4": 96, "C5": None, "C6": 95},
    "S3": {"C1": 96, "C2": None, "C3": 98, "C4": 98, "C5": 94, "C6": 97},
    "S4": {"C1": None, "C2": 94, "C3": 97, "C4": 98, "C5": None, "C6": 92},
    "S5": {"C1": 93, "C2": 96, "C3": None, "C4": None, "C5": 98, "C6": 94},
    "S6": {"C1": None, "C2": 98, "C3": 94, "C4": 97, "C5": 93, "C6": None},
    "S7": {"C1": 97, "C2": None, "C3": 96, "C4": None, "C5": 95, "C6": 98},
    "S8": {"C1": None, "C2": 95, "C3": None, "C4": 94, "C5": 97, "C6": 93}
}

available = [(s, j) for s in suppliers for j in components if cost[s][j] is not None]

model = gp.Model("L03_approvvigionamento")
model.setParam("OutputFlag", 0)

a = {s: model.addVar(vtype=GRB.BINARY, name=f"a_{s}") for s in suppliers}
y = {(s, j): model.addVar(vtype=GRB.BINARY, name=f"y_{s}_{j}") for (s, j) in available}
x = {(s, j): model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{s}_{j}") for (s, j) in available}

model.setObjective(
    gp.quicksum(fixed_cost[s] * a[s] for s in suppliers) +
    gp.quicksum(cost[s][j] * x[(s, j)] for (s, j) in available),
    GRB.MINIMIZE
)

for j in components:
    model.addConstr(
        gp.quicksum(x[(s, j)] for s in suppliers if (s, j) in available) == demand[j],
        name=f"demand_{j}"
    )

for s in suppliers:
    model.addConstr(
        gp.quicksum(x[(s, j)] for j in components if (s, j) in available) <= capacity[s] * a[s],
        name=f"capacity_{s}"
    )

for j in components:
    model.addConstr(
        gp.quicksum(y[(s, j)] for s in suppliers if (s, j) in available) >= 2,
        name=f"min_suppliers_{j}"
    )
    model.addConstr(
        gp.quicksum(y[(s, j)] for s in suppliers if (s, j) in available) <= 3,
        name=f"max_suppliers_{j}"
    )

for (s, j) in available:
    model.addConstr(x[(s, j)] >= min_lot[j] * y[(s, j)], name=f"min_lot_{s}_{j}")
    model.addConstr(x[(s, j)] <= demand[j] * y[(s, j)], name=f"link_{s}_{j}")
    model.addConstr(y[(s, j)] <= a[s], name=f"active_{s}_{j}")

model.addConstr(gp.quicksum(a[s] for s in suppliers) <= 6, name="max_activated")
model.addConstr(a["S1"] + a["S2"] >= 1, name="at_least_S1_S2")

for j in components:
    model.addConstr(
        gp.quicksum(quality[s][j] * x[(s, j)] for s in suppliers if (s, j) in available) >= 95 * demand[j],
        name=f"quality_{j}"
    )

model.addConstr(
    gp.quicksum(risk[s] * x[(s, j)] for (s, j) in available) <= 1300,
    name="risk_total"
)

model.optimize()

if model.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = model.ObjVal
    all_vars = list(a.values()) + list(y.values()) + list(x.values())
    variables = {v.VarName: v.X for v in all_vars}
else:
    status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD"
    }.get(model.status, f"STATUS_{model.status}")
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status,
    "objective": objective,
    "variables": variables
}))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
