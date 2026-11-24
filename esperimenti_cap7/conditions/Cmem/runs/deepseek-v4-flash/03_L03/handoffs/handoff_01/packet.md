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
| 0 | INITIAL | stop | 6743 | 60355 | sì | validazione_indipendente_fallita |

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
      "constraint": "min_sources_C1",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
    {
      "constraint": "min_sources_C2",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
    {
      "constraint": "min_sources_C3",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
    {
      "constraint": "min_sources_C4",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
    {
      "constraint": "min_sources_C5",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
    {
      "constraint": "min_sources_C6",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 2.0,
      "violation": 2.0
    },
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
      "constraint": "upper_link_S1_C1",
      "lhs": 76.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 76.0
    },
    {
      "constraint": "upper_link_S2_C2",
      "lhs": 68.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 68.0
    },
    {
      "constraint": "upper_link_S3_C1",
      "lhs": 14.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 14.0
    },
    {
      "constraint": "upper_link_S3_C3",
      "lhs": 63.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 63.0
    },
    {
      "constraint": "upper_link_S3_C4",
      "lhs": 10.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 10.0
    },
    {
      "constraint": "upper_link_S3_C6",
      "lhs": 10.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 10.0
    },
    {
      "constraint": "upper_link_S4_C2",
      "lhs": 12.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 12.0
    },
    {
      "constraint": "upper_link_S4_C4",
      "lhs": 60.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 60.0
    },
    {
      "constraint": "upper_link_S5_C5",
      "lhs": 54.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 54.0
    },
    {
      "constraint": "upper_link_S7_C3",
      "lhs": 12.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 12.0
    },
    {
      "constraint": "upper_link_S7_C5",
      "lhs": 11.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 11.0
    },
    {
      "constraint": "upper_link_S7_C6",
      "lhs": 50.0,
      "sense": "<=",
      "rhs": 0.0,
      "violation": 50.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "y_S1_C1",
    "y_S2_C2",
    "y_S3_C1",
    "y_S3_C3",
    "y_S3_C4",
    "y_S3_C6",
    "y_S4_C2",
    "y_S4_C4",
    "y_S5_C5",
    "y_S7_C3",
    "y_S7_C5",
    "y_S7_C6",
    "z_S1",
    "z_S2",
    "z_S3",
    "z_S4",
    "z_S5",
    "z_S7"
  ],
  "missing_variables_assumed_zero": [
    "y_S1",
    "y_S2",
    "y_S3",
    "y_S4",
    "y_S5",
    "y_S6",
    "y_S7",
    "y_S8",
    "z_S1_C1",
    "z_S1_C2",
    "z_S1_C3",
    "z_S1_C5",
    "z_S2_C1",
    "z_S2_C2",
    "z_S2_C4",
    "z_S2_C6",
    "z_S3_C1",
    "z_S3_C3",
    "z_S3_C4",
    "z_S3_C5",
    "z_S3_C6",
    "z_S4_C2",
    "z_S4_C3",
    "z_S4_C4",
    "z_S4_C6",
    "z_S5_C1",
    "z_S5_C2",
    "z_S5_C5",
    "z_S5_C6",
    "z_S6_C2",
    "z_S6_C3",
    "z_S6_C4",
    "z_S6_C5",
    "z_S7_C1",
    "z_S7_C3",
    "z_S7_C5",
    "z_S7_C6",
    "z_S8_C2",
    "z_S8_C4",
    "z_S8_C5",
    "z_S8_C6"
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

A = [(i, j) for i in suppliers for j in components if cost[i][j] is not None]

m = gp.Model("procurement_milp")
m.setParam("OutputFlag", 0)

x = {}
y = {}
for (i, j) in A:
    x[i, j] = m.addVar(lb=0, vtype=GRB.INTEGER, name=f"x_{i}_{j}")
    y[i, j] = m.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j}")

z = {i: m.addVar(vtype=GRB.BINARY, name=f"z_{i}") for i in suppliers}

m.setObjective(
    gp.quicksum(fixed_cost[i] * z[i] for i in suppliers)
    + gp.quicksum(cost[i][j] * x[i, j] for (i, j) in A),
    GRB.MINIMIZE
)

# Domanda esatta
for j in components:
    m.addConstr(
        gp.quicksum(x[i, cc] for (i, cc) in A if cc == j) == demand[j],
        name=f"demand_{j}"
    )

# Lotto minimo e legame quantità-uso
for (i, j) in A:
    m.addConstr(x[i, j] >= min_lot[j] * y[i, j], name=f"lot_{i}_{j}")
    m.addConstr(x[i, j] <= demand[j] * y[i, j], name=f"link_{i}_{j}")

# Capacità del fornitore attivato
for i in suppliers:
    m.addConstr(
        gp.quicksum(x[ii, cc] for (ii, cc) in A if ii == i) <= capacity[i] * z[i],
        name=f"cap_{i}"
    )

# Da 2 a 3 fornitori per componente
for j in components:
    m.addConstr(
        gp.quicksum(y[i, cc] for (i, cc) in A if cc == j) >= 2,
        name=f"min_suppliers_{j}"
    )
    m.addConstr(
        gp.quicksum(y[i, cc] for (i, cc) in A if cc == j) <= 3,
        name=f"max_suppliers_{j}"
    )

# Attivazione fornitori
m.addConstr(gp.quicksum(z[i] for i in suppliers) <= 6, name="max_active")
m.addConstr(z["S1"] + z["S2"] >= 1, name="at_least_s1_s2")

# Qualità media per componente
for j in components:
    m.addConstr(
        gp.quicksum(quality[i][cc] * x[i, cc] for (i, cc) in A if cc == j) >= 95 * demand[j],
        name=f"quality_{j}"
    )

# Rischio complessivo
m.addConstr(
    gp.quicksum(risk[i] * x[i, j] for (i, j) in A) <= 1300,
    name="risk"
)

m.optimize()

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: v.X for v in m.getVars()}
else:
    status = f"STATUS_{m.status}"
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({"status": status, "objective": objective, "variables": variables}))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
