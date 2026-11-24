\ Model H01
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xc70756c3a1375773
Minimize
  110 x[A] + 95 x[B] + 120 x[C] + 90 x[D] + 105 x[E] + 100 x[F] + 4 y[A,Z1]
   + 5 y[A,Z2] + 7 y[A,Z3] + 9 y[A,Z4] + 8 y[A,Z5] + 10 y[A,Z6] + 6 y[A,Z7]
   + 7 y[A,Z8] + 7 y[B,Z1] + 4 y[B,Z2] + 5 y[B,Z3] + 8 y[B,Z4] + 9 y[B,Z5]
   + 8 y[B,Z6] + 7 y[B,Z7] + 6 y[B,Z8] + 6 y[C,Z1] + 8 y[C,Z2] + 4 y[C,Z3]
   + 7 y[C,Z4] + 6 y[C,Z5] + 7 y[C,Z6] + 5 y[C,Z7] + 8 y[C,Z8] + 10 y[D,Z1]
   + 9 y[D,Z2] + 8 y[D,Z3] + 4 y[D,Z4] + 5 y[D,Z5] + 6 y[D,Z6] + 8 y[D,Z7]
   + 5 y[D,Z8] + 9 y[E,Z1] + 7 y[E,Z2] + 9 y[E,Z3] + 5 y[E,Z4] + 4 y[E,Z5]
   + 5 y[E,Z6] + 6 y[E,Z7] + 7 y[E,Z8] + 11 y[F,Z1] + 10 y[F,Z2]
   + 7 y[F,Z3] + 6 y[F,Z4] + 7 y[F,Z5] + 4 y[F,Z6] + 7 y[F,Z7] + 4 y[F,Z8]
Subject To
 domanda[Z1]: y[A,Z1] + y[B,Z1] + y[C,Z1] + y[D,Z1] + y[E,Z1] + y[F,Z1]
   = 30
 domanda[Z2]: y[A,Z2] + y[B,Z2] + y[C,Z2] + y[D,Z2] + y[E,Z2] + y[F,Z2]
   = 25
 domanda[Z3]: y[A,Z3] + y[B,Z3] + y[C,Z3] + y[D,Z3] + y[E,Z3] + y[F,Z3]
   = 35
 domanda[Z4]: y[A,Z4] + y[B,Z4] + y[C,Z4] + y[D,Z4] + y[E,Z4] + y[F,Z4]
   = 20
 domanda[Z5]: y[A,Z5] + y[B,Z5] + y[C,Z5] + y[D,Z5] + y[E,Z5] + y[F,Z5]
   = 28
 domanda[Z6]: y[A,Z6] + y[B,Z6] + y[C,Z6] + y[D,Z6] + y[E,Z6] + y[F,Z6]
   = 32
 domanda[Z7]: y[A,Z7] + y[B,Z7] + y[C,Z7] + y[D,Z7] + y[E,Z7] + y[F,Z7]
   = 24
 domanda[Z8]: y[A,Z8] + y[B,Z8] + y[C,Z8] + y[D,Z8] + y[E,Z8] + y[F,Z8]
   = 26
 min_centri: x[A] + x[B] + x[C] + x[D] + x[E] + x[F] >= 3
 max_centri: x[A] + x[B] + x[C] + x[D] + x[E] + x[F] <= 4
 nord: x[A] + x[B] + x[C] >= 1
 sud: x[D] + x[E] + x[F] >= 1
 movim_min[A]: - 20 x[A] + y[A,Z1] + y[A,Z2] + y[A,Z3] + y[A,Z4] + y[A,Z5]
   + y[A,Z6] + y[A,Z7] + y[A,Z8] >= 0
 movim_min[B]: - 20 x[B] + y[B,Z1] + y[B,Z2] + y[B,Z3] + y[B,Z4] + y[B,Z5]
   + y[B,Z6] + y[B,Z7] + y[B,Z8] >= 0
 movim_min[C]: - 20 x[C] + y[C,Z1] + y[C,Z2] + y[C,Z3] + y[C,Z4] + y[C,Z5]
   + y[C,Z6] + y[C,Z7] + y[C,Z8] >= 0
 movim_min[D]: - 20 x[D] + y[D,Z1] + y[D,Z2] + y[D,Z3] + y[D,Z4] + y[D,Z5]
   + y[D,Z6] + y[D,Z7] + y[D,Z8] >= 0
 movim_min[E]: - 20 x[E] + y[E,Z1] + y[E,Z2] + y[E,Z3] + y[E,Z4] + y[E,Z5]
   + y[E,Z6] + y[E,Z7] + y[E,Z8] >= 0
 movim_min[F]: - 20 x[F] + y[F,Z1] + y[F,Z2] + y[F,Z3] + y[F,Z4] + y[F,Z5]
   + y[F,Z6] + y[F,Z7] + y[F,Z8] >= 0
 capacita[A]: - 90 x[A] + y[A,Z1] + y[A,Z2] + y[A,Z3] + y[A,Z4] + y[A,Z5]
   + y[A,Z6] + y[A,Z7] + y[A,Z8] <= 0
 capacita[B]: - 80 x[B] + y[B,Z1] + y[B,Z2] + y[B,Z3] + y[B,Z4] + y[B,Z5]
   + y[B,Z6] + y[B,Z7] + y[B,Z8] <= 0
 capacita[C]: - 110 x[C] + y[C,Z1] + y[C,Z2] + y[C,Z3] + y[C,Z4] + y[C,Z5]
   + y[C,Z6] + y[C,Z7] + y[C,Z8] <= 0
 capacita[D]: - 75 x[D] + y[D,Z1] + y[D,Z2] + y[D,Z3] + y[D,Z4] + y[D,Z5]
   + y[D,Z6] + y[D,Z7] + y[D,Z8] <= 0
 capacita[E]: - 95 x[E] + y[E,Z1] + y[E,Z2] + y[E,Z3] + y[E,Z4] + y[E,Z5]
   + y[E,Z6] + y[E,Z7] + y[E,Z8] <= 0
 capacita[F]: - 85 x[F] + y[F,Z1] + y[F,Z2] + y[F,Z3] + y[F,Z4] + y[F,Z5]
   + y[F,Z6] + y[F,Z7] + y[F,Z8] <= 0
 emissioni: y[A,Z1] + 2 y[A,Z2] + 3 y[A,Z3] + 4 y[A,Z4] + 3 y[A,Z5]
   + 4 y[A,Z6] + 2 y[A,Z7] + 3 y[A,Z8] + 2 y[B,Z1] + y[B,Z2] + 2 y[B,Z3]
   + 3 y[B,Z4] + 4 y[B,Z5] + 3 y[B,Z6] + 3 y[B,Z7] + 2 y[B,Z8] + 2 y[C,Z1]
   + 3 y[C,Z2] + y[C,Z3] + 3 y[C,Z4] + 2 y[C,Z5] + 3 y[C,Z6] + y[C,Z7]
   + 3 y[C,Z8] + 4 y[D,Z1] + 3 y[D,Z2] + 3 y[D,Z3] + y[D,Z4] + 2 y[D,Z5]
   + 2 y[D,Z6] + 3 y[D,Z7] + y[D,Z8] + 3 y[E,Z1] + 2 y[E,Z2] + 4 y[E,Z3]
   + 2 y[E,Z4] + y[E,Z5] + 2 y[E,Z6] + 2 y[E,Z7] + 3 y[E,Z8] + 4 y[F,Z1]
   + 4 y[F,Z2] + 3 y[F,Z3] + 2 y[F,Z4] + 3 y[F,Z5] + y[F,Z6] + 3 y[F,Z7]
   + y[F,Z8] <= 470
Bounds
Binaries
 x[A] x[B] x[C] x[D] x[E] x[F]
Generals
 y[A,Z1] y[A,Z2] y[A,Z3] y[A,Z4] y[A,Z5] y[A,Z6] y[A,Z7] y[A,Z8] y[B,Z1]
 y[B,Z2] y[B,Z3] y[B,Z4] y[B,Z5] y[B,Z6] y[B,Z7] y[B,Z8] y[C,Z1] y[C,Z2]
 y[C,Z3] y[C,Z4] y[C,Z5] y[C,Z6] y[C,Z7] y[C,Z8] y[D,Z1] y[D,Z2] y[D,Z3]
 y[D,Z4] y[D,Z5] y[D,Z6] y[D,Z7] y[D,Z8] y[E,Z1] y[E,Z2] y[E,Z3] y[E,Z4]
 y[E,Z5] y[E,Z6] y[E,Z7] y[E,Z8] y[F,Z1] y[F,Z2] y[F,Z3] y[F,Z4] y[F,Z5]
 y[F,Z6] y[F,Z7] y[F,Z8]
End
