\ Model M02_piano_produzione_setup
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xca19c079e42714ce
Maximize
  42 x[A] + 36 x[B] + 50 x[C] + 31 x[D] - 80 delta[A] - 65 delta[B]
   - 90 delta[C] - 50 delta[D]
Subject To
 ore_macchina: 3 x[A] + 2 x[B] + 4 x[C] + x[D] <= 90
 ore_lavoro: 2 x[A] + 3 x[B] + 2 x[C] + 2 x[D] <= 100
 lotto_minimo[A]: x[A] - 4 delta[A] >= 0
 lotto_minimo[B]: x[B] - 5 delta[B] >= 0
 lotto_minimo[C]: x[C] - 3 delta[C] >= 0
 lotto_minimo[D]: x[D] - 6 delta[D] >= 0
 domanda_massima[A]: x[A] - 20 delta[A] <= 0
 domanda_massima[B]: x[B] - 25 delta[B] <= 0
 domanda_massima[C]: x[C] - 16 delta[C] <= 0
 domanda_massima[D]: x[D] - 30 delta[D] <= 0
 almeno_due_articoli: delta[A] + delta[B] + delta[C] + delta[D] >= 2
Bounds
Binaries
 delta[A] delta[B] delta[C] delta[D]
Generals
 x[A] x[B] x[C] x[D]
End
