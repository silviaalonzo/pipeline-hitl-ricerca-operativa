# H02 · Produzione multi-periodo con setup e scorte — Scheda Scenario A

**Dominio:** Produzione e scorte · **Classe:** MILP intera · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **1575** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 1575 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Piano di produzione: A 20 in T1 e 24 in T3; B 10, 8, 14, 12 in tutti e quattro i periodi;
C 16 in T2 e 11 in T4. Esattamente due setup attivi in ciascun periodo, al limite del
vincolo. Scorte di fine periodo: A 12 dopo T1 e 14 dopo T3, C 6 in apertura e 7 dopo T2,
tutte nulle a fine orizzonte. Capacità satura in T3 (90/90 ore) e quasi satura in T2
(88/95). Costo di produzione 1159, di setup 350, di mantenimento 66.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0054 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 25 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **80 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole. Le tre voci mancanti non sono deducibili dai log.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Formulazione (parametro non definito).** La struttura del modello è completa e corretta,
ma il vincolo di lotto usa un big-M `M_ij` che non è definito né fra i parametri della
formulazione né nelle tabelle del testo. La traduzione è rimasta sospesa fino al
chiarimento dell'autrice; nessuna scelta è stata fatta in autonomia.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 39 (12 intere di produzione + 15 intere di scorta + 12 binarie di setup) |
| Vincoli | 54 |

La ground truth del dataset registra 36 variabili e 51 vincoli. Lo scarto di tre unità su
entrambi i conteggi è interamente spiegato dalle scorte di apertura: la formulazione
dell'esperto le scrive come tre vincoli espliciti (`y_A0 = 0`, `y_B0 = 0`, `y_C0 = 6`),
trattando quindi `y_i0` come variabili fissate, mentre la ground truth le incorpora nei
dati del vincolo di bilancio del primo periodo. Le due scritture sono equivalenti e
producono lo stesso ottimo; qui è stata riprodotta la scrittura dell'esperto.

## Chiarimento dell'autrice — il parametro `M_ij`

Il vincolo di lotto è scritto

```
LOTTOMIN_i · δ_ij ≤ x_ij ≤ M_ij · δ_ij        ∀i ∀j
```

Il parametro `M_ij` non compare fra le definizioni della formulazione e non ha un valore
numerico nelle tabelle del problema: il modello non era scrivibile senza di esso. Non si
tratta di un errore di modellazione — la struttura del vincolo di lotto è quella canonica,
con il lotto minimo e il collegamento alla binaria di setup — ma di un parametro lasciato
implicito.

Valore chiarito dall'autrice il 17 agosto 2026:

```
M_ij = ⌊ CAPACITÀ_j / ORE_i ⌋
```

cioè il massimo producibile dell'articolo `i` nel periodo `j` date le ore disponibili in
quel periodo. Ne risultano i valori 45, 47, 45, 50 per A; 30, 31, 30, 33 per B; 22, 23,
22, 25 per C.

La scelta è coerente con il resto del modello: il limite è già implicito nel vincolo di
capacità oraria, quindi il big-M non introduce alcuna restrizione aggiuntiva rispetto alla
formulazione ed è al tempo stesso il più stretto fra quelli deducibili dalle sole capacità,
il che evita i rilassamenti lineari deboli tipici dei big-M sovradimensionati.

## Nota di traduzione

Il doppio vincolo `LOTTOMIN_i·δ_ij ≤ x_ij ≤ M_ij·δ_ij` è reso come due vincoli distinti,
come da scrittura. La coppia collega correttamente produzione e setup senza bisogno di un
vincolo di attivazione separato: se `δ_ij = 0` la produzione è forzata a zero da entrambi i
lati, se `δ_ij = 1` deve raggiungere almeno il lotto minimo.

Il divieto di arretrati posto dal testo è affidato al dominio delle scorte
(`y_ij ∈ Z ≥ 0`, scritto esplicitamente con il segno nella formulazione), come già
osservato per M09 nella Parte I.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H02.sol` — file soluzione di Gurobi
