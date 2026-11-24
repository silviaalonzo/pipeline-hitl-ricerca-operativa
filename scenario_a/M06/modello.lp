\ Model M06_bilanciamento_due_macchine
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xa3f3a63882a25e7e
Minimize
  Cmax
Subject To
 assegnazione[J1]: x[J1,A] + x[J1,B] = 1
 assegnazione[J2]: x[J2,A] + x[J2,B] = 1
 assegnazione[J3]: x[J3,A] + x[J3,B] = 1
 assegnazione[J4]: x[J4,A] + x[J4,B] = 1
 assegnazione[J5]: x[J5,A] + x[J5,B] = 1
 assegnazione[J6]: x[J6,A] + x[J6,B] = 1
 assegnazione[J7]: x[J7,A] + x[J7,B] = 1
 carico_A: - 7 x[J1,A] - 6 x[J2,A] - 8 x[J3,A] - 5 x[J4,A] - 9 x[J5,A]
   - 4 x[J6,A] + Cmax >= 0
 carico_B: - 9 x[J1,B] - 5 x[J2,B] - 7 x[J3,B] - 8 x[J4,B] - 6 x[J5,B]
   - 7 x[J6,B] - 5 x[J7,B] + Cmax >= 0
 incompatibilita_J7A: x[J7,B] = 1
Bounds
Binaries
 x[J1,A] x[J1,B] x[J2,A] x[J2,B] x[J3,A] x[J3,B] x[J4,A] x[J4,B] x[J5,A]
 x[J5,B] x[J6,A] x[J6,B] x[J7,A] x[J7,B]
End
