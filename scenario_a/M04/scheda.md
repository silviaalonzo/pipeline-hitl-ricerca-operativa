# M04 · Composizione di una flotta giornaliera — Scheda Scenario A

**Dominio:** Trasporto · **Classe:** IP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **1240** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 1240 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione: 2 Autocarri, 1 Refrigerato, 1 Elettrico, 2 Bilici (nessun Van).
Volume 180 (≥ 180, vincolo attivo) · portata 109 (≥ 95) · emissioni 127 (≤ 145).

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0018 s** |
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

**Nessuna.** Scelta di modellazione efficace: i requisiti «almeno un mezzo refrigerato e un
mezzo elettrico» e i limiti di disponibilità sono espressi direttamente come bound sulle
variabili (`1 ≤ x3 ≤ 4`, `1 ≤ x4 ≤ 5`) invece che come vincoli separati. Il modello
risultante ha solo tre vincoli di riga ed è equivalente alla formulazione di riferimento.

## Nota di traduzione

L'ordine degli indici 1–5 della formulazione segue quello della tabella del testo:
1 Van, 2 Autocarro, 3 Refrigerato, 4 Elettrico, 5 Bilico. I lower bound unitari cadono
quindi su Refrigerato ed Elettrico, come richiesto dal testo.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M04.sol` — file soluzione di Gurobi
