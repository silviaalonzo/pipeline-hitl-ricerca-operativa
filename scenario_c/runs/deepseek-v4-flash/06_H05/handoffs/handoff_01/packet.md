# Handoff 1 — H05 / deepseek-v4-flash

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
| 0 | INITIAL | length | 0 | 23999 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 3100 | 19345 | sì | corretta |

## Traccia

# H05 — Portafoglio pluriennale con sinergie

Difficoltà: Elevata
Classe: IP binaria

Un’impresa seleziona progetti su un orizzonte triennale. Deve massimizzare il VAN complessivo rispettando budget annuali pari a 110, 100 e 90, un limite di 28 unità di personale e un rischio complessivo non superiore a 32.
G richiede B, J richiede E e K richiede C. Le coppie D–H e F–L sono incompatibili. Servono almeno due progetti digitali tra A, C, G e J e almeno un progetto sostenibile tra E, H e K; si possono scegliere al massimo otto progetti.
Se A e C sono entrambi scelti si ottiene una sinergia di 12; se E e K sono entrambi scelti la sinergia è 10. Le sinergie devono essere modellate esplicitamente.

## Dati dei progetti

Prog. | VAN | Costo A1 | Costo A2 | Costo A3 | Personale | Rischio
--- | --- | --- | --- | --- | --- | ---
A | 42 | 18 | 12 | 10 | 4 | 5
B | 35 | 20 | 18 | 14 | 4 | 4
C | 48 | 25 | 20 | 18 | 5 | 6
D | 31 | 15 | 14 | 12 | 3 | 3
E | 40 | 22 | 16 | 15 | 4 | 4
F | 28 | 14 | 12 | 10 | 3 | 2
G | 55 | 30 | 25 | 22 | 6 | 7
H | 37 | 20 | 18 | 16 | 4 | 5
I | 33 | 17 | 15 | 12 | 3 | 3
J | 50 | 27 | 21 | 18 | 5 | 6
K | 46 | 24 | 19 | 17 | 5 | 5
L | 29 | 16 | 13 | 11 | 3 | 3

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

projects = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

data = {
    "A": (42, 18, 12, 10, 4, 5),
    "B": (35, 20, 18, 14, 4, 4),
    "C": (48, 25, 20, 18, 5, 6),
    "D": (31, 15, 14, 12, 3, 3),
    "E": (40, 22, 16, 15, 4, 4),
    "F": (28, 14, 12, 10, 3, 2),
    "G": (55, 30, 25, 22, 6, 7),
    "H": (37, 20, 18, 16, 4, 5),
    "I": (33, 17, 15, 12, 3, 3),
    "J": (50, 27, 21, 18, 5, 6),
    "K": (46, 24, 19, 17, 5, 5),
    "L": (29, 16, 13, 11, 3, 3),
}

van = {p: data[p][0] for p in projects}
c1 = {p: data[p][1] for p in projects}
c2 = {p: data[p][2] for p in projects}
c3 = {p: data[p][3] for p in projects}
pers = {p: data[p][4] for p in projects}
risk = {p: data[p][5] for p in projects}

model = gp.Model("H05_portfolio")
model.setParam("OutputFlag", 0)

x = {}
for p in projects:
    x[p] = model.addVar(vtype=GRB.BINARY, name=f"x_{p}")

y_AC = model.addVar(vtype=GRB.BINARY, name="y_AC")
y_EK = model.addVar(vtype=GRB.BINARY, name="y_EK")

model.update()

model.setObjective(
    gp.quicksum(van[p] * x[p] for p in projects) + 12 * y_AC + 10 * y_EK,
    GRB.MAXIMIZE,
)

model.addConstr(gp.quicksum(c1[p] * x[p] for p in projects) <= 110, "budget_anno1")
model.addConstr(gp.quicksum(c2[p] * x[p] for p in projects) <= 100, "budget_anno2")
model.addConstr(gp.quicksum(c3[p] * x[p] for p in projects) <= 90, "budget_anno3")
model.addConstr(gp.quicksum(pers[p] * x[p] for p in projects) <= 28, "personale")
model.addConstr(gp.quicksum(risk[p] * x[p] for p in projects) <= 32, "rischio")
model.addConstr(gp.quicksum(x[p] for p in projects) <= 8, "max_progetti")

model.addConstr(x["G"] <= x["B"], "G_richiede_B")
model.addConstr(x["J"] <= x["E"], "J_richiede_E")
model.addConstr(x["K"] <= x["C"], "K_richiede_C")

model.addConstr(x["D"] + x["H"] <= 1, "D_H_incompatibili")
model.addConstr(x["F"] + x["L"] <= 1, "F_L_incompatibili")

model.addConstr(x["A"] + x["C"] + x["G"] + x["J"] >= 2, "almeno_due_digitali")
model.addConstr(x["E"] + x["H"] + x["K"] >= 1, "almeno_uno_sostenibile")

model.addConstr(y_AC <= x["A"], "yAC_le_A")
model.addConstr(y_AC <= x["C"], "yAC_le_C")
model.addConstr(y_AC >= x["A"] + x["C"] - 1, "yAC_ge_AC")

model.addConstr(y_EK <= x["E"], "yEK_le_E")
model.addConstr(y_EK <= x["K"], "yEK_le_K")
model.addConstr(y_EK >= x["E"] + x["K"] - 1, "yEK_ge_EK")

model.optimize()

if model.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(model.ObjVal)
    variables = {v.VarName: float(v.X) for v in model.getVars()}
else:
    status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.NODE_LIMIT: "NODE_LIMIT",
    }.get(model.Status, str(model.Status))
    objective = None
    variables = {}

result = {
    "status": status,
    "objective": objective,
    "variables": variables,
}

print("SOLUTION_JSON=" + json.dumps(result))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
