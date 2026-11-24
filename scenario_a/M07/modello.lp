\ Model M07_selezione_fornitori
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x2c0abfb51a2937c7
Minimize
  11 x[A] + 10 x[B] + 12 x[C] + 9 x[D] + 80 delta[A] + 95 delta[B]
   + 60 delta[C] + 120 delta[D]
Subject To
 fornitori_minimi: delta[A] + delta[B] + delta[C] + delta[D] >= 2
 fabbisogno: x[A] + x[B] + x[C] + x[D] = 180
 qualita: 96 delta[A] + 90 delta[B] + 98 delta[C] + 88 delta[D] >= 92
 emissioni: 3 x[A] + 4 x[B] + 2 x[C] + 5 x[D] <= 650
 ordine_minimo[A]: - x[A] + 20 delta[A] <= 0
 ordine_minimo[B]: - x[B] + 25 delta[B] <= 0
 ordine_minimo[C]: - x[C] + 15 delta[C] <= 0
 ordine_minimo[D]: - x[D] + 20 delta[D] <= 0
 capacita[A]: x[A] - 80 delta[A] <= 0
 capacita[B]: x[B] - 100 delta[B] <= 0
 capacita[C]: x[C] - 70 delta[C] <= 0
 capacita[D]: x[D] - 90 delta[D] <= 0
Bounds
Binaries
 delta[A] delta[B] delta[C] delta[D]
Generals
 x[A] x[B] x[C] x[D]
End
