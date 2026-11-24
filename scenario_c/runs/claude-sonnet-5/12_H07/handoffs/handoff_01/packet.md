# Handoff 1 — H07 / claude-sonnet-5

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
| 0 | INITIAL | stop | 6282 | 3342 | sì | soluzione_non_leggibile |
| 1 | AUTO_REPAIR | stop | 3113 | 0 | sì | corretta |

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

suppliers = ['A','B','C','D','E','F']
components = ['C1','C2','C3']

demand = {'C1':80,'C2':70,'C3':60}
fixed  = {'A':120,'B':140,'C':100,'D':150,'E':90,'F':110}
cap    = {'A':100,'B':110,'C':90,'D':120,'E':80,'F':95}
risk   = {'A':2,'B':3,'C':1,'D':4,'E':2,'F':3}

cost = {
    ('A','C1'):9, ('A','C2'):12, ('A','C3'):11,
    ('B','C1'):10,('B','C2'):9,  ('B','C3'):12,
    ('C','C1'):11,('C','C2'):10, ('C','C3'):9,
                 ('D','C2'):11, ('D','C3'):10,
    ('E','C1'):12,('E','C2'):8,
    ('F','C1'):10,               ('F','C3'):8,
}

quality = {
    ('A','C1'):96, ('A','C2'):94, ('A','C3'):95,
    ('B','C1'):93, ('B','C2'):97, ('B','C3'):92,
    ('C','C1'):98, ('C','C2'):95, ('C','C3'):96,
                    ('D','C2'):94, ('D','C3'):93,
    ('E','C1'):97, ('E','C2'):98,
    ('F','C1'):94,                ('F','C3'):98,
}

S = list(cost.keys())

m = gp.Model("H07_sourcing")
m.Params.OutputFlag = 0

x = m.addVars(S, vtype=GRB.INTEGER, lb=0, name="x")
z = m.addVars(S, vtype=GRB.BINARY, name="z")
y = m.addVars(suppliers, vtype=GRB.BINARY, name="y")

# 1. Domanda esatta
for k in components:
    m.addConstr(
        gp.quicksum(x[i,k] for i in suppliers if (i,k) in cost) == demand[k],
        name=f"demand_{k}"
    )

# 2. Legame quantità-uso e minimo 10 unità
for (i,k) in S:
    M_ik = min(cap[i], demand[k])
    m.addConstr(x[i,k] <= M_ik * z[i,k], name=f"bigM_{i}_{k}")
    m.addConstr(x[i,k] >= 10 * z[i,k], name=f"min10_{i}_{k}")

# 3. Almeno 2 fornitori per componente
for k in components:
    m.addConstr(
        gp.quicksum(z[i,k] for i in suppliers if (i,k) in cost) >= 2,
        name=f"multisource_{k}"
    )

# 4. Capacità complessiva per fornitore
for i in suppliers:
    m.addConstr(
        gp.quicksum(x[i,k] for k in components if (i,k) in cost) <= cap[i]*y[i],
        name=f"cap_{i}"
    )

# 5. Coerenza uso-attivazione
for (i,k) in S:
    m.addConstr(z[i,k] <= y[i], name=f"link_{i}_{k}")

# 6. Massimo 4 fornitori attivi
m.addConstr(gp.quicksum(y[i] for i in suppliers) <= 4, name="max_suppliers")

# 7. Almeno uno tra A e B
m.addConstr(y['A'] + y['B'] >= 1, name="A_or_B")

# 8. Qualità media minima
for k in components:
    m.addConstr(
        gp.quicksum(quality[i,k]*x[i,k] for i in suppliers if (i,k) in cost) >= 95*demand[k],
        name=f"quality_{k}"
    )

# 9. Rischio totale massimo
m.addConstr(
    gp.quicksum(risk[i]*x[i,k] for (i,k) in S) <= 580,
    name="risk_total"
)

# Obiettivo
m.setObjective(
    gp.quicksum(cost[i,k]*x[i,k] for (i,k) in S) +
    gp.quicksum(fixed[i]*y[i] for i in suppliers),
    GRB.MINIMIZE
)

m.optimize()

status = m.Status
if status == GRB.OPTIMAL:
    variables = {}
    for (i,k) in S:
        variables[f"x_{i}_{k}"] = x[i,k].X
        variables[f"z_{i}_{k}"] = z[i,k].X
    for i in suppliers:
        variables[f"y_{i}"] = y[i].X
    obj = m.ObjVal
    result = {"status":"OPTIMAL","objective":obj,"variables":variables}
else:
    result = {"status":str(status),"objective":None,"variables":{}}

print(f"SOLUTION_JSON={json.dumps(result)}")
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
