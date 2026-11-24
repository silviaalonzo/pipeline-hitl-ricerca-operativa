# H01 · Rete capacitada di centri distributivi — Scheda Scenario A

**Dominio:** Localizzazione e distribuzione · **Classe:** MILP · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **1355** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 1355 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Siti aperti: A (55 unità movimentate su 90 di capacità), C (87 su 110), F (78 su 85).
Assegnazioni: A → Z1 30, Z2 25; C → Z3 35, Z5 28, Z7 24; F → Z4 20, Z6 32, Z8 26.
Emissioni complessive 293 sulle 470 ammesse; tre centri aperti, entro la finestra 3–4,
con A e C nel gruppo Nord e F nel gruppo Sud.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0107 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 20 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **70 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole. Le tre voci mancanti non sono deducibili dai log.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** La formulazione è completa e non ambigua: tutti i parametri usati sono
definiti, i domini sono dichiarati esplicitamente (`x_i ∈ {0,1}`, `y_ij ∈ Z ≥ 0`, con il
segno scritto) e nessun vincolo richiede interpretazione. La traduzione è avvenuta senza
scelte discrezionali e il modello ha chiuso all'ottimo alla prima esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 54 (6 binarie di apertura + 48 intere di flusso) |
| Vincoli | 25 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (54 variabili,
25 vincoli).

## Nota di traduzione

Il doppio vincolo `20·x_i ≤ Σ_j y_ij ≤ CAPACITÀ_i·x_i` e il doppio vincolo
`3 ≤ Σ_i x_i ≤ 4` sono resi come coppie di vincoli distinti, come da scrittura. La
struttura `20·x_i ≤ Σ_j y_ij` fa correttamente doppio servizio: impone il movimento
minimo di 20 unità **solo** ai centri aperti e obbliga a flusso nullo quelli chiusi,
senza bisogno di un vincolo di collegamento separato.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H01.sol` — file soluzione di Gurobi
