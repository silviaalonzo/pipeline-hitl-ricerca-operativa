# Dataset definitivo del Capitolo 7

La versione `definitivo_v2` contiene cinque istanze IP/MILP di difficoltà elevata,
costruite per l'ablation appaiata della doppia memoria. Ciascuna istanza riprende
un pattern di errore osservato nello Scenario C del Capitolo 5, ma cambia dati,
dimensione e struttura rispetto al problema sorgente.

| ID | Dominio | Variabili | Vincoli | Ottimo |
|---|---|---:|---:|---:|
| L01 | Distribuzione urbana | 136 | 43 | 394,0 |
| L02 | Produzione e scorte | 72 | 94 | 8.134,8 |
| L03 | Approvvigionamento | 74 | 134 | 2.770,0 |
| L04 | Produzione multi-prodotto | 102 | 126 | 9.077,6 |
| L05 | Assegnazione e qualificazione | 190 | 83 | 371,0 |

Gli ottimi sono risolti con gap nullo da `build_dataset_cap7.py` e ricertificati
indipendentemente da `verify_with_gurobi.py`. Lo script
`audit_target_patterns.py` risolve inoltre cinque formulazioni volutamente
difettose e verifica che il pattern bersaglio sia sostanziale in tutte le
istanze. La ground truth e i principi bersaglio non sono inclusi nei prompt
consegnati al modello.

Una versione precedente delle istanze, usata per una calibrazione preliminare, è
esclusa dall'analisi principale e non è pubblicata qui. I file del protocollo vi
fanno riferimento come `archivio_cap7/calibrazione_v1_20260826`.
