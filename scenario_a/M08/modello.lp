\ Model M08_copertura_zone
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x7720c9abd3e7e331
Minimize
  24 y[A] + 20 y[B] + 27 y[C] + 22 y[D] + 25 y[E] + 19 y[F] + 23 y[G]
   + 21 y[H]
Subject To
 copertura_Z1: y[A] + y[C] >= 1
 copertura_Z2: y[A] + y[B] >= 1
 copertura_Z3: y[A] + y[B] + y[D] >= 2
 copertura_Z4: y[B] + y[E] >= 1
 copertura_Z5: y[B] + y[C] + y[F] >= 1
 copertura_Z6: y[C] + y[D] + y[G] >= 1
 copertura_Z7: y[D] + y[E] + y[H] >= 2
 copertura_Z8: y[E] + y[F] + y[H] >= 1
 copertura_Z9: y[F] + y[G] >= 1
 copertura_Z10: y[G] + y[H] >= 1
 numero_centri: y[A] + y[B] + y[C] + y[D] + y[E] + y[F] + y[G] + y[H] <= 5
Bounds
Binaries
 y[A] y[B] y[C] y[D] y[E] y[F] y[G] y[H]
End
