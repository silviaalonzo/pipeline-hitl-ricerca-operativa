\ Model H06
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xe53bb4423da5e0b6
Minimize
  4 T[J1] + 3 T[J2] + 5 T[J3] + 2 T[J4] + 6 T[J5] + 2 T[J6] + 4 T[J7]
Subject To
 fine[J1]: - S[J1] + C[J1] = 5
 fine[J2]: - S[J2] + C[J2] = 7
 fine[J3]: - S[J3] + C[J3] = 4
 fine[J4]: - S[J4] + C[J4] = 6
 fine[J5]: - S[J5] + C[J5] = 3
 fine[J6]: - S[J6] + C[J6] = 8
 fine[J7]: - S[J7] + C[J7] = 5
 disponibilita[J1]: S[J1] >= 0
 disponibilita[J2]: S[J2] >= 0
 disponibilita[J3]: S[J3] >= 2
 disponibilita[J4]: S[J4] >= 3
 disponibilita[J5]: S[J5] >= 5
 disponibilita[J6]: S[J6] >= 0
 disponibilita[J7]: S[J7] >= 6
 nosovr_1[J1,J2]: S[J1] - S[J2] + 44 y[J1,J2] <= 39
 nosovr_1[J1,J3]: S[J1] - S[J3] + 44 y[J1,J3] <= 39
 nosovr_1[J1,J4]: S[J1] - S[J4] + 44 y[J1,J4] <= 39
 nosovr_1[J1,J5]: S[J1] - S[J5] + 44 y[J1,J5] <= 39
 nosovr_1[J1,J6]: S[J1] - S[J6] + 44 y[J1,J6] <= 39
 nosovr_1[J1,J7]: S[J1] - S[J7] + 44 y[J1,J7] <= 39
 nosovr_1[J2,J3]: S[J2] - S[J3] + 44 y[J2,J3] <= 37
 nosovr_1[J2,J4]: S[J2] - S[J4] + 44 y[J2,J4] <= 37
 nosovr_1[J2,J5]: S[J2] - S[J5] + 44 y[J2,J5] <= 37
 nosovr_1[J2,J6]: S[J2] - S[J6] + 44 y[J2,J6] <= 37
 nosovr_1[J2,J7]: S[J2] - S[J7] + 44 y[J2,J7] <= 37
 nosovr_1[J3,J4]: S[J3] - S[J4] + 44 y[J3,J4] <= 40
 nosovr_1[J3,J5]: S[J3] - S[J5] + 44 y[J3,J5] <= 40
 nosovr_1[J3,J6]: S[J3] - S[J6] + 44 y[J3,J6] <= 40
 nosovr_1[J3,J7]: S[J3] - S[J7] + 44 y[J3,J7] <= 40
 nosovr_1[J4,J5]: S[J4] - S[J5] + 44 y[J4,J5] <= 38
 nosovr_1[J4,J6]: S[J4] - S[J6] + 44 y[J4,J6] <= 38
 nosovr_1[J4,J7]: S[J4] - S[J7] + 44 y[J4,J7] <= 38
 nosovr_1[J5,J6]: S[J5] - S[J6] + 44 y[J5,J6] <= 41
 nosovr_1[J5,J7]: S[J5] - S[J7] + 44 y[J5,J7] <= 41
 nosovr_1[J6,J7]: S[J6] - S[J7] + 44 y[J6,J7] <= 36
 nosovr_2[J1,J2]: - S[J1] + S[J2] - 44 y[J1,J2] <= -7
 nosovr_2[J1,J3]: - S[J1] + S[J3] - 44 y[J1,J3] <= -4
 nosovr_2[J1,J4]: - S[J1] + S[J4] - 44 y[J1,J4] <= -6
 nosovr_2[J1,J5]: - S[J1] + S[J5] - 44 y[J1,J5] <= -3
 nosovr_2[J1,J6]: - S[J1] + S[J6] - 44 y[J1,J6] <= -8
 nosovr_2[J1,J7]: - S[J1] + S[J7] - 44 y[J1,J7] <= -5
 nosovr_2[J2,J3]: - S[J2] + S[J3] - 44 y[J2,J3] <= -4
 nosovr_2[J2,J4]: - S[J2] + S[J4] - 44 y[J2,J4] <= -6
 nosovr_2[J2,J5]: - S[J2] + S[J5] - 44 y[J2,J5] <= -3
 nosovr_2[J2,J6]: - S[J2] + S[J6] - 44 y[J2,J6] <= -8
 nosovr_2[J2,J7]: - S[J2] + S[J7] - 44 y[J2,J7] <= -5
 nosovr_2[J3,J4]: - S[J3] + S[J4] - 44 y[J3,J4] <= -6
 nosovr_2[J3,J5]: - S[J3] + S[J5] - 44 y[J3,J5] <= -3
 nosovr_2[J3,J6]: - S[J3] + S[J6] - 44 y[J3,J6] <= -8
 nosovr_2[J3,J7]: - S[J3] + S[J7] - 44 y[J3,J7] <= -5
 nosovr_2[J4,J5]: - S[J4] + S[J5] - 44 y[J4,J5] <= -3
 nosovr_2[J4,J6]: - S[J4] + S[J6] - 44 y[J4,J6] <= -8
 nosovr_2[J4,J7]: - S[J4] + S[J7] - 44 y[J4,J7] <= -5
 nosovr_2[J5,J6]: - S[J5] + S[J6] - 44 y[J5,J6] <= -8
 nosovr_2[J5,J7]: - S[J5] + S[J7] - 44 y[J5,J7] <= -5
 nosovr_2[J6,J7]: - S[J6] + S[J7] - 44 y[J6,J7] <= -5
 prec_J1_J2: - S[J2] + C[J1] <= 0
 prec_J3_J5: - S[J5] + C[J3] <= 0
 ritardo[J1]: - C[J1] + T[J1] >= -9
 ritardo[J2]: - C[J2] + T[J2] >= -17
 ritardo[J3]: - C[J3] + T[J3] >= -12
 ritardo[J4]: - C[J4] + T[J4] >= -22
 ritardo[J5]: - C[J5] + T[J5] >= -15
 ritardo[J6]: - C[J6] + T[J6] >= -28
 ritardo[J7]: - C[J7] + T[J7] >= -25
 ritardo_nonneg[J1]: T[J1] >= 0
 ritardo_nonneg[J2]: T[J2] >= 0
 ritardo_nonneg[J3]: T[J3] >= 0
 ritardo_nonneg[J4]: T[J4] >= 0
 ritardo_nonneg[J5]: T[J5] >= 0
 ritardo_nonneg[J6]: T[J6] >= 0
 ritardo_nonneg[J7]: T[J7] >= 0
Bounds
Binaries
 y[J1,J2] y[J1,J3] y[J1,J4] y[J1,J5] y[J1,J6] y[J1,J7] y[J2,J3] y[J2,J4]
 y[J2,J5] y[J2,J6] y[J2,J7] y[J3,J4] y[J3,J5] y[J3,J6] y[J3,J7] y[J4,J5]
 y[J4,J6] y[J4,J7] y[J5,J6] y[J5,J7] y[J6,J7]
Generals
 S[J1] S[J2] S[J3] S[J4] S[J5] S[J6] S[J7] C[J1] C[J2] C[J3] C[J4] C[J5]
 C[J6] C[J7] T[J1] T[J2] T[J3] T[J4] T[J5] T[J6] T[J7]
End
