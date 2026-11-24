# Handoff 1 — H07 / deepseek-v4-flash

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
| 1 | AUTO_REPAIR | stop | 2781 | 20325 | no | codice_non_estratto |
| 2 | AUTO_REPAIR | stop | 4004 | 18100 | sì | corretta |

## Traccia

# H07 — Sourcing multi-componente con rischio e multisourcing

Difficoltà: Elevata
Classe: MILP intera

Un produttore deve acquistare esattamente 80 unità di C1, 70 di C2 e 60 di C3. Ogni componente deve provenire da almeno due fornitori, con almeno 10 unità per ogni combinazione fornitore–componente utilizzata.
La capacità indicata è complessiva sui tre componenti. La qualità media di ciascun componente deve essere almeno 95. Si possono attivare al massimo quattro fornitori e almeno uno tra A e B. Il rischio totale, pari a quantità per coefficiente del fornitore, non può superare 580.
Le celle “—” indicano componenti non fornibili. Minimizzare costi d’acquisto e attivazione.

## Fornitori

Fornitore | Costo fisso | Capacità totale | Rischio
--- | --- | --- | ---
A | 120 | 100 | 2
B | 140 | 110 | 3
C | 100 | 90 | 1
D | 150 | 120 | 4
E | 90 | 80 | 2
F | 110 | 95 | 3

## Costi unitari

Fornitore | C1 | C2 | C3
--- | --- | --- | ---
A | 9 | 12 | 11
B | 10 | 9 | 12
C | 11 | 10 | 9
D | — | 11 | 10
E | 12 | 8 | —
F | 10 | — | 8

## Qualità

Fornitore | C1 | C2 | C3
--- | --- | --- | ---
A | 96 | 94 | 95
B | 93 | 97 | 92
C | 98 | 95 | 96
D | — | 94 | 93
E | 97 | 98 | —
F | 94 | — | 98

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

suppliers = ["A", "B", "C", "D", "E", "F"]
components = ["C1", "C2", "C3"]

fixed_cost = {
    "A": 120,
    "B": 140,
    "C": 100,
    "D": 150,
    "E": 90,
    "F": 110,
}

capacity = {
    "A": 100,
    "B": 110,
    "C": 90,
    "D": 120,
    "E": 80,
    "F": 95,
}

risk = {
    "A": 2,
    "B": 3,
    "C": 1,
    "D": 4,
    "E": 2,
    "F": 3,
}

unit_cost = {
    ("A", "C1"): 9,
    ("A", "C2"): 12,
    ("A", "C3"): 11,
    ("B", "C1"): 10,
    ("B", "C2"): 9,
    ("B", "C3"): 12,
    ("C", "C1"): 11,
    ("C", "C2"): 10,
    ("C", "C3"): 9,
    ("D", "C2"): 11,
    ("D", "C3"): 10,
    ("E", "C1"): 12,
    ("E", "C2"): 8,
    ("F", "C1"): 10,
    ("F", "C3"): 8,
}

quality = {
    "A": {"C1": 96, "C2": 94, "C3": 95},
    "B": {"C1": 93, "C2": 97, "C3": 92},
    "C": {"C1": 98, "C2": 95, "C3": 96},
    "D": {"C2": 94, "C3": 93},
    "E": {"C1": 97, "C2": 98},
    "F": {"C1": 94, "C3": 98},
}

demand = {"C1": 80, "C2": 70, "C3": 60}

m = gp.Model("sourcing_components")
m.setParam("OutputFlag", 0)
m.setParam("MIPGap", 0)

y = {s: m.addVar(vtype=GRB.BINARY, name=f"y_{s}") for s in suppliers}
x = {}
z = {}

for s in suppliers:
    for comp in components:
        if (s, comp) in unit_cost:
            z[s, comp] = m.addVar(vtype=GRB.BINARY, name=f"z_{s}_{comp}")
            x[s, comp] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{s}_{comp}")

m.setObjective(
    gp.quicksum(fixed_cost[s] * y[s] for s in suppliers)
    + gp.quicksum(unit_cost[s, comp] * x[s, comp] for (s, comp) in x),
    GRB.MINIMIZE,
)

for comp in components:
    m.addConstr(
        gp.quicksum(x[s, comp] for s in suppliers if (s, comp) in x) == demand[comp],
        name=f"demand_{comp}",
    )

for s in suppliers:
    m.addConstr(
        gp.quicksum(x[s, comp] for comp in components if (s, comp) in x)
        <= capacity[s] * y[s],
        name=f"capacity_{s}",
    )

for s in suppliers:
    for comp in components:
        if (s, comp) in x:
            m.addConstr(z[s, comp] <= y[s], name=f"active_link_{s}_{comp}")
            m.addConstr(x[s, comp] >= 10 * z[s, comp], name=f"min_qty_{s}_{comp}")
            m.addConstr(x[s, comp] <= capacity[s] * z[s, comp], name=f"max_qty_{s}_{comp}")

m.addConstr(gp.quicksum(y[s] for s in suppliers) <= 4, name="max_active_suppliers")
m.addConstr(y["A"] + y["B"] >= 1, name="at_least_one_AB")

for comp in components:
    m.addConstr(
        gp.quicksum(z[s, comp] for s in suppliers if (s, comp) in z) >= 2,
        name=f"min_two_suppliers_{comp}",
    )

for comp in components:
    weighted_quality = gp.quicksum(
        quality[s][comp] * x[s, comp]
        for s in suppliers
        if (s, comp) in x
    )
    total_quantity = gp.quicksum(
        x[s, comp]
        for s in suppliers
        if (s, comp) in x
    )
    m.addConstr(weighted_quality >= 95 * total_quantity, name=f"quality_{comp}")

m.addConstr(
    gp.quicksum(risk[s] * x[s, comp] for s in suppliers for comp in components if (s, comp) in x)
    <= 580,
    name="risk_limit",
)

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
}

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = m.ObjVal
    variables = {}
    for s in suppliers:
        variables[y[s].VarName] = y[s].X
    for(s, comp) in x:
        variables[z[s, comp].VarName] = z[s, comp].X
        variables[x[s, comp].VarName] = x[s, comp].X
else:
    status = status_map.get(m.Status, str(m.Status))
    objective = 0.0
    variables = {}

result = {
    "status": status,
    "objective": objective,
    "variables": variables,
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
