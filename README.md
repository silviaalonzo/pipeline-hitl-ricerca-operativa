# Materiali sperimentali

Dataset, codice e tracce di esecuzione a corredo del lavoro su una pipeline
*human-in-the-loop* per la formulazione e la risoluzione di problemi di Ricerca
Operativa con Large Language Model.

Ogni risultato riportato nel paper può essere ricondotto alla specifica esecuzione
che lo ha generato: per ciascuna prova sono archiviati la richiesta inviata, la
risposta originale del modello, il codice estratto, l'esito dell'esecuzione e la
validazione indipendente della soluzione.

## Che cosa contiene

| Cartella | Sezione del paper | Contenuto |
|---|---|---|
| `dataset_cap4/` | §4.1 | I 20 problemi IP/MILP del benchmark: tracce, prompt, ground truth certificata, script di verifica con Gurobi |
| `scenario_a/` | §5 | Scenario A, il riferimento umano: formulazioni, modelli `.lp`, codice e output per ciascuno dei 20 problemi |
| `esperimenti_cap5/` | §4.3, §5 | Harness degli esperimenti e tracce complete dello Scenario B (3 modelli × 20 problemi × 3 repliche) |
| `scenario_c/` | §5 | Tracce dello Scenario C, registro degli interventi dell'esperto e stato della memoria |
| `dataset_cap7/` | §4.6 | I 5 problemi aggiuntivi L01–L05 costruiti per l'ablazione, con ottimi certificati da due procedure indipendenti |
| `esperimenti_cap7/` | §6 | Ablazione appaiata della doppia memoria: condizioni `Cmem` e `C0`, risultati e analisi |

Ogni cartella ha un proprio `README.md` con la descrizione dei file e i comandi
per rieseguire la procedura.

## Dove si trovano i risultati principali

- Scenario B: `esperimenti_cap5/RISULTATI_DEFINITIVI_SCENARIO_B.csv`
- Scenario C: `scenario_c/RISULTATI_DEFINITIVI_SCENARIO_C.json` e `scenario_c/REGISTRO_SCENARIO_C.csv`
- Interventi dell'esperto e tempi: `scenario_c/INTERVENTI_ESPERTO.csv`
- Ablazione della memoria: `esperimenti_cap7/RISULTATI_DEFINITIVI_CAP7.csv`

## Criterio di correttezza

Una soluzione è considerata corretta solo se è ammissibile nel problema
*originale*, entro le tolleranze dichiarate nel paper, e se il valore della
funzione obiettivo *ricalcolato* coincide con l'ottimo certificato. Non è
richiesto che il vettore delle variabili coincida con quello salvato nella ground
truth: un ottimo alternativo è valido a tutti gli effetti.

## Date delle esecuzioni e riuso delle istanze

Le 301 esecuzioni archiviate, 180 dello Scenario B, 96 dello Scenario C e 25 dell'ablazione,
sono state condotte **fra il 10 e il 26 agosto 2026**, prima della pubblicazione di queste
istanze: lo Scenario B il 10 agosto, lo Scenario C il 24, l'ablazione il 26. I problemi sono originali e fino a quelle date non esistevano in rete, né
in questa né in altra forma; la data di ciascuna chiamata è nel campo `started_at_utc`, o
`created_at_utc`, del relativo `request.json`.

Da oggi questo non vale più. Chi riusi i venti problemi del benchmark, o i cinque
dell'ablazione, per valutare modelli addestrati dopo la pubblicazione deve considerare la
possibilità che li abbiano incontrati in addestramento, soluzioni comprese, e trattare con
cautela i risultati che ne ottiene. Le istanze sono scritte a mano una per una in
`dataset_cap4/build_dataset.py` e non sono generate da un seme casuale: non è quindi
possibile produrne varianti equivalenti e non contaminate cambiando un parametro.

Chi volesse costruire istanze nuove può seguire il metodo usato per i cinque problemi
dell'ablazione, descritti in `dataset_cap7/README.md`: ciascuno riprende un pattern di errore
osservato nel benchmark, ma con dati, dimensione e struttura differenti.

## Riprodurre le verifiche

La ricertificazione degli ottimi richiede Gurobi con una licenza valida:

```bash
pip install -r esperimenti_cap5/requirements.txt
python3 dataset_cap4/verify_with_gurobi.py
python3 dataset_cap7/verify_with_gurobi.py
```

La riesecuzione delle chiamate ai modelli richiede inoltre una chiave OpenRouter.
Nessuna chiave è presente in questo repository: le credenziali vengono lette
dalle variabili d'ambiente o dal Portachiavi di macOS
(`esperimenti_cap5/secret_store.py`). Si veda `esperimenti_cap5/README.md` per
l'ordine operativo.

Le risposte dei modelli dipendono dal provider e dalla versione servita, quindi
una riesecuzione non riproduce necessariamente gli stessi testi. Le tracce
archiviate qui restano la registrazione delle esecuzioni effettivamente condotte.

## Che cosa non è incluso

Il caso applicativo aziendale non è pubblicato. I dati provengono da un'impresa
che non ne ha autorizzato la diffusione; nel paper il caso è descritto in forma
anonima e il modello è presentato in forma interamente parametrica.

## Licenza

I dati e la documentazione sono distribuiti con licenza
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); il codice con licenza
MIT. Si veda il file `LICENSE`.
