# Handoff 1 — H06 / deepseek-v4-flash

- **Stadio:** 4
- **Categoria:** validazione_indipendente_fallita
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** la soluzione viola almeno un requisito del problema originale; il gap supera la soglia dello 0,1%; sono presenti variabili operative non riconosciute
- **Cicli automatici già usati:** 3
- **Ground truth mostrata:** no

## Diagnosi automatica

Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. Esaminare le violazioni e il codice riportati nel pacchetto.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 3 | AUTO_REPAIR | stop | 1999 | 17426 | sì | validazione_indipendente_fallita |

## Traccia

# H06 — Sequenziamento con ritardi pesati

Difficoltà: Elevata
Classe: MILP intera

Sette lavori devono essere sequenziati senza sovrapposizioni su una sola macchina. Ogni lavoro ha durata, data di disponibilità, scadenza e peso di priorità.
J1 deve terminare prima dell’inizio di J2; J3 deve terminare prima dell’inizio di J5. Il ritardo di un lavoro è max(0, completamento − scadenza).
Minimizzare la somma dei ritardi moltiplicati per i rispettivi pesi. Modellare la non sovrapposizione mediante variabili binarie di ordinamento e una costante big-M giustificata.

## Dati dei lavori

Lavoro | Durata | Disponibilità | Scadenza | Peso
--- | --- | --- | --- | ---
J1 | 5 | 0 | 9 | 4
J2 | 7 | 0 | 17 | 3
J3 | 4 | 2 | 12 | 5
J4 | 6 | 3 | 22 | 2
J5 | 3 | 5 | 15 | 6
J6 | 8 | 0 | 28 | 2
J7 | 5 | 6 | 25 | 4

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "H06",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 14.0,
  "constraint_violations": [
    {
      "constraint": "completion_J1",
      "lhs": 7.0,
      "sense": "=",
      "rhs": 5.0,
      "violation": 2.0
    },
    {
      "constraint": "tardiness_J1",
      "lhs": -17.0,
      "sense": ">=",
      "rhs": -9.0,
      "violation": 8.0
    },
    {
      "constraint": "completion_J2",
      "lhs": 4.0,
      "sense": "=",
      "rhs": 7.0,
      "violation": 3.0
    },
    {
      "constraint": "completion_J3",
      "lhs": 6.0,
      "sense": "=",
      "rhs": 4.0,
      "violation": 2.0
    },
    {
      "constraint": "tardiness_J3",
      "lhs": -22.0,
      "sense": ">=",
      "rhs": -12.0,
      "violation": 10.0
    },
    {
      "constraint": "completion_J4",
      "lhs": 3.0,
      "sense": "=",
      "rhs": 6.0,
      "violation": 3.0
    },
    {
      "constraint": "completion_J5",
      "lhs": 8.0,
      "sense": "=",
      "rhs": 3.0,
      "violation": 5.0
    },
    {
      "constraint": "tardiness_J5",
      "lhs": -28.0,
      "sense": ">=",
      "rhs": -15.0,
      "violation": 13.0
    },
    {
      "constraint": "completion_J6",
      "lhs": 5.0,
      "sense": "=",
      "rhs": 8.0,
      "violation": 3.0
    },
    {
      "constraint": "completion_J7",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 5.0,
      "violation": 5.0
    },
    {
      "constraint": "ordine2_J1_J4",
      "lhs": 3.0,
      "sense": ">=",
      "rhs": 6.0,
      "violation": 3.0
    },
    {
      "constraint": "ordine1_J2_J4",
      "lhs": -40.0,
      "sense": ">=",
      "rhs": -37.0,
      "violation": 3.0
    },
    {
      "constraint": "ordine2_J3_J6",
      "lhs": 5.0,
      "sense": ">=",
      "rhs": 8.0,
      "violation": 3.0
    },
    {
      "constraint": "precedenza_J1_J2",
      "lhs": -14.0,
      "sense": ">=",
      "rhs": 0.0,
      "violation": 14.0
    }
  ],
  "bound_violations": [
    {
      "variable": "S_J7",
      "value": 0.0,
      "violation": 6.0
    }
  ],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "C_J0",
    "o_J0_J1",
    "o_J0_J2",
    "o_J0_J3",
    "o_J0_J4",
    "o_J0_J5",
    "o_J0_J6"
  ],
  "missing_variables_assumed_zero": [
    "C_J7",
    "S_J7",
    "T_J7",
    "o_J1_J7",
    "o_J2_J7",
    "o_J3_J7",
    "o_J4_J7",
    "o_J5_J7",
    "o_J6_J7"
  ]
}
```

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB
import json

n = 7
p = [5, 7, 4, 6, 3, 8, 5]
r = [0, 0, 2, 3, 5, 0, 6]
d = [9, 17, 12, 22, 15, 28, 25]
w = [4, 3, 5, 2, 6, 2, 4]

pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
H = sum(p) + max(r)
M = H

m = gp.Model("weighted_tardiness")
m.Params.OutputFlag = 0
m.Params.MIPGap = 0.0

S = m.addVars(n, lb=0, ub=[H - p[i] for i in range(n)], name="S")
C = m.addVars(n, lb=0, ub=H, name="C")
T = m.addVars(n, lb=0, name="T")
y = m.addVars(pairs, vtype=GRB.BINARY, name="y")

m.setObjective(gp.quicksum(w[i] * T[i] for i in range(n)), GRB.MINIMIZE)

m.addConstrs((S[i] + p[i] == C[i] for i in range(n)), name="comp")
m.addConstrs((T[i] >= C[i] - d[i] for i in range(n)), name="tardy")
m.addConstrs((S[i] >= r[i] for i in range(n)), name="release")

for i, j in pairs:
    m.addConstr(C[i] <= S[j] + M * (1 - y[i, j]), name=f"ord_{i}_{j}_ij")
    m.addConstr(C[j] <= S[i] + M * y[i, j], name=f"ord_{i}_{j}_ji")

m.addConstr(C[0] <= S[1], name="prec_J1_J2")
m.addConstr(C[2] <= S[4], name="prec_J3_J5")

m.optimize()

status_names = {
    1: "LOADED",
    2: "OPTIMAL",
    3: "INFEASIBLE",
    4: "INF_OR_UNBD",
    5: "UNBOUNDED",
    6: "CUTOFF",
    7: "ITERATION_LIMIT",
    8: "NODE_LIMIT",
    9: "TIME_LIMIT",
    10: "SOLUTION_LIMIT",
    11: "INTERRUPTED",
    12: "NUMERIC",
    13: "SUBOPTIMAL",
    14: "INPROGRESS",
    15: "USER_OBJ_LIMIT",
}

if m.status == GRB.OPTIMAL:
    status = "OPTIMAL"
    variables = {}
    for var in m.getVars():
        val = round(float(var.X), 6)
        if abs(val) < 5e-12:
            val = 0.0
        variables[var.VarName] = val
    payload = {
        "status": status,
        "objective": float(m.ObjVal),
        "variables": variables,
    }
else:
    status = status_names.get(m.status, str(m.status))
    payload = {
        "status": status,
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(payload, separators=(",", ":")))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
