# Esperimenti del Capitolo 7 — ablation della doppia memoria

Questa cartella contiene il confronto appaiato definitivo sui cinque problemi
L01–L05 della versione `definitivo_v2` del dataset.

- `Cmem`: DeepSeek V4 Flash riceve lo snapshot congelato della memoria accumulata nello Scenario C del Capitolo 5.
- `C0`: la stessa pipeline riceve una sezione di memoria esplicitamente vuota.

Le due condizioni mantengono invariati modello, prompt di sistema, traccia, solver,
validatore, limiti di esecuzione, self-repair e regole di handoff. Durante le dieci
prove entrambe le memorie restano congelate: gli eventuali interventi sono registrati,
ma non modificano lo snapshot usato nei problemi successivi.

Una calibrazione preliminare ha mostrato un effetto soffitto ed è esclusa
dall'analisi principale; non è pubblicata qui, ma `protocol.json` e
`freeze_protocol.py` la registrano come `archivio_cap7/calibrazione_v1_20260826`
perché il protocollo è stato congelato prima di questa scelta e i suoi file non
vengono modificati a posteriori. Le istanze definitive sono state rese più ampie
e più dense prima del congelamento del protocollo. I loro ottimi sono stati
certificati da due procedure indipendenti e un audit separato ha verificato che
l'omissione del principio bersaglio produca, in ogni caso, una soluzione non
accettabile rispetto al problema originale.

Il limite di output è fissato a 64.000 token per entrambe le condizioni. Nessuna
istanza, regola di validazione o configurazione potrà essere modificata in base
agli esiti osservati dopo il congelamento.

## Ordine controbilanciato

1. L01: C0 → Cmem
2. L02: Cmem → C0
3. L03: C0 → Cmem
4. L04: Cmem → C0
5. L05: C0 → Cmem

## Comandi

```bash
python3 esperimenti_cap7/freeze_protocol.py
python3 esperimenti_cap7/check_setup.py
python3 esperimenti_cap7/run_ablation.py --status
python3 esperimenti_cap7/run_ablation.py
```

Il runner si arresta al primo handoff e non avvia la prova successiva finché
l'intervento dell'esperto non è stato registrato.
