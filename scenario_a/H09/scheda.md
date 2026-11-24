# H09 · Produzione e scorte multi-prodotto con straordinario — Scheda Scenario A

**Dominio:** Production-inventory · **Classe:** MILP · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **2941** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 2941 |
| Ammissibilità nel problema originale | Ammissibile |
| Esito complessivo | **CORRETTO** |

Il costo si scompone in 2024 di produzione, 525 di setup, 194 di giacenza e 198 di
straordinario. Le quindici attivazioni rispettano il tetto: tutti e tre i prodotti nel
primo periodo, due in ciascuno dei successivi. Lo straordinario è usato con parsimonia —
2 ore in T1, 6 in T4 e 3 in T5, undici in tutto sulle 120 disponibili — e in tre periodi
su sei la capacità base viene saturata esattamente. Le scorte finali sono 2 unità per
ciascun prodotto, il minimo richiesto.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0194 s** |
| Tempo-uomo — lettura e comprensione | 20 min |
| Tempo-uomo — formulazione matematica | 35 min |
| Tempo-uomo — scrittura del codice | 35 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **105 min** |

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

**Nessuna.** È il problema più grande della Parte II per numero di variabili e quello con
più requisiti intrecciati: bilancio senza arretrati, setup con lotto minimo, tetto sulle
attivazioni variabile fra primo periodo e successivi, capacità estendibile a pagamento,
limite sulla scorta aggregata e scorta finale minima. La formulazione li tiene tutti
distinti e chiude all'ottimo alla prima esecuzione.

Rispetto a H02, dove il big-M del vincolo di lotto era rimasto indefinito e ha richiesto
un chiarimento dell'autrice, qui la costante è calcolata nella formulazione stessa:
`M_it = ⌊(capacità_t + 20) / ore_i⌋`, cioè il massimo producibile del prodotto `i` nel
periodo `t` sfruttando anche tutto lo straordinario. È un maggiorante valido e stretto.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 60 (18 `x` + 18 `s` + 18 `y` + 6 `o`) |
| Vincoli | 75 |

Dimensioni identiche a quelle registrate nella ground truth del dataset (60 variabili,
75 vincoli).

## Nota di traduzione

**Scorte iniziali come costanti.** La formulazione scrive `s_A0 = s_B0 = s_C0 = 0`. Sono
condizioni al contorno, non variabili: entrano come termine noto nel bilancio del primo
periodo. Tradurle come variabili fissate a zero avrebbe portato il modello a 63 variabili
invece delle 60 della ground truth.

**Straordinario come bound.** «`0 ≤ o_t ≤ 20`» è reso con i bound della variabile continua
`o_t` anziché con sei vincoli espliciti. Anche questa scelta è confermata dal conteggio
della ground truth, che si ritrova esatto solo leggendo la doppia disuguaglianza come
dominio della variabile.

**Assenza di arretrati.** Il testo la richiede esplicitamente e la formulazione la ottiene
senza un vincolo dedicato, per il solo dominio `s_it ∈ Z≥0`: una scorta non negativa in
ogni periodo equivale a domanda sempre soddisfatta per intero. La verifica a posteriori
controlla comunque la condizione in modo indipendente.

**Dominio delle variabili.** `x_it, s_it ∈ Z≥0` è tradotto con `vtype=GRB.INTEGER` e lower
bound 0, secondo la convenzione fissata dall'autrice per il simbolo `Z`; `o_t` resta
continua, come indicato dal testo e dalla formulazione.

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H09.sol` — file soluzione di Gurobi
