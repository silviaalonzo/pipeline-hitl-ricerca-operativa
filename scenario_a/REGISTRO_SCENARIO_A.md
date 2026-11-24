# Registro Scenario A — problemi M01–M10 e H01–H10

Esperto umano senza assistenza LLM. Le formulazioni matematiche sono state prodotte
dall'esperto e tradotte in `gurobipy`: variabili, funzione obiettivo e vincoli dei file
`modello.py` corrispondono uno a uno alla formulazione. Le scelte di traduzione sono
annotate in testa a ciascun `modello.py` e nelle rispettive schede.

- **Ambiente:** Gurobi 13.0.2, licenza accademica named-user, Python 3.12, macOS.
- **Date di esecuzione:** M01–M05 il 13 agosto 2026; M06–M10 il 16 agosto 2026;
  riesecuzione di M02, M07, M09 e M10 il 16 agosto 2026 dopo i chiarimenti dell'autrice
  sulle convenzioni di scrittura; H01–H05 il 17 agosto 2026; H06–H10 il 19 agosto 2026.
- **Ottimi di riferimento:** `dataset_cap4/solutions_summary.csv`.
- **Testi dei problemi:** `dataset_cap4/problems.jsonl` e
  `dataset_cap4/Dataset_20_problemi_IP_MILP.docx`.
- **Criterio di correttezza:** ammissibilità nel problema originale **e** valore
  dell'obiettivo verificato pari all'ottimo noto. Non è richiesta l'uguaglianza con il
  vettore di variabili salvato nella ground truth.

## Protocollo sperimentale

Lo Scenario A misura che cosa ottiene l'esperto umano **da solo**, senza assistenza LLM.
Le regole seguite, che vanno conosciute per interpretare correttamente i dati di questo
registro, sono state:

1. **Traduzione 1:1 e nient'altro.** La formulazione prodotta dall'esperto è stata
   *esclusivamente* tradotta in `gurobipy`, salvata ed eseguita. Non è mai stata corretta,
   migliorata o riparata — nemmeno quando ha prodotto `INFEASIBLE` o un ottimo diverso da
   quello atteso. Si è sempre riportato l'esito osservato. Qualsiasi intervento sulla
   modellazione avrebbe invalidato la misura.
2. **Solo errori di codice.** Sono stati corretti soltanto errori di sintassi o di API
   `gurobipy`, mai di modellazione.
3. **Segnalazione separata.** I dubbi sulla formulazione sono stati segnalati all'autrice
   senza toccare il modello, lasciando a lei la decisione. È il caso di H07.
4. **Autorizzazioni caso per caso.** L'autrice poteva autorizzare una correzione, ma solo
   per quel problema e per quella richiesta. È accaduto per M01 e per H04.
5. **Tempo-uomo misurato, non stimato.** I tempi sono cronometrati dall'esperto e
   trascritti dal registro di compilazione. Non sono deducibili dai log e non vanno mai
   ricostruiti a posteriori.
6. **Nessuna contaminazione.** Durante lo Scenario A non sono stati consultati la ground
   truth né gli output dello Scenario B, per non influenzare l'esperto con le soluzioni
   prodotte dagli LLM. Gli ottimi certificati sono stati usati solo a valle, come metro di
   giudizio degli esiti.

Ne segue una distinzione che il Capitolo 5 deve mantenere netta: le **correzioni di
traduzione** (5 in tutto) non consumano tempo-uomo dell'esperto e non contano come suoi
errori, mentre gli **errori di modellazione** sono l'oggetto della misura. Nello Scenario A
se n'è verificato uno solo, H07.

## Quadro di sintesi — Parte I (difficoltà media)

| ID | Stato Gurobi | Obiettivo | Ottimo noto | Ammissibile | Esito | Runtime Gurobi | Esec. | Corr. | Difficoltà principale |
|---|---|---|---|---|---|---|---|---|---|
| M01 | `OPTIMAL` | 149 | 149 | Sì | CORRETTO | 0,0106 s | 1 | 0 | Nessuna |
| M02 | `OPTIMAL` | 1640 | 1640 | Sì | CORRETTO | 0,0093 s | 2 | 1 | Nessuna |
| M03 | `OPTIMAL` | 49 | 49 | Sì | CORRETTO | 0,0012 s | 1 | 0 | Nessuna |
| M04 | `OPTIMAL` | 1240 | 1240 | Sì | CORRETTO | 0,0018 s | 1 | 0 | Nessuna |
| M05 | `OPTIMAL` | 136 | 136 | Sì | CORRETTO | 0,0027 s | 1 | 0 | Verifica (refuso di trascrizione) |
| M06 | `OPTIMAL` | 22 | 22 | Sì | CORRETTO | 0,0021 s | 1 | 0 | Nessuna |
| M07 | `OPTIMAL` | 2055 | 2055 | Sì | CORRETTO | 0,0015 s | 2 | 1 | Verifica (refuso di trascrizione) |
| M08 | `OPTIMAL` | 106 | 106 | Sì | CORRETTO | 0,0006 s | 1 | 0 | Nessuna |
| M09 | `OPTIMAL` | 1370 | 1370 | Sì | CORRETTO | 0,0022 s | 2 | 1 | Nessuna |
| M10 | `OPTIMAL` | 443 | 443 | Sì | CORRETTO | 0,0022 s | 2 | 1 | Nessuna |

**Accuratezza su M01–M10: 10/10 (100%).** Tempo di solver 0,0342 s ·
14 esecuzioni · 4 correzioni.

## Quadro di sintesi — Parte II (difficoltà elevata)

| ID | Stato Gurobi | Obiettivo | Ottimo noto | Ammissibile | Esito | Runtime Gurobi | Esec. | Corr. | Difficoltà principale |
|---|---|---|---|---|---|---|---|---|---|
| H01 | `OPTIMAL` | 1355 | 1355 | Sì | CORRETTO | 0,0107 s | 1 | 0 | Nessuna |
| H02 | `OPTIMAL` | 1575 | 1575 | Sì | CORRETTO | 0,0054 s | 1 | 0 | Formulazione (parametro non definito) |
| H03 | `OPTIMAL` | 227 | 227 | Sì | CORRETTO | 0,0098 s | 1 | 0 | Nessuna |
| H04 | `OPTIMAL` | 962 | 962 | Sì | CORRETTO | 0,0120 s | 2 | 1 | Verifica (refuso di trascrizione) |
| H05 | `OPTIMAL` | 235 | 235 | Sì | CORRETTO | 0,0093 s | 1 | 0 | Nessuna |
| H06 | `OPTIMAL` | 42 | 42 | Sì | CORRETTO | 0,0159 s | 1 | 0 | Nessuna |
| H07 | `OPTIMAL` | 2090 | 2160 | **No** | **NON CORRETTO** | 0,0097 s | 1 | 0 | Formulazione (dominio di una variabile) |
| H08 | `OPTIMAL` | 697 | 697 | Sì | CORRETTO | 0,0039 s | 1 | 0 | Nessuna |
| H09 | `OPTIMAL` | 2941 | 2941 | Sì | CORRETTO | 0,0194 s | 1 | 0 | Nessuna |
| H10 | `OPTIMAL` | 583 | 583 | Sì | CORRETTO | 0,0103 s | 1 | 0 | Nessuna |

**Accuratezza su H01–H10: 9/10 (90%).** Tempo di solver 0,1064 s ·
11 esecuzioni · 1 correzione.

## Totale (20 problemi su 20)

**Accuratezza complessiva: 19/20 (95%)** — 10/10 sulla Parte I, 9/10 sulla Parte II.
**Tempo di solver complessivo: 0,1406 s.**
**Esecuzioni totali: 25 · correzioni totali: 5.**

Nessun errore di sintassi e nessun errore di solver in nessuna delle venticinque
esecuzioni: tutti i modelli sono girati al primo tentativo. Le cinque correzioni
riguardano la **traduzione** in `gurobipy` — la convenzione di scrittura `∈ Z` per M02,
M07, M09 e M10, e il recepimento di un refuso di trascrizione per H04 — e non la
formulazione matematica, che non è mai stata modificata.

Un solo problema su venti, H04, ha prodotto alla prima esecuzione un esito diverso
dall'ottimo (`INFEASIBLE`), poi ricondotto a un errore di scrittura nella trascrizione
confermato dall'autrice. Un secondo, H02, non era eseguibile fino al chiarimento di un
parametro lasciato implicito.

**L'unico esito non corretto è H07**, e non si manifesta come errore visibile: il solver
chiude regolarmente all'`OPTIMAL` su un modello sintatticamente sano, ma il valore trovato
(2090) è *migliore* dell'ottimo vero (2160) perché il modello è più permissivo del
problema. È il caso più interessante dell'intero Scenario A per il Capitolo 5, perché
mostra un modo di sbagliare che nessun controllo interno al solver può intercettare: senza
la verifica indipendente di ammissibilità nel problema originale, un risultato del genere
verrebbe accettato come corretto. Il dettaglio è nella scheda `H07/scheda.md`.

## Chiarimenti dell'autrice (16 agosto 2026)

Due punti della notazione sono stati chiariti dall'autrice delle formulazioni dopo la prima
tornata di esecuzioni. Entrambi riguardano *come leggere quanto scritto*, non *cosa
scrivere*; i modelli matematici non sono stati modificati.

**1. Il simbolo `∈ Z`.** Nelle formulazioni di M02, M07, M09 e M10 le variabili quantitative
sono dichiarate `∈ Z` senza indicazione di segno. La prima traduzione aveva seguito la
lettura letterale — interi di segno qualsiasi, lower bound `−∞`. L'autrice ha precisato che
con `Z` intende gli **interi non negativi**. La convenzione è ora applicata in modo uniforme
a tutti i problemi che scrivono `∈ Z`, ed è annotata in testa a ciascun `modello.py`.

Effetto sui risultati:

| Problema | Prima lettura (`Z` con segno) | Lettura dell'autrice (`Z ≥ 0`) |
|---|---|---|
| M02 | 1640 — ininfluente | 1640 |
| M07 | ininfluente (implicata da altri vincoli) | ininfluente |
| M09 | 985, scorte fino a −55 | **1370 = ottimo** |
| M10 | 443, due archi con flusso negativo | **443 con soluzione ammissibile** |

**2. Il limite superiore in M07.** Il manoscritto riporta
`ORDINEMIN_i·δ_i ≤ x_i ≤ CAPACITÀ_i`, senza `δ_i` a destra. L'autrice ha confermato che si
tratta di un errore di scrittura nella trascrizione e che il limite superiore inteso è
`CAPACITÀ_i·δ_i`, cioè legato all'attivazione. La traduzione recepisce l'intenzione
dichiarata; il valore passa da 2010 a 2055, l'ottimo certificato.

È lo stesso tipo di intervento già registrato per M05, dove il vincolo di copertura digitale
era trascritto con un indice inesistente (`x9`) poi chiarito in `x7`. In entrambi i casi si
tratta di un errore di scrittura nella trascrizione e non di modellazione, e in entrambi i
casi la lettura corretta è stata confermata dall'autrice della formulazione.

**Nota metodologica.** I due chiarimenti sono arrivati dopo la prima esecuzione. Nel
Cap. 5 va detto esplicitamente che l'oggetto della misura dello Scenario A è la formulazione
**secondo l'intenzione dichiarata dall'esperto**, non la sua trascrizione letterale: sono
due cose che qui coincidono per otto problemi su dieci e divergono su M07 e M09.

## Chiarimenti dell'autrice (17 agosto 2026)

**3. Il parametro `M_ij` di H02.** Il vincolo di lotto è scritto
`LOTTOMIN_i·δ_ij ≤ x_ij ≤ M_ij·δ_ij`, ma `M_ij` non compare fra le definizioni della
formulazione né nelle tabelle del problema: il modello non era scrivibile. Non è un errore
di modellazione — la struttura del vincolo di lotto è quella canonica — ma un parametro
lasciato implicito. L'autrice ha indicato `M_ij = ⌊CAPACITÀ_j / ORE_i⌋`, il massimo
producibile date le ore del periodo. La scelta non introduce restrizioni rispetto alla
formulazione, perché quel limite è già implicito nel vincolo di capacità oraria, ed è al
tempo stesso il big-M più stretto deducibile dalle sole capacità. Il modello chiude
all'ottimo certificato di 1575 alla prima esecuzione.

**4. Il vincolo di copertura di H04.** Il manoscritto scrive `Σ_i x_ij ≥ DOMANDA_j`, dove
`x_ij` è definita nella formulazione stessa come *numero di viaggi*: la domanda risulta
così confrontata con un conteggio di viaggi anziché con la capacità trasportata.
Il modello, tradotto ed eseguito nella forma letterale, è risultato **`INFEASIBLE`**:
servirebbero 199 viaggi contro una disponibilità di flotta di 25. L'IIS calcolato da Gurobi
(sette vincoli: le quattro coperture, due disponibilità e le emissioni) coincide con il
conto aritmetico.

L'autrice ha confermato che si tratta di un errore di scrittura nella trascrizione e che il
vincolo inteso è `Σ_i CAPACITÀ_i·x_ij ≥ DOMANDA_j`, coerentemente con il testo del problema
(«la capacità complessiva assegnata a ogni rotta deve coprirne la domanda»). Recepita
l'intenzione dichiarata, il modello passa da nessuna soluzione ammissibile all'ottimo
certificato di **962**.

Vale per H04 la stessa osservazione già fatta per M05 e M07: il modello aveva fin dalla
prima esecuzione le dimensioni esatte della ground truth (24 variabili, 37 vincoli), cioè
la struttura era corretta e mancava un coefficiente dentro una riga. La prima esecuzione è
conservata in `H04/output_terminale_esecuzione_1.txt` e `H04/modello.ilp`.

**Nota metodologica (aggiornamento).** Con H04 i casi di divergenza fra trascrizione
letterale e intenzione dichiarata salgono a tre su quindici (M05, M07, H04), ai quali si
aggiungono i quattro di convenzione notazionale (`∈ Z`) e il parametro implicito di H02.
Il Cap. 5 deve distinguere nettamente queste categorie dagli errori di modellazione veri e
propri, che nello Scenario A non si sono finora mai verificati.

## Tempo-uomo

Il tempo-uomo è misurato dall'esperto e non è deducibile dai log. La fonte autorevole è
il registro di compilazione; i valori qui sotto ne sono la trascrizione. Il
tempo di solver riportato nei quadri di sintesi è il valore `m.Runtime` restituito da
Gurobi ed è quindi già separato dal tempo-uomo.

| ID | Lettura e comprensione | Formulazione matematica | Scrittura del codice | Debug e autocorrezioni | Verifica finale | Totale |
|---|---|---|---|---|---|---|
| M01 | 10 min | 10 min | 15 min | 0 min | 10 min | **45 min** |
| M02 | 10 min | 10 min | 20 min | 0 min | 15 min | **55 min** |
| M03 | 10 min | 15 min | 20 min | 0 min | 15 min | **60 min** |
| M04 | 10 min | 10 min | 15 min | 0 min | 10 min | **45 min** |
| M05 | 10 min | 10 min | 15 min | 0 min | 10 min | **45 min** |
| M06 | 15 min | 15 min | 20 min | 0 min | 10 min | **60 min** |
| M07 | 10 min | 15 min | 15 min | 0 min | 15 min | **55 min** |
| M08 | 15 min | 10 min | 15 min | 0 min | 10 min | **50 min** |
| M09 | 15 min | 15 min | 20 min | 0 min | 15 min | **65 min** |
| M10 | 15 min | 15 min | 20 min | 0 min | 10 min | **60 min** |
| H01 | 15 min | 20 min | 20 min | 0 min | 15 min | **70 min** |
| H02 | 20 min | 25 min | 20 min | 0 min | 15 min | **80 min** |
| H03 | 20 min | 20 min | 20 min | 0 min | 15 min | **75 min** |
| H04 | 20 min | 20 min | 20 min | 5 min | 15 min | **80 min** |
| H05 | 15 min | 20 min | 15 min | 0 min | 15 min | **65 min** |
| H06 | 20 min | 30 min | 30 min | 0 min | 15 min | **95 min** |
| H07 | 25 min | 35 min | 35 min | 0 min | 15 min | **110 min** |
| H08 | 20 min | 30 min | 30 min | 0 min | 15 min | **95 min** |
| H09 | 20 min | 35 min | 35 min | 0 min | 15 min | **105 min** |
| H10 | 20 min | 25 min | 30 min | 0 min | 10 min | **85 min** |

Il registro di compilazione è stato completato dall'esperto il 19 agosto 2026: tutte e sei
le voci sono compilate su tutti e venti i problemi. Le cifre che seguono sono definitive.

**Totale dello Scenario A: 1400 minuti**, cioè **23 ore e 20 minuti** di lavoro umano.
Parte I 540 minuti (9 ore esatte, media **54 minuti per problema**, da 45 a 65); Parte II
860 minuti (14 ore e 20 minuti, media **86 minuti**, da 65 a 110).

**Effetto della difficoltà.** Il tempo medio per problema sale in modo monotono lungo i tre
blocchi: **54** minuti sui dieci a difficoltà media, **74** su H01–H05, **98** su H06–H10.
Fra il primo e l'ultimo blocco il costo umano per problema **si raddoppia** (+81%), a
parità di esperto, di procedura e di strumento. Il confronto con il tempo di solver è di
un altro ordine di grandezza: 0,0342 secondi in Parte I e 0,1064 in Parte II, e anche
questo cresce con la difficoltà, ma resta sempre sui centesimi di secondo.

**Il rapporto fra le due scale.** 1400 minuti sono 84 000 secondi contro 0,1406 secondi di
solver: il tempo umano vale circa **600 000 volte** quello di calcolo. È il dato che il
Capitolo 5 deve mettere al centro — nello Scenario A l'ottimizzazione non è il collo di
bottiglia, lo è la modellazione.

**Dove va il tempo.** La ripartizione sulle cinque fasi, sui venti problemi:

| Fase | Totale | Quota |
|---|---|---|
| Scrittura del codice | 430 min | 30,7% |
| Formulazione matematica | 385 min | 27,5% |
| Lettura e comprensione | 315 min | 22,5% |
| Verifica finale | 265 min | 18,9% |
| Debug e autocorrezioni | 5 min | 0,4% |

Formulazione e codifica insieme valgono il **58%** del totale: è il lavoro di traduzione
dal testo al modello, cioè esattamente ciò che lo Scenario B chiede all'LLM. Il debug è
praticamente assente perché l'esperto sbaglia poco e, quando sbaglia, non se ne accorge —
il che rende la voce *Verifica finale*, quasi un quinto del totale, la più interessante
delle cinque: quindici minuti a problema spesi a controllare un risultato che in un caso
su venti resta comunque sbagliato.

**Costo per soluzione corretta: 73,7 minuti** (1400 minuti diviso 19 esiti corretti), da
confrontare con i 70 minuti nominali per problema. Il caso H07 è il più eloquente
dell'intero campione: con **110 minuti** è il problema su cui l'esperto ha speso di più fra
tutti e venti, ed è l'unico dei venti a dare un risultato sbagliato. Nessuna delle tre fasi
di controllo — codifica, esecuzione, verifica finale — ha intercettato l'errore.

**Debug e autocorrezioni — questione chiusa il 19 agosto 2026.** I 5 minuti di debug
attribuiti a M07, M09 e M10 sono stati rimossi su decisione dell'autrice, portando la voce
a **0 su tutti e quattro** i problemi interessati (M02 era già a 0). La ragione è che la
seconda esecuzione di M02, M07, M09 e M10 è la ritraduzione di `∈ Z` effettuata dopo il
chiarimento sulla convenzione di scrittura: è un'operazione di *traduzione* svolta in sede
di codifica, non un ciclo di debug dell'esperto sulla propria formulazione. Il totale di
Parte I passa così da 555 a **540 minuti**. Restano 5 minuti di debug su H04, che è invece
un ciclo reale dell'esperto: lì la prima esecuzione è tornata `INFEASIBLE` e il refuso è
stato individuato da lei. Le correzioni restano in ogni caso contate nella colonna «Corr.»
del quadro di sintesi, che misura le esecuzioni del codice e non lo sforzo dell'esperto.

## Osservazioni sulle singole formulazioni

**M01.** I vincoli di collegamento `y_ij ≤ x_i` rendono effettiva la richiesta di assegnare
ogni zona a un centro aperto. La capacità complessiva vincola fortemente la scelta: fra le
sei coppie di siti possibili solo B + D copre le sei zone (3 + 3).

**M02.** La coppia `x_i ≥ LOTTOMIN_i·δ_i` e `x_i ≤ DOMMAX_i·δ_i` collega produzione e setup
senza bisogno di un big-M esplicito. Entrambe le risorse risultano sature all'ottimo
(90/90 ore-macchina, 100/100 ore di lavoro).

**M03.** Le celle «—» della tabella sono rese come otto vincoli espliciti di
indisponibilità `x_ij = 0`, uno per cella; il conteggio è verificato a runtime dallo script.

**M04.** I requisiti di composizione minima della flotta e i limiti di disponibilità sono
espressi come bound sulle variabili (`1 ≤ x3 ≤ 4`, `1 ≤ x4 ≤ 5`) anziché come vincoli di
riga: il modello risultante ha solo tre vincoli ed è equivalente a quello di riferimento.

**M05 — refuso di trascrizione.** Il vincolo di copertura digitale è trascritto nel
manoscritto come `x1 + x3 + x9 ≥ 1`; l'indice 9 non esiste (i progetti sono otto) ed è stato
letto come `x7`, coerentemente con il testo («almeno un progetto digitale tra P1, P3 e P7»).
La lettura è stata confermata dall'autrice della formulazione ed è supportata da due
riscontri indipendenti: il modello viene a 7 vincoli come la ground truth e il valore ottimo
coincide con quello certificato.

**M06.** La linearizzazione del `max` è quella canonica: `Cmax` vincolata dal basso dai due
carichi e minimizzata. L'incompatibilità di J7 con la macchina A è espressa come `x_7B = 1`
anziché `x_7A = 0`: forme equivalenti in presenza dell'assegnazione unica.

**M07 — refuso di trascrizione.** Vedi sopra: limite superiore da leggersi
`x_i ≤ CAPACITÀ_i·δ_i`. Resta da segnalare una differenza di forma sul vincolo di qualità:
la formulazione lo scrive sulle binarie (`Σ QUALITÀ_i·δ_i ≥ 92`), mentre il testo chiede che
«la qualità media ponderata deve essere almeno 92», cioè un requisito sulle quantità. Sulla
soluzione ottima il punto non incide — la media ponderata vale 92,67 e il verificatore
indipendente, che controlla proprio la media ponderata, non rileva violazioni — ma la
differenza è annotata nella scheda di M07.

**M08.** L'inversione della matrice di copertura da «centro → zone» a «zona → centri» è
eseguita senza errori su tutte e dieci le righe, ed è il passaggio in cui in genere si
perdono vincoli. La doppia copertura di Z3 e Z7 è resa alzando a 2 il termine noto.

**M09.** Il divieto di arretrati posto dal testo è affidato interamente al dominio delle
scorte (`y_i ∈ Z`, interi non negativi): nessun altro vincolo lo implica, dato che
`y_6 ≥ 5` blocca solo l'ultimo periodo. Tutto il resto — bilancio, capacità, lotto minimo
legato a `δ`, scorta iniziale e finale, struttura dei costi — è corretto.

**M10.** Come in M09, la non negatività è affidata al dominio: `x_ij ≤ CAPACITÀ_ij·y_ij`
impone solo il limite superiore. Da notare che l'ottimo di questa istanza è degenere —
esistono direzioni a costo nullo lungo le quali il flusso potrebbe scendere sotto zero senza
cambiare l'obiettivo — quindi il dominio è ciò che garantisce non solo il valore ottimo ma
anche l'interpretabilità della soluzione restituita.

**H01.** Formulazione completa e non ambigua: tutti i parametri usati sono definiti, i
domini sono dichiarati con il segno (`y_ij ∈ Z ≥ 0`) e nessun vincolo richiede
interpretazione. Il doppio vincolo `20·x_i ≤ Σ_j y_ij ≤ CAPACITÀ_i·x_i` fa correttamente
doppio servizio: impone il movimento minimo di 20 unità solo ai centri aperti e obbliga a
flusso nullo quelli chiusi, senza bisogno di un vincolo di collegamento separato.

**H02.** Struttura corretta, ma con il big-M lasciato implicito (vedi «Chiarimenti
dell'autrice» del 17 agosto). Da segnalare una differenza di forma nel conteggio: la
formulazione scrive le scorte di apertura come tre vincoli espliciti (`y_A0 = 0`,
`y_B0 = 0`, `y_C0 = 6`), trattando quindi `y_i0` come variabili fissate, mentre la ground
truth le incorpora nei dati del bilancio del primo periodo. Da qui lo scarto di tre
variabili e tre vincoli (39/54 contro 36/51); le due scritture sono equivalenti e producono
lo stesso ottimo. Il divieto di arretrati è affidato al dominio delle scorte, come già in
M09.

**H03.** È il problema con il maggior numero di famiglie di vincoli eterogenee affrontato
finora — copertura, seniority, minimo e massimo di giorni, divieto di quattro giorni
consecutivi, competenze specialistiche, fine settimana, indisponibilità — e la formulazione
le tratta tutte senza omissioni, con dimensioni identiche alla ground truth. Il divieto di
quattro giorni consecutivi è scritto come quattro famiglie esplicite di vincoli anziché come
un unico vincolo parametrizzato sulla finestra scorrevole: le due forme sono equivalenti,
perché quattro finestre di ampiezza quattro esauriscono la settimana. La corrispondenza fra
i sei vincoli di indisponibilità e le celle «—» della tabella è esatta su tutte e sei; è il
passaggio in cui in genere si perdono vincoli.

**H04 — refuso di trascrizione.** Vedi sopra: vincolo di copertura da leggersi
`Σ_i CAPACITÀ_i·x_ij ≥ DOMANDA_j`. Da notare che la disuguaglianza di sinistra del
collegamento, scritta `y_ij ≤ x_ij`, è più forte del consueto `x_ij ≤ M·y_ij`: impone che,
se un tipo è dichiarato in uso su una rotta, vi sia effettivamente almeno un viaggio. Il
limite «al massimo due tipi per rotta» è così correttamente contato sui tipi realmente
impiegati e non su attivazioni fittizie.

**H05.** Il punto tecnicamente delicato è la richiesta esplicita di modellare le sinergie,
che introduce un prodotto logico fra binarie; la formulazione lo linearizza nel modo
canonico e completo, con tutte e sei le disuguaglianze. In un problema di massimo con
coefficiente positivo su `z` le disuguaglianze `z ≤ x_1` e `z ≤ x_2` basterebbero, perché
l'obiettivo spinge comunque `z` verso l'alto; la terza è ridondante all'ottimo ma rende la
variabile ausiliaria un vero indicatore della congiunzione e non solo un maggiorante. È la
scrittura più difendibile ed è quella che il testo chiede parlando di sinergie «modellate
esplicitamente». La verifica indipendente ricalcola le sinergie dalle sole `x`, senza usare
`z_AC` e `z_EK`, e le conferma entrambe attive.

**H06.** Il punto delicato è la costante big-M dei vincoli disgiuntivi di non
sovrapposizione, che il testo chiede esplicitamente di giustificare: la formulazione la
calcola per esteso come `max(disponibilità) + Σ durate = 6 + 38 = 44`, un maggiorante
dell'orizzonte valido e al tempo stesso stretto. Il conteggio dei vincoli è 72 contro 58
perché disponibilità e non negatività dei ritardi sono scritte come disuguaglianze anziché
come bound: `72 − 7 − 7 = 58` restituisce esattamente la ground truth. La verifica
indipendente ricalcola i ritardi come `max(0, completamento − scadenza)`, senza usare le
variabili `T`, e ritrova 42.

**H07 — unico esito non corretto.** Il modello è strutturalmente completo, ma il vincolo
`10·z_ij ≤ x_ij ≤ U_ij·z_ij` è imposto «∀ ij disponibile», cioè solo sulle quindici coppie
fornibili. Sulle tre coppie non fornibili la formulazione azzera `x_ij` ma lascia `z_ij`
libera, e il solver pone `z_C2,F = 1` e `z_C3,E = 1` con quantità nulla: il requisito di
multisourcing `Σ_j z_ij ≥ 2` risulta così soddisfatto senza acquistare davvero da due
fornitori. C2 arriva tutto da E e C3 tutto da F, e il costo scende a 2090 contro i 2160
dell'ottimo. Estendere il solo lato sinistro del vincolo a tutte le coppie basta a
chiudere il punto e riporta il modello a 2160 (prova condotta in copia di lavoro; il
`modello.py` non è stato modificato). Vedi `H07/scheda.md` per la segnalazione completa.

**H08.** Il backup delle zone critiche è tradotto correttamente come vincolo sulle sole
variabili di *apertura* e non di assegnazione: non si chiede che la zona sia servita da due
stazioni — l'assegnazione resta unica — ma che fra quelle che la raggiungono ne siano
aperte almeno due. È la lettura giusta di una richiesta facile da fraintendere, e le
dimensioni coincidono con la ground truth.

**H09.** È il modello più grande della Parte II e quello con più requisiti intrecciati;
la formulazione li tiene tutti distinti e chiude all'ottimo alla prima esecuzione.
A differenza di H02, qui il big-M del vincolo di lotto è calcolato nella formulazione
stessa — `M_it = ⌊(capacità_t + 20) / ore_i⌋`, il massimo producibile sfruttando anche
tutto lo straordinario — senza bisogno di chiarimenti. Le scorte iniziali sono trattate
come costanti e non come variabili fissate, scelta opposta a quella fatta in H02 e che qui
fa coincidere il conteggio con la ground truth (60 variabili, 75 vincoli). Il divieto di
arretrati è affidato al dominio delle scorte, come già in M09 e H02.

**H10.** La capacità è condivisa fra i due prodotti mentre i costi unitari sono per
prodotto: il legame passa da un unico vincolo, `x_ij,K1 + x_ij,K2 ≤ capacità_ij·y_ij`, che
somma i flussi ma li lascia distinti nell'obiettivo, e la formulazione lo scrive nella forma
giusta. La conservazione è elencata nodo per nodo anziché in notazione compatta; le due
uguaglianze in ingresso a T sono ridondanti — implicate dalla conservazione ai nodi
intermedi e dalle condizioni all'origine — ma sono state comunque tradotte perché l'esperto
le scrive, e spiegano parte dello scarto di conteggio (24 vincoli contro 23).

## Struttura dei file

```
scenario_a/
├── Registro_compilazione_Scenario_A.docx   registro dell'esperto, fonte del tempo-uomo
├── REGISTRO_SCENARIO_A.md          questo file
├── verifica_ammissibilita.py       verifica indipendente a posteriori
├── verifica_ammissibilita_output.txt
├── M01/ … M10/ · H01/ … H10/
│   ├── modello.py                  codice definitivo
│   ├── modello.lp                  modello in formato LP
│   ├── output_terminale.txt        output completo del terminale
│   ├── scheda.md                   registro del singolo problema
│   └── <ID>.sol                    file soluzione di Gurobi
```

In `H04/` sono conservati anche `output_terminale_esecuzione_1.txt` e `modello.ilp`, cioè
l'output e il sottosistema inammissibile irriducibile della prima esecuzione, quella con la
formulazione nella forma letterale.

Lo script `verifica_ammissibilita.py` non risolve né modifica i modelli: rilegge i file
`.sol` e controlla le decisioni ottenute contro i vincoli del problema descritto a parole,
confrontando poi l'obiettivo con l'ottimo certificato. Sui venti problemi eseguiti rileva
violazioni in un solo caso, H07, dove segnala che C2 e C3 provengono da un unico fornitore
ciascuno contro i due richiesti dal testo.

Il registro di compilazione è stato completato il 19 agosto 2026 ed è **integralmente
compilato**: venti schede da sei tabelle ciascuna, nessuna cella vuota, tutte le somme dei
tempi verificate. È la fonte autorevole del tempo-uomo; questo file e le `scheda.md` ne
sono trascrizioni allineate alla stessa data.
