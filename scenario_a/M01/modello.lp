\ Model M01_localizzazione_centri_assistenza
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xa449e32ad71504ad
Minimize
  38 x[A] + 42 x[B] + 35 x[C] + 46 x[D] + 8 y[A,Z1] + 10 y[A,Z2]
   + 12 y[A,Z3] + 15 y[A,Z4] + 9 y[A,Z5] + 14 y[A,Z6] + 14 y[B,Z1]
   + 9 y[B,Z2] + 8 y[B,Z3] + 11 y[B,Z4] + 13 y[B,Z5] + 10 y[B,Z6]
   + 11 y[C,Z1] + 13 y[C,Z2] + 14 y[C,Z3] + 9 y[C,Z4] + 8 y[C,Z5]
   + 7 y[C,Z6] + 17 y[D,Z1] + 15 y[D,Z2] + 10 y[D,Z3] + 7 y[D,Z4]
   + 14 y[D,Z5] + 9 y[D,Z6]
Subject To
 aperture: x[A] + x[B] + x[C] + x[D] = 2
 assegnazione[Z1]: y[A,Z1] + y[B,Z1] + y[C,Z1] + y[D,Z1] = 1
 assegnazione[Z2]: y[A,Z2] + y[B,Z2] + y[C,Z2] + y[D,Z2] = 1
 assegnazione[Z3]: y[A,Z3] + y[B,Z3] + y[C,Z3] + y[D,Z3] = 1
 assegnazione[Z4]: y[A,Z4] + y[B,Z4] + y[C,Z4] + y[D,Z4] = 1
 assegnazione[Z5]: y[A,Z5] + y[B,Z5] + y[C,Z5] + y[D,Z5] = 1
 assegnazione[Z6]: y[A,Z6] + y[B,Z6] + y[C,Z6] + y[D,Z6] = 1
 capacita[A]: y[A,Z1] + y[A,Z2] + y[A,Z3] + y[A,Z4] + y[A,Z5] + y[A,Z6]
   <= 2
 capacita[B]: y[B,Z1] + y[B,Z2] + y[B,Z3] + y[B,Z4] + y[B,Z5] + y[B,Z6]
   <= 3
 capacita[C]: y[C,Z1] + y[C,Z2] + y[C,Z3] + y[C,Z4] + y[C,Z5] + y[C,Z6]
   <= 2
 capacita[D]: y[D,Z1] + y[D,Z2] + y[D,Z3] + y[D,Z4] + y[D,Z5] + y[D,Z6]
   <= 3
 collegamento[A,Z1]: - x[A] + y[A,Z1] <= 0
 collegamento[A,Z2]: - x[A] + y[A,Z2] <= 0
 collegamento[A,Z3]: - x[A] + y[A,Z3] <= 0
 collegamento[A,Z4]: - x[A] + y[A,Z4] <= 0
 collegamento[A,Z5]: - x[A] + y[A,Z5] <= 0
 collegamento[A,Z6]: - x[A] + y[A,Z6] <= 0
 collegamento[B,Z1]: - x[B] + y[B,Z1] <= 0
 collegamento[B,Z2]: - x[B] + y[B,Z2] <= 0
 collegamento[B,Z3]: - x[B] + y[B,Z3] <= 0
 collegamento[B,Z4]: - x[B] + y[B,Z4] <= 0
 collegamento[B,Z5]: - x[B] + y[B,Z5] <= 0
 collegamento[B,Z6]: - x[B] + y[B,Z6] <= 0
 collegamento[C,Z1]: - x[C] + y[C,Z1] <= 0
 collegamento[C,Z2]: - x[C] + y[C,Z2] <= 0
 collegamento[C,Z3]: - x[C] + y[C,Z3] <= 0
 collegamento[C,Z4]: - x[C] + y[C,Z4] <= 0
 collegamento[C,Z5]: - x[C] + y[C,Z5] <= 0
 collegamento[C,Z6]: - x[C] + y[C,Z6] <= 0
 collegamento[D,Z1]: - x[D] + y[D,Z1] <= 0
 collegamento[D,Z2]: - x[D] + y[D,Z2] <= 0
 collegamento[D,Z3]: - x[D] + y[D,Z3] <= 0
 collegamento[D,Z4]: - x[D] + y[D,Z4] <= 0
 collegamento[D,Z5]: - x[D] + y[D,Z5] <= 0
 collegamento[D,Z6]: - x[D] + y[D,Z6] <= 0
Bounds
Binaries
 x[A] x[B] x[C] x[D] y[A,Z1] y[A,Z2] y[A,Z3] y[A,Z4] y[A,Z5] y[A,Z6]
 y[B,Z1] y[B,Z2] y[B,Z3] y[B,Z4] y[B,Z5] y[B,Z6] y[C,Z1] y[C,Z2] y[C,Z3]
 y[C,Z4] y[C,Z5] y[C,Z6] y[D,Z1] y[D,Z2] y[D,Z3] y[D,Z4] y[D,Z5] y[D,Z6]
End
