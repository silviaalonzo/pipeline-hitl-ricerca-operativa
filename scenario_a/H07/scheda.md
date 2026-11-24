# H07 · Sourcing multi-componente con rischio e multisourcing — Scheda Scenario A

**Dominio:** Procurement · **Classe:** MILP intera · **Difficoltà:** Elevata

## 1. Stato finale di Gurobi e valore dell'obiettivo

| Voce | Esito |
|---|---|
| Stato finale | `OPTIMAL` (codice 2) |
| Valore funzione obiettivo | **2090** |
| Ottimo certificato (`dataset_cap4/solutions_summary.csv`) | 2160 |
| Ammissibilità nel problema originale | **Non ammissibile** |
| Esito complessivo | **NON CORRETTO** |

Il solver chiude regolarmente all'ottimo, ma su un problema più permissivo di quello del
testo: il valore trovato, 2090, è inferiore all'ottimo certificato di 70 unità. Le
quantità acquistate sono 70 unità di C1 da A e 10 da F, 70 di C2 da E, 60 di C3 da F, con
i fornitori A, E ed F attivati. La verifica indipendente in `verifica_ammissibilita.py`
registra due violazioni del problema originale:

> C2 proviene da 1 fornitore/i, ne servono almeno 2
> C3 proviene da 1 fornitore/i, ne servono almeno 2

Il requisito di multisourcing — «ogni componente deve provenire da almeno due fornitori,
con almeno 10 unità per ogni combinazione fornitore–componente utilizzata» — risulta
soddisfatto nel modello ma non nei fatti.

## 2. Tempi

| Voce | Valore |
|---|---|
| Tempo di esecuzione Gurobi (`m.Runtime`) | **0,0097 s** |
| Tempo-uomo — lettura e comprensione | 25 min |
| Tempo-uomo — formulazione matematica | 35 min |
| Tempo-uomo — scrittura del codice | 35 min |
| Tempo-uomo — debug e autocorrezioni | 0 min |
| Tempo-uomo — verifica finale | 15 min |
| **Tempo-uomo totale** | **110 min** |

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

Il modello è stato eseguito una sola volta e riportato così com'è. Nessuna correzione è
stata applicata alla formulazione: il protocollo dello Scenario A lo vieta e l'autrice non
ha autorizzato alcun intervento su questo problema.

## 4. Difficoltà principale

**Formulazione.** Il modello è strutturalmente completo — obiettivo, domanda, capacità,
qualità, rischio, tetto sui fornitori e vincolo su A/B sono tutti presenti e corretti — ma
il vincolo che lega la binaria `z_ij` alla quantità `x_ij` è scritto con la restrizione
«∀ ij disponibile», cioè solo sulle quindici coppie effettivamente fornibili. Sulle tre
coppie non fornibili (C1–D, C2–F, C3–E) la formulazione impone `x_ij = 0` ma lascia
`z_ij` libera.

Il solver ne approfitta: pone `z_C2,F = 1` e `z_C3,E = 1` con quantità nulla, e con questo
soddisfa formalmente `Σ_j z_ij ≥ 2` senza comprare davvero da due fornitori. Il
multisourcing diventa così contabile anziché reale, e il costo scende sotto l'ottimo vero.

## Struttura del modello

| Voce | Valore |
|---|---|
| Variabili | 42 (18 `x` + 18 `z` + 6 `y`) |
| Vincoli | 75 |

Il numero di variabili coincide con quello della ground truth (42), il che conferma che
anche il modello di riferimento definisce `x` e `z` su tutte e diciotto le coppie e non
solo su quelle fornibili. I vincoli sono 75 contro 84.

## Segnalazione all'autrice — accolta il 19 agosto 2026

**Decisione dell'autrice.** La diagnosi qui sotto è stata sottoposta a Silvia il 19 agosto
2026 e da lei confermata. La conferma riguarda la *diagnosi*, non una autorizzazione a
correggere: l'esito resta **NON CORRETTO** a 2090, `modello.py` non va modificato e il caso
viene trattato nel Capitolo 5. È il risultato sperimentale più significativo dello
Scenario A e va conservato nella forma in cui si è prodotto.

Il punto è isolato e la sua rimozione è di una riga. Estendere il solo lato sinistro del
vincolo di lotto, `10·z_ij ≤ x_ij`, a **tutte** le coppie anziché alle sole disponibili
basta: dove `x_ij` è azzerata, la disuguaglianza forza `z_ij = 0` e il multisourcing torna
a contare fornitori reali. Equivalentemente si possono aggiungere i tre azzeramenti
espliciti `z_C1,D = z_C2,F = z_C3,E = 0`, già impliciti nel significato dichiarato della
variabile («1 se il componente i è acquistato dal fornitore j»: se non se ne acquista
nulla, la variabile non dovrebbe valere 1).

Con quella sola aggiunta il modello chiude a **2160**, esattamente l'ottimo certificato,
acquistando 70 unità di C1 da A e 10 da F, 10 di C2 da A e 60 da E, 10 di C3 da A e 50 da
F. La prova è stata condotta in una copia di lavoro fuori dalla cartella del problema: il
modello di `modello.py` **non** è stato modificato.

Il caso somiglia ai refusi di trascrizione già incontrati in M05, M07 e H04 — struttura
giusta, una condizione non estesa fin dove serviva — ma se ne distingue per due aspetti
che il Capitolo 5 deve tenere separati. Primo: la differenza tocca il **dominio di una
variabile**, non un coefficiente, quindi non è visibile rileggendo i dati del problema.
Secondo, e decisivo: i refusi precedenti si sono manifestati come `INFEASIBLE` o come un
valore palesemente fuori scala, mentre qui il modello chiude regolarmente all'`OPTIMAL` su
un valore *migliore* dell'ottimo vero. È un errore **silenzioso**: nessun controllo interno
al solver può intercettarlo, perché dal punto di vista di Gurobi non è successo nulla di
anomalo. Solo la verifica di ammissibilità condotta sul testo del problema — cioè
`verifica_ammissibilita.py`, uno strumento esterno al modello — lo scopre.

Questo è il motivo per cui l'errore va conservato e non corretto: è l'unica evidenza
sperimentale, in tutto lo Scenario A, che l'esperto umano può produrre un risultato
sbagliato *e non accorgersene*, avendo speso 110 minuti sul problema, i quindici finali dei
quali proprio in verifica. Regge da solo l'argomento sul perché il criterio di correttezza
adottato nella tesi non possa essere «il solver ha chiuso all'ottimo».

## File prodotti

- `modello.py` — codice definitivo (traduzione 1:1 della formulazione, **non corretto**)
- `modello.lp` — modello in formato LP
- `output_terminale.txt` — output completo del terminale
- `H07.sol` — file soluzione di Gurobi
