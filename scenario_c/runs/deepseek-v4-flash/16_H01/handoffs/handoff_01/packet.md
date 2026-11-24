# Handoff 1 — H01 / deepseek-v4-flash

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
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 3 | AUTO_REPAIR | stop | 3937 | 17304 | sì | corretta |

## Traccia

# H01 — Rete capacitada di centri distributivi

Difficoltà: Elevata
Classe: MILP

Un’azienda deve soddisfare integralmente la domanda di otto zone aprendo da tre a quattro centri tra sei siti candidati. La domanda di una zona può essere ripartita tra più centri.
Ogni centro aperto deve movimentare almeno 20 unità e non può superare la propria capacità. Per resilienza deve essere aperto almeno un sito nel gruppo Nord (A–C) e almeno uno nel gruppo Sud (D–F).
Il costo è dato dai costi fissi più il costo unitario di distribuzione. Le emissioni complessive, calcolate mediante i coefficienti della seconda matrice, non possono superare 470 unità.

## Domanda

Zona | Z1 | Z2 | Z3 | Z4 | Z5 | Z6 | Z7 | Z8
--- | --- | --- | --- | --- | --- | --- | --- | ---
Unità | 30 | 25 | 35 | 20 | 28 | 32 | 24 | 26

## Siti

Sito | Costo fisso | Capacità
--- | --- | ---
A | 110 | 90
B | 95 | 80
C | 120 | 110
D | 90 | 75
E | 105 | 95
F | 100 | 85

## Costi unitari

Zona | A | B | C | D | E | F
--- | --- | --- | --- | --- | --- | ---
Z1 | 4 | 7 | 6 | 10 | 9 | 11
Z2 | 5 | 4 | 8 | 9 | 7 | 10
Z3 | 7 | 5 | 4 | 8 | 9 | 7
Z4 | 9 | 8 | 7 | 4 | 5 | 6
Z5 | 8 | 9 | 6 | 5 | 4 | 7
Z6 | 10 | 8 | 7 | 6 | 5 | 4
Z7 | 6 | 7 | 5 | 8 | 6 | 7
Z8 | 7 | 6 | 8 | 5 | 7 | 4

## Coefficienti di emissione

Zona | A | B | C | D | E | F
--- | --- | --- | --- | --- | --- | ---
Z1 | 1 | 2 | 2 | 4 | 3 | 4
Z2 | 2 | 1 | 3 | 3 | 2 | 4
Z3 | 3 | 2 | 1 | 3 | 4 | 3
Z4 | 4 | 3 | 3 | 1 | 2 | 2
Z5 | 3 | 4 | 2 | 2 | 1 | 3
Z6 | 4 | 3 | 3 | 2 | 2 | 1
Z7 | 2 | 3 | 1 | 3 | 2 | 3
Z8 | 3 | 2 | 3 | 1 | 3 | 1

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

zones = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8"]
sites = ["A", "B", "C", "D", "E", "F"]

demand = {
    "Z1": 30, "Z2": 25, "Z3": 35, "Z4": 20,
    "Z5": 28, "Z6": 32, "Z7": 24, "Z8": 26,
}

fixed_cost = {"A": 110, "B": 95, "C": 120, "D": 90, "E": 105, "F": 100}
capacity = {"A": 90, "B": 80, "C": 110, "D": 75, "E": 95, "F": 85}

cost = {
    ("Z1", "A"): 4, ("Z1", "B"): 7, ("Z1", "C"): 6, ("Z1", "D"): 10, ("Z1", "E"): 9, ("Z1", "F"): 11,
    ("Z2", "A"): 5, ("Z2", "B"): 4, ("Z2", "C"): 8, ("Z2", "D"): 9, ("Z2", "E"): 7, ("Z2", "F"): 10,
    ("Z3", "A"): 7, ("Z3", "B"): 5, ("Z3", "C"): 4, ("Z3", "D"): 8, ("Z3", "E"): 9, ("Z3", "F"): 7,
    ("Z4", "A"): 9, ("Z4", "B"): 8, ("Z4", "C"): 7, ("Z4", "D"): 4, ("Z4", "E"): 5, ("Z4", "F"): 6,
    ("Z5", "A"): 8, ("Z5", "B"): 9, ("Z5", "C"): 6, ("Z5", "D"): 5, ("Z5", "E"): 4, ("Z5", "F"): 7,
    ("Z6", "A"): 10, ("Z6", "B"): 8, ("Z6", "C"): 7, ("Z6", "D"): 6, ("Z6", "E"): 5, ("Z6", "F"): 4,
    ("Z7", "A"): 6, ("Z7", "B"): 7, ("Z7", "C"): 5, ("Z7", "D"): 8, ("Z7", "E"): 6, ("Z7", "F"): 7,
    ("Z8", "A"): 7, ("Z8", "B"): 6, ("Z8", "C"): 8, ("Z8", "D"): 5, ("Z8", "E"): 7, ("Z8", "F"): 4,
}

emission = {
    ("Z1", "A"): 1, ("Z1", "B"): 2, ("Z1", "C"): 2, ("Z1", "D"): 4, ("Z1", "E"): 3, ("Z1", "F"): 4,
    ("Z2", "A"): 2, ("Z2", "B"): 1, ("Z2", "C"): 3, ("Z2", "D"): 3, ("Z2", "E"): 2, ("Z2", "F"): 4,
    ("Z3", "A"): 3, ("Z3", "B"): 2, ("Z3", "C"): 1, ("Z3", "D"): 3, ("Z3", "E"): 4, ("Z3", "F"): 3,
    ("Z4", "A"): 4, ("Z4", "B"): 3, ("Z4", "C"): 3, ("Z4", "D"): 1, ("Z4", "E"): 2, ("Z4", "F"): 2,
    ("Z5", "A"): 3, ("Z5", "B"): 4, ("Z5", "C"): 2, ("Z5", "D"): 2, ("Z5", "E"): 1, ("Z5", "F"): 3,
    ("Z6", "A"): 4, ("Z6", "B"): 3, ("Z6", "C"): 3, ("Z6", "D"): 2, ("Z6", "E"): 2, ("Z6", "F"): 1,
    ("Z7", "A"): 2, ("Z7", "B"): 3, ("Z7", "C"): 1, ("Z7", "D"): 3, ("Z7", "E"): 2, ("Z7", "F"): 3,
    ("Z8", "A"): 3, ("Z8", "B"): 2, ("Z8", "C"): 3, ("Z8", "D"): 1, ("Z8", "E"): 3, ("Z8", "F"): 1,
}

model = gp.Model("H01")
model.Params.OutputFlag = 0

y = {}
for j in sites:
    y[j] = model.addVar(vtype=GRB.BINARY, name=f"y_{j}")

x = {}
for i in zones:
    for j in sites:
        x[i, j] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=f"x_{i}_{j}")

model.update()

model.setObjective(
    gp.quicksum(fixed_cost[j] * y[j] for j in sites)
    + gp.quicksum(cost[i, j] * x[i, j] for i in zones for j in sites),
    GRB.MINIMIZE,
)

model.addConstrs(
    (gp.quicksum(x[i, j] for j in sites) == demand[i] for i in zones),
    name="Demand",
)
model.addConstrs(
    (gp.quicksum(x[i, j] for i in zones) >= 20 * y[j] for j in sites),
    name="MinThroughput",
)
model.addConstrs(
    (gp.quicksum(x[i, j] for i in zones) <= capacity[j] * y[j] for j in sites),
    name="Capacity",
)
model.addConstr(gp.quicksum(y[j] for j in sites) >= 3, name="MinOpen")
model.addConstr(gp.quicksum(y[j] for j in sites) <= 4, name="MaxOpen")
model.addConstr(gp.quicksum(y[j] for j in ["A", "B", "C"]) >= 1, name="AtLeastOneNorth")
model.addConstr(gp.quicksum(y[j] for j in ["D", "E", "F"]) >= 1, name="AtLeastOneSouth")
model.addConstr(
    gp.quicksum(emission[i, j] * x[i, j] for i in zones for j in sites) <= 470,
    name="EmissionCap",
)

model.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.NUMERIC: "NUMERIC",
}

result = {
    "status": status_names.get(model.status, str(model.status)),
    "objective": 0.0,
    "variables": {},
}

if model.status == GRB.OPTIMAL:
    result["objective"] = float(model.ObjVal)
    result["variables"] = {v.VarName: float(v.X) for v in model.getVars()}

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":"), ensure_ascii=False))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
