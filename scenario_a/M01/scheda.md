# M01 · Localizzazione di centri di assistenza — Scheda Scenario A

**Dominio:** Localizzazione e assegnazione · **Classe:** IP binaria · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **149** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 149 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione: aprono i centri **B** (costo fisso 42) e **D** (46), entrambi saturi con tre
zone ciascuno. Assegnazioni: Z1, Z2, Z3 → B (14 + 9 + 8 = 31); Z4, Z5, Z6 → D
(7 + 14 + 9 = 30). Costi fissi 88 + costi di assegnazione 61 = 149.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0106 s** |
| Tempo-uomo — lettura e comprensione | 10 min |
| Tempo-uomo — formulazione matematica | 10 min |
| Tempo-uomo — scrittura del codice | 15 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 10 min |
| **Tempo-uomo totale** | **45 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** Il modello è corretto in tutte le sue componenti e Gurobi chiude all'ottimo in
centesimi di secondo. Il punto critico di questa classe di problemi — il legame fra la
decisione di apertura e quella di assegnazione — è gestito correttamente dai vincoli di
collegamento `y_ij ≤ x_i`, che impediscono di servire una zona da un centro non aperto e
rendono effettiva la richiesta del testo di assegnare ogni zona «a un solo centro aperto».

Da notare che la capacità complessiva dei siti vincola pesantemente la scelta: fra le sei
coppie possibili solo B + D raggiunge le sei zone da servire (3 + 3), il che rende la
struttura del problema meno libera di quanto suggerisca il numero di combinazioni.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 28 (4 binarie di apertura + 24 binarie di assegnazione) |
| Vincoli | 35 (1 cardinalità + 6 assegnazione + 4 capacità + 24 collegamento) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo
- `modello.lp` — modello in formato LP, per il riscontro sulla fedeltà della traduzione
- `output_terminale.txt` — output completo del terminale
- `M01.sol` — file soluzione di Gurobi
