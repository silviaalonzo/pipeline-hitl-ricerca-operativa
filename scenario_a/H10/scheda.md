# H10 · Rete multi-prodotto con capacità condivise — Scheda Scenario A

**Dominio:** Network design · **Classe:** MILP intera · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **583** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 583 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Archi attivati: S→A, S→B, A→C, B→C, C→D, C→T, D→T, cioè sette, il massimo consentito,
per 277 di costi fissi e 306 di costo di flusso. I due prodotti si separano subito
all'origine — K1 tutto su S→A, K2 tutto su S→B — e si ricongiungono in C, dove la capacità
condivisa dell'arco C→T viene saturata esattamente (35 su 35) e il resto di K1 devia su
C→D→T. Gli archi A→B e B→D restano spenti.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0103 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 25 min |
| Tempo-uomo — scrittura del codice | 30 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 10 min |
| **Tempo-uomo totale** | **85 min** |

I tempi-uomo sono misurati dall'esperto e trascritti dal registro di compilazione, che ne
resta la fonte autorevole. Non sono deducibili dai log.

Tutte le voci sono trascritte da `Registro_compilazione_Scenario_A.docx`, che il 19 agosto
2026 è stato completato dall'esperto. Il debug vale 0 perché il modello non ha richiesto
correzioni.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** Il tratto distintivo del problema è che la capacità è condivisa fra i due
prodotti mentre i costi unitari sono per prodotto: il legame fra le due cose passa da un
unico vincolo, `x_ij,K1 + x_ij,K2 ≤ capacità_ij·y_ij`, che somma i flussi ma li lascia
distinti nell'obiettivo. La formulazione lo scrive nella forma giusta e il modello ha
chiuso all'ottimo alla prima esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 27 (18 flussi `x` + 9 binarie di attivazione `y`) |
| Vincoli | 24 |

Le variabili coincidono con le 27 registrate nella ground truth. I vincoli sono 24 contro
23 perché la formulazione scrive la resilienza come due uguaglianze esplicite,
`y_SA = 1` e `y_SB = 1`, mentre nella ground truth almeno una delle due è verosimilmente
fissata come bound della variabile. È una differenza di scrittura, non di modello: la
soluzione e il valore ottimo coincidono.

## Nota di traduzione

**Conservazione scritta nodo per nodo.** La formulazione non usa una notazione compatta
sugli archi entranti e uscenti, ma elenca le quattro uguaglianze di conservazione per A,
B, C e D, ciascuna replicata sui due prodotti, più le due di origine e le due di
destinazione. La traduzione le riproduce nello stesso ordine e con gli stessi membri.

**Ridondanza dei vincoli di destinazione.** Le due uguaglianze in ingresso a T
(`x_CT,k + x_DT,k = q_k`) sono implicate dalla conservazione ai nodi intermedi e dalle due
di origine. Sono comunque state tradotte perché l'esperto le scrive: sono ridondanti, non
errate, e la loro presenza spiega parte dello scarto di conteggio con la ground truth.

**Dominio delle variabili.** `x_ijk ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower
bound 0, secondo la convenzione fissata dall'autrice per il simbolo `Z`.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H10.sol` — file soluzione di Gurobi
