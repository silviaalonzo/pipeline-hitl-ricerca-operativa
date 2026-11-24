# Handoff 1 — H03 / deepseek-v4-flash

- **Stadio:** 2
- **Categoria:** revisione_di_assicurazione_post_riparazione
- **Tipo di handoff:** ASSURANCE_REVIEW
- **Dettaglio:** Problema di difficoltà elevata risolto dopo almeno una riparazione automatica: il protocollo richiede una revisione umana prima dell'accettazione.
- **Cicli automatici già usati:** 2
- **Ground truth mostrata:** no

## Diagnosi automatica

Il problema è di difficoltà elevata e la soluzione ha richiesto almeno una riparazione automatica. Prima dell'accettazione, il protocollo richiede una revisione umana del modello e del codice rispetto alla traccia, senza mostrare la ground truth.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | stop | 2980 | 19411 | sì | corretta |

## Traccia

# H03 — Turnazione settimanale con competenze e riposi

Difficoltà: Elevata
Classe: IP binaria

Un servizio deve pianificare otto dipendenti su sette giorni. Ogni giorno deve essere coperta almeno la domanda indicata e deve essere presente almeno un senior tra E1, E2 ed E3.
Ogni dipendente lavora da tre a cinque giorni e non può lavorare quattro giorni consecutivi. E7 ed E8 sono specialisti: almeno uno deve essere presente giovedì e venerdì. E1 ed E2 possono lavorare al massimo uno dei due giorni del fine settimana.
Le indisponibilità sono indicate con “—”. Minimizzare il costo del piano settimanale.

## Domanda giornaliera

Giorno | Lun | Mar | Mer | Gio | Ven | Sab | Dom
--- | --- | --- | --- | --- | --- | --- | ---
Addetti | 4 | 3 | 4 | 4 | 5 | 3 | 3

## Costi e disponibilità

Dipendente | Lun | Mar | Mer | Gio | Ven | Sab | Dom
--- | --- | --- | --- | --- | --- | --- | ---
E1 | 9 | 9 | 10 | 9 | 11 | 14 | —
E2 | 10 | 9 | 9 | 10 | 10 | — | 14
E3 | 9 | 10 | 9 | 9 | 12 | 12 | 13
E4 | 7 | — | 7 | 8 | 8 | 11 | 11
E5 | 8 | 7 | 8 | — | 9 | 10 | 12
E6 | — | 8 | 8 | 7 | 8 | 12 | 10
E7 | 8 | 8 | 7 | 9 | 7 | 11 | —
E8 | 9 | 7 | 8 | 8 | 7 | 10 | 11

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Codice da esaminare

```python
import json
import gurobipy as gp
from gurobipy import GRB

employees = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

demand = {
    "Lun": 4,
    "Mar": 3,
    "Mer": 4,
    "Gio": 4,
    "Ven": 5,
    "Sab": 3,
    "Dom": 3,
}

cost = {
    "E1": [9, 9, 10, 9, 11, 14, None],
    "E2": [10, 9, 9, 10, 10, None, 14],
    "E3": [9, 10, 9, 9, 12, 12, 13],
    "E4": [7, None, 7, 8, 8, 11, 11],
    "E5": [8, 7, 8, None, 9, 10, 12],
    "E6": [None, 8, 8, 7, 8, 12, 10],
    "E7": [8, 8, 7, 9, 7, 11, None],
    "E8": [9, 7, 8, 8, 7, 10, 11],
}

seniors = ["E1", "E2", "E3"]
specialists = ["E7", "E8"]

model = gp.Model("turnazione_settimanale")
model.Params.OutputFlag = 0

x = model.addVars(employees, days, vtype=GRB.BINARY, name="x")

for emp in employees:
    for idx, day in enumerate(days):
        if cost[emp][idx] is None:
            model.addConstr(x[emp, day] == 0, name=f"unavail_{emp}_{day}")

model.setObjective(
    gp.quicksum(
        cost[emp][idx] * x[emp, days[idx]]
        for emp in employees
        for idx in range(len(days))
        if cost[emp][idx] is not None
    ),
    GRB.MINIMIZE,
)

for day in days:
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in employees) >= demand[day],
        name=f"demand_{day}",
    )
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in seniors) >= 1,
        name=f"senior_{day}",
    )

for emp in employees:
    model.addConstr(
        gp.quicksum(x[emp, day] for day in days) >= 3,
        name=f"min_days_{emp}",
    )
    model.addConstr(
        gp.quicksum(x[emp, day] for day in days) <= 5,
        name=f"max_days_{emp}",
    )
    for start in range(4):
        model.addConstr(
            gp.quicksum(x[emp, days[start + k]] for k in range(4)) <= 3,
            name=f"no4_{emp}_{days[start]}",
        )

for day in ["Gio", "Ven"]:
    model.addConstr(
        gp.quicksum(x[emp, day] for emp in specialists) >= 1,
        name=f"specialist_{day}",
    )

model.addConstr(
    x["E1", "Sab"] + x["E1", "Dom"] + x["E2", "Sab"] + x["E2", "Dom"] <= 1,
    name="weekend_E1_E2",
)

model.optimize()

status_names = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

if model.Status == GRB.OPTIMAL:
    result = {
        "status": "OPTIMAL",
        "objective": float(model.ObjVal),
        "variables": {v.VarName: v.X for v in model.getVars()},
    }
else:
    result = {
        "status": status_names.get(model.Status, str(model.Status)),
        "objective": 0.0,
        "variables": {},
    }

print("SOLUTION_JSON=" + json.dumps(result, separators=(",", ":")))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
