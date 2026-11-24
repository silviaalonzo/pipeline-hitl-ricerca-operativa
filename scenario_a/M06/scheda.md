# M06 · Bilanciamento di lavori su due macchine — Scheda Scenario A

**Dominio:** Scheduling · **Classe:** MILP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **22** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 22 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Assegnazione: J1, J2, J4, J6 → macchina A (7 + 6 + 5 + 4 = 22); J3, J5, J7 → macchina B
(7 + 6 + 5 = 18). Il makespan è quindi 22, determinato dalla macchina A.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0021 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 15 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 10 min |
| **Tempo-uomo totale** | **60 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** La linearizzazione del `max` è gestita nel modo canonico: `Cmax` è introdotta
come variabile e vincolata dal basso dai carichi delle due macchine, cosa che insieme alla
minimizzazione di `Cmax` la rende uguale al massimo dei due. L'incompatibilità di J7 con la
macchina A è espressa come `x_7B = 1` anziché come `x_7A = 0`: le due scritture sono
equivalenti in presenza del vincolo di assegnazione unica, e il modello risultante è corretto.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 15 (14 binarie di assegnazione + `Cmax`) |
| Vincoli | 10 (7 assegnazione + 2 su `Cmax` + 1 incompatibilità) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## Nota di traduzione

La cella «—» della tabella dei tempi (J7 su macchina A) non ha valore numerico; il
coefficiente è posto a 0. La scelta è ininfluente perché `x_7A` è forzata a zero da
`x_7B = 1` insieme al vincolo di assegnazione unica. `Cmax` non ha dominio dichiarato nella
formulazione ed è introdotta come variabile continua non negativa; all'ottimo assume comunque
valore intero.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M06.sol` — file soluzione di Gurobi
