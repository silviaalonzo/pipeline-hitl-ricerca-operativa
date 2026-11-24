# Handoff 1 — H10 / claude-sonnet-5

- **Stadio:** 2
- **Categoria:** revisione_di_assicurazione_post_riparazione
- **Tipo di handoff:** ASSURANCE_REVIEW
- **Dettaglio:** Problema di difficoltà elevata risolto dopo almeno una riparazione automatica: il protocollo richiede una revisione umana prima dell'accettazione.
- **Cicli automatici già usati:** 3
- **Ground truth mostrata:** no

## Diagnosi automatica

Il problema è di difficoltà elevata e la soluzione ha richiesto almeno una riparazione automatica. Prima dell'accettazione, il protocollo richiede una revisione umana del modello e del codice rispetto alla traccia, senza mostrare la ground truth.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | stop | 5463 | 1256 | sì | errore_di_esecuzione |
| 1 | AUTO_REPAIR | stop | 2854 | 0 | sì | errore_di_esecuzione |
| 2 | AUTO_REPAIR | stop | 2854 | 0 | sì | errore_di_esecuzione |
| 3 | AUTO_REPAIR | stop | 2955 | 514 | sì | corretta |

## Traccia

# H10 — Rete multi-prodotto con capacità condivise

Difficoltà: Elevata
Classe: MILP intera

Una rete deve trasportare due prodotti K1 e K2 da S a T, rispettivamente per 28 e 22 unità. Gli archi attivati condividono la capacità tra i due prodotti.
Per resilienza devono essere attivati entrambi gli archi in uscita da S. Per limiti gestionali possono essere attivati al massimo sette archi complessivi. I costi unitari dipendono dal prodotto.
I flussi sono interi. Minimizzare costi fissi e costi di flusso rispettando conservazione e capacità condivise.

## Archi e costi fissi

Arco | Costo fisso | Capacità
--- | --- | ---
S→A | 55 | 35
S→B | 50 | 35
A→B | 18 | 15
A→C | 38 | 30
B→C | 22 | 25
B→D | 35 | 25
C→D | 20 | 20
C→T | 48 | 35
D→T | 44 | 35

## Costi unitari per prodotto

Arco | K1 | K2
--- | --- | ---
S→A | 2 | 3
S→B | 3 | 2
A→B | 1 | 2
A→C | 2 | 3
B→C | 2 | 1
B→D | 3 | 2
C→D | 1 | 2
C→T | 3 | 2
D→T | 2 | 3

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Codice da esaminare

```python
import gurobipy as gp
from gurobipy import GRB
import json

# --- Insiemi ---
ARCS = [('S','A'), ('S','B'), ('A','B'), ('A','C'), ('B','C'),
         ('B','D'), ('C','D'), ('C','T'), ('D','T')]
NODES = ['S','A','B','C','D','T']
PRODUCTS = ['K1','K2']

# --- Parametri ---
fixed = {
    ('S','A'):55, ('S','B'):50, ('A','B'):18, ('A','C'):38,
    ('B','C'):22, ('B','D'):35, ('C','D'):20, ('C','T'):48, ('D','T'):44
}
cap = {
    ('S','A'):35, ('S','B'):35, ('A','B'):15, ('A','C'):30,
    ('B','C'):25, ('B','D'):25, ('C','D'):20, ('C','T'):35, ('D','T'):35
}
cost = {
    ('S','A'): {'K1':2, 'K2':3},
    ('S','B'): {'K1':3, 'K2':2},
    ('A','B'): {'K1':1, 'K2':2},
    ('A','C'): {'K1':2, 'K2':3},
    ('B','C'): {'K1':2, 'K2':1},
    ('B','D'): {'K1':3, 'K2':2},
    ('C','D'): {'K1':1, 'K2':2},
    ('C','T'): {'K1':3, 'K2':2},
    ('D','T'): {'K1':2, 'K2':3},
}
demand = {'K1':28, 'K2':22}
MAXARCS = 7

model = gp.Model("H10_multiproduct_network")
model.setParam('OutputFlag', 0)

# --- Variabili ---
y = model.addVars(ARCS, vtype=GRB.BINARY, name="y")

x_keys = [(a[0], a[1], k) for a in ARCS for k in PRODUCTS]
x = model.addVars(x_keys, vtype=GRB.INTEGER, lb=0, name="x")

# --- Funzione obiettivo ---
obj = gp.quicksum(fixed[a] * y[a] for a in ARCS) + \
      gp.quicksum(cost[(i, j)][k] * x[i, j, k] for (i, j) in ARCS for k in PRODUCTS)
model.setObjective(obj, GRB.MINIMIZE)

# --- Vincoli di conservazione del flusso ---
for n in NODES:
    for k in PRODUCTS:
        inflow = gp.quicksum(x[a[0], a[1], k] for a in ARCS if a[1] == n)
        outflow = gp.quicksum(x[a[0], a[1], k] for a in ARCS if a[0] == n)
        if n == 'S':
            rhs = -demand[k]
        elif n == 'T':
            rhs = demand[k]
        else:
            rhs = 0
        model.addConstr(inflow - outflow == rhs, name=f"balance_{n}_{k}")

# --- Capacità condivisa ---
for a in ARCS:
    model.addConstr(
        gp.quicksum(x[a[0], a[1], k] for k in PRODUCTS) <= cap[a] * y[a],
        name=f"cap_{a[0]}_{a[1]}"
    )

# --- Attivazione obbligatoria degli archi da S ---
model.addConstr(y[('S','A')] == 1, name="force_SA")
model.addConstr(y[('S','B')] == 1, name="force_SB")

# --- Limite sul numero di archi attivati ---
model.addConstr(gp.quicksum(y[a] for a in ARCS) <= MAXARCS, name="max_arcs")

model.optimize()

variables = {}
status_str = "UNKNOWN"
objective_value = None

if model.status == GRB.OPTIMAL:
    status_str = "OPTIMAL"
    objective_value = model.ObjVal
    for a in ARCS:
        variables[f"y_{a[0]}_{a[1]}"] = float(round(y[a].X))
    for a in ARCS:
        for k in PRODUCTS:
            variables[f"x_{a[0]}_{a[1]}_{k}"] = float(round(x[a[0], a[1], k].X))
else:
    status_str = "INFEASIBLE" if model.status == GRB.INFEASIBLE else str(model.status)
    objective_value = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps({
    "status": status_str,
    "objective": objective_value,
    "variables": variables
}))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
