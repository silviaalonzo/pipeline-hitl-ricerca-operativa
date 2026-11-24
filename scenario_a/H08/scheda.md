# H08 · Rete di emergenza capacitada con backup — Scheda Scenario A

**Dominio:** Localizzazione e copertura · **Classe:** IP binaria · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **697** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 697 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Stazioni aperte: A, B, D, H, per 128 di costi fissi e 569 di costo di percorrenza. Le zone
si distribuiscono su A (Z1, Z2, Z11), B (Z6), D (Z3, Z4, Z5, Z8) e H (Z7, Z9, Z10, Z12).
D lavora quasi al limite, con 36 unità di domanda su 40 di capacità; le altre restano più
larghe (A 23/42, H 29/42, B 8/44). B apre di fatto per una zona sola, Z6, che nessun'altra
stazione aperta può raggiungere.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0039 s** |
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

**Nessuna.** Il punto concettualmente scivoloso è il backup delle zone critiche: la
richiesta non è che la zona sia assegnata a due stazioni — l'assegnazione resta unica — ma
che fra le stazioni che la raggiungono ne siano *aperte* almeno due. La formulazione lo
traduce correttamente con tre vincoli sulle sole variabili di apertura,
`y_B + y_C + y_D ≥ 2` per Z3, `y_D + y_G + y_H ≥ 2` per Z8 e `y_A + y_E + y_H ≥ 2` per
Z11, senza toccare le variabili di assegnazione. Il modello ha chiuso all'ottimo alla
prima esecuzione.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 43 (35 binarie di assegnazione + 8 di apertura) |
| Vincoli | 61 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (43 variabili,
61 vincoli).

## Nota di traduzione

**Variabili sulle sole coppie raggiungibili.** Le `x_ij` esistono solo per `i ∈ R_j`,
cioè per le stazioni che il testo elenca fra quelle raggiungibili da ciascuna zona: sono
35 e non 96. È la lettura letterale della formulazione, che indicizza esplicitamente
`i ∈ R_j`, ed è anche ciò che rende il conteggio delle variabili identico alla ground
truth.

**Capacità e apertura in un vincolo solo.** Il vincolo di capacità è scritto nella forma
`Σ_j domanda_j·x_ij ≤ capacità_i·y_i`, che assorbe anche il legame fra assegnazione e
apertura: se la stazione è chiusa il membro destro è nullo e nessuna zona può esserle
assegnata. La formulazione mantiene comunque anche i vincoli espliciti `x_ij ≤ y_i`, più
stretti nel rilassamento continuo.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H08.sol` — file soluzione di Gurobi
