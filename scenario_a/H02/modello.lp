\ Model H02
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x9ff4d064e33724d6
Minimize
  9 x[A,1] + 11 x[A,2] + 10 x[A,3] + 12 x[A,4] + 8 x[B,1] + 9 x[B,2]
   + 11 x[B,3] + 10 x[B,4] + 13 x[C,1] + 12 x[C,2] + 14 x[C,3] + 11 x[C,4]
   + 2 y[A,1] + 2 y[A,2] + 2 y[A,3] + 2 y[A,4] + 3 y[B,1] + 3 y[B,2]
   + 3 y[B,3] + 3 y[B,4] + 2 y[C,1] + 2 y[C,2] + 2 y[C,3] + 2 y[C,4]
   + 45 delta[A,1] + 45 delta[A,2] + 45 delta[A,3] + 45 delta[A,4]
   + 40 delta[B,1] + 40 delta[B,2] + 40 delta[B,3] + 40 delta[B,4]
   + 50 delta[C,1] + 50 delta[C,2] + 50 delta[C,3] + 50 delta[C,4]
Subject To
 bilancio[A,1]: x[A,1] + y[A,0] - y[A,1] = 8
 bilancio[A,2]: x[A,2] + y[A,1] - y[A,2] = 12
 bilancio[A,3]: x[A,3] + y[A,2] - y[A,3] = 10
 bilancio[A,4]: x[A,4] + y[A,3] - y[A,4] = 14
 bilancio[B,1]: x[B,1] + y[B,0] - y[B,1] = 10
 bilancio[B,2]: x[B,2] + y[B,1] - y[B,2] = 8
 bilancio[B,3]: x[B,3] + y[B,2] - y[B,3] = 14
 bilancio[B,4]: x[B,4] + y[B,3] - y[B,4] = 12
 bilancio[C,1]: x[C,1] + y[C,0] - y[C,1] = 6
 bilancio[C,2]: x[C,2] + y[C,1] - y[C,2] = 9
 bilancio[C,3]: x[C,3] + y[C,2] - y[C,3] = 7
 bilancio[C,4]: x[C,4] + y[C,3] - y[C,4] = 11
 scorta_max[1]: y[A,1] + y[B,1] + y[C,1] <= 20
 scorta_max[2]: y[A,2] + y[B,2] + y[C,2] <= 20
 scorta_max[3]: y[A,3] + y[B,3] + y[C,3] <= 20
 scorta_max[4]: y[A,4] + y[B,4] + y[C,4] <= 20
 scorta_iniz_A: y[A,0] = 0
 scorta_iniz_B: y[B,0] = 0
 scorta_iniz_C: y[C,0] = 6
 max_due_setup[1]: delta[A,1] + delta[B,1] + delta[C,1] <= 2
 max_due_setup[2]: delta[A,2] + delta[B,2] + delta[C,2] <= 2
 max_due_setup[3]: delta[A,3] + delta[B,3] + delta[C,3] <= 2
 max_due_setup[4]: delta[A,4] + delta[B,4] + delta[C,4] <= 2
 scorta_fin_A: y[A,4] = 0
 scorta_fin_B: y[B,4] = 0
 scorta_fin_C: y[C,4] = 0
 capacita[1]: 2 x[A,1] + 3 x[B,1] + 4 x[C,1] <= 90
 capacita[2]: 2 x[A,2] + 3 x[B,2] + 4 x[C,2] <= 95
 capacita[3]: 2 x[A,3] + 3 x[B,3] + 4 x[C,3] <= 90
 capacita[4]: 2 x[A,4] + 3 x[B,4] + 4 x[C,4] <= 100
 lotto_min[A,1]: x[A,1] - 4 delta[A,1] >= 0
 lotto_min[A,2]: x[A,2] - 4 delta[A,2] >= 0
 lotto_min[A,3]: x[A,3] - 4 delta[A,3] >= 0
 lotto_min[A,4]: x[A,4] - 4 delta[A,4] >= 0
 lotto_min[B,1]: x[B,1] - 4 delta[B,1] >= 0
 lotto_min[B,2]: x[B,2] - 4 delta[B,2] >= 0
 lotto_min[B,3]: x[B,3] - 4 delta[B,3] >= 0
 lotto_min[B,4]: x[B,4] - 4 delta[B,4] >= 0
 lotto_min[C,1]: x[C,1] - 3 delta[C,1] >= 0
 lotto_min[C,2]: x[C,2] - 3 delta[C,2] >= 0
 lotto_min[C,3]: x[C,3] - 3 delta[C,3] >= 0
 lotto_min[C,4]: x[C,4] - 3 delta[C,4] >= 0
 lotto_max[A,1]: x[A,1] - 45 delta[A,1] <= 0
 lotto_max[A,2]: x[A,2] - 47 delta[A,2] <= 0
 lotto_max[A,3]: x[A,3] - 45 delta[A,3] <= 0
 lotto_max[A,4]: x[A,4] - 50 delta[A,4] <= 0
 lotto_max[B,1]: x[B,1] - 30 delta[B,1] <= 0
 lotto_max[B,2]: x[B,2] - 31 delta[B,2] <= 0
 lotto_max[B,3]: x[B,3] - 30 delta[B,3] <= 0
 lotto_max[B,4]: x[B,4] - 33 delta[B,4] <= 0
 lotto_max[C,1]: x[C,1] - 22 delta[C,1] <= 0
 lotto_max[C,2]: x[C,2] - 23 delta[C,2] <= 0
 lotto_max[C,3]: x[C,3] - 22 delta[C,3] <= 0
 lotto_max[C,4]: x[C,4] - 25 delta[C,4] <= 0
Bounds
Binaries
 delta[A,1] delta[A,2] delta[A,3] delta[A,4] delta[B,1] delta[B,2]
 delta[B,3] delta[B,4] delta[C,1] delta[C,2] delta[C,3] delta[C,4]
Generals
 x[A,1] x[A,2] x[A,3] x[A,4] x[B,1] x[B,2] x[B,3] x[B,4] x[C,1] x[C,2]
 x[C,3] x[C,4] y[A,0] y[A,1] y[A,2] y[A,3] y[A,4] y[B,0] y[B,1] y[B,2]
 y[B,3] y[B,4] y[C,0] y[C,1] y[C,2] y[C,3] y[C,4]
End
