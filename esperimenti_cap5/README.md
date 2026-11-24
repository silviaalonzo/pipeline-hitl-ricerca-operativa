# Esperimenti — Capitolo 5

Questa cartella contiene l'infrastruttura riproducibile per lo Scenario B
(LLM + Gurobi, senza intervento dell'esperto) e il validatore comune ai tre
scenari.

## Ordine operativo

1. Salvare la chiave OpenRouter nel Portachiavi di macOS. La chiave non viene
   mostrate durante l'inserimento e non vengono scritte nei file della tesi:

   ```bash
   python3 configure_keys.py
   ```

2. Verificare Gurobi e le chiavi API:

   ```bash
   python3 check_setup.py
   ```

3. Eseguire una singola prova pilota, senza mostrare la ground truth al modello:

   ```bash
   python3 run_scenario_b.py --model gpt-5.6-sol --problem M01 --run 1
   ```

4. Controllare il codice estratto prima di eseguirlo:

   ```bash
   python3 execute_response.py --run-dir runs/B/gpt-5.6-sol/M01/run_01
   ```

5. Validare la soluzione prodotta rispetto al problema originale e all'ottimo
   certificato:

   ```bash
   python3 validate_candidate.py --run-dir runs/B/gpt-5.6-sol/M01/run_01
   ```

## Regole anti-contaminazione

- Alle API viene inviato esclusivamente il contenuto del singolo file in
  `dataset_cap4/prompts/` insieme al prompt di sistema.
- `ground_truth.json` non viene mai incluso nella richiesta.
- Nello Scenario B il risultato della validazione non viene restituito al
  modello e non sono consentiti tentativi di correzione.
- La chiave OpenRouter deve essere salvata nel Portachiavi di macOS o nella
  variabile d'ambiente `OPENROUTER_API_KEY`; non deve essere inserita nei file
  o nei log.
- Per ciascun modello il routing è limitato al provider ufficiale, i fallback
  sono disabilitati e vengono accettati soltanto endpoint che supportano tutti
  i parametri richiesti.

## Struttura degli output

Ogni esecuzione produce una cartella separata con:

- `request.json`: configurazione della chiamata e prompt;
- `response.json`: risposta grezza del provider;
- `response.txt`: testo generato dal modello;
- `generated.py`: codice Python estratto dalla risposta;
- `execution.json`: esito dell'esecuzione e tempi;
- `candidate_solution.json`: soluzione dichiarata dal codice;
- `validation.json`: verifica indipendente rispetto al problema originale.

## Risultato definitivo dello Scenario B

L'unico file riepilogativo da utilizzare per l'analisi e per il Capitolo 5 è
`RISULTATI_DEFINITIVI_SCENARIO_B.csv`. Contiene tutte le 180 esecuzioni e applica
il criterio di validazione definitivo: non è richiesta l'uguaglianza con il
vettore di variabili salvato nella ground truth; sono invece richiesti sia il
rispetto dei vincoli del problema originale sia la coincidenza del valore
dell'obiettivo verificato con l'ottimo noto.

Le cartelle in `runs/B/` conservano le evidenze grezze delle chiamate API e delle
esecuzioni. La verifica canonica si esegue con `audit_scenario_b.py`;
`revalidate_aliases.py` è mantenuto soltanto come modulo di supporto per la
normalizzazione documentata dei nomi delle variabili.
