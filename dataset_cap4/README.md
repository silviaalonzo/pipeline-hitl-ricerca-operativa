# Dataset sperimentale — Capitolo 4

Questa cartella contiene 20 problemi IP/MILP originali e deterministici: 10 di difficoltà media e 10 di difficoltà elevata, organizzati in coppie per dominio.

## File da usare

- `Dataset_20_problemi_IP_MILP.docx`: tracce da somministrare nei tre scenari.
- `Ground_truth_20_problemi_IP_MILP.docx`: soluzioni riservate e riepilogo dei modelli.
- `problems.jsonl`: versione machine-readable delle sole tracce.
- `prompts/M01.md` … `prompts/H10.md`: un prompt autonomo per ogni istanza.
- `ground_truth.json`: matrice completa di variabili, funzione obiettivo, vincoli e soluzione.
- `solutions_summary.csv`: riepilogo degli ottimi e delle dimensioni.
- `verify_with_gurobi.py`: ricostruzione e soluzione con Gurobi.
- `build_dataset.py`: sorgente deterministica e certificazione HiGHS.

## Regola anti-contaminazione

Durante i test distribuire soltanto il DOCX delle tracce oppure il singolo file nella cartella `prompts`. Non mostrare `ground_truth.json`, il Word delle soluzioni o output di run precedenti.

## Riproduzione

Con Gurobi installato:

```bash
python verify_with_gurobi.py
python verify_with_gurobi.py --id H03
```

Le risposte non devono necessariamente coincidere con il vettore salvato: un ottimo alternativo è valido se è ammissibile e raggiunge lo stesso valore obiettivo entro tolleranza.
