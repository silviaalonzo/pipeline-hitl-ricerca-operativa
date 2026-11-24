# Rapporto combinato — ablation della doppia memoria

Le venti osservazioni (cinque problemi × due condizioni × due repliche) sono state ricertificate sul modello originale e sull'ottimo noto.

| Condizione | Accuratezza | Riparazioni | Handoff | Tempo-uomo | Chiamate | Costo API | Latenza totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 10/10 (100%) | 4 | 4 | 70 min | 14 | $0.404466 | 85.1 min |
| Cmem | 10/10 (100%) | 1 | 1 | 20 min | 11 | $0.339127 | 71.9 min |

## Effetto per problema nelle due repliche

| Problema | Repliche con vantaggio | Repliche con svantaggio | Minuti risparmiati | Riparazioni evitate | Handoff evitati |
| --- | ---: | ---: | ---: | ---: | ---: |
| L01 | 2/2 | 0/2 | 30 | 2 | 2 |
| L02 | 1/2 | 0/2 | 20 | 1 | 1 |
| L03 | 0/2 | 0/2 | 0 | 0 | 0 |
| L04 | 0/2 | 1/2 | -20 | -1 | -1 |
| L05 | 1/2 | 0/2 | 20 | 1 | 1 |

## Lettura

A parità di accuratezza, la memoria riduce il tempo-uomo da 70 a 20 minuti, le riparazioni da 4 a 1 e gli handoff da 4 a 1. Il vantaggio compare in 4 delle dieci coppie replicate e interessa tre famiglie: L01, L02 e L05. L03 non mostra differenze; in una replica di L04 la condizione con memoria richiede una riparazione in più. L'effetto non è quindi universale.

Tutti gli interventi umani osservati sono revisioni di assicurazione, non correzioni del codice. I risultati sostengono quindi la riduzione dello sforzo umano operativo, ma non dimostrano ancora una diminuzione del costo di correzione in senso stretto.
