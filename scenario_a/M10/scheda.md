# M10 · Progettazione di una rete distributiva — Scheda Scenario A

**Dominio:** Network design · **Classe:** MILP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **443** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 443 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione restituita:

| Arco | S→A | S→B | A→B | A→C | B→C | B→T | C→T |
|---|---|---|---|---|---|---|---|
| Flusso `x` | 25 | 15 | 0 | 25 | 0 | 15 | 25 |
| Attivo `y` | 1 | 1 | 0 | 1 | 0 | 1 | 1 |

Cinque archi attivati, due inutilizzati e non attivati. Conservazione del flusso rispettata in
tutti i nodi: 40 unità escono da S, 40 arrivano a T. Costi di attivazione
40 + 35 + 30 + 45 + 38 = 188, costi di trasporto 255, totale **443**.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0022 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 15 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 10 min |
| **Tempo-uomo totale** | **60 min** |

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
matematico non è stato toccato. Nessun errore di sintassi né di solver.

## 4. Difficoltà principale

**Nessuna.** Il modello è corretto in tutte le sue componenti: obiettivo con costi fissi e
variabili, vincolo di attivazione/capacità `x_ij ≤ CAPACITÀ_ij·y_ij` arco per arco, e cinque
righe di conservazione del flusso scritte esplicitamente nodo per nodo (uscita da S, transito
in A, B e C, ingresso in T).

Il punto delicato è la non negatività dei flussi: `x_ij ≤ CAPACITÀ_ij·y_ij` impone soltanto il
limite **superiore**, quindi ciò che esclude i flussi negativi è il dominio delle variabili.
Con `x_ij ∈ Z` inteso sugli interi non negativi il modello è chiuso correttamente. Vale la
pena notare che l'ottimo di questa istanza è **degenere**: esistono direzioni a costo nullo
lungo le quali il flusso potrebbe scendere sotto zero senza cambiare il valore
dell'obiettivo, quindi senza `x_ij ≥ 0` il valore ottimo resterebbe 443 ma il solver potrebbe
restituire una soluzione priva di senso fisico.

## Nota di traduzione

`x_ij ∈ Z` è inteso sugli interi **non negativi**, come precisato dall'autrice il 16 agosto
2026; la convenzione è applicata in modo uniforme a tutti i problemi che scrivono `∈ Z`.
La conservazione del flusso è tradotta nelle cinque equazioni esattamente come scritte nella
formulazione, senza riscriverle in forma compatta.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 14 (7 flussi interi + 7 binarie di attivazione) |
| Vincoli | 12 (7 attivazione/capacità + 5 conservazione del flusso) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M10.sol` — file soluzione di Gurobi
