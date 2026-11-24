\ Model M09_piano_riordino
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xf6031acfc75b2aa3
Minimize
  9 x[1] + 8 x[2] + 11 x[3] + 7 x[4] + 10 x[5] + 9 x[6] + 2 y[1] + 2 y[2]
   + 2 y[3] + 2 y[4] + 2 y[5] + 2 y[6] + 40 delta[1] + 40 delta[2]
   + 40 delta[3] + 40 delta[4] + 40 delta[5] + 40 delta[6]
Subject To
 bilancio_1: x[1] - y[1] = 10
 bilancio_2: x[2] + y[1] - y[2] = 30
 bilancio_3: x[3] + y[2] - y[3] = 15
 bilancio_4: x[4] + y[3] - y[4] = 35
 bilancio_5: x[5] + y[4] - y[5] = 25
 bilancio_6: x[6] + y[5] - y[6] = 20
 capacita[1]: x[1] - 50 delta[1] <= 0
 capacita[2]: x[2] - 50 delta[2] <= 0
 capacita[3]: x[3] - 45 delta[3] <= 0
 capacita[4]: x[4] - 55 delta[4] <= 0
 capacita[5]: x[5] - 45 delta[5] <= 0
 capacita[6]: x[6] - 50 delta[6] <= 0
 ordine_minimo[1]: x[1] - 10 delta[1] >= 0
 ordine_minimo[2]: x[2] - 10 delta[2] >= 0
 ordine_minimo[3]: x[3] - 10 delta[3] >= 0
 ordine_minimo[4]: x[4] - 10 delta[4] >= 0
 ordine_minimo[5]: x[5] - 10 delta[5] >= 0
 ordine_minimo[6]: x[6] - 10 delta[6] >= 0
 scorta_finale: y[6] >= 5
Bounds
Binaries
 delta[1] delta[2] delta[3] delta[4] delta[5] delta[6]
Generals
 x[1] x[2] x[3] x[4] x[5] x[6] y[1] y[2] y[3] y[4] y[5] y[6]
End
