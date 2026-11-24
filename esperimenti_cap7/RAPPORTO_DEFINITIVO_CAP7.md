# Rapporto definitivo — ablation della doppia memoria

Tutte le dieci soluzioni sono state ricertificate sul modello originale e sull'ottimo noto.
Le memorie sono rimaste identiche agli snapshot congelati prima della campagna.

| Condizione | Accuratezza | Riparazioni | Handoff | Tempo-uomo | Correzione | Chiamate | Costo API |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 5/5 (100%) | 1 | 1 | 20 min | 0 min | 6 | $0.143941 |
| Cmem | 5/5 (100%) | 0 | 0 | 0 min | 0 min | 5 | $0.143562 |

## Confronto appaiato

| Problema | Tempo C0 | Tempo Cmem | Correzione C0/Cmem | Riparazioni C0 | Riparazioni Cmem | Principio bersaglio dichiarato |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| L01 | 20 min | 0 min | 0/0 min | 1 | 0 | sì |
| L02 | 0 min | 0 min | 0/0 min | 0 | 0 | sì |
| L03 | 0 min | 0 min | 0/0 min | 0 | 0 | sì |
| L04 | 0 min | 0 min | 0/0 min | 0 | 0 | sì |
| L05 | 0 min | 0 min | 0/0 min | 0 | 0 | sì |

## Valutazione di H5

H5 riceve un supporto parziale ed esplorativo. A parità di accuratezza, la memoria riduce il tempo-uomo totale da 20 a 0 minuti, le riparazioni automatiche da 1 a 0 e gli handoff da 1 a 0. La differenza è concentrata su L01: senza memoria il primo output richiede un self-repair e una revisione umana, mentre con memoria il problema viene chiuso al primo tentativo dichiarando l'uso del principio bersaglio S-001. L'intervento evitato è tuttavia una revisione di approvazione e non una correzione del codice; con cinque coppie e una sola esecuzione per condizione, il risultato documenta il vantaggio operativo della memoria ma non costituisce una prova conclusiva della riduzione del costo di correzione in senso stretto.
