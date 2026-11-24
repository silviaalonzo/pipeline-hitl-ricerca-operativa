# Handoff 1 — H09 / deepseek-v4-flash

- **Stadio:** 3
- **Categoria:** output_troncato_o_senza_codice
- **Tipo di handoff:** CORRECTION
- **Dettaglio:** Atteso un solo blocco Python, trovati 0
- **Cicli automatici già usati:** 3
- **Ground truth mostrata:** no

## Diagnosi automatica

Tutti i tentativi hanno esaurito il limite di output nel ragionamento interno: il modello non ha emesso contenuto finale né codice eseguibile. L'handoff riguarda quindi la capacità di concludere la risposta, non un errore matematico già osservabile.

| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | INITIAL | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 1 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 2 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |
| 3 | AUTO_REPAIR | length | 0 | 24000 | no | output_troncato_o_senza_codice |

## Traccia

# H09 — Produzione e scorte multi-prodotto con straordinario

Difficoltà: Elevata
Classe: MILP

Un impianto pianifica tre prodotti per sei periodi. La domanda deve essere soddisfatta senza arretrati; le scorte iniziali sono nulle e a fine orizzonte devono restare almeno 2 unità di ciascun prodotto.
Ogni prodotto richiede un setup nel periodo in cui viene prodotto e un lotto minimo. Nel primo periodo possono essere attivati tutti e tre i prodotti; nei periodi successivi se ne possono attivare al massimo due. La capacità base può essere aumentata con al massimo 20 ore di straordinario al costo di 18 per ora.
La scorta totale a fine periodo non può superare 40. Produzione e scorte sono intere; lo straordinario è continuo. Minimizzare tutti i costi.

## Domanda

Prodotto | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
A | 12 | 18 | 14 | 20 | 16 | 19
B | 10 | 9 | 15 | 12 | 17 | 14
C | 8 | 11 | 10 | 13 | 9 | 15

## Costo unitario di produzione

Prodotto | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
A | 7 | 8 | 9 | 7 | 10 | 8
B | 9 | 8 | 8 | 10 | 7 | 9
C | 11 | 10 | 12 | 9 | 11 | 8

## Parametri di prodotto

Prodotto | Setup | Holding | Ore/unità | Lotto min.
--- | --- | --- | --- | ---
A | 35 | 2 | 2 | 5
B | 40 | 2 | 3 | 4
C | 45 | 3 | 4 | 3

## Capacità base

Periodo | T1 | T2 | T3 | T4 | T5 | T6
--- | --- | --- | --- | --- | --- | ---
Ore | 120 | 115 | 125 | 110 | 120 | 115

## Consegna

1. Definire con precisione insiemi, parametri e variabili decisionali.
2. Formulare il modello matematico completo, indicando dominio delle variabili, funzione obiettivo e vincoli.
3. Scrivere codice Python eseguibile con Gurobi che costruisca e risolva il modello.
4. Riportare lo stato del solver, il valore ottimo e tutte le decisioni non nulle.

## Ultima risposta non vuota disponibile

```python

```

## Cosa deve fornire l'esperto

1. I minuti di lavoro attivo.
2. Un'istruzione precisa con la correzione da applicare.
3. Una breve sintesi della correzione.
4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.
