\ Model M04_composizione_flotta
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xf2473fc587e77fc6
Minimize
  120 x[1] + 180 x[2] + 210 x[3] + 150 x[4] + 260 x[5]
Subject To
 volume: 18 x[1] + 30 x[2] + 20 x[3] + 16 x[4] + 42 x[5] >= 180
 portata: 8 x[1] + 18 x[2] + 10 x[3] + 7 x[4] + 28 x[5] >= 95
 emissioni: 12 x[1] + 22 x[2] + 15 x[3] + 4 x[4] + 32 x[5] <= 145
Bounds
 x[1] <= 8
 x[2] <= 6
 1 <= x[3] <= 4
 1 <= x[4] <= 5
 x[5] <= 3
Generals
 x[1] x[2] x[3] x[4] x[5]
End
