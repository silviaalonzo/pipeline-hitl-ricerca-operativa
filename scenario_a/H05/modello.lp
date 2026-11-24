\ Model H05
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x81bef63a837cb884
Maximize
  42 x[A] + 35 x[B] + 48 x[C] + 31 x[D] + 40 x[E] + 28 x[F] + 55 x[G]
   + 37 x[H] + 33 x[I] + 50 x[J] + 46 x[K] + 29 x[L] + 12 z_AC + 10 z_EK
Subject To
 budget_A1: 18 x[A] + 20 x[B] + 25 x[C] + 15 x[D] + 22 x[E] + 14 x[F]
   + 30 x[G] + 20 x[H] + 17 x[I] + 27 x[J] + 24 x[K] + 16 x[L] <= 110
 budget_A2: 12 x[A] + 18 x[B] + 20 x[C] + 14 x[D] + 16 x[E] + 12 x[F]
   + 25 x[G] + 18 x[H] + 15 x[I] + 21 x[J] + 19 x[K] + 13 x[L] <= 100
 budget_A3: 10 x[A] + 14 x[B] + 18 x[C] + 12 x[D] + 15 x[E] + 10 x[F]
   + 22 x[G] + 16 x[H] + 12 x[I] + 18 x[J] + 17 x[K] + 11 x[L] <= 90
 personale: 4 x[A] + 4 x[B] + 5 x[C] + 3 x[D] + 4 x[E] + 3 x[F] + 6 x[G]
   + 4 x[H] + 3 x[I] + 5 x[J] + 5 x[K] + 3 x[L] <= 28
 rischio: 5 x[A] + 4 x[B] + 6 x[C] + 3 x[D] + 4 x[E] + 2 x[F] + 7 x[G]
   + 5 x[H] + 3 x[I] + 6 x[J] + 5 x[K] + 3 x[L] <= 32
 prereq_G_B: - x[B] + x[G] <= 0
 prereq_J_E: - x[E] + x[J] <= 0
 prereq_K_C: - x[C] + x[K] <= 0
 incomp_D_H: x[D] + x[H] <= 1
 incomp_F_L: x[F] + x[L] <= 1
 digitali: x[A] + x[C] + x[G] + x[J] >= 2
 sostenibili: x[E] + x[H] + x[K] >= 1
 max_progetti: x[A] + x[B] + x[C] + x[D] + x[E] + x[F] + x[G] + x[H] + x[I]
   + x[J] + x[K] + x[L] <= 8
 sin_AC_1: - x[A] + z_AC <= 0
 sin_AC_2: - x[C] + z_AC <= 0
 sin_AC_3: - x[A] - x[C] + z_AC >= -1
 sin_EK_1: - x[E] + z_EK <= 0
 sin_EK_2: - x[K] + z_EK <= 0
 sin_EK_3: - x[E] - x[K] + z_EK >= -1
Bounds
Binaries
 x[A] x[B] x[C] x[D] x[E] x[F] x[G] x[H] x[I] x[J] x[K] x[L] z_AC z_EK
End
