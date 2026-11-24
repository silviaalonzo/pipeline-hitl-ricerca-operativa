# M08 · Copertura di zone con centri di servizio — Scheda Scenario A

**Dominio:** Set covering · **Classe:** IP binaria · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **106** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 106 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Centri aperti: **A** (24), **B** (20), **D** (22), **F** (19), **H** (21) — cinque centri, il
massimo consentito, per un costo di 106. Le due zone critiche ricevono la doppia copertura
richiesta: Z3 da A, B e D (tre coperture), Z7 da D e H (due, esattamente al limite).

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0006 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 10 min |
| Tempo-uomo — scrittura del codice | 15 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 10 min |
| **Tempo-uomo totale** | **50 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** I dieci vincoli di copertura sono stati ricavati a mano invertendo la tabella
«centro → zone coperte» in «zona → centri che la coprono», e il controllo indipendente
conferma che tutte e dieci le righe corrispondono alla tabella del testo. La doppia copertura
di Z3 e Z7 è resa alzando a 2 il termine noto delle due righe corrispondenti, che è la forma
corretta. Il limite sul numero di centri è un vincolo di cardinalità separato.

Questa inversione della matrice di copertura è il passaggio in cui in genere si perdono righe
o si scambiano indici; qui è stata eseguita senza errori.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 8 (binarie di apertura, una per centro) |
| Vincoli | 11 (10 di copertura + 1 sul numero massimo di centri) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M08.sol` — file soluzione di Gurobi
