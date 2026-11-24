# M07 · Selezione dei fornitori con qualità minima — Scheda Scenario A

**Dominio:** Procurement · **Classe:** MILP intera · **Difficoltà:** Media

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **2055** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 2055 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Soluzione: **80 unità dal fornitore A** e **100 dal fornitore B**, entrambi attivati.
Costi fissi 80 + 95 = 175, costi variabili 11·80 + 10·100 = 1880, totale 2055.
Requisiti rispettati: 180 unità acquistate, 2 fornitori attivi, emissioni 640 ≤ 650,
qualità media ponderata (96·80 + 90·100)/180 = **92,67 ≥ 92**.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0015 s** |
| Tempo-uomo — lettura e comprensione | 10 min |
| Tempo-uomo — formulazione matematica | 15 min |
| Tempo-uomo — scrittura del codice | 15 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **55 min** |

I tempi-uomo sono misurati dall'esperto e trascritti da `Registro_compilazione_Scenario_A.docx`, che ne resta la fonte autorevole.

La voce *debug e autocorrezioni* vale 0: la seconda esecuzione è la ritraduzione
conseguente al chiarimento dell'autrice, cioè un'operazione di traduzione svolta in sede
di codifica, non un ciclo di debug dell'esperto sulla propria formulazione (decisione
del 16 agosto 2026, applicata al registro il 19 agosto).

## 3. Esecuzioni e correzioni

| Voce | Valore |
|---|---|
| Esecuzioni del codice | 2 |
| Correzioni al codice | 1 (traduzione di `∈ Z`) |
| Correzioni alla formulazione | 0 — refuso di trascrizione chiarito dall'autrice |

Il codice è girato senza errori a entrambe le esecuzioni: non ci sono stati errori di sintassi
né di solver. La seconda esecuzione segue due chiarimenti dell'autrice, entrambi del
16 agosto 2026, descritti nella nota di trascrizione qui sotto.

## 4. Difficoltà principale

**Verifica (refuso di trascrizione).** La modellazione è corretta in tutte le sue componenti;
il punto critico di questa classe di problemi — il legame fra quantità acquistata e attivazione
del fornitore, che deve valere in entrambe le direzioni — è gestito correttamente dalla coppia

```
ORDINEMIN_i · δ_i ≤ x_i ≤ CAPACITÀ_i · δ_i        ∀i
```

che impedisce a un fornitore di consegnare senza essere attivato e quindi senza pagarne il
costo fisso. È questo vincolo a determinare l'ottimo: il fornitore D ha il costo variabile più
basso (9) ma il costo fisso più alto (120), ed è conveniente solo se lo si può usare senza
attivarlo.

## Nota di trascrizione (chiarita dall'autrice)

Due punti del manoscritto sono stati chiariti dall'autrice il **16 agosto 2026**:

1. **Limite superiore.** Il manoscritto riporta `ORDINEMIN_i·δ_i ≤ x_i ≤ CAPACITÀ_i`, senza
   `δ_i` a destra. L'autrice ha confermato che si tratta di un errore di scrittura nella
   trascrizione e che il limite superiore inteso è `CAPACITÀ_i·δ_i`. La traduzione recepisce
   l'intenzione dichiarata.
2. **Dominio delle quantità.** `x_i ∈ Z` è da intendersi sugli interi **non negativi**
   (convenzione uniforme su tutti i problemi). Su M07 la scelta è ininfluente: la non
   negatività era già implicata da `ORDINEMIN_i·δ_i ≤ x_i` con `δ_i = 0`.

## Nota sul vincolo di qualità

La formulazione scrive il requisito di qualità sulle binarie, `Σ QUALITÀ_i·δ_i ≥ 92`, e la
traduzione lo riporta così com'è. Il testo del problema chiede però letteralmente che
«la qualità media ponderata deve essere almeno 92», cioè un requisito sulle quantità
acquistate, che nella forma lineare consueta si scrive `Σ QUALITÀ_i·x_i ≥ 92·180`.

**Sull'istanza il punto non incide.** La soluzione ottima trovata (80 da A, 100 da B) ha
qualità media ponderata 92,67 e soddisfa quindi anche la lettura del testo: il verificatore
indipendente controlla proprio la media ponderata e non rileva violazioni. Il valore ottimo è
2055 con entrambe le scritture del vincolo — riscontro effettuato a parte, fuori
dall'esperimento. Resta una differenza di forma fra il vincolo scritto e il requisito del
testo, che su un'altra istanza potrebbe non essere innocua.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 8 (4 intere di quantità + 4 binarie di attivazione) |
| Vincoli | 12 (1 numero fornitori + 1 fabbisogno + 1 qualità + 1 emissioni + 4 ordine minimo + 4 capacità) |

Dimensioni identiche a quelle registrate nella ground truth del dataset.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `M07.sol` — file soluzione di Gurobi
