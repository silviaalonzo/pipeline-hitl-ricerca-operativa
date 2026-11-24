# Handoff 1 — L05 / deepseek-v4-flash

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
| 1 | AUTO_REPAIR | stop | 4575 | 24625 | sì | corretta |

## Traccia

# L05 — Assegnazione di ispettori a un portafoglio di audit

Difficoltà: Elevata
Classe: IP binaria

Un portafoglio di venti audit deve essere assegnato a dodici ispettori. Gli audit ordinari richiedono esattamente un ispettore; quelli ad alto rischio A04, A08, A12, A16 e A20 richiedono esattamente due ispettori distinti, dei quali almeno uno senior. Le celle «—» indicano una qualificazione assente e la combinazione non può essere utilizzata.

Ogni ispettore attivato deve rispettare sia il monte ore sia il numero massimo di audit riportati in tabella. Per ciascun ispettore, le coppie A01–A02, A06–A07, A11–A12 e A17–A18 sono incompatibili: non possono essere assegnati entrambi gli audit della stessa coppia. Possono essere attivati al massimo dieci ispettori. Minimizzare costi fissi e costi di assegnazione.

## Ispettori

Ispettore | Livello | Costo fisso | Ore max | Audit max
--- | --- | --- | --- | ---
I1 | Senior | 18 | 13 | 3
I2 | Senior | 23 | 14 | 3
I3 | Senior | 28 | 15 | 3
I4 | Senior | 22 | 16 | 3
I5 | Standard | 27 | 17 | 4
I6 | Standard | 21 | 13 | 4
I7 | Standard | 26 | 14 | 4
I8 | Standard | 20 | 15 | 4
I9 | Standard | 25 | 16 | 4
I10 | Standard | 19 | 17 | 4
I11 | Standard | 24 | 13 | 4
I12 | Standard | 18 | 14 | 4

## Audit

Audit | A01 | A02 | A03 | A04 | A05 | A06 | A07 | A08 | A09 | A10 | A11 | A12 | A13 | A14 | A15 | A16 | A17 | A18 | A19 | A20
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Durata | 3 | 4 | 2 | 6 | 5 | 3 | 4 | 7 | 2 | 5 | 3 | 6 | 4 | 2 | 5 | 7 | 3 | 4 | 5 | 6
Ispettori richiesti | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2

## Costi e qualificazioni

Ispettore | A01 | A02 | A03 | A04 | A05 | A06 | A07 | A08 | A09 | A10 | A11 | A12 | A13 | A14 | A15 | A16 | A17 | A18 | A19 | A20
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
I1 | — | 6 | 9 | 12 | — | 18 | 8 | 11 | 14 | 17 | 7 | 10 | 13 | 16 | — | 9 | 12 | 15 | — | 8
I2 | 10 | 13 | — | 6 | 9 | — | 15 | 18 | 8 | — | 14 | 17 | — | 10 | 13 | 16 | — | 9 | 12 | 15
I3 | — | 7 | 10 | 13 | 16 | 6 | 9 | 12 | 15 | 18 | — | 11 | 14 | 17 | — | 10 | 13 | — | 6 | 9
I4 | 11 | — | 17 | 7 | 10 | — | 16 | 6 | — | 12 | 15 | 18 | — | 11 | 14 | 17 | 7 | 10 | 13 | 16
I5 | 18 | 8 | 11 | — | 17 | 7 | — | 13 | 16 | 6 | — | 12 | 15 | — | 8 | 11 | 14 | — | 7 | 10
I6 | 12 | — | 18 | 8 | — | 14 | 17 | 7 | — | 13 | 16 | — | 9 | 12 | 15 | — | 8 | 11 | — | 17
I7 | 6 | 9 | — | 15 | 18 | 8 | — | 14 | 17 | — | 10 | 13 | 16 | — | 9 | 12 | — | 18 | 8 | 11
I8 | — | 16 | 6 | 9 | — | 15 | 18 | — | 11 | 14 | 17 | — | 10 | 13 | — | 6 | 9 | 12 | — | 18
I9 | 7 | 10 | — | 16 | 6 | — | 12 | 15 | 18 | — | 11 | 14 | — | 7 | 10 | 13 | — | 6 | 9 | —
I10 | — | 17 | 7 | — | 13 | 16 | 6 | — | 12 | 15 | — | 8 | 11 | 14 | — | 7 | 10 | — | 16 | 6
I11 | 8 | — | 14 | 17 | 7 | — | 13 | 16 | — | 9 | 12 | 15 | — | 8 | 11 | — | 17 | 7 | 10 | —
I12 | 15 | 18 | 8 | — | 14 | 17 | — | 10 | 13 | 16 | — | 9 | 12 | — | 18 | 8 | 11 | — | 17 | 7

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Codice da esaminare

```python
import json
from gurobipy import Model, GRB, quicksum

audits = [f"A{k:02d}" for k in range(1, 21)]
inspectors = [f"I{k}" for k in range(1, 13)]

durations = {
    "A01": 3, "A02": 4, "A03": 2, "A04": 6, "A05": 5,
    "A06": 3, "A07": 4, "A08": 7, "A09": 2, "A10": 5,
    "A11": 3, "A12": 6, "A13": 4, "A14": 2, "A15": 5,
    "A16": 7, "A17": 3, "A18": 4, "A19": 5, "A20": 6,
}

required = {f"A{k:02d}": (2 if k in (4, 8, 12, 16, 20) else 1) for k in range(1, 21)}

cost_rows = [
    [None, 6, 9, 12, None, 18, 8, 11, 14, 17, 7, 10, 13, 16, None, 9, 12, 15, None, 8],
    [10, 13, None, 6, 9, None, 15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, 15],
    [None, 7, 10, 13, 16, 6, 9, 12, 15, 18, None, 11, 14, 17, None, 10, 13, None, 6, 9],
    [11, None, 17, 7, 10, None, 16, 6, None, 12, 15, 18, None, 11, 14, 17, 7, 10, 13, 16],
    [18, 8, 11, None, 17, 7, None, 13, 16, 6, None, 12, 15, None, 8, 11, 14, None, 7, 10],
    [12, None, 18, 8, None, 14, 17, 7, None, 13, 16, None, 9, 12, 15, None, 8, 11, None, 17],
    [6, 9, None, 15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, None, 18, 8, 11],
    [None, 16, 6, 9, None, 15, 18, None, 11, 14, 17, None, 10, 13, None, 6, 9, 12, None, 18],
    [7, 10, None, 16, 6, None, 12, 15, 18, None, 11, 14, None, 7, 10, 13, None, 6, 9, None],
    [None, 17, 7, None, 13, 16, 6, None, 12, 15, None, 8, 11, 14, None, 7, 10, None, 16, 6],
    [8, None, 14, 17, 7, None, 13, 16, None, 9, 12, 15, None, 8, 11, None, 17, 7, 10, None],
    [15, 18, 8, None, 14, 17, None, 10, 13, 16, None, 9, 12, None, 18, 8, 11, None, 17, 7],
]

cost = {}
for idx, insp in enumerate(inspectors):
    cost[insp] = {}
    for j, aud in enumerate(audits):
        cost[insp][aud] = cost_rows[idx][j]

fixed_cost = {
    "I1": 18, "I2": 23, "I3": 28, "I4": 22,
    "I5": 27, "I6": 21, "I7": 26, "I8": 20,
    "I9": 25, "I10": 19, "I11": 24, "I12": 18,
}

hours = {
    "I1": 13, "I2": 14, "I3": 15, "I4": 16,
    "I5": 17, "I6": 13, "I7": 14, "I8": 15,
    "I9": 16, "I10": 17, "I11": 13, "I12": 14,
}

max_audits = {
    "I1": 3, "I2": 3, "I3": 3, "I4": 3,
    "I5": 4, "I6": 4, "I7": 4, "I8": 4,
    "I9": 4, "I10": 4, "I11": 4, "I12": 4,
}

senior = {"I1", "I2", "I3", "I4"}

m = Model("audit_assignment")
m.setParam("OutputFlag", 0)

y = {i: m.addVar(vtype=GRB.BINARY, name=f"y_{i}") for i in inspectors}
x = {}
for i in inspectors:
    for a in audits:
        if cost[i][a] is not None:
            x[i, a] = m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{a}")

m.setObjective(
    quicksum(fixed_cost[i] * y[i] for i in inspectors)
    + quicksum(cost[i][a] * x[i, a] for (i, a) in x),
    GRB.MINIMIZE
)

for a in audits:
    m.addConstr(
        quicksum(x[i, a] for i in inspectors if (i, a) in x) == required[a],
        name=f"req_{a}"
    )

for a in audits:
    if required[a] == 2:
        m.addConstr(
            quicksum(x[i, a] for i in senior if (i, a) in x) >= 1,
            name=f"senior_{a}"
        )

for i in inspectors:
    m.addConstr(
        quicksum(durations[a] * x[i, a] for a in audits if (i, a) in x) <= hours[i] * y[i],
        name=f"hours_{i}"
    )
    m.addConstr(
        quicksum(x[i, a] for a in audits if (i, a) in x) <= max_audits[i] * y[i],
        name=f"audits_{i}"
    )
    m.addConstr(
        y[i] <= quicksum(x[i, a] for a in audits if (i, a) in x),
        name=f"use_{i}"
    )
    for a in audits:
        if (i, a) in x:
            m.addConstr(x[i, a] <= y[i], name=f"link_{i}_{a}")

for a1, a2 in [("A01", "A02"), ("A06", "A07"), ("A11", "A12"), ("A17", "A18")]:
    for i in inspectors:
        if (i, a1) in x and (i, a2) in x:
            m.addConstr(x[i, a1] + x[i, a2] <= 1, name=f"inc_{i}_{a1}_{a2}")

m.addConstr(quicksum(y[i] for i in inspectors) <= 10, name="max_active")

m.optimize()

status_map = {}
for _name in (
    "LOADED", "OPTIMAL", "INFEASIBLE", "INF_OR_UNBD", "UNBOUNDED",
    "CUTOFF", "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT", "SOLUTION_LIMIT",
    "INTERRUPTED", "NUMERIC", "SUBOPTIMAL", "USER_OBJ_LIMIT", "WORK_LIMIT",
    "MEM_LIMIT", "NO_MEMORY", "FAILED"
):
    _val = getattr(GRB, _name, None)
    if isinstance(_val, int):
        status_map[_val] = _name

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: float(v.X) for v in m.getVars()}
else:
    status = status_map.get(m.Status, str(m.Status))
    objective = None
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {"status": status, "objective": objective, "variables": variables},
    separators=(",", ":")
))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
