# H03 · Turnazione settimanale con competenze e riposi — Scheda Scenario A

**Dominio:** Workforce scheduling · **Classe:** IP binaria · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **227** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 227 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Piano settimanale: E1 Lun-Mar-Gio; E2 Mar-Mer-Ven; E3 Gio-Sab-Dom; E4 Lun-Mer-Ven-Dom;
E5 Lun-Mer-Sab; E6 Gio-Ven-Dom; E7 Lun-Mer-Ven; E8 Mar-Gio-Ven-Sab. La copertura è esatta
in tutti e sette i giorni (4, 3, 4, 4, 5, 3, 3), sei dipendenti su otto lavorano il minimo
di tre giorni e nessuno supera i cinque.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0098 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 20 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **75 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole. Le tre voci mancanti non sono deducibili dai log.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** È il problema con il maggior numero di famiglie di vincoli eterogenee fra
quelli affrontati finora (copertura, seniority, minimo e massimo di giorni, divieto di
quattro giorni consecutivi, competenze specialistiche, fine settimana, indisponibilità) e
la formulazione le tratta tutte senza omissioni. Il modello ha chiuso all'ottimo alla prima
esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 56 (8 dipendenti × 7 giorni, binarie) |
| Vincoli | 72 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (56 variabili,
72 vincoli).

## Note di traduzione

**Divieto di quattro giorni consecutivi.** La formulazione lo scrive come quattro famiglie
esplicite di vincoli — le finestre Lun-Gio, Mar-Ven, Mer-Sab, Gio-Dom, ciascuna `∀i` e
ciascuna con termine noto 3 — anziché come un unico vincolo parametrizzato sulla finestra
scorrevole. Le due scritture sono equivalenti: quattro finestre di ampiezza quattro
esauriscono la settimana.

**Indisponibilità.** Le sei celle «—» della tabella dei costi sono rese come sei vincoli
espliciti di fissaggio a zero, uno per cella, scritti per esteso nella formulazione:
`x_1,7 = 0` (E1 domenica), `x_2,6 = 0` (E2 sabato), `x_4,2 = 0` (E4 martedì),
`x_5,4 = 0` (E5 giovedì), `x_6,1 = 0` (E6 lunedì), `x_7,7 = 0` (E7 domenica). La
corrispondenza con la tabella è esatta su tutte e sei. Alle celle «—» non corrisponde un
costo numerico: il coefficiente è posto a 0, scelta ininfluente perché le variabili
relative sono comunque fissate a zero.

**Seniority.** Il vincolo è scritto `Σ_{i=1}^{3} x_ij ≥ 1 ∀j`: la somma sui primi tre
indici corrisponde ai senior E1, E2, E3 indicati dal testo.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H03.sol` — file soluzione di Gurobi
