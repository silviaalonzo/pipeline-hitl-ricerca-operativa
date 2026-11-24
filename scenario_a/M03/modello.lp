\ Model M03_assegnazione_personale_turni
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0x5cc45949e9276c60
Minimize
  8 x[Ana,M1] + 7 x[Ana,M2] + 9 x[Ana,P1] + 8 x[Ana,P2] + 7 x[Bruno,M1]
   + 8 x[Bruno,M2] + 8 x[Bruno,P1] + 9 x[Bruno,P2] + 9 x[Carla,M2]
   + 8 x[Carla,P1] + 8 x[Carla,P2] + 11 x[Carla,N1] + 12 x[Carla,N2]
   + 10 x[Diego,M1] + 9 x[Diego,P1] + 8 x[Diego,P2] + 10 x[Diego,N1]
   + 11 x[Diego,N2] + 8 x[Elena,M1] + 10 x[Elena,M2] + 9 x[Elena,P1]
   + 9 x[Elena,P2] + 12 x[Elena,N1] + 10 x[Elena,N2] + 9 x[Fabio,M1]
   + 8 x[Fabio,M2] + 10 x[Fabio,P1] + 7 x[Fabio,P2]
Subject To
 max_due_turni[Ana]: x[Ana,M1] + x[Ana,M2] + x[Ana,P1] + x[Ana,P2]
   + x[Ana,N1] + x[Ana,N2] <= 2
 max_due_turni[Bruno]: x[Bruno,M1] + x[Bruno,M2] + x[Bruno,P1]
   + x[Bruno,P2] + x[Bruno,N1] + x[Bruno,N2] <= 2
 max_due_turni[Carla]: x[Carla,M1] + x[Carla,M2] + x[Carla,P1]
   + x[Carla,P2] + x[Carla,N1] + x[Carla,N2] <= 2
 max_due_turni[Diego]: x[Diego,M1] + x[Diego,M2] + x[Diego,P1]
   + x[Diego,P2] + x[Diego,N1] + x[Diego,N2] <= 2
 max_due_turni[Elena]: x[Elena,M1] + x[Elena,M2] + x[Elena,P1]
   + x[Elena,P2] + x[Elena,N1] + x[Elena,N2] <= 2
 max_due_turni[Fabio]: x[Fabio,M1] + x[Fabio,M2] + x[Fabio,P1]
   + x[Fabio,P2] + x[Fabio,N1] + x[Fabio,N2] <= 2
 max_un_notturno[Ana]: x[Ana,N1] + x[Ana,N2] <= 1
 max_un_notturno[Bruno]: x[Bruno,N1] + x[Bruno,N2] <= 1
 max_un_notturno[Carla]: x[Carla,N1] + x[Carla,N2] <= 1
 max_un_notturno[Diego]: x[Diego,N1] + x[Diego,N2] <= 1
 max_un_notturno[Elena]: x[Elena,N1] + x[Elena,N2] <= 1
 max_un_notturno[Fabio]: x[Fabio,N1] + x[Fabio,N2] <= 1
 copertura[M1]: x[Ana,M1] + x[Bruno,M1] + x[Carla,M1] + x[Diego,M1]
   + x[Elena,M1] + x[Fabio,M1] = 1
 copertura[M2]: x[Ana,M2] + x[Bruno,M2] + x[Carla,M2] + x[Diego,M2]
   + x[Elena,M2] + x[Fabio,M2] = 1
 copertura[P1]: x[Ana,P1] + x[Bruno,P1] + x[Carla,P1] + x[Diego,P1]
   + x[Elena,P1] + x[Fabio,P1] = 1
 copertura[P2]: x[Ana,P2] + x[Bruno,P2] + x[Carla,P2] + x[Diego,P2]
   + x[Elena,P2] + x[Fabio,P2] = 1
 copertura[N1]: x[Ana,N1] + x[Bruno,N1] + x[Carla,N1] + x[Diego,N1]
   + x[Elena,N1] + x[Fabio,N1] = 1
 copertura[N2]: x[Ana,N2] + x[Bruno,N2] + x[Carla,N2] + x[Diego,N2]
   + x[Elena,N2] + x[Fabio,N2] = 1
 indisponibilita_Ana_N1: x[Ana,N1] = 0
 indisponibilita_Ana_N2: x[Ana,N2] = 0
 indisponibilita_Bruno_N1: x[Bruno,N1] = 0
 indisponibilita_Bruno_N2: x[Bruno,N2] = 0
 indisponibilita_Carla_M1: x[Carla,M1] = 0
 indisponibilita_Diego_M2: x[Diego,M2] = 0
 indisponibilita_Fabio_N1: x[Fabio,N1] = 0
 indisponibilita_Fabio_N2: x[Fabio,N2] = 0
Bounds
Binaries
 x[Ana,M1] x[Ana,M2] x[Ana,P1] x[Ana,P2] x[Ana,N1] x[Ana,N2] x[Bruno,M1]
 x[Bruno,M2] x[Bruno,P1] x[Bruno,P2] x[Bruno,N1] x[Bruno,N2] x[Carla,M1]
 x[Carla,M2] x[Carla,P1] x[Carla,P2] x[Carla,N1] x[Carla,N2] x[Diego,M1]
 x[Diego,M2] x[Diego,P1] x[Diego,P2] x[Diego,N1] x[Diego,N2] x[Elena,M1]
 x[Elena,M2] x[Elena,P1] x[Elena,P2] x[Elena,N1] x[Elena,N2] x[Fabio,M1]
 x[Fabio,M2] x[Fabio,P1] x[Fabio,P2] x[Fabio,N1] x[Fabio,N2]
End
