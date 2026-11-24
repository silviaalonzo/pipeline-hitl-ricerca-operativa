# Handoff 1 — H02 / claude-sonnet-5

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
| 0 | INITIAL | stop | 6668 | 1526 | sì | validazione_indipendente_fallita |

## Traccia

# H02 — Produzione multi-periodo con setup e scorte

Difficoltà: Elevata
Classe: MILP intera

Un impianto pianifica la produzione di tre articoli per quattro periodi. La domanda deve essere soddisfatta senza arretrati mediante produzione corrente e scorte provenienti dal periodo precedente. Le scorte iniziali sono 0 unità di A, 0 di B e 6 di C.
L’avvio di un articolo in un periodo comporta un setup. Si possono attivare al massimo due articoli per periodo, la scorta totale non può superare 20 unità e tutte le scorte finali devono essere nulle.
La capacità è espressa in ore. Produzione e scorte sono quantità intere. Minimizzare costi di produzione, setup e mantenimento.

## Domande per periodo

Prodotto | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
A | 8 | 12 | 10 | 14
B | 10 | 8 | 14 | 12
C | 6 | 9 | 7 | 11

## Costi unitari di produzione

Prodotto | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
A | 9 | 11 | 10 | 12
B | 8 | 9 | 11 | 10
C | 13 | 12 | 14 | 11

## Parametri per prodotto

Prodotto | Setup | Holding | Ore/unità | Lotto min.
--- | --- | --- | --- | ---
A | 45 | 2 | 2 | 4
B | 40 | 3 | 3 | 4
C | 50 | 2 | 4 | 3

## Capacità

Periodo | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
Ore | 90 | 95 | 90 | 100

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Esito pubblico della validazione

```json
{
  "problem_id": "H02",
  "correct": false,
  "candidate_status": "OPTIMAL",
  "feasible_in_original_problem": false,
  "gap_within_tolerance": false,
  "declared_objective_corrected_automatically": false,
  "max_constraint_violation": 14.0,
  "constraint_violations": [
    {
      "constraint": "bilancio_A_1",
      "lhs": 20.0,
      "sense": "=",
      "rhs": 8.0,
      "violation": 12.0
    },
    {
      "constraint": "bilancio_A_2",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 12.0,
      "violation": 12.0
    },
    {
      "constraint": "bilancio_A_3",
      "lhs": 24.0,
      "sense": "=",
      "rhs": 10.0,
      "violation": 14.0
    },
    {
      "constraint": "bilancio_A_4",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 14.0,
      "violation": 14.0
    },
    {
      "constraint": "bilancio_C_2",
      "lhs": 16.0,
      "sense": "=",
      "rhs": 9.0,
      "violation": 7.0
    },
    {
      "constraint": "bilancio_C_3",
      "lhs": 0.0,
      "sense": "=",
      "rhs": 7.0,
      "violation": 7.0
    }
  ],
  "bound_violations": [],
  "integrality_violations": [],
  "unknown_nonzero_variables": [
    "s_A_1",
    "s_A_3",
    "s_C_2"
  ],
  "missing_variables_assumed_zero": [
    "I_A_1",
    "I_A_2",
    "I_A_3",
    "I_A_4",
    "I_B_1",
    "I_B_2",
    "I_B_3",
    "I_B_4",
    "I_C_1",
    "I_C_2",
    "I_C_3",
    "I_C_4"
  ]
}
```

## Codice da esaminare

```python
import json
import gurobipy as gp
from gurobipy import GRB

# ---------------- Dati ----------------
products = ['A', 'B', 'C']
periods = [1, 2, 3, 4]

demand = {
    ('A',1):8, ('A',2):12, ('A',3):10, ('A',4):14,
    ('B',1):10,('B',2):8,  ('B',3):14, ('B',4):12,
    ('C',1):6, ('C',2):9,  ('C',3):7,  ('C',4):11,
}

prod_cost = {
    ('A',1):9,  ('A',2):11, ('A',3):10, ('A',4):12,
    ('B',1):8,  ('B',2):9,  ('B',3):11, ('B',4):10,
    ('C',1):13, ('C',2):12, ('C',3):14, ('C',4):11,
}

setup_cost = {'A':45, 'B':40, 'C':50}
holding_cost = {'A':2, 'B':3, 'C':2}
hours_per_unit = {'A':2, 'B':3, 'C':4}
min_lot = {'A':4, 'B':4, 'C':3}
initial_inv = {'A':0, 'B':0, 'C':6}

capacity = {1:90, 2:95, 3:90, 4:100}

max_setups_per_period = 2
max_total_inventory = 20

# Big-M: somma totale della domanda per prodotto (limite sicuro sulla produzione in un periodo)
bigM = {i: sum(demand[(i,t)] for t in periods) for i in products}

# ---------------- Modello ----------------
m = gp.Model("H02_produzione_multiperiodo")

x = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="x")
s = m.addVars(products, periods, vtype=GRB.INTEGER, lb=0, name="s")
y = m.addVars(products, periods, vtype=GRB.BINARY, name="y")

# Bilancio di scorte
for i in products:
    prev = initial_inv[i]
    for t in periods:
        m.addConstr(prev + x[i,t] - demand[(i,t)] == s[i,t], name=f"bal_{i}_{t}")
        prev = s[i,t]

# Scorte finali nulle
last_t = periods[-1]
for i in products:
    m.addConstr(s[i,last_t] == 0, name=f"final_inv_{i}")

# Legame produzione-setup (big-M) e lotto minimo
for i in products:
    for t in periods:
        m.addConstr(x[i,t] <= bigM[i] * y[i,t], name=f"link_{i}_{t}")
        m.addConstr(x[i,t] >= min_lot[i] * y[i,t], name=f"minlot_{i}_{t}")

# Massimo due articoli attivi per periodo
for t in periods:
    m.addConstr(gp.quicksum(y[i,t] for i in products) <= max_setups_per_period,
                name=f"max_setups_{t}")

# Scorta totale massima
for t in periods:
    m.addConstr(gp.quicksum(s[i,t] for i in products) <= max_total_inventory,
                name=f"max_inv_{t}")

# Capacità oraria
for t in periods:
    m.addConstr(gp.quicksum(hours_per_unit[i] * x[i,t] for i in products) <= capacity[t],
                name=f"cap_{t}")

# ---------------- Obiettivo ----------------
obj = gp.quicksum(prod_cost[(i,t)] * x[i,t] for i in products for t in periods) \
    + gp.quicksum(setup_cost[i] * y[i,t] for i in products for t in periods) \
    + gp.quicksum(holding_cost[i] * s[i,t] for i in products for t in periods)

m.setObjective(obj, GRB.MINIMIZE)

m.optimize()

# ---------------- Output ----------------
status = m.Status
result = {"status": None, "objective": None, "variables": {}}

if status == GRB.OPTIMAL:
    result["status"] = "OPTIMAL"
    result["objective"] = round(m.ObjVal, 4)
    variables = {}
    for i in products:
        for t in periods:
            variables[f"x_{i}_{t}"] = round(x[i,t].X, 4)
            variables[f"s_{i}_{t}"] = round(s[i,t].X, 4)
            variables[f"y_{i}_{t}"] = round(y[i,t].X, 4)
    result["variables"] = variables
else:
    result["status"] = "NOT_OPTIMAL_STATUS_%d" % status
    result["objective"] = None
    result["variables"] = {}

print("SOLUTION_JSON=" + json.dumps(result))
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
