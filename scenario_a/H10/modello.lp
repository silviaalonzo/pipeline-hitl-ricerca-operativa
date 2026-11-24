\ Model H10
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x607daeaa4e8dc6df
Minimize
  2 x[SA,K1] + 3 x[SA,K2] + 3 x[SB,K1] + 2 x[SB,K2] + x[AB,K1] + 2 x[AB,K2]
   + 2 x[AC,K1] + 3 x[AC,K2] + 2 x[BC,K1] + x[BC,K2] + 3 x[BD,K1]
   + 2 x[BD,K2] + x[CD,K1] + 2 x[CD,K2] + 3 x[CT,K1] + 2 x[CT,K2]
   + 2 x[DT,K1] + 3 x[DT,K2] + 55 y[SA] + 50 y[SB] + 18 y[AB] + 38 y[AC]
   + 22 y[BC] + 35 y[BD] + 20 y[CD] + 48 y[CT] + 44 y[DT]
Subject To
 origine[K1]: x[SA,K1] + x[SB,K1] = 28
 origine[K2]: x[SA,K2] + x[SB,K2] = 22
 nodo_A[K1]: x[SA,K1] - x[AB,K1] - x[AC,K1] = 0
 nodo_A[K2]: x[SA,K2] - x[AB,K2] - x[AC,K2] = 0
 nodo_B[K1]: x[SB,K1] + x[AB,K1] - x[BC,K1] - x[BD,K1] = 0
 nodo_B[K2]: x[SB,K2] + x[AB,K2] - x[BC,K2] - x[BD,K2] = 0
 nodo_C[K1]: x[AC,K1] + x[BC,K1] - x[CD,K1] - x[CT,K1] = 0
 nodo_C[K2]: x[AC,K2] + x[BC,K2] - x[CD,K2] - x[CT,K2] = 0
 nodo_D[K1]: x[BD,K1] + x[CD,K1] - x[DT,K1] = 0
 nodo_D[K2]: x[BD,K2] + x[CD,K2] - x[DT,K2] = 0
 destinazione[K1]: x[CT,K1] + x[DT,K1] = 28
 destinazione[K2]: x[CT,K2] + x[DT,K2] = 22
 capacita[SA]: x[SA,K1] + x[SA,K2] - 35 y[SA] <= 0
 capacita[SB]: x[SB,K1] + x[SB,K2] - 35 y[SB] <= 0
 capacita[AB]: x[AB,K1] + x[AB,K2] - 15 y[AB] <= 0
 capacita[AC]: x[AC,K1] + x[AC,K2] - 30 y[AC] <= 0
 capacita[BC]: x[BC,K1] + x[BC,K2] - 25 y[BC] <= 0
 capacita[BD]: x[BD,K1] + x[BD,K2] - 25 y[BD] <= 0
 capacita[CD]: x[CD,K1] + x[CD,K2] - 20 y[CD] <= 0
 capacita[CT]: x[CT,K1] + x[CT,K2] - 35 y[CT] <= 0
 capacita[DT]: x[DT,K1] + x[DT,K2] - 35 y[DT] <= 0
 resilienza_SA: y[SA] = 1
 resilienza_SB: y[SB] = 1
 max_archi: y[SA] + y[SB] + y[AB] + y[AC] + y[BC] + y[BD] + y[CD] + y[CT]
   + y[DT] <= 7
Bounds
Binaries
 y[SA] y[SB] y[AB] y[AC] y[BC] y[BD] y[CD] y[CT] y[DT]
Generals
 x[SA,K1] x[SA,K2] x[SB,K1] x[SB,K2] x[AB,K1] x[AB,K2] x[AC,K1] x[AC,K2]
 x[BC,K1] x[BC,K2] x[BD,K1] x[BD,K2] x[CD,K1] x[CD,K2] x[CT,K1] x[CT,K2]
 x[DT,K1] x[DT,K2]
End
