# H05 · Portafoglio pluriennale con sinergie — Scheda Scenario A

**Dominio:** Project portfolio · **Classe:** IP binaria · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **235** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 235 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Progetti scelti: A, C, E, H, K. VAN dei progetti 213, più entrambe le sinergie
(A-C = 12 ed E-K = 10), per un totale di 235. Il budget del primo anno è quasi saturo
(109 su 110), mentre gli altri vincoli restano larghi: 85/100, 76/90, personale 22/28,
rischio 25/32.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0093 s** |
| Tempo-uomo — lettura e comprensione | 15 min |
| Tempo-uomo — formulazione matematica | 20 min |
| Tempo-uomo — scrittura del codice | 15 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **65 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole. Le tre voci mancanti non sono deducibili dai log.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** Il punto tecnicamente delicato del problema è la richiesta esplicita di
modellare le sinergie, che introduce un prodotto logico fra binarie. La formulazione lo
linearizza nel modo canonico e completo, scrivendo per esteso tutte e sei le disuguaglianze
necessarie. Il modello ha chiuso all'ottimo alla prima esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 14 (12 binarie di selezione + `z_AC` + `z_EK`) |
| Vincoli | 19 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (14 variabili,
19 vincoli).

## Nota di traduzione

**Linearizzazione delle sinergie.** Per ciascuna coppia la formulazione scrive le tre
disuguaglianze `z ≤ x_1`, `z ≤ x_2`, `z ≥ x_1 + x_2 − 1`. In un problema di massimo con
coefficiente positivo su `z` le prime due basterebbero, perché l'obiettivo spinge comunque
`z` verso l'alto; la terza è ridondante all'ottimo ma rende la variabile ausiliaria
correttamente vincolata in entrambe le direzioni, cioè un vero indicatore della congiunzione
e non solo un maggiorante. La scrittura completa è quindi la più difendibile ed è quella
che il testo chiede quando parla di sinergie «modellate esplicitamente».

**Prerequisiti.** Sono scritti nella forma `x_G ≤ x_B`, `x_J ≤ x_E`, `x_K ≤ x_C`, che
traduce correttamente «G richiede B, J richiede E e K richiede C»: il progetto richiedente
può essere scelto solo se lo è il progetto richiesto.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H05.sol` — file soluzione di Gurobi
