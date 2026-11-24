\ Model H04
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x6d5059c44af0bd65
Minimize
  45 x[Piccolo,R1] + 52 x[Piccolo,R2] + 40 x[Piccolo,R3] + 60 x[Piccolo,R4]
   + 62 x[Medio,R1] + 68 x[Medio,R2] + 58 x[Medio,R3] + 77 x[Medio,R4]
   + 82 x[Grande,R1] + 88 x[Grande,R2] + 79 x[Grande,R3] + 96 x[Grande,R4]
Subject To
 domanda[R1]: 8 x[Piccolo,R1] + 14 x[Medio,R1] + 20 x[Grande,R1] >= 42
 domanda[R2]: 8 x[Piccolo,R2] + 14 x[Medio,R2] + 20 x[Grande,R2] >= 55
 domanda[R3]: 8 x[Piccolo,R3] + 14 x[Medio,R3] + 20 x[Grande,R3] >= 38
 domanda[R4]: 8 x[Piccolo,R4] + 14 x[Medio,R4] + 20 x[Grande,R4] >= 64
 max_due_tipi[R1]: y[Piccolo,R1] + y[Medio,R1] + y[Grande,R1] <= 2
 max_due_tipi[R2]: y[Piccolo,R2] + y[Medio,R2] + y[Grande,R2] <= 2
 max_due_tipi[R3]: y[Piccolo,R3] + y[Medio,R3] + y[Grande,R3] <= 2
 max_due_tipi[R4]: y[Piccolo,R4] + y[Medio,R4] + y[Grande,R4] <= 2
 grande_su_R4: y[Grande,R4] = 1
 disponibilita[Piccolo]: x[Piccolo,R1] + x[Piccolo,R2] + x[Piccolo,R3]
   + x[Piccolo,R4] <= 10
 disponibilita[Medio]: x[Medio,R1] + x[Medio,R2] + x[Medio,R3]
   + x[Medio,R4] <= 9
 disponibilita[Grande]: x[Grande,R1] + x[Grande,R2] + x[Grande,R3]
   + x[Grande,R4] <= 6
 emissioni: 5 x[Piccolo,R1] + 5 x[Piccolo,R2] + 5 x[Piccolo,R3]
   + 5 x[Piccolo,R4] + 8 x[Medio,R1] + 8 x[Medio,R2] + 8 x[Medio,R3]
   + 8 x[Medio,R4] + 11 x[Grande,R1] + 11 x[Grande,R2] + 11 x[Grande,R3]
   + 11 x[Grande,R4] <= 145
 link_inf[Piccolo,R1]: - x[Piccolo,R1] + y[Piccolo,R1] <= 0
 link_inf[Piccolo,R2]: - x[Piccolo,R2] + y[Piccolo,R2] <= 0
 link_inf[Piccolo,R3]: - x[Piccolo,R3] + y[Piccolo,R3] <= 0
 link_inf[Piccolo,R4]: - x[Piccolo,R4] + y[Piccolo,R4] <= 0
 link_inf[Medio,R1]: - x[Medio,R1] + y[Medio,R1] <= 0
 link_inf[Medio,R2]: - x[Medio,R2] + y[Medio,R2] <= 0
 link_inf[Medio,R3]: - x[Medio,R3] + y[Medio,R3] <= 0
 link_inf[Medio,R4]: - x[Medio,R4] + y[Medio,R4] <= 0
 link_inf[Grande,R1]: - x[Grande,R1] + y[Grande,R1] <= 0
 link_inf[Grande,R2]: - x[Grande,R2] + y[Grande,R2] <= 0
 link_inf[Grande,R3]: - x[Grande,R3] + y[Grande,R3] <= 0
 link_inf[Grande,R4]: - x[Grande,R4] + y[Grande,R4] <= 0
 link_sup[Piccolo,R1]: x[Piccolo,R1] - 10 y[Piccolo,R1] <= 0
 link_sup[Piccolo,R2]: x[Piccolo,R2] - 10 y[Piccolo,R2] <= 0
 link_sup[Piccolo,R3]: x[Piccolo,R3] - 10 y[Piccolo,R3] <= 0
 link_sup[Piccolo,R4]: x[Piccolo,R4] - 10 y[Piccolo,R4] <= 0
 link_sup[Medio,R1]: x[Medio,R1] - 9 y[Medio,R1] <= 0
 link_sup[Medio,R2]: x[Medio,R2] - 9 y[Medio,R2] <= 0
 link_sup[Medio,R3]: x[Medio,R3] - 9 y[Medio,R3] <= 0
 link_sup[Medio,R4]: x[Medio,R4] - 9 y[Medio,R4] <= 0
 link_sup[Grande,R1]: x[Grande,R1] - 6 y[Grande,R1] <= 0
 link_sup[Grande,R2]: x[Grande,R2] - 6 y[Grande,R2] <= 0
 link_sup[Grande,R3]: x[Grande,R3] - 6 y[Grande,R3] <= 0
 link_sup[Grande,R4]: x[Grande,R4] - 6 y[Grande,R4] <= 0
Bounds
Binaries
 y[Piccolo,R1] y[Piccolo,R2] y[Piccolo,R3] y[Piccolo,R4] y[Medio,R1]
 y[Medio,R2] y[Medio,R3] y[Medio,R4] y[Grande,R1] y[Grande,R2] y[Grande,R3]
 y[Grande,R4]
Generals
 x[Piccolo,R1] x[Piccolo,R2] x[Piccolo,R3] x[Piccolo,R4] x[Medio,R1]
 x[Medio,R2] x[Medio,R3] x[Medio,R4] x[Grande,R1] x[Grande,R2] x[Grande,R3]
 x[Grande,R4]
End
