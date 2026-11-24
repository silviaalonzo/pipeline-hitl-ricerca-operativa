# Handoff 1 — L02 / deepseek-v4-flash

- **Stadio:** 2
- **Categoria:** revisione_di_assicurazione_post_riparazione
- **Tipo di handoff:** ASSURANCE_REVIEW
- **Dettaglio:** Problema di difficoltà elevata risolto dopo almeno una riparazione automatica: il protocollo richiede una revisione umana prima dell'accettazione.
- **Cicli automatici già usati:** 1
- **Ground truth mostrata:** no

## Diagnosi automatica

Il problema è di difficoltà elevata e la soluzione ha richiesto almeno una riparazione automatica. Prima dell'accettazione, il protocollo richiede una revisione umana del modello e del codice rispetto alla traccia, senza mostrare la ground truth.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 64000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 3139 | 46707 | sì | corretta |

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

## Codice da esaminare

```python
import json
from gurobipy import GRB, Model, quicksum

products = [0, 1, 2]
periods = list(range(8))

initial_stock = [22, 18, 25]
required_final = [18, 15, 20]
hours_per_unit = [2, 3, 1]
min_lot = [24, 20, 28]
max_lot = [82, 70, 90]
setup_cost = [52, 60, 45]
holding_cost = [1.2, 1.6, 0.9]

production_cost = [
    [5, 8, 5, 8, 5, 8, 5, 8],
    [7, 10, 7, 10, 7, 10, 7, 10],
    [9, 6, 9, 6, 9, 6, 9, 6],
]

demand = [
    [34, 48, 42, 55, 38, 50, 46, 40],
    [28, 32, 45, 36, 50, 34, 42, 39],
    [40, 35, 38, 44, 36, 48, 41, 45],
]

capacity = [250, 245, 235, 260, 240, 255, 245, 265]

m = Model("packing_plan")
m.setParam("OutputFlag", 0)

x = {}
y = {}
inv = {}

for p in products:
    for t in periods:
        x[p, t] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_P{p+1}_T{t+1}")
        y[p, t] = m.addVar(vtype=GRB.BINARY, name=f"y_P{p+1}_T{t+1}")
        inv[p, t] = m.addVar(vtype=GRB.INTEGER, lb=0, ub=75, name=f"inv_P{p+1}_T{t+1}")

m.setObjective(
    quicksum(
        production_cost[p][t] * x[p, t]
        + setup_cost[p] * y[p, t]
        + holding_cost[p] * inv[p, t]
        for p in products
        for t in periods
    ),
    GRB.MINIMIZE,
)

for p in products:
    for t in periods:
        m.addConstr(x[p, t] >= min_lot[p] * y[p, t], name=f"min_lot_{p+1}_{t+1}")
        m.addConstr(x[p, t] <= max_lot[p] * y[p, t], name=f"max_lot_{p+1}_{t+1}")

for p in products:
    m.addConstr(inv[p, 0] == initial_stock[p] + x[p, 0] - demand[p][0], name=f"balance_{p+1}_1")
    for t in range(1, len(periods)):
        m.addConstr(inv[p, t] == inv[p, t - 1] + x[p, t] - demand[p][t], name=f"balance_{p+1}_{t+1}")

for p in products:
    m.addConstr(inv[p, len(periods) - 1] >= required_final[p], name=f"final_inv_{p+1}")

for t in periods:
    m.addConstr(quicksum(inv[p, t] for p in products) <= 150, name=f"total_inv_{t+1}")
    m.addConstr(quicksum(hours_per_unit[p] * x[p, t] for p in products) <= capacity[t], name=f"capacity_{t+1}")

m.addConstr(quicksum(y[p, t] for p in products for t in periods) <= 18, name="total_setups")

for t in (2, 5):
    m.addConstr(quicksum(y[p, t] for p in products) <= 2, name=f"max2_setup_T{t+1}")

m.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.CUTOFF: "CUTOFF",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
}

if m.status == GRB.OPTIMAL:
    variables = {}
    for v in sorted(m.getVars(), key=lambda var: var.VarName):
        val = float(v.X)
        variables[v.VarName] = 0.0 if abs(val) < 1e-9 else val
    solution = {
        "status": "OPTIMAL",
        "objective": float(m.ObjVal),
        "variables": variables,
    }
else:
    solution = {
        "status": status_names.get(m.status, str(m.status)),
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(solution, separators=(",", ":")))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
