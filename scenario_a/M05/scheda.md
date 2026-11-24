# M05 · Selezione di un portafoglio progetti — Scheda Scenario A

**Dominio:** Project portfolio · **Classe:** IP binaria · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **136** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 136 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Portafoglio selezionato: P1, P2, P3, P6, P8.
Budget 99/100 · personale 17/18 · cinque progetti (≥ 3) · P1 e P3 digitali (≥ 1) ·
P5 e P7 non selezionati (nessuna precedenza violata) · P4 escluso, quindi P4/P6 compatibili.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0027 s** |
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

**Verifica (trascrizione).** La modellazione è corretta in tutte le sue componenti — i
vincoli logici di precedenza (`x5 ≤ x2`, `x7 ≤ x3`), l'incompatibilità (`x4 + x6 ≤ 1`), la
copertura digitale e la cardinalità minima sono tutti espressi nella forma canonica. L'unico
punto di attenzione è un refuso di scrittura, descritto qui sotto, che non ha effetto sul
risultato.

## Refuso di trascrizione (chiarito)

Nel manoscritto il vincolo di copertura digitale è scritto come:

```
x1 + x3 + x9 ≥ 1
```

L'indice **9 non esiste**: i progetti sono otto. È stato letto come **x7**, unico indice
compatibile sia con l'insieme delle variabili sia con il testo del problema («almeno un
progetto digitale tra **P1, P3 e P7**»). Nessun'altra modifica è stata apportata.

La lettura è **confermata dall'autrice della formulazione** (13 agosto 2026): l'indice
inteso era x7. Due riscontri indipendenti erano già coerenti con questa lettura:

1. il modello risultante ha **7 vincoli**, esattamente come la ground truth del dataset;
2. il valore ottimo coincide con quello certificato (136).

Si tratta quindi di un errore di scrittura nella trascrizione, non di un errore di
modellazione: il vincolo inteso dall'esperto e quello implementato coincidono.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M05.sol` — file soluzione di Gurobi
