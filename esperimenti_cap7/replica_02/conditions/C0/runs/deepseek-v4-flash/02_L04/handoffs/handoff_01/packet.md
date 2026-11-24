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
| 0 | INITIAL | stop | 6905 | 43397 | sì | validazione_indipendente_fallita |

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
  "max_constraint_violation": 68.0,
  "constraint_violations": [
    {
      "constraint": "balance_A_T1",
      "lhs": -25.0,
      "sense": "=",
      "rhs": 18.0,
      "violation": 43.0
    },
    {
      "constraint": "balance_A_T2",
      "lhs": 35.0,
      "sense": "=",
      "rhs": 42.0,
      "violation": 7.0
    },
    {
      "constraint": "balance_A_T3",
      "lhs": 50.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_A_T4",
      "lhs": 45.0,
      "sense": "=",
      "rhs": 50.0,
      "violation": 5.0
    },
    {
      "constraint": "balance_A_T5",
      "lhs": 40.0,
      "sense": "=",
      "rhs": 45.0,
      "violation": 5.0
    },
    {
      "constraint": "balance_A_T6",
      "lhs": 15.0,
      "sense": "=",
      "rhs": 40.0,
      "violation": 25.0
    },
    {
      "constraint": "final_A",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 15.0,
      "violation": 15.0
    },
    {
      "constraint": "balance_B_T1",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 17.0,
      "violation": 17.0
    },
    {
      "constraint": "balance_B_T2",
      "lhs": 44.0,
      "sense": "=",
      "rhs": 36.0,
      "violation": 8.0
    },
    {
      "constraint": "balance_B_T3",
      "lhs": 38.0,
      "sense": "=",
      "rhs": 44.0,
      "violation": 6.0
    },
    {
      "constraint": "balance_B_T4",
      "lhs": 46.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 8.0
    },
    {
      "constraint": "balance_B_T5",
      "lhs": 34.0,
      "sense": "=",
      "rhs": 46.0,
      "violation": 12.0
    },
    {
      "constraint": "balance_B_T6",
      "lhs": 10.0,
      "sense": "=",
      "rhs": 34.0,
      "violation": 24.0
    },
    {
      "constraint": "final_B",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 10.0,
      "violation": 10.0
    },
    {
      "constraint": "balance_C_T1",
      "lhs": 20.0,
      "sense": "=",
      "rhs": 15.0,
      "violation": 5.0
    },
    {
      "constraint": "balance_C_T2",
      "lhs": 28.0,
      "sense": "=",
      "rhs": 30.0,
      "violation": 2.0
    },
    {
      "constraint": "balance_C_T3",
      "lhs": 35.0,
      "sense": "=",
      "rhs": 28.0,
      "violation": 7.0
    },
    {
      "constraint": "balance_C_T4",
      "lhs": 30.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 5.0
    },
    {
      "constraint": "balance_C_T5",
      "lhs": 32.0,
      "sense": "=",
      "rhs": 30.0,
      "violation": 2.0
    },
    {
      "constraint": "balance_C_T6",
      "lhs": 8.0,
      "sense": "=",
      "rhs": 32.0,
      "violation": 24.0
    },
    {
      "constraint": "final_C",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 8.0,
      "violation": 8.0
    },
    {
      "constraint": "balance_D_T1",
      "lhs": 17.0,
      "sense": "=",
      "rhs": 22.0,
      "violation": 5.0
    },
    {
      "constraint": "balance_D_T2",
      "lhs": 45.0,
      "sense": "=",
      "rhs": 35.0,
      "violation": 10.0
    },
    {
      "constraint": "balance_D_T3",
      "lhs": 42.0,
      "sense": "=",
      "rhs": 45.0,
      "violation": 3.0
    },
    {
      "constraint": "balance_D_T4",
      "lhs": 38.0,
      "sense": "=",
      "rhs": 42.0,
      "violation": 4.0
    },
    {
      "constraint": "balance_D_T5",
      "lhs": 48.0,
      "sense": "=",
      "rhs": 38.0,
      "violation": 10.0
    },
    {
      "constraint": "balance_D_T6",
      "lhs": 12.0,
      "sense": "=",
      "rhs": 48.0,
      "violation": 36.0
    },
    {
      "constraint": "final_D",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 12.0,
      "violation": 12.0
    },
    {
      "constraint": "balance_E_T1",
      "lhs": 19.0,
      "sense": "=",
      "rhs": -5.0,
      "violation": 24.0
    },
    {
      "constraint": "balance_E_T2",
      "lhs": 22.0,
      "sense": "=",
      "rhs": 24.0,
      "violation": 2.0
    },
    {
      "constraint": "balance_E_T3",
      "lhs": 28.0,
      "sense": "=",
      "rhs": 22.0,
      "violation": 6.0
    },
    {
      "constraint": "balance_E_T4",
      "lhs": 26.0,
      "sense": "=",
      "rhs": 28.0,
      "violation": 2.0
    },
    {
      "constraint": "balance_E_T5",
      "lhs": 25.0,
      "sense": "=",
      "rhs": 26.0,
      "violation": 1.0
    },
    {
      "constraint": "balance_E_T6",
      "lhs": 5.0,
      "sense": "=",
      "rhs": 25.0,
      "violation": 20.0
    },
    {
      "constraint": "final_E",
      "lhs": 0.0,
      "sense": ">=",
      "rhs": 5.0,
      "violation": 5.0
    },
    {
      "constraint": "capacity_T1",
      "lhs": 360.0,
      "sense": "<=",
      "rhs": 350.0,
      "violation": 10.0
    },
    {
      "constraint": "capacity_T2",
      "lhs": 428.0,
      "sense": "<=",
      "rhs": 360.0,
      "violation": 68.0
    },
    {
      "constraint": "capacity_T3",
      "lhs": 370.0,
      "sense": "<=",
      "rhs": 345.0,
      "violation": 25.0
    },
    {
      "constraint": "capacity_T5",
      "lhs": 380.0,
      "sense": "<=",
      "rhs": 355.0,
      "violation": 25.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "x_A_0",
    "x_B_0",
    "x_C_0",
    "x_D_0",
    "I_A_0",
    "I_B_0",
    "I_C_0",
    "I_D_0",
    "I_E_0",
    "setup_A_0",
    "setup_B_0",
    "setup_C_0",
    "setup_D_0",
    "straordinario_0",
    "straordinario_2",
    "attiva_straordinario_0",
    "attiva_straordinario_2"
  ],
  "missing_variables_assumed_zero": [
    "I_A_T6",
    "I_B_T6",
    "I_C_T6",
    "I_D_T6",
    "I_E_T6",
    "o_T1",
    "o_T2",
    "o_T3",
    "o_T4",
    "o_T5",
    "o_T6",
    "u_T1",
    "u_T2",
    "u_T3",
    "u_T4",
    "u_T5",
    "u_T6",
    "x_A_T6",
    "x_B_T6",
    "x_C_T6",
    "x_D_T6",
    "x_E_T6",
    "y_A_T6",
    "y_B_T6",
    "y_C_T6",
    "y_D_T6",
    "y_E_T6"
  ]
}
```

## Codice da esaminare

```python
import json
import gurobipy as gp

prodotti = ["A", "B", "C", "D", "E"]
periodi = range(6)

S0 = {"A": 20, "B": 15, "C": 10, "D": 18, "E": 25}
SF = {"A": 15, "B": 10, "C": 8, "D": 12, "E": 5}
h = {"A": 2, "B": 3, "C": 1, "D": 2, "E": 4}
Lmin = {"A": 22, "B": 18, "C": 25, "D": 20, "E": 15}
Lmax = {"A": 85, "B": 75, "C": 90, "D": 80, "E": 65}
costo_setup = {"A": 48, "B": 55, "C": 40, "D": 52, "E": 45}
costo_scorta = {"A": 1.1, "B": 1.4, "C": 0.8, "D": 1.2, "E": 1.5}

domanda = {
    "A": [38, 42, 35, 50, 45, 40],
    "B": [32, 36, 44, 38, 46, 34],
    "C": [25, 30, 28, 35, 30, 32],
    "D": [40, 35, 45, 42, 38, 48],
    "E": [20, 24, 22, 28, 26, 25],
}

costo_prod = {
    "A": [4, 6, 8, 10, 5, 7],
    "B": [7, 9, 4, 6, 8, 10],
    "C": [10, 5, 7, 9, 4, 6],
    "D": [6, 8, 10, 5, 7, 9],
    "E": [9, 4, 6, 8, 10, 5],
}

cap_ord = [350, 360, 345, 370, 355, 380]
max_straord = [85, 80, 90, 75, 85, 80]
costo_straord = [7, 8, 7, 9, 8, 7]
costo_fisso_straord = 25

m = gp.Model("L04_produzione")
m.Params.OutputFlag = 0

x = m.addVars(prodotti, periodi, vtype=gp.GRB.INTEGER, name="x")
I = m.addVars(prodotti, periodi, vtype=gp.GRB.INTEGER, name="I")
y = m.addVars(prodotti, periodi, vtype=gp.GRB.BINARY, name="setup")
R = m.addVars(periodi, vtype=gp.GRB.CONTINUOUS, name="straordinario")
A = m.addVars(periodi, vtype=gp.GRB.BINARY, name="attiva_straordinario")

# Bilancio di scorta
for p in prodotti:
    m.addConstr(I[p, 0] == S0[p] + x[p, 0] - domanda[p][0], name=f"bilancio_{p}_1")
    for t in range(1, 6):
        m.addConstr(I[p, t] == I[p, t-1] + x[p, t] - domanda[p][t], name=f"bilancio_{p}_{t+1}")

# Scorta finale minima e limiti di giacenza
for p in prodotti:
    m.addConstr(I[p, 5] >= SF[p], name=f"finale_{p}")
    for t in periodi:
        m.addConstr(I[p, t] <= 75, name=f"stock_max_{p}_{t}")

for t in periodi:
    m.addConstr(gp.quicksum(I[p, t] for p in prodotti) <= 210, name=f"stock_tot_{t}")

# Lotto minimo/massimo e setup
for p in prodotti:
    for t in periodi:
        m.addConstr(x[p, t] >= Lmin[p] * y[p, t], name=f"lotto_min_{p}_{t}")
        m.addConstr(x[p, t] <= Lmax[p] * y[p, t], name=f"lotto_max_{p}_{t}")

# Capacità ordinaria e straordinario
for t in periodi:
    m.addConstr(gp.quicksum(h[p] * x[p, t] for p in prodotti) <= cap_ord[t] + R[t], name=f"capacity_{t}")
    m.addConstr(R[t] <= max_straord[t] * A[t], name=f"ot_max_{t}")
    m.addConstr(R[t] >= 10 * A[t], name=f"ot_min_{t}")

# Limiti sui setup
m.addConstr(y.sum() <= 26, name="setup_total")
for t in periodi:
    m.addConstr(gp.quicksum(y[p, t] for p in prodotti) <= 4, name=f"setup_per_{t}")

# Funzione obiettivo
obj = (
    gp.quicksum(costo_prod[p][t] * x[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_setup[p] * y[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_scorta[p] * I[p, t] for p in prodotti for t in periodi)
    + gp.quicksum(costo_fisso_straord * A[t] + costo_straord[t] * R[t] for t in periodi)
)
m.setObjective(obj, gp.GRB.MINIMIZE)

m.optimize()

if m.Status == gp.GRB.OPTIMAL:
    sol = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": {v.VarName: v.X for v in m.getVars()},
    }
else:
    status = {
        gp.GRB.INFEASIBLE: "INFEASIBLE",
        gp.GRB.UNBOUNDED: "UNBOUNDED",
        gp.GRB.INF_OR_UNBD: "INF_OR_UNBD",
    }.get(m.Status, f"STATUS_{m.Status}")
    sol = {"status": status, "objective": None, "variables": {}}

print("SOLUTION_JSON=" + json.dumps(sol, separators=(",", ":")))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
