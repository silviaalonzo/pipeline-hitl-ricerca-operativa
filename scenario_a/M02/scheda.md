# M02 · Piano di produzione con costi di setup — Scheda Scenario A

**Dominio:** Produzione · **Classe:** MILP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **1640** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 1640 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione: `x[A] = 20`, `x[D] = 30`, `delta[A] = delta[D] = 1`.
Entrambe le risorse sono sature: 90/90 ore-macchina e 100/100 ore di lavoro.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0093 s** |
| Tempo-uomo — lettura e comprensione | 10 min |
| Tempo-uomo — formulazione matematica | 10 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **55 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 2 |
| Correzioni al codice | 1 (traduzione di `∈ Z`) |
| Correzioni alla formulazione | 0 |

La seconda esecuzione segue il chiarimento dell'autrice sul significato di `∈ Z` (interi non
negativi) ed è una correzione della **traduzione**, non della formulazione né di un errore di
sintassi. Su questo problema non cambia nulla: il risultato è 1640 in entrambe le letture,
perché la non negatività era già implicata da `x_i ≥ LOTTOMIN_i·δ_i` con `δ_i = 0`.

## 4. Difficoltà principale

**Nessuna.** Il modello è corretto al primo tentativo su tutti i fronti: comprensione,
formulazione, codice, solver e verifica. La coppia di vincoli
`x_i ≥ LOTTOMIN_i·δ_i` e `x_i ≤ DOMMAX_i·δ_i` collega correttamente le variabili di
produzione alle binarie di setup e rende superfluo un big-M esplicito.

## Nota di traduzione

La formulazione dichiara `x_i ∈ Z` senza indicarne il segno. L'autrice ha precisato
(16 agosto 2026) che con `Z` intende gli **interi non negativi**: le variabili sono quindi
dichiarate intere con il lower bound di default 0, e la convenzione è applicata in modo
uniforme a tutti i problemi che scrivono `∈ Z`. Su M02 la scelta è ininfluente, perché la non
negatività era già implicata da `x_i ≥ LOTTOMIN_i·δ_i` con `δ_i = 0`.

Riscontro dimensionale: 8 variabili e 11 vincoli, identici alla ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M02.sol` — file soluzione di Gurobi
