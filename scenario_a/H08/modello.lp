\ Model H08
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xe240ccd29892729d
Minimize
  24 x[A,Z1] + 40 x[B,Z1] + 42 x[A,Z2] + 56 x[B,Z2] + 70 x[C,Z2]
   + 110 x[B,Z3] + 40 x[C,Z3] + 60 x[D,Z3] + 42 x[C,Z4] + 54 x[D,Z4]
   + 54 x[A,Z5] + 27 x[D,Z5] + 45 x[E,Z5] + 88 x[B,Z6] + 64 x[E,Z6]
   + 80 x[F,Z6] + 49 x[C,Z7] + 28 x[F,Z7] + 42 x[G,Z7] + 56 x[H,Z7]
   + 33 x[D,Z8] + 99 x[G,Z8] + 121 x[H,Z8] + 48 x[E,Z9] + 60 x[F,Z9]
   + 30 x[H,Z9] + 36 x[F,Z10] + 54 x[G,Z10] + 72 x[H,Z10] + 48 x[A,Z11]
   + 40 x[E,Z11] + 88 x[H,Z11] + 77 x[B,Z12] + 21 x[G,Z12] + 35 x[H,Z12]
   + 35 y[A] + 32 y[B] + 40 y[C] + 30 y[D] + 38 y[E] + 33 y[F] + 36 y[G]
   + 31 y[H]
Subject To
 assegnazione[Z1]: x[A,Z1] + x[B,Z1] = 1
 assegnazione[Z2]: x[A,Z2] + x[B,Z2] + x[C,Z2] = 1
 assegnazione[Z3]: x[B,Z3] + x[C,Z3] + x[D,Z3] = 1
 assegnazione[Z4]: x[C,Z4] + x[D,Z4] = 1
 assegnazione[Z5]: x[A,Z5] + x[D,Z5] + x[E,Z5] = 1
 assegnazione[Z6]: x[B,Z6] + x[E,Z6] + x[F,Z6] = 1
 assegnazione[Z7]: x[C,Z7] + x[F,Z7] + x[G,Z7] + x[H,Z7] = 1
 assegnazione[Z8]: x[D,Z8] + x[G,Z8] + x[H,Z8] = 1
 assegnazione[Z9]: x[E,Z9] + x[F,Z9] + x[H,Z9] = 1
 assegnazione[Z10]: x[F,Z10] + x[G,Z10] + x[H,Z10] = 1
 assegnazione[Z11]: x[A,Z11] + x[E,Z11] + x[H,Z11] = 1
 assegnazione[Z12]: x[B,Z12] + x[G,Z12] + x[H,Z12] = 1
 solo_aperte[A,Z1]: x[A,Z1] - y[A] <= 0
 solo_aperte[B,Z1]: x[B,Z1] - y[B] <= 0
 solo_aperte[A,Z2]: x[A,Z2] - y[A] <= 0
 solo_aperte[B,Z2]: x[B,Z2] - y[B] <= 0
 solo_aperte[C,Z2]: x[C,Z2] - y[C] <= 0
 solo_aperte[B,Z3]: x[B,Z3] - y[B] <= 0
 solo_aperte[C,Z3]: x[C,Z3] - y[C] <= 0
 solo_aperte[D,Z3]: x[D,Z3] - y[D] <= 0
 solo_aperte[C,Z4]: x[C,Z4] - y[C] <= 0
 solo_aperte[D,Z4]: x[D,Z4] - y[D] <= 0
 solo_aperte[A,Z5]: x[A,Z5] - y[A] <= 0
 solo_aperte[D,Z5]: x[D,Z5] - y[D] <= 0
 solo_aperte[E,Z5]: x[E,Z5] - y[E] <= 0
 solo_aperte[B,Z6]: x[B,Z6] - y[B] <= 0
 solo_aperte[E,Z6]: x[E,Z6] - y[E] <= 0
 solo_aperte[F,Z6]: x[F,Z6] - y[F] <= 0
 solo_aperte[C,Z7]: x[C,Z7] - y[C] <= 0
 solo_aperte[F,Z7]: x[F,Z7] - y[F] <= 0
 solo_aperte[G,Z7]: x[G,Z7] - y[G] <= 0
 solo_aperte[H,Z7]: x[H,Z7] - y[H] <= 0
 solo_aperte[D,Z8]: x[D,Z8] - y[D] <= 0
 solo_aperte[G,Z8]: x[G,Z8] - y[G] <= 0
 solo_aperte[H,Z8]: x[H,Z8] - y[H] <= 0
 solo_aperte[E,Z9]: x[E,Z9] - y[E] <= 0
 solo_aperte[F,Z9]: x[F,Z9] - y[F] <= 0
 solo_aperte[H,Z9]: x[H,Z9] - y[H] <= 0
 solo_aperte[F,Z10]: x[F,Z10] - y[F] <= 0
 solo_aperte[G,Z10]: x[G,Z10] - y[G] <= 0
 solo_aperte[H,Z10]: x[H,Z10] - y[H] <= 0
 solo_aperte[A,Z11]: x[A,Z11] - y[A] <= 0
 solo_aperte[E,Z11]: x[E,Z11] - y[E] <= 0
 solo_aperte[H,Z11]: x[H,Z11] - y[H] <= 0
 solo_aperte[B,Z12]: x[B,Z12] - y[B] <= 0
 solo_aperte[G,Z12]: x[G,Z12] - y[G] <= 0
 solo_aperte[H,Z12]: x[H,Z12] - y[H] <= 0
 capacita[A]: 8 x[A,Z1] + 7 x[A,Z2] + 9 x[A,Z5] + 8 x[A,Z11] - 42 y[A]
   <= 0
 capacita[B]: 8 x[B,Z1] + 7 x[B,Z2] + 10 x[B,Z3] + 8 x[B,Z6] + 7 x[B,Z12]
   - 44 y[B] <= 0
 capacita[C]: 7 x[C,Z2] + 10 x[C,Z3] + 6 x[C,Z4] + 7 x[C,Z7] - 46 y[C]
   <= 0
 capacita[D]: 10 x[D,Z3] + 6 x[D,Z4] + 9 x[D,Z5] + 11 x[D,Z8] - 40 y[D]
   <= 0
 capacita[E]: 9 x[E,Z5] + 8 x[E,Z6] + 6 x[E,Z9] + 8 x[E,Z11] - 45 y[E]
   <= 0
 capacita[F]: 8 x[F,Z6] + 7 x[F,Z7] + 6 x[F,Z9] + 9 x[F,Z10] - 43 y[F]
   <= 0
 capacita[G]: 7 x[G,Z7] + 11 x[G,Z8] + 9 x[G,Z10] + 7 x[G,Z12] - 44 y[G]
   <= 0
 capacita[H]: 7 x[H,Z7] + 11 x[H,Z8] + 6 x[H,Z9] + 9 x[H,Z10] + 8 x[H,Z11]
   + 7 x[H,Z12] - 42 y[H] <= 0
 quattro_stazioni: y[A] + y[B] + y[C] + y[D] + y[E] + y[F] + y[G] + y[H]
   = 4
 ovest: y[A] + y[B] + y[C] + y[D] >= 1
 est: y[E] + y[F] + y[G] + y[H] >= 1
 backup_Z3: y[B] + y[C] + y[D] >= 2
 backup_Z8: y[D] + y[G] + y[H] >= 2
 backup_Z11: y[A] + y[E] + y[H] >= 2
Bounds
Binaries
 x[A,Z1] x[B,Z1] x[A,Z2] x[B,Z2] x[C,Z2] x[B,Z3] x[C,Z3] x[D,Z3] x[C,Z4]
 x[D,Z4] x[A,Z5] x[D,Z5] x[E,Z5] x[B,Z6] x[E,Z6] x[F,Z6] x[C,Z7] x[F,Z7]
 x[G,Z7] x[H,Z7] x[D,Z8] x[G,Z8] x[H,Z8] x[E,Z9] x[F,Z9] x[H,Z9] x[F,Z10]
 x[G,Z10] x[H,Z10] x[A,Z11] x[E,Z11] x[H,Z11] x[B,Z12] x[G,Z12] x[H,Z12]
 y[A] y[B] y[C] y[D] y[E] y[F] y[G] y[H]
End
