# Handoff 1 — H02 / deepseek-v4-flash

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
| 1 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 3 | AUTO_REPAIR | length | 439 | 23768 | no | output_troncato_o_senza_codice |

## Traccia

# H02 — Produzione multi-periodo con setup e scorte

Difficoltà: Elevata
Classe: MILP intera

Un impianto pianifica la produzione di tre articoli per quattro periodi. La domanda deve essere soddisfatta senza arretrati mediante produzione corrente e scorte provenienti dal periodo precedente. Le scorte iniziali sono 0 unità di A, 0 di B e 6 di C.
L’avvio di un articolo in un periodo comporta un setup. Si possono attivare al massimo due articoli per periodo, la scorta totale non può superare 20 unità e tutte le scorte finali devono essere nulle.
La capacità è espressa in ore. Produzione e scorte sono quantità intere. Minimizzare costi di produzione, setup e mantenimento.

## Domande per periodo

Prodotto | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
A | 8 | 12 | 10 | 14
B | 10 | 8 | 14 | 12
C | 6 | 9 | 7 | 11

## Costi unitari di produzione

Prodotto | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
A | 9 | 11 | 10 | 12
B | 8 | 9 | 11 | 10
C | 13 | 12 | 14 | 11

## Parametri per prodotto

Prodotto | Setup | Holding | Ore/unità | Lotto min.
--- | --- | --- | --- | ---
A | 45 | 2 | 2 | 4
B | 40 | 3 | 3 | 4
C | 50 | 2 | 4 | 3

## Capacità

Periodo | T1 | T2 | T3 | T4
--- | --- | --- | --- | ---
Ore | 90 | 95 | 90 | 100

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Ultima risposta non vuota disponibile (tentativo 3)

```python
```python
import gurobipy as gp
import json

products = ["A", "B", "C"]
periods = [1, 2, 3, 4]

demand = {
    "A": [8, 12, 10, 14],
    "B": [10, 8, 14, 12],
    "C": [6, 9, 7, 11],
}

prod_cost = {
    "A": [9, 11, 10, 12],
    "B": [8, 9, 11, 10],
    "C": [13, 12, 14, 11],
}

setup_cost = {"A": 45, "B": 40, "C": 50}
holding_cost = {"A": 2, "B": 3, "C": 2}
hours_per_unit = {"A": 2, "B": 3, "C": 4}
min_lot = {"A": 4, "B": 4, "C": 3}
```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
