\ Model H07
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x5291e0c67a0064
Minimize
  9 x[C1,A] + 10 x[C1,B] + 11 x[C1,C] + 12 x[C1,E] + 10 x[C1,F] + 12 x[C2,A]
   + 9 x[C2,B] + 10 x[C2,C] + 11 x[C2,D] + 8 x[C2,E] + 11 x[C3,A]
   + 12 x[C3,B] + 9 x[C3,C] + 10 x[C3,D] + 8 x[C3,F] + 120 y[A] + 140 y[B]
   + 100 y[C] + 150 y[D] + 90 y[E] + 110 y[F]
Subject To
 domanda[C1]: x[C1,A] + x[C1,B] + x[C1,C] + x[C1,D] + x[C1,E] + x[C1,F]
   = 80
 domanda[C2]: x[C2,A] + x[C2,B] + x[C2,C] + x[C2,D] + x[C2,E] + x[C2,F]
   = 70
 domanda[C3]: x[C3,A] + x[C3,B] + x[C3,C] + x[C3,D] + x[C3,E] + x[C3,F]
   = 60
 non_fornibile[C1,D]: x[C1,D] = 0
 non_fornibile[C2,F]: x[C2,F] = 0
 non_fornibile[C3,E]: x[C3,E] = 0
 lotto_min[C1,A]: - x[C1,A] + 10 z[C1,A] <= 0
 lotto_min[C1,B]: - x[C1,B] + 10 z[C1,B] <= 0
 lotto_min[C1,C]: - x[C1,C] + 10 z[C1,C] <= 0
 lotto_min[C1,E]: - x[C1,E] + 10 z[C1,E] <= 0
 lotto_min[C1,F]: - x[C1,F] + 10 z[C1,F] <= 0
 lotto_min[C2,A]: - x[C2,A] + 10 z[C2,A] <= 0
 lotto_min[C2,B]: - x[C2,B] + 10 z[C2,B] <= 0
 lotto_min[C2,C]: - x[C2,C] + 10 z[C2,C] <= 0
 lotto_min[C2,D]: - x[C2,D] + 10 z[C2,D] <= 0
 lotto_min[C2,E]: - x[C2,E] + 10 z[C2,E] <= 0
 lotto_min[C3,A]: - x[C3,A] + 10 z[C3,A] <= 0
 lotto_min[C3,B]: - x[C3,B] + 10 z[C3,B] <= 0
 lotto_min[C3,C]: - x[C3,C] + 10 z[C3,C] <= 0
 lotto_min[C3,D]: - x[C3,D] + 10 z[C3,D] <= 0
 lotto_min[C3,F]: - x[C3,F] + 10 z[C3,F] <= 0
 lotto_max[C1,A]: x[C1,A] - 80 z[C1,A] <= 0
 lotto_max[C1,B]: x[C1,B] - 80 z[C1,B] <= 0
 lotto_max[C1,C]: x[C1,C] - 80 z[C1,C] <= 0
 lotto_max[C1,E]: x[C1,E] - 80 z[C1,E] <= 0
 lotto_max[C1,F]: x[C1,F] - 80 z[C1,F] <= 0
 lotto_max[C2,A]: x[C2,A] - 70 z[C2,A] <= 0
 lotto_max[C2,B]: x[C2,B] - 70 z[C2,B] <= 0
 lotto_max[C2,C]: x[C2,C] - 70 z[C2,C] <= 0
 lotto_max[C2,D]: x[C2,D] - 70 z[C2,D] <= 0
 lotto_max[C2,E]: x[C2,E] - 70 z[C2,E] <= 0
 lotto_max[C3,A]: x[C3,A] - 60 z[C3,A] <= 0
 lotto_max[C3,B]: x[C3,B] - 60 z[C3,B] <= 0
 lotto_max[C3,C]: x[C3,C] - 60 z[C3,C] <= 0
 lotto_max[C3,D]: x[C3,D] - 60 z[C3,D] <= 0
 lotto_max[C3,F]: x[C3,F] - 60 z[C3,F] <= 0
 multisourcing[C1]: z[C1,A] + z[C1,B] + z[C1,C] + z[C1,D] + z[C1,E]
   + z[C1,F] >= 2
 multisourcing[C2]: z[C2,A] + z[C2,B] + z[C2,C] + z[C2,D] + z[C2,E]
   + z[C2,F] >= 2
 multisourcing[C3]: z[C3,A] + z[C3,B] + z[C3,C] + z[C3,D] + z[C3,E]
   + z[C3,F] >= 2
 attiva_fornitore[C1,A]: z[C1,A] - y[A] <= 0
 attiva_fornitore[C1,B]: z[C1,B] - y[B] <= 0
 attiva_fornitore[C1,C]: z[C1,C] - y[C] <= 0
 attiva_fornitore[C1,D]: z[C1,D] - y[D] <= 0
 attiva_fornitore[C1,E]: z[C1,E] - y[E] <= 0
 attiva_fornitore[C1,F]: z[C1,F] - y[F] <= 0
 attiva_fornitore[C2,A]: z[C2,A] - y[A] <= 0
 attiva_fornitore[C2,B]: z[C2,B] - y[B] <= 0
 attiva_fornitore[C2,C]: z[C2,C] - y[C] <= 0
 attiva_fornitore[C2,D]: z[C2,D] - y[D] <= 0
 attiva_fornitore[C2,E]: z[C2,E] - y[E] <= 0
 attiva_fornitore[C2,F]: z[C2,F] - y[F] <= 0
 attiva_fornitore[C3,A]: z[C3,A] - y[A] <= 0
 attiva_fornitore[C3,B]: z[C3,B] - y[B] <= 0
 attiva_fornitore[C3,C]: z[C3,C] - y[C] <= 0
 attiva_fornitore[C3,D]: z[C3,D] - y[D] <= 0
 attiva_fornitore[C3,E]: z[C3,E] - y[E] <= 0
 attiva_fornitore[C3,F]: z[C3,F] - y[F] <= 0
 fornitore_usato[A]: - z[C1,A] - z[C2,A] - z[C3,A] + y[A] <= 0
 fornitore_usato[B]: - z[C1,B] - z[C2,B] - z[C3,B] + y[B] <= 0
 fornitore_usato[C]: - z[C1,C] - z[C2,C] - z[C3,C] + y[C] <= 0
 fornitore_usato[D]: - z[C1,D] - z[C2,D] - z[C3,D] + y[D] <= 0
 fornitore_usato[E]: - z[C1,E] - z[C2,E] - z[C3,E] + y[E] <= 0
 fornitore_usato[F]: - z[C1,F] - z[C2,F] - z[C3,F] + y[F] <= 0
 capacita[A]: x[C1,A] + x[C2,A] + x[C3,A] - 100 y[A] <= 0
 capacita[B]: x[C1,B] + x[C2,B] + x[C3,B] - 110 y[B] <= 0
 capacita[C]: x[C1,C] + x[C2,C] + x[C3,C] - 90 y[C] <= 0
 capacita[D]: x[C1,D] + x[C2,D] + x[C3,D] - 120 y[D] <= 0
 capacita[E]: x[C1,E] + x[C2,E] + x[C3,E] - 80 y[E] <= 0
 capacita[F]: x[C1,F] + x[C2,F] + x[C3,F] - 95 y[F] <= 0
 max_fornitori: y[A] + y[B] + y[C] + y[D] + y[E] + y[F] <= 4
 almeno_A_o_B: y[A] + y[B] >= 1
 qualita[C1]: 96 x[C1,A] + 93 x[C1,B] + 98 x[C1,C] + 97 x[C1,E]
   + 94 x[C1,F] >= 7600
 qualita[C2]: 94 x[C2,A] + 97 x[C2,B] + 95 x[C2,C] + 94 x[C2,D]
   + 98 x[C2,E] >= 6650
 qualita[C3]: 95 x[C3,A] + 92 x[C3,B] + 96 x[C3,C] + 93 x[C3,D]
   + 98 x[C3,F] >= 5700
 rischio: 2 x[C1,A] + 3 x[C1,B] + x[C1,C] + 4 x[C1,D] + 2 x[C1,E]
   + 3 x[C1,F] + 2 x[C2,A] + 3 x[C2,B] + x[C2,C] + 4 x[C2,D] + 2 x[C2,E]
   + 3 x[C2,F] + 2 x[C3,A] + 3 x[C3,B] + x[C3,C] + 4 x[C3,D] + 2 x[C3,E]
   + 3 x[C3,F] <= 580
Bounds
Binaries
 z[C1,A] z[C1,B] z[C1,C] z[C1,D] z[C1,E] z[C1,F] z[C2,A] z[C2,B] z[C2,C]
 z[C2,D] z[C2,E] z[C2,F] z[C3,A] z[C3,B] z[C3,C] z[C3,D] z[C3,E] z[C3,F]
 y[A] y[B] y[C] y[D] y[E] y[F]
Generals
 x[C1,A] x[C1,B] x[C1,C] x[C1,D] x[C1,E] x[C1,F] x[C2,A] x[C2,B] x[C2,C]
 x[C2,D] x[C2,E] x[C2,F] x[C3,A] x[C3,B] x[C3,C] x[C3,D] x[C3,E] x[C3,F]
End
