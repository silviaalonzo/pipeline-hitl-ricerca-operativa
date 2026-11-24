# Handoff 1 — M03 / deepseek-v4-flash

- **Stadio:** 3
- **Categoria:** output_troncato_o_senza_codice
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** Atteso un solo blocco Python, trovati 0
- **Cicli automatici già usati:** 3
- **Ground truth mostrata:** no

## Diagnosi automatica

Atteso un solo blocco Python, trovati 0

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | length | 1658 | 23240 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 3 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |

## Traccia

# M03 — Assegnazione del personale ai turni

Difficoltà: Media
Classe: IP binaria

Un centro operativo deve coprire sei turni con sei dipendenti. Ogni turno richiede esattamente una persona; ogni dipendente può lavorare al massimo due turni e non più di un turno notturno.
Le celle indicate con “—” rappresentano indisponibilità. Minimizzare il costo complessivo dei turni.

## Costi e disponibilità

Dipendente | M1 | M2 | P1 | P2 | N1 | N2
--- | --- | --- | --- | --- | --- | ---
Ana | 8 | 7 | 9 | 8 | — | —
Bruno | 7 | 8 | 8 | 9 | — | —
Carla | — | 9 | 8 | 8 | 11 | 12
Diego | 10 | — | 9 | 8 | 10 | 11
Elena | 8 | 10 | 9 | 9 | 12 | 10
Fabio | 9 | 8 | 10 | 7 | — | —

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Ultima risposta non vuota disponibile (tentativo 1)

```python
```python
import gurobipy as gp
from gurobipy import GRB
import json

employees = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
shifts = ["M1", "M2", "P1", "P2", "N1", "N2"]

cost = {
    ("Ana", "M1"): 8, ("Ana", "M2"): 7, ("Ana", "P1"): 9, ("Ana", "P2"): 8,
    ("Bruno", "M1"): 7, ("Bruno", "M2"): 8, ("Bruno", "P1"): 8, ("Bruno", "P2"): 9,
    ("Carla", "M2"): 9, ("Carla", "P1"): 8, ("Carla", "P2"): 8, ("Carla", "N1"): 11, ("Carla", "N2"): 12,
    ("Diego", "M1"): 10, ("Diego", "P1"): 9, ("Diego", "P2"): 8, ("Diego", "N1"): 10, ("Diego", "N2"): 11,
    ("Elena", "M1"): 8, ("Elena", "M2"): 10, ("Elena", "P1"): 9, ("Elena", "P2"): 9, ("Elena", "N1"): 12, ("Elena", "N2"): 10,
    ("Fabio", "M1"): 9, ("Fabio", "M2"): 8, ("Fabio", "P1"): 10, ("Fabio", "P2"): 7,
}

available = [(e, s) for e in employees for s in shifts if (e, s) in cost]

m = gp.Model("M03_Turni")
m.Params.OutputFlag = 0

x = {}
for e, s in available:
    x[e, s] = m.addVar(vtype=GRB.BINARY, name=f"x[{e},{s}]")

m.setObjective(gp.quicksum(cost[e, s] * x[e, s] for e, s in available), GRB.MINIMIZE)

for s in shifts:
    m.addConstr(gp.quicksum(x[e, s] for e in employees if (e, s) in x) == 1, name=f"turno_{s}")

for e in employees:
    m.addConstr(gp.quicksum(x[e, s] for s in shifts if (e, s) in x) <= 2, name=f"max_turni_{e}")
    m.addConstr(gp.quicksum(x[e, s] for s in ("N1", "N2") if (e, s) in x) <= 1, name=f"max_notte_{e}")

m.update()
m.optimize()

if m.Status == GRB.OPTIMAL:
    status = "OPTIMAL"
    objective = float(m.ObjVal)
    variables = {v.VarName: float(v.X) for v in m.getVars()}
else:
    status = {
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
