# Handoff 1 — H10 / deepseek-v4-flash

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
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 3096 | 22295 | sì | corretta |

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
from gurobipy import Model, GRB, quicksum
import json

products = ["K1", "K2"]
arcs = [
    ("S", "A"), ("S", "B"), ("A", "B"), ("A", "C"),
    ("B", "C"), ("B", "D"), ("C", "D"), ("C", "T"), ("D", "T")
]

fixed_cost = {
    ("S", "A"): 55, ("S", "B"): 50, ("A", "B"): 18, ("A", "C"): 38,
    ("B", "C"): 22, ("B", "D"): 35, ("C", "D"): 20, ("C", "T"): 48,
    ("D", "T"): 44
}

capacity = {
    ("S", "A"): 35, ("S", "B"): 35, ("A", "B"): 15, ("A", "C"): 30,
    ("B", "C"): 25, ("B", "D"): 25, ("C", "D"): 20, ("C", "T"): 35,
    ("D", "T"): 35
}

unit_cost = {
    "K1": {
        ("S", "A"): 2, ("S", "B"): 3, ("A", "B"): 1, ("A", "C"): 2,
        ("B", "C"): 2, ("B", "D"): 3, ("C", "D"): 1, ("C", "T"): 3,
        ("D", "T"): 2
    },
    "K2": {
        ("S", "A"): 3, ("S", "B"): 2, ("A", "B"): 2, ("A", "C"): 3,
        ("B", "C"): 1, ("B", "D"): 2, ("C", "D"): 2, ("C", "T"): 2,
        ("D", "T"): 3
    }
}

demand = {"K1": 28, "K2": 22}

m = Model("H10")
m.setParam("OutputFlag", 0)
m.setParam("MIPGap", 0)

x = {}
for p in products:
    for a in arcs:
        x[p, a] = m.addVar(
            vtype=GRB.INTEGER,
            lb=0,
            name=f"x_{p}_{a[0]}_{a[1]}"
        )

y = {}
for a in arcs:
    y[a] = m.addVar(vtype=GRB.BINARY, name=f"y_{a[0]}_{a[1]}")

m.setObjective(
    quicksum(fixed_cost[a] * y[a] for a in arcs) +
    quicksum(unit_cost[p][a] * x[p, a] for p in products for a in arcs),
    GRB.MINIMIZE
)

for a in arcs:
    m.addConstr(
        quicksum(x[p, a] for p in products) <= capacity[a] * y[a],
        name=f"cap_{a[0]}_{a[1]}"
    )

m.addConstr(y[("S", "A")] == 1, name="req_SA")
m.addConstr(y[("S", "B")] == 1, name="req_SB")
m.addConstr(quicksum(y[a] for a in arcs) <= 7, name="max_arcs")

nodes = ["S", "A", "B", "C", "D", "T"]
out_arcs = {n: [a for a in arcs if a[0] == n] for n in nodes}
in_arcs = {n: [a for a in arcs if a[1] == n] for n in nodes}

for p in products:
    m.addConstr(
        quicksum(x[p, a] for a in out_arcs["S"]) == demand[p],
        name=f"source_{p}"
    )
    m.addConstr(
        quicksum(x[p, a] for a in in_arcs["T"]) == demand[p],
        name=f"sink_{p}"
    )
    for n in ["A", "B", "C", "D"]:
        m.addConstr(
            quicksum(x[p, a] for a in in_arcs[n]) ==
            quicksum(x[p, a] for a in out_arcs[n]),
            name=f"balance_{p}_{n}"
        )

m.optimize()

status_map = {
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.NUMERIC: "NUMERIC"
}

status = status_map.get(m.Status, str(m.Status))

if status == "OPTIMAL":
    objective = float(m.ObjVal)
    variables = {
        v.VarName: float(v.X)
        for v in sorted(m.getVars(), key=lambda var: var.VarName)
    }
else:
    objective = 0.0
    variables = {}

print("SOLUTION_JSON=" + json.dumps(
    {
        "status": status,
        "objective": objective,
        "variables": variables
    },
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
