\ Model H09
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xacbf160701d1a13e
Minimize
  7 x[A,1] + 8 x[A,2] + 9 x[A,3] + 7 x[A,4] + 10 x[A,5] + 8 x[A,6]
   + 9 x[B,1] + 8 x[B,2] + 8 x[B,3] + 10 x[B,4] + 7 x[B,5] + 9 x[B,6]
   + 11 x[C,1] + 10 x[C,2] + 12 x[C,3] + 9 x[C,4] + 11 x[C,5] + 8 x[C,6]
   + 2 s[A,1] + 2 s[A,2] + 2 s[A,3] + 2 s[A,4] + 2 s[A,5] + 2 s[A,6]
   + 2 s[B,1] + 2 s[B,2] + 2 s[B,3] + 2 s[B,4] + 2 s[B,5] + 2 s[B,6]
   + 3 s[C,1] + 3 s[C,2] + 3 s[C,3] + 3 s[C,4] + 3 s[C,5] + 3 s[C,6]
   + 35 y[A,1] + 35 y[A,2] + 35 y[A,3] + 35 y[A,4] + 35 y[A,5] + 35 y[A,6]
   + 40 y[B,1] + 40 y[B,2] + 40 y[B,3] + 40 y[B,4] + 40 y[B,5] + 40 y[B,6]
   + 45 y[C,1] + 45 y[C,2] + 45 y[C,3] + 45 y[C,4] + 45 y[C,5] + 45 y[C,6]
   + 18 o[1] + 18 o[2] + 18 o[3] + 18 o[4] + 18 o[5] + 18 o[6]
Subject To
 bilancio[A,1]: x[A,1] - s[A,1] = 12
 bilancio[A,2]: x[A,2] + s[A,1] - s[A,2] = 18
 bilancio[A,3]: x[A,3] + s[A,2] - s[A,3] = 14
 bilancio[A,4]: x[A,4] + s[A,3] - s[A,4] = 20
 bilancio[A,5]: x[A,5] + s[A,4] - s[A,5] = 16
 bilancio[A,6]: x[A,6] + s[A,5] - s[A,6] = 19
 bilancio[B,1]: x[B,1] - s[B,1] = 10
 bilancio[B,2]: x[B,2] + s[B,1] - s[B,2] = 9
 bilancio[B,3]: x[B,3] + s[B,2] - s[B,3] = 15
 bilancio[B,4]: x[B,4] + s[B,3] - s[B,4] = 12
 bilancio[B,5]: x[B,5] + s[B,4] - s[B,5] = 17
 bilancio[B,6]: x[B,6] + s[B,5] - s[B,6] = 14
 bilancio[C,1]: x[C,1] - s[C,1] = 8
 bilancio[C,2]: x[C,2] + s[C,1] - s[C,2] = 11
 bilancio[C,3]: x[C,3] + s[C,2] - s[C,3] = 10
 bilancio[C,4]: x[C,4] + s[C,3] - s[C,4] = 13
 bilancio[C,5]: x[C,5] + s[C,4] - s[C,5] = 9
 bilancio[C,6]: x[C,6] + s[C,5] - s[C,6] = 15
 capacita[1]: 2 x[A,1] + 3 x[B,1] + 4 x[C,1] - o[1] <= 120
 capacita[2]: 2 x[A,2] + 3 x[B,2] + 4 x[C,2] - o[2] <= 115
 capacita[3]: 2 x[A,3] + 3 x[B,3] + 4 x[C,3] - o[3] <= 125
 capacita[4]: 2 x[A,4] + 3 x[B,4] + 4 x[C,4] - o[4] <= 110
 capacita[5]: 2 x[A,5] + 3 x[B,5] + 4 x[C,5] - o[5] <= 120
 capacita[6]: 2 x[A,6] + 3 x[B,6] + 4 x[C,6] - o[6] <= 115
 lotto_min[A,1]: - x[A,1] + 5 y[A,1] <= 0
 lotto_min[A,2]: - x[A,2] + 5 y[A,2] <= 0
 lotto_min[A,3]: - x[A,3] + 5 y[A,3] <= 0
 lotto_min[A,4]: - x[A,4] + 5 y[A,4] <= 0
 lotto_min[A,5]: - x[A,5] + 5 y[A,5] <= 0
 lotto_min[A,6]: - x[A,6] + 5 y[A,6] <= 0
 lotto_min[B,1]: - x[B,1] + 4 y[B,1] <= 0
 lotto_min[B,2]: - x[B,2] + 4 y[B,2] <= 0
 lotto_min[B,3]: - x[B,3] + 4 y[B,3] <= 0
 lotto_min[B,4]: - x[B,4] + 4 y[B,4] <= 0
 lotto_min[B,5]: - x[B,5] + 4 y[B,5] <= 0
 lotto_min[B,6]: - x[B,6] + 4 y[B,6] <= 0
 lotto_min[C,1]: - x[C,1] + 3 y[C,1] <= 0
 lotto_min[C,2]: - x[C,2] + 3 y[C,2] <= 0
 lotto_min[C,3]: - x[C,3] + 3 y[C,3] <= 0
 lotto_min[C,4]: - x[C,4] + 3 y[C,4] <= 0
 lotto_min[C,5]: - x[C,5] + 3 y[C,5] <= 0
 lotto_min[C,6]: - x[C,6] + 3 y[C,6] <= 0
 lotto_max[A,1]: x[A,1] - 70 y[A,1] <= 0
 lotto_max[A,2]: x[A,2] - 67 y[A,2] <= 0
 lotto_max[A,3]: x[A,3] - 72 y[A,3] <= 0
 lotto_max[A,4]: x[A,4] - 65 y[A,4] <= 0
 lotto_max[A,5]: x[A,5] - 70 y[A,5] <= 0
 lotto_max[A,6]: x[A,6] - 67 y[A,6] <= 0
 lotto_max[B,1]: x[B,1] - 46 y[B,1] <= 0
 lotto_max[B,2]: x[B,2] - 45 y[B,2] <= 0
 lotto_max[B,3]: x[B,3] - 48 y[B,3] <= 0
 lotto_max[B,4]: x[B,4] - 43 y[B,4] <= 0
 lotto_max[B,5]: x[B,5] - 46 y[B,5] <= 0
 lotto_max[B,6]: x[B,6] - 45 y[B,6] <= 0
 lotto_max[C,1]: x[C,1] - 35 y[C,1] <= 0
 lotto_max[C,2]: x[C,2] - 33 y[C,2] <= 0
 lotto_max[C,3]: x[C,3] - 36 y[C,3] <= 0
 lotto_max[C,4]: x[C,4] - 32 y[C,4] <= 0
 lotto_max[C,5]: x[C,5] - 35 y[C,5] <= 0
 lotto_max[C,6]: x[C,6] - 33 y[C,6] <= 0
 attivazioni_t1: y[A,1] + y[B,1] + y[C,1] <= 3
 attivazioni[2]: y[A,2] + y[B,2] + y[C,2] <= 2
 attivazioni[3]: y[A,3] + y[B,3] + y[C,3] <= 2
 attivazioni[4]: y[A,4] + y[B,4] + y[C,4] <= 2
 attivazioni[5]: y[A,5] + y[B,5] + y[C,5] <= 2
 attivazioni[6]: y[A,6] + y[B,6] + y[C,6] <= 2
 scorta_totale[1]: s[A,1] + s[B,1] + s[C,1] <= 40
 scorta_totale[2]: s[A,2] + s[B,2] + s[C,2] <= 40
 scorta_totale[3]: s[A,3] + s[B,3] + s[C,3] <= 40
 scorta_totale[4]: s[A,4] + s[B,4] + s[C,4] <= 40
 scorta_totale[5]: s[A,5] + s[B,5] + s[C,5] <= 40
 scorta_totale[6]: s[A,6] + s[B,6] + s[C,6] <= 40
 scorta_finale[A]: s[A,6] >= 2
 scorta_finale[B]: s[B,6] >= 2
 scorta_finale[C]: s[C,6] >= 2
Bounds
 o[1] <= 20
 o[2] <= 20
 o[3] <= 20
 o[4] <= 20
 o[5] <= 20
 o[6] <= 20
Binaries
 y[A,1] y[A,2] y[A,3] y[A,4] y[A,5] y[A,6] y[B,1] y[B,2] y[B,3] y[B,4]
 y[B,5] y[B,6] y[C,1] y[C,2] y[C,3] y[C,4] y[C,5] y[C,6]
Generals
 x[A,1] x[A,2] x[A,3] x[A,4] x[A,5] x[A,6] x[B,1] x[B,2] x[B,3] x[B,4]
 x[B,5] x[B,6] x[C,1] x[C,2] x[C,3] x[C,4] x[C,5] x[C,6] s[A,1] s[A,2]
 s[A,3] s[A,4] s[A,5] s[A,6] s[B,1] s[B,2] s[B,3] s[B,4] s[B,5] s[B,6]
 s[C,1] s[C,2] s[C,3] s[C,4] s[C,5] s[C,6]
End
