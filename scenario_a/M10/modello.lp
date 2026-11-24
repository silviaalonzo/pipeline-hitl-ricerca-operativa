\ Model M10_rete_distributiva
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x39f4524f1c53428e
Minimize
  2 x[S,A] + 3 x[S,B] + x[A,B] + 2 x[A,C] + 2 x[B,C] + 4 x[B,T] + 2 x[C,T]
   + 40 y[S,A] + 35 y[S,B] + 15 y[A,B] + 30 y[A,C] + 18 y[B,C] + 45 y[B,T]
   + 38 y[C,T]
Subject To
 attivazione[S,A]: x[S,A] - 30 y[S,A] <= 0
 attivazione[S,B]: x[S,B] - 35 y[S,B] <= 0
 attivazione[A,B]: x[A,B] - 15 y[A,B] <= 0
 attivazione[A,C]: x[A,C] - 25 y[A,C] <= 0
 attivazione[B,C]: x[B,C] - 20 y[B,C] <= 0
 attivazione[B,T]: x[B,T] - 25 y[B,T] <= 0
 attivazione[C,T]: x[C,T] - 35 y[C,T] <= 0
 uscita_S: x[S,A] + x[S,B] = 40
 nodo_A: x[S,A] - x[A,B] - x[A,C] = 0
 nodo_B: x[S,B] + x[A,B] - x[B,C] - x[B,T] = 0
 nodo_C: x[A,C] + x[B,C] - x[C,T] = 0
 ingresso_T: x[B,T] + x[C,T] = 40
Bounds
Binaries
 y[S,A] y[S,B] y[A,B] y[A,C] y[B,C] y[B,T] y[C,T]
Generals
 x[S,A] x[S,B] x[A,B] x[A,C] x[B,C] x[B,T] x[C,T]
End
