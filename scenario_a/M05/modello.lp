\ Model M05_selezione_portafoglio_progetti
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x7e7efb099ff50266
Maximize
  30 x[1] + 24 x[2] + 35 x[3] + 28 x[4] + 33 x[5] + 26 x[6] + 38 x[7]
   + 21 x[8]
Subject To
 budget: 20 x[1] + 18 x[2] + 27 x[3] + 24 x[4] + 22 x[5] + 19 x[6]
   + 30 x[7] + 15 x[8] <= 100
 personale: 4 x[1] + 3 x[2] + 5 x[3] + 4 x[4] + 4 x[5] + 3 x[6] + 5 x[7]
   + 2 x[8] <= 18
 P5_richiede_P2: - x[2] + x[5] <= 0
 P7_richiede_P3: - x[3] + x[7] <= 0
 P4_P6_incompatibili: x[4] + x[6] <= 1
 almeno_un_digitale: x[1] + x[3] + x[7] >= 1
 almeno_tre_progetti: x[1] + x[2] + x[3] + x[4] + x[5] + x[6] + x[7] + x[8]
   >= 3
Bounds
Binaries
 x[1] x[2] x[3] x[4] x[5] x[6] x[7] x[8]
End
