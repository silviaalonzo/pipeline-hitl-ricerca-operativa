# Handoff 1 — L01 / deepseek-v4-flash

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
| 0 | INITIAL | length | 2441 | 62983 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | stop | 4430 | 27547 | sì | corretta |

## Traccia

# L01 — Assegnazione di consegne a una flotta con limiti individuali

Difficoltà: Elevata
Classe: IP binaria

Un operatore deve assegnare sedici rotte a otto veicoli. Ogni rotta deve essere affidata a un solo veicolo. Un veicolo può essere usato soltanto se attivato e deve rispettare sia la capacità complessiva di carico sia il numero massimo di rotte riportati in tabella.

Devono essere attivati al massimo sette veicoli e almeno due dei tre elettrici. Le rotte R06, R09, R11, R13, R15 e R16 sono lunghe: ciascun veicolo elettrico può servirne al massimo una. Inoltre, ciascun diesel può effettuare al massimo due delle rotte di centro R01, R03, R05, R08 e R12. Le emissioni complessive, calcolate come distanza per fattore del veicolo, non possono superare 1.050. Minimizzare costi fissi e di assegnazione.

## Veicoli

Veicolo | Tipo | Costo fisso | Capacità | Rotte max | Fattore emissione
--- | --- | --- | --- | --- | ---
E1 | Elettrico | 62 | 30 | 3 | 0
E2 | Elettrico | 58 | 32 | 3 | 0
E3 | Elettrico | 55 | 28 | 3 | 0
D1 | Diesel | 46 | 38 | 4 | 3
D2 | Diesel | 44 | 40 | 4 | 2
D3 | Diesel | 41 | 36 | 4 | 3
D4 | Diesel | 49 | 42 | 4 | 2
D5 | Diesel | 43 | 35 | 4 | 3

## Rotte

Rotta | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 | R16
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Carico | 5 | 7 | 4 | 8 | 6 | 9 | 5 | 7 | 8 | 6 | 9 | 7 | 10 | 6 | 8 | 5
Distanza | 18 | 28 | 16 | 34 | 22 | 51 | 26 | 20 | 48 | 31 | 55 | 24 | 52 | 29 | 47 | 45

## Costi di assegnazione

Veicolo | R01 | R02 | R03 | R04 | R05 | R06 | R07 | R08 | R09 | R10 | R11 | R12 | R13 | R14 | R15 | R16
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
E1 | 9 | 12 | 15 | 18 | 21 | 2 | 14 | 17 | 10 | 10 | 3 | 16 | 9 | 9 | 2 | 5
E2 | 16 | 19 | 9 | 12 | 15 | 9 | 21 | 11 | 5 | 17 | 11 | 10 | 4 | 16 | 10 | 3
E3 | 10 | 13 | 16 | 19 | 9 | 3 | 15 | 18 | 11 | 11 | 4 | 17 | 10 | 10 | 3 | 6
D1 | 17 | 20 | 10 | 13 | 16 | 19 | 9 | 12 | 15 | 18 | 21 | 11 | 14 | 17 | 20 | 10
D2 | 11 | 14 | 17 | 20 | 10 | 13 | 16 | 19 | 9 | 12 | 15 | 18 | 21 | 11 | 14 | 17
D3 | 18 | 21 | 11 | 14 | 17 | 20 | 10 | 13 | 16 | 19 | 9 | 12 | 15 | 18 | 21 | 11
D4 | 12 | 15 | 18 | 21 | 11 | 14 | 17 | 20 | 10 | 13 | 16 | 19 | 9 | 12 | 15 | 18
D5 | 19 | 9 | 12 | 15 | 18 | 21 | 11 | 14 | 17 | 20 | 10 | 13 | 16 | 19 | 9 | 12

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Codice da esaminare

```python
import gurobipy as gp
import json

vehicles_data = [
    ("E1", "E", 62, 30, 3, 0),
    ("E2", "E", 58, 32, 3, 0),
    ("E3", "E", 55, 28, 3, 0),
    ("D1", "D", 46, 38, 4, 3),
    ("D2", "D", 44, 40, 4, 2),
    ("D3", "D", 41, 36, 4, 3),
    ("D4", "D", 49, 42, 4, 2),
    ("D5", "D", 43, 35, 4, 3),
]

routes_data = [
    ("R01", 5, 18),
    ("R02", 7, 28),
    ("R03", 4, 16),
    ("R04", 8, 34),
    ("R05", 6, 22),
    ("R06", 9, 51),
    ("R07", 5, 26),
    ("R08", 7, 20),
    ("R09", 8, 48),
    ("R10", 6, 31),
    ("R11", 9, 55),
    ("R12", 7, 24),
    ("R13", 10, 52),
    ("R14", 6, 29),
    ("R15", 8, 47),
    ("R16", 5, 45),
]

routes = [r[0] for r in routes_data]
load = {r[0]: r[1] for r in routes_data}
distance = {r[0]: r[2] for r in routes_data}

vehicle_names = [v[0] for v in vehicles_data]
vehicle_type = {v[0]: v[1] for v in vehicles_data}
fixed_cost = {v[0]: v[2] for v in vehicles_data}
capacity = {v[0]: v[3] for v in vehicles_data}
max_routes = {v[0]: v[4] for v in vehicles_data}
emission_factor = {v[0]: v[5] for v in vehicles_data}

electric = [v for v in vehicle_names if vehicle_type[v] == "E"]
diesel = [v for v in vehicle_names if vehicle_type[v] == "D"]

cost = {
    "E1": dict(zip(routes, [9, 12, 15, 18, 21, 2, 14, 17, 10, 10, 3, 16, 9, 9, 2, 5])),
    "E2": dict(zip(routes, [16, 19, 9, 12, 15, 9, 21, 11, 5, 17, 11, 10, 4, 16, 10, 3])),
    "E3": dict(zip(routes, [10, 13, 16, 19, 9, 3, 15, 18, 11, 11, 4, 17, 10, 10, 3, 6])),
    "D1": dict(zip(routes, [17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10])),
    "D2": dict(zip(routes, [11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11, 14, 17])),
    "D3": dict(zip(routes, [18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18, 21, 11])),
    "D4": dict(zip(routes, [12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12, 15, 18])),
    "D5": dict(zip(routes, [19, 9, 12, 15, 18, 21, 11, 14, 17, 20, 10, 13, 16, 19, 9, 12])),
}

long_routes = ["R06", "R09", "R11", "R13", "R15", "R16"]
center_routes = ["R01", "R03", "R05", "R08", "R12"]

m = gp.Model("L01")
m.Params.OutputFlag = 0

y = {}
for v in vehicle_names:
    y[v] = m.addVar(vtype=gp.GRB.BINARY, name=f"y_{v}")

x = {}
for v in vehicle_names:
    for r in routes:
        x[v, r] = m.addVar(vtype=gp.GRB.BINARY, name=f"x_{v}_{r}")

m.setObjective(
    gp.quicksum(fixed_cost[v] * y[v] for v in vehicle_names)
    + gp.quicksum(cost[v][r] * x[v, r] for v in vehicle_names for r in routes),
    gp.GRB.MINIMIZE
)

for r in routes:
    m.addConstr(gp.quicksum(x[v, r] for v in vehicle_names) == 1, name=f"assign_{r}")

for v in vehicle_names:
    for r in routes:
        m.addConstr(x[v, r] <= y[v], name=f"link_{v}_{r}")

for v in vehicle_names:
    m.addConstr(y[v] <= gp.quicksum(x[v, r] for r in routes), name=f"activated_used_{v}")

for v in vehicle_names:
    m.addConstr(
        gp.quicksum(load[r] * x[v, r] for r in routes) <= capacity[v] * y[v],
        name=f"capacity_{v}"
    )
    m.addConstr(
        gp.quicksum(x[v, r] for r in routes) <= max_routes[v] * y[v],
        name=f"maxroutes_{v}"
    )

m.addConstr(gp.quicksum(y[v] for v in vehicle_names) <= 7, name="max_activation")
m.addConstr(gp.quicksum(y[v] for v in electric) >= 2, name="min_electric_activation")

for v in electric:
    m.addConstr(
        gp.quicksum(x[v, r] for r in long_routes) <= 1,
        name=f"electric_long_{v}"
    )

for v in diesel:
    m.addConstr(
        gp.quicksum(x[v, r] for r in center_routes) <= 2,
        name=f"diesel_center_{v}"
    )

m.addConstr(
    gp.quicksum(emission_factor[v] * distance[r] * x[v, r] for v in diesel for r in routes) <= 1050,
    name="emission_limit"
)

m.optimize()

status_names = {}
for sname in [
    "OPTIMAL", "INFEASIBLE", "UNBOUNDED", "INF_OR_UNBD", "CUTOFF",
    "ITERATION_LIMIT", "NODE_LIMIT", "TIME_LIMIT", "SOLUTION_LIMIT",
    "INTERRUPTED", "NUMERIC", "SUBOPTIMAL", "INPROGRESS"
]:
    if hasattr(gp.GRB, sname):
        status_names[getattr(gp.GRB, sname)] = sname

if m.Status == gp.GRB.OPTIMAL:
    status_str = "OPTIMAL"
    objective = m.ObjVal
    solution_vars = {var.VarName: var.X for var in m.getVars()}
else:
    status_str = status_names.get(m.Status, str(m.Status))
    objective = None
    solution_vars = {}

output = {
    "status": status_str,
    "objective": objective,
    "variables": solution_vars,
}

print("SOLUTION_JSON=" + json.dumps(output, separators=(",", ":")))
```

## Checklist di revisione dello Stadio 2

Verificare il codice rispetto alla traccia, senza consultare la ground truth:

1. variabili decisionali e relativi domini;
2. funzione obiettivo e verso di ottimizzazione;
3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;
4. coefficienti, indici e unità di misura;
5. vincoli impliciti necessari alla corretta interpretazione del problema.

Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.
