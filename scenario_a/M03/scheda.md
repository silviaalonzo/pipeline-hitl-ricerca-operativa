# M03 · Assegnazione del personale ai turni — Scheda Scenario A

**Dominio:** Workforce scheduling · **Classe:** IP binaria · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **49** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 49 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione: Bruno M1 (7) e P1 (8) · Ana M2 (7) · Fabio P2 (7) · Diego N1 (10) ·
Elena N2 (10). Bruno è l'unico a coprire due turni; nessuno supera un turno notturno.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0012 s** |
| Tempo-uomo — lettura e comprensione | 10 min |
| Tempo-uomo — formulazione matematica | 15 min |
| Tempo-uomo — scrittura del codice | 20 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **60 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 1 |
| Correzioni al codice | 0 |
| Correzioni alla formulazione | 0 |

## 4. Difficoltà principale

**Nessuna.** Tutte le componenti sono corrette al primo tentativo. Il punto delicato del
problema — le celle «—» della tabella — è stato trattato correttamente: la formulazione
annota «8 vincoli di indisponibilità» e le celle indisponibili sono effettivamente otto.

## Gli 8 vincoli di indisponibilità

Resi come otto vincoli espliciti `x_ij = 0` (nel codice, riga 87-89; nel file `.lp` sono i
vincoli `indisponibilita_*`). Corrispondono una a una alle celle «—» della tabella:

| # | Vincolo | Dipendente · turno |
|---|---|---|
| 1 | `x[Ana,N1] = 0` | Ana, notturno 1 |
| 2 | `x[Ana,N2] = 0` | Ana, notturno 2 |
| 3 | `x[Bruno,N1] = 0` | Bruno, notturno 1 |
| 4 | `x[Bruno,N2] = 0` | Bruno, notturno 2 |
| 5 | `x[Carla,M1] = 0` | Carla, mattina 1 |
| 6 | `x[Diego,M2] = 0` | Diego, mattina 2 |
| 7 | `x[Fabio,N1] = 0` | Fabio, notturno 1 |
| 8 | `x[Fabio,N2] = 0` | Fabio, notturno 2 |

L'output del terminale riporta il controllo automatico
«Numero di vincoli di indisponibilità inseriti: 8».

Per le celle indisponibili il costo non è definito nel testo; poiché le variabili sono
forzate a zero, il coefficiente in funzione obiettivo è irrilevante ed è posto a 0.

Riscontro dimensionale: 36 variabili e 26 vincoli (6 + 6 + 6 + 8), identici alla ground
truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M03.sol` — file soluzione di Gurobi
