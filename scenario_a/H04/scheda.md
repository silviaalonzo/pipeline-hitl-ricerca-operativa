# H04 · Allocazione della flotta su più rotte — Scheda Scenario A

**Dominio:** Trasporto · **Classe:** MILP intera · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **962** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 962 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Viaggi assegnati: Medio → R1 3, R2 4, R4 2; Grande → R3 2, R4 2. La capacità offerta
copre la domanda su tutte e quattro le rotte (42/42, 56/55, 40/38, 68/64), su nessuna
rotta si usano più di due tipi di veicolo, la rotta R4 impiega veicoli grandi ed emissioni
complessive di 116 unità sulle 145 ammesse. Nessun veicolo piccolo entra in soluzione.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0120 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 20 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 5 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **80 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole. Le tre voci mancanti non sono deducibili dai log.

Il tempo di solver riportato è quello dell'esecuzione definitiva. La prima esecuzione,
chiusa con certificato di inammissibilità, aveva impiegato 0,0021 s.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 2 |
| Correzioni al codice | 1 (recepimento del refuso di trascrizione) |
| Correzioni alla formulazione | 0 |

Nessun errore di sintassi e nessun errore del solver in nessuna delle due esecuzioni.

## 4. Difficoltà principale

**Verifica (refuso di trascrizione).** Il modello è sempre stato sintatticamente corretto
e sempre risolto dal solver; la prima esecuzione ha però restituito `INFEASIBLE` a causa di
un coefficiente mancante in una riga, individuato in sede di verifica dell'esito e poi
chiarito dall'autrice. Stessa categoria già registrata per M05 e M07 nella Parte I.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 24 (12 intere di viaggio + 12 binarie di utilizzo) |
| Vincoli | 37 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (24 variabili,
37 vincoli), invariate fra le due esecuzioni: il refuso riguardava un coefficiente interno
a un vincolo, non la struttura del modello.

## Refuso di trascrizione — prima esecuzione e chiarimento

**Prima esecuzione (formulazione letterale): `INFEASIBLE`.** Il manoscritto scrive il
vincolo di copertura come

```
Σ_i x_ij ≥ DOMANDA_j        ∀j
```

dove `x_ij` è definita nella formulazione stessa come **numero di viaggi** del veicolo `i`
sulla rotta `j`. Nella forma scritta la domanda risulta confrontata con un conteggio di
viaggi anziché con la capacità trasportata: servirebbero 42 + 55 + 38 + 64 = **199 viaggi**
contro una disponibilità complessiva di flotta di 10 + 9 + 6 = **25**.

Gurobi ha calcolato l'*Irreducible Infeasible Subsystem*, salvato in `modello.ilp`: sette
vincoli, cioè le quattro coperture di domanda, le disponibilità di Piccolo e Medio e il
limite di emissione. La diagnosi coincide esattamente con il conto aritmetico.

**Chiarimento dell'autrice (17 agosto 2026).** Il testo del problema recita: «La capacità
complessiva assegnata a ogni rotta deve coprirne la domanda». L'autrice ha confermato che
si tratta di un errore di scrittura nella trascrizione e che il vincolo inteso è

```
Σ_i CAPACITÀ_i · x_ij ≥ DOMANDA_j        ∀j
```

con i coefficienti di capacità 8, 14 e 20. La traduzione recepisce l'intenzione dichiarata
e il valore passa da nessuna soluzione ammissibile a 962, l'ottimo certificato.

È lo stesso tipo di intervento già registrato per M05, dove il vincolo di copertura digitale
era trascritto con un indice inesistente (`x9`) poi chiarito in `x7`, e per M07, dove il
limite superiore era scritto senza `δ_i`. In tutti e tre i casi si tratta di un errore di
scrittura nella trascrizione e non di modellazione, e in tutti e tre la lettura corretta è
stata confermata dall'autrice della formulazione. Depone nella stessa direzione il fatto che
il modello avesse fin dalla prima esecuzione le dimensioni esatte della ground truth: la
struttura era quella giusta, mancava un coefficiente dentro una riga.

## Note di traduzione

Il doppio vincolo `y_ij ≤ x_ij ≤ DISPONIBILITÀ_i·y_ij` è reso come due vincoli distinti,
come da scrittura. La disuguaglianza di sinistra è più forte del consueto collegamento
`x_ij ≤ M·y_ij`: impone che, se il tipo `i` è dichiarato in uso sulla rotta `j`, vi sia
effettivamente almeno un viaggio. La condizione «su ogni rotta al massimo due tipi di
veicolo» è così correttamente contata sui tipi realmente impiegati.

Il vincolo `y_GRANDE,4 = 1` fissa la binaria del tipo «Grande» sulla rotta R4; in presenza
del collegamento `y_ij ≤ x_ij` questo obbliga ad almeno un viaggio con veicolo grande su
R4, come richiesto dal testo.

## File prodotti

- `modello.py` — codice definitivo
- `modello.lp` — modello in formato LP
- `modello.ilp` — sottosistema inammissibile irriducibile della **prima** esecuzione
- `output_terminale_esecuzione_1.txt` — output completo della prima esecuzione (`INFEASIBLE`)
- `output_terminale.txt` — output completo dell'esecuzione definitiva
- `H04.sol` — file soluzione di Gurobi
