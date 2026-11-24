# H06 · Sequenziamento con ritardi pesati — Scheda Scenario A

**Dominio:** Scheduling · **Classe:** MILP intera · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **42** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 42 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Sequenza ottima: J1 (0–5), J3 (5–9), J5 (9–12), J2 (12–19), J7 (19–24), J4 (24–30),
J6 (30–38). Tre soli lavori arrivano in ritardo: J2 di 2 unità (peso 3, costo 6),
J4 di 8 (peso 2, costo 16) e J6 di 10 (peso 2, costo 20), per un totale di 42. La
macchina non resta mai ferma: i lavori si susseguono senza tempi morti, e i tre
ritardi si concentrano sui lavori a peso più basso o con scadenza più lontana.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0159 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 30 min |
| Tempo-uomo — scrittura del codice | 30 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **95 min** |

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

**Nessuna.** Il punto delicato del problema è la costante big-M dei vincoli di non
sovrapposizione, che il testo chiede esplicitamente di giustificare. La formulazione la
calcola per esteso come `M = max(disponibilità) + Σ durate = 6 + 38 = 44`, cioè un
maggiorante dell'orizzonte temporale: qualunque sequenza ammissibile termina entro
quell'istante, quindi la costante è valida e al tempo stesso stretta. Il modello ha chiuso
all'ottimo alla prima esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 42 (21 fra `S`, `C`, `T` + 21 binarie di ordinamento `y`) |
| Vincoli | 72 |

Le variabili coincidono con le 42 registrate nella ground truth. I vincoli sono 72 contro
58 perché la formulazione scrive per esteso, come disuguaglianze, sia le sette condizioni
di disponibilità `S_i ≥ disponibilità_i` sia le sette di non negatività `T_i ≥ 0`: in
Gurobi sarebbero esprimibili come bound delle variabili, e 72 − 14 = 58 restituisce
esattamente il conteggio della ground truth. È una differenza di scrittura, non di modello.

## Nota di traduzione

**Ordinamento a coppie.** Le binarie `y_ij` sono definite solo per `i < j`, con la coppia
di vincoli disgiuntivi che impone l'una o l'altra precedenza a seconda del valore di
`y_ij`. È la formulazione classica del sequenziamento su macchina singola e vale 21
binarie per sette lavori.

**Ritardo.** La linearizzazione `T_i ≥ C_i − scadenza_i` con `T_i ≥ 0` rende `T_i` un
maggiorante del ritardo; poiché l'obiettivo minimizza una somma a pesi positivi, all'ottimo
`T_i` coincide con `max(0, C_i − scadenza_i)`. La verifica a posteriori ricalcola i ritardi
direttamente con la formula del massimo, senza usare le variabili `T`, e ritrova 42.

**Dominio delle variabili.** `S_i, C_i, T_i ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e
lower bound 0, secondo la convenzione fissata dall'autrice per il simbolo `Z`.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H06.sol` — file soluzione di Gurobi
