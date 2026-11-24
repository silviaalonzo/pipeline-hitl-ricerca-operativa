# M09 · Piano di riordino con costi fissi — Scheda Scenario A

**Dominio:** Inventory management · **Classe:** MILP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **1370** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 1370 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Piano ottenuto:

| Periodo | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Domanda | 20 | 30 | 15 | 35 | 25 | 20 |
| Ordine `x` | 10 | 50 | 0 | 55 | 0 | 25 |
| Scorta `y` | 0 | 20 | 5 | 25 | 0 | 5 |

Quattro ordini, concentrati nei periodi con prezzo d'acquisto più basso (8 nel periodo 2,
7 nel periodo 4), con anticipo della domanda dei periodi successivi. Composizione del costo:
acquisto 1100 + costi fissi 160 (4 ordini × 40) + mantenimento 110 (55 unità × 2) = **1370**.
Scorta finale 5, esattamente al minimo richiesto.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0022 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 15 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **65 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

La voce *debug e autocorrezioni* vale 0: la seconda esecuzione è la ritraduzione
conseguente al chiarimento dell'autrice, cioè un'operazione di traduzione svolta in sede
di codifica, non un ciclo di debug dell'esperto sulla propria formulazione (decisione
del 16 agosto 2026, applicata al registro il 19 agosto).

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 2 |
| Correzioni al codice | 1 (traduzione di `∈ Z`) |
| Correzioni alla formulazione | 0 |

La seconda esecuzione segue il chiarimento dell'autrice sul significato di `∈ Z` (interi non
negativi) ed è una correzione della **traduzione**, non della formulazione: il modello
matematico non è stato toccato. Nessun errore di sintassi né di solver in nessuna delle due
esecuzioni.

## 4. Difficoltà principale

**Nessuna.** Il modello è corretto in tutte le sue componenti: bilancio di magazzino periodo
per periodo, capacità di ordine legata a `δ_i`, lotto minimo di 10 unità legato a `δ_i`,
scorta iniziale, scorta finale e struttura dei costi. Gurobi chiude all'ottimo certificato.

Il punto delicato di questa classe di problemi è il divieto di arretrati, che qui è espresso
dal dominio delle scorte: `y_i ∈ Z` con `Z` inteso come interi non negativi impone
`y_i ≥ 0` per ogni periodo, ed è l'unico elemento della formulazione che lo esprima —
nessun altro vincolo lo implica, perché `y_6 ≥ 5` blocca solo l'ultimo periodo e i vincoli
di bilancio si accontentano di qualsiasi valore purché la catena torni.

## Note di traduzione

**Dominio delle variabili.** `x_i ∈ Z` e `y_i ∈ Z` sono intesi sugli interi **non negativi**,
come precisato dall'autrice il 16 agosto 2026; la convenzione è applicata in modo uniforme a
tutti i problemi che scrivono `∈ Z`. Su M09 è determinante, per la ragione appena detta.

**Scorta iniziale.** `y_0` non compare fra le variabili dichiarate (`y_i` è definita per
i = 1..6): «`y_0 = 10`» è quindi la scorta iniziale, usata come costante nel bilancio del primo
periodo e non come variabile con un proprio vincolo. È questa lettura a produrre le 18
variabili e i 19 vincoli della ground truth.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 18 (6 ordini + 6 scorte + 6 binarie di setup) |
| Vincoli | 19 (6 bilancio + 6 capacità + 6 ordine minimo + 1 scorta finale) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M09.sol` — file soluzione di Gurobi
