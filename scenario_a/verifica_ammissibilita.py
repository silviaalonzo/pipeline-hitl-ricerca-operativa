#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica indipendente a posteriori delle soluzioni dello Scenario A (M01-M10).

Questo script NON modifica e NON risolve i modelli dell'esperto: legge i file
.sol prodotti da Gurobi e controlla se le decisioni ottenute sono ammissibili
nel PROBLEMA ORIGINALE (quello descritto a parole nel testo), confrontando poi
il valore dell'obiettivo con l'ottimo certificato in
dataset_cap4/solutions_summary.csv.

Criterio di correttezza (Cap. 4/5 della tesi): la risposta e' corretta se le
decisioni sono ammissibili nel problema originale e il valore dell'obiettivo
verificato coincide con l'ottimo noto.
"""

import csv
from pathlib import Path

QUI = Path(__file__).resolve().parent
OTTIMI_CSV = QUI.parent / "dataset_cap4" / "solutions_summary.csv"


def leggi_sol(percorso):
    """Legge un file .sol di Gurobi e restituisce {nome_variabile: valore}."""
    valori = {}
    with open(percorso) as f:
        for riga in f:
            riga = riga.strip()
            if not riga or riga.startswith("#"):
                continue
            nome, _, valore = riga.rpartition(" ")
            valori[nome.strip()] = float(valore)
    return valori


def ottimi_noti():
    with open(OTTIMI_CSV) as f:
        return {r["id"]: float(r["ottimo"]) for r in csv.DictReader(f)}


def esito(violazioni):
    return "AMMISSIBILE" if not violazioni else "NON AMMISSIBILE"


# --------------------------------------------------------------------- M01
def verifica_M01():
    v = leggi_sol(QUI / "M01" / "M01.sol")
    siti, zone = ["A", "B", "C", "D"], ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6"]
    cf = {"A": 38, "B": 42, "C": 35, "D": 46}
    cap = {"A": 2, "B": 3, "C": 2, "D": 3}
    ca = {
        "A": {"Z1": 8, "Z2": 10, "Z3": 12, "Z4": 15, "Z5": 9, "Z6": 14},
        "B": {"Z1": 14, "Z2": 9, "Z3": 8, "Z4": 11, "Z5": 13, "Z6": 10},
        "C": {"Z1": 11, "Z2": 13, "Z3": 14, "Z4": 9, "Z5": 8, "Z6": 7},
        "D": {"Z1": 17, "Z2": 15, "Z3": 10, "Z4": 7, "Z5": 14, "Z6": 9},
    }
    x = {i: v[f"x[{i}]"] for i in siti}
    y = {(i, j): v[f"y[{i},{j}]"] for i in siti for j in zone}

    viol = []
    if abs(sum(x.values()) - 2) > 1e-6:
        viol.append(f"centri aperti = {sum(x.values()):g}, richiesti esattamente 2")
    for j in zone:
        if abs(sum(y[i, j] for i in siti) - 1) > 1e-6:
            viol.append(f"zona {j} non assegnata esattamente a un sito")
    for i in siti:
        n = sum(y[i, j] for j in zone)
        if n > cap[i] + 1e-6:
            viol.append(f"capacita' del sito {i} superata ({n:g} > {cap[i]})")
    # requisito del testo: "ogni zona assegnata a un solo centro APERTO"
    for i in siti:
        for j in zone:
            if y[i, j] > 0.5 and x[i] < 0.5:
                viol.append(f"zona {j} assegnata al sito {i} che NON e' aperto")

    obj = sum(cf[i] * x[i] for i in siti) + sum(
        ca[i][j] * y[i, j] for i in siti for j in zone
    )
    return obj, viol


# --------------------------------------------------------------------- M02
def verifica_M02():
    v = leggi_sol(QUI / "M02" / "M02.sol")
    art = ["A", "B", "C", "D"]
    margine = {"A": 42, "B": 36, "C": 50, "D": 31}
    setup = {"A": 80, "B": 65, "C": 90, "D": 50}
    ore_m = {"A": 3, "B": 2, "C": 4, "D": 1}
    ore_l = {"A": 2, "B": 3, "C": 2, "D": 2}
    lotto_min = {"A": 4, "B": 5, "C": 3, "D": 6}
    dom_max = {"A": 20, "B": 25, "C": 16, "D": 30}
    x = {i: v[f"x[{i}]"] for i in art}
    d = {i: v[f"delta[{i}]"] for i in art}

    viol = []
    if sum(ore_m[i] * x[i] for i in art) > 90 + 1e-6:
        viol.append("ore macchina superate")
    if sum(ore_l[i] * x[i] for i in art) > 100 + 1e-6:
        viol.append("ore di lavoro superate")
    for i in art:
        if x[i] < -1e-6:
            viol.append(f"produzione negativa per l'articolo {i}")
        if abs(x[i] - round(x[i])) > 1e-6:
            viol.append(f"lotti non interi per l'articolo {i}")
        if x[i] > 1e-6 and d[i] < 0.5:
            viol.append(f"articolo {i} prodotto senza setup")
        if d[i] > 0.5 and x[i] < lotto_min[i] - 1e-6:
            viol.append(f"lotto minimo non rispettato per l'articolo {i}")
        if x[i] > dom_max[i] + 1e-6:
            viol.append(f"domanda massima superata per l'articolo {i}")
    if sum(d.values()) < 2 - 1e-6:
        viol.append("prodotti meno di due articoli diversi")

    obj = sum(margine[i] * x[i] for i in art) - sum(setup[i] * d[i] for i in art)
    return obj, viol


# --------------------------------------------------------------------- M03
def verifica_M03():
    v = leggi_sol(QUI / "M03" / "M03.sol")
    dip = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabio"]
    turni = ["M1", "M2", "P1", "P2", "N1", "N2"]
    notte = ["N1", "N2"]
    costo = {
        "Ana": {"M1": 8, "M2": 7, "P1": 9, "P2": 8, "N1": None, "N2": None},
        "Bruno": {"M1": 7, "M2": 8, "P1": 8, "P2": 9, "N1": None, "N2": None},
        "Carla": {"M1": None, "M2": 9, "P1": 8, "P2": 8, "N1": 11, "N2": 12},
        "Diego": {"M1": 10, "M2": None, "P1": 9, "P2": 8, "N1": 10, "N2": 11},
        "Elena": {"M1": 8, "M2": 10, "P1": 9, "P2": 9, "N1": 12, "N2": 10},
        "Fabio": {"M1": 9, "M2": 8, "P1": 10, "P2": 7, "N1": None, "N2": None},
    }
    x = {(i, j): v[f"x[{i},{j}]"] for i in dip for j in turni}

    viol = []
    for j in turni:
        if abs(sum(x[i, j] for i in dip) - 1) > 1e-6:
            viol.append(f"turno {j} non coperto da esattamente una persona")
    for i in dip:
        if sum(x[i, j] for j in turni) > 2 + 1e-6:
            viol.append(f"{i} assegnato a piu' di due turni")
        if sum(x[i, j] for j in notte) > 1 + 1e-6:
            viol.append(f"{i} assegnato a piu' di un turno notturno")
    for i in dip:
        for j in turni:
            if costo[i][j] is None and x[i, j] > 0.5:
                viol.append(f"{i} assegnato al turno {j} in cui e' indisponibile")

    obj = sum(
        (costo[i][j] or 0) * x[i, j] for i in dip for j in turni
    )
    return obj, viol


# --------------------------------------------------------------------- M04
def verifica_M04():
    v = leggi_sol(QUI / "M04" / "M04.sol")
    tipi = [1, 2, 3, 4, 5]
    nome = {1: "Van", 2: "Autocarro", 3: "Refrigerato", 4: "Elettrico", 5: "Bilico"}
    volume = {1: 18, 2: 30, 3: 20, 4: 16, 5: 42}
    portata = {1: 8, 2: 18, 3: 10, 4: 7, 5: 28}
    costo = {1: 120, 2: 180, 3: 210, 4: 150, 5: 260}
    emiss = {1: 12, 2: 22, 3: 15, 4: 4, 5: 32}
    disp = {1: 8, 2: 6, 3: 4, 4: 5, 5: 3}
    x = {i: v[f"x[{i}]"] for i in tipi}

    viol = []
    if sum(volume[i] * x[i] for i in tipi) < 180 - 1e-6:
        viol.append("volume complessivo insufficiente")
    if sum(portata[i] * x[i] for i in tipi) < 95 - 1e-6:
        viol.append("portata complessiva insufficiente")
    if sum(emiss[i] * x[i] for i in tipi) > 145 + 1e-6:
        viol.append("emissioni complessive superate")
    if x[3] < 1 - 1e-6:
        viol.append("nessun mezzo refrigerato impiegato")
    if x[4] < 1 - 1e-6:
        viol.append("nessun mezzo elettrico impiegato")
    for i in tipi:
        if x[i] < -1e-6:
            viol.append(f"numero negativo di veicoli {nome[i]}")
        if x[i] > disp[i] + 1e-6:
            viol.append(f"disponibilita' superata per {nome[i]}")
        if abs(x[i] - round(x[i])) > 1e-6:
            viol.append(f"numero non intero di veicoli {nome[i]}")

    obj = sum(costo[i] * x[i] for i in tipi)
    return obj, viol


# --------------------------------------------------------------------- M05
def verifica_M05():
    v = leggi_sol(QUI / "M05" / "M05.sol")
    prog = list(range(1, 9))
    valore = {1: 30, 2: 24, 3: 35, 4: 28, 5: 33, 6: 26, 7: 38, 8: 21}
    budget = {1: 20, 2: 18, 3: 27, 4: 24, 5: 22, 6: 19, 7: 30, 8: 15}
    personale = {1: 4, 2: 3, 3: 5, 4: 4, 5: 4, 6: 3, 7: 5, 8: 2}
    x = {i: v[f"x[{i}]"] for i in prog}

    viol = []
    if sum(budget[i] * x[i] for i in prog) > 100 + 1e-6:
        viol.append("budget superato")
    if sum(personale[i] * x[i] for i in prog) > 18 + 1e-6:
        viol.append("personale superato")
    if x[5] > x[2] + 1e-6:
        viol.append("P5 selezionato senza P2")
    if x[7] > x[3] + 1e-6:
        viol.append("P7 selezionato senza P3")
    if x[4] + x[6] > 1 + 1e-6:
        viol.append("P4 e P6 selezionati insieme (incompatibili)")
    if x[1] + x[3] + x[7] < 1 - 1e-6:
        viol.append("nessun progetto digitale selezionato")
    if sum(x.values()) < 3 - 1e-6:
        viol.append("meno di tre progetti selezionati")

    obj = sum(valore[i] * x[i] for i in prog)
    return obj, viol


# --------------------------------------------------------------------- M06
def verifica_M06():
    v = leggi_sol(QUI / "M06" / "M06.sol")
    lavori = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
    macchine = ["A", "B"]
    tempo = {
        "J1": {"A": 7, "B": 9},
        "J2": {"A": 6, "B": 5},
        "J3": {"A": 8, "B": 7},
        "J4": {"A": 5, "B": 8},
        "J5": {"A": 9, "B": 6},
        "J6": {"A": 4, "B": 7},
        "J7": {"A": None, "B": 5},
    }
    x = {(i, j): v[f"x[{i},{j}]"] for i in lavori for j in macchine}

    viol = []
    for i in lavori:
        if abs(sum(x[i, j] for j in macchine) - 1) > 1e-6:
            viol.append(f"il lavoro {i} non e' eseguito su esattamente una macchina")
    for i in lavori:
        for j in macchine:
            if tempo[i][j] is None and x[i, j] > 0.5:
                viol.append(f"{i} assegnato alla macchina {j}, con cui non e' compatibile")

    carichi = {
        j: sum((tempo[i][j] or 0) * x[i, j] for i in lavori) for j in macchine
    }
    # obiettivo del problema originale: il makespan effettivo
    obj = max(carichi.values())
    return obj, viol


# --------------------------------------------------------------------- M07
def verifica_M07():
    v = leggi_sol(QUI / "M07" / "M07.sol")
    forn = ["A", "B", "C", "D"]
    cv = {"A": 11, "B": 10, "C": 12, "D": 9}
    cf = {"A": 80, "B": 95, "C": 60, "D": 120}
    cap = {"A": 80, "B": 100, "C": 70, "D": 90}
    om = {"A": 20, "B": 25, "C": 15, "D": 20}
    qual = {"A": 96, "B": 90, "C": 98, "D": 88}
    emis = {"A": 3, "B": 4, "C": 2, "D": 5}
    x = {i: v[f"x[{i}]"] for i in forn}
    d = {i: v[f"delta[{i}]"] for i in forn}

    viol = []
    if abs(sum(x.values()) - 180) > 1e-6:
        viol.append(f"unita' acquistate = {sum(x.values()):g}, richieste esattamente 180")
    usati = [i for i in forn if x[i] > 1e-6]
    if len(usati) < 2:
        viol.append("acquisto da meno di due fornitori")
    for i in forn:
        if x[i] < -1e-6:
            viol.append(f"quantita' negativa dal fornitore {i}")
        if abs(x[i] - round(x[i])) > 1e-6:
            viol.append(f"quantita' non intera dal fornitore {i}")
        if x[i] > cap[i] + 1e-6:
            viol.append(f"capacita' del fornitore {i} superata")
        if x[i] > 1e-6 and x[i] < om[i] - 1e-6:
            viol.append(f"ordine minimo non rispettato per il fornitore {i}")
        # nel problema originale fornire implica attivare, e quindi pagare il costo fisso
        if x[i] > 1e-6 and d[i] < 0.5:
            viol.append(
                f"il fornitore {i} fornisce {x[i]:g} unita' con delta = 0:"
                f" costo fisso {cf[i]} non contabilizzato"
            )
    tot = sum(x.values())
    if abs(tot) > 1e-9:
        media = sum(qual[i] * x[i] for i in forn) / tot
        if media < 92 - 1e-6:
            viol.append(f"qualita' media ponderata = {media:.4f}, richiesta >= 92")
    if sum(emis[i] * x[i] for i in forn) > 650 + 1e-6:
        viol.append("emissioni totali superate")

    # obiettivo del problema originale: i costi fissi si pagano per i fornitori usati
    obj = sum(cv[i] * x[i] for i in forn) + sum(cf[i] for i in usati)
    return obj, viol


# --------------------------------------------------------------------- M08
def verifica_M08():
    v = leggi_sol(QUI / "M08" / "M08.sol")
    centri = ["A", "B", "C", "D", "E", "F", "G", "H"]
    costo = {"A": 24, "B": 20, "C": 27, "D": 22, "E": 25, "F": 19, "G": 23, "H": 21}
    # colonna "Zone coperte" della tabella del testo
    copre = {
        "A": ["Z1", "Z2", "Z3"],
        "B": ["Z2", "Z3", "Z4", "Z5"],
        "C": ["Z1", "Z5", "Z6"],
        "D": ["Z3", "Z6", "Z7"],
        "E": ["Z4", "Z7", "Z8"],
        "F": ["Z5", "Z8", "Z9"],
        "G": ["Z6", "Z9", "Z10"],
        "H": ["Z7", "Z8", "Z10"],
    }
    zone = [f"Z{k}" for k in range(1, 11)]
    critiche = {"Z3", "Z7"}
    y = {i: v[f"y[{i}]"] for i in centri}

    viol = []
    for z in zone:
        n = sum(y[i] for i in centri if z in copre[i])
        richiesta = 2 if z in critiche else 1
        if n < richiesta - 1e-6:
            viol.append(f"zona {z} coperta {n:g} volte, richieste {richiesta}")
    aperti = sum(y.values())
    if aperti > 5 + 1e-6:
        viol.append(f"centri aperti = {aperti:g}, ammessi al massimo 5")

    obj = sum(costo[i] * y[i] for i in centri)
    return obj, viol


# --------------------------------------------------------------------- M09
def verifica_M09():
    v = leggi_sol(QUI / "M09" / "M09.sol")
    per = [1, 2, 3, 4, 5, 6]
    domanda = {1: 20, 2: 30, 3: 15, 4: 35, 5: 25, 6: 20}
    cacq = {1: 9, 2: 8, 3: 11, 4: 7, 5: 10, 6: 9}
    cap = {1: 50, 2: 50, 3: 45, 4: 55, 5: 45, 6: 50}
    x = {i: v[f"x[{i}]"] for i in per}
    y = {i: v[f"y[{i}]"] for i in per}

    viol = []
    scorta = 10
    for i in per:
        scorta = scorta + x[i] - domanda[i]
        if abs(scorta - y[i]) > 1e-6:
            viol.append(f"bilancio del periodo {i} non rispettato")
        # il testo: "non sono ammessi arretrati"
        if y[i] < -1e-6:
            viol.append(f"scorta negativa a fine periodo {i} ({y[i]:g}): arretrato non ammesso")
        if x[i] < -1e-6:
            viol.append(f"ordine negativo nel periodo {i}")
        if abs(x[i] - round(x[i])) > 1e-6 or abs(y[i] - round(y[i])) > 1e-6:
            viol.append(f"quantita' non intere nel periodo {i}")
        if x[i] > cap[i] + 1e-6:
            viol.append(f"capacita' di ordine superata nel periodo {i}")
        if x[i] > 1e-6 and x[i] < 10 - 1e-6:
            viol.append(f"ordine inferiore al minimo di 10 unita' nel periodo {i}")
    if y[6] < 5 - 1e-6:
        viol.append(f"scorta finale = {y[6]:g}, richiesta >= 5")

    ordini = [i for i in per if x[i] > 1e-6]
    obj = sum(cacq[i] * x[i] for i in per) + 40 * len(ordini) + 2 * sum(y.values())
    return obj, viol


# --------------------------------------------------------------------- M10
def verifica_M10():
    v = leggi_sol(QUI / "M10" / "M10.sol")
    archi = [("S", "A"), ("S", "B"), ("A", "B"), ("A", "C"), ("B", "C"),
             ("B", "T"), ("C", "T")]
    cf = dict(zip(archi, [40, 35, 15, 30, 18, 45, 38]))
    cv = dict(zip(archi, [2, 3, 1, 2, 2, 4, 2]))
    cap = dict(zip(archi, [30, 35, 15, 25, 20, 25, 35]))
    x = {a: v[f"x[{a[0]},{a[1]}]"] for a in archi}
    y = {a: v[f"y[{a[0]},{a[1]}]"] for a in archi}

    viol = []
    for a in archi:
        et = f"{a[0]}->{a[1]}"
        if x[a] < -1e-6:
            viol.append(f"flusso negativo sull'arco {et} ({x[a]:g})")
        if abs(x[a] - round(x[a])) > 1e-6:
            viol.append(f"flusso non intero sull'arco {et}")
        if x[a] > cap[a] + 1e-6:
            viol.append(f"capacita' superata sull'arco {et}")
        if abs(x[a]) > 1e-6 and y[a] < 0.5:
            viol.append(f"l'arco {et} porta flusso {x[a]:g} senza essere attivato")

    def uscente(nodo):
        return sum(x[a] for a in archi if a[0] == nodo)

    def entrante(nodo):
        return sum(x[a] for a in archi if a[1] == nodo)

    if abs(uscente("S") - 40) > 1e-6:
        viol.append("dal nodo S non partono 40 unita'")
    if abs(entrante("T") - 40) > 1e-6:
        viol.append("al nodo T non arrivano 40 unita'")
    for nodo in ["A", "B", "C"]:
        if abs(entrante(nodo) - uscente(nodo)) > 1e-6:
            viol.append(f"conservazione del flusso violata nel nodo {nodo}")

    # Nel problema originale y_ij e' una decisione: un piano paga il costo fisso
    # di ogni arco che dichiara attivo, anche se poi non lo usa. L'obiettivo e'
    # quindi ricalcolato sulle attivazioni dichiarate; il caso opposto (flusso
    # su un arco non attivato) e' gia' segnalato fra le violazioni.
    obj = sum(cf[a] * y[a] for a in archi) + sum(cv[a] * x[a] for a in archi)
    return obj, viol


# --------------------------------------------------------------------- H01
def verifica_H01():
    v = leggi_sol(QUI / "H01" / "H01.sol")
    siti = ["A", "B", "C", "D", "E", "F"]
    zone = ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7", "Z8"]
    d = dict(zip(zone, [30, 25, 35, 20, 28, 32, 24, 26]))
    cf = dict(zip(siti, [110, 95, 120, 90, 105, 100]))
    cap = dict(zip(siti, [90, 80, 110, 75, 95, 85]))
    cv_righe = {
        "Z1": [4, 7, 6, 10, 9, 11], "Z2": [5, 4, 8, 9, 7, 10],
        "Z3": [7, 5, 4, 8, 9, 7], "Z4": [9, 8, 7, 4, 5, 6],
        "Z5": [8, 9, 6, 5, 4, 7], "Z6": [10, 8, 7, 6, 5, 4],
        "Z7": [6, 7, 5, 8, 6, 7], "Z8": [7, 6, 8, 5, 7, 4],
    }
    em_righe = {
        "Z1": [1, 2, 2, 4, 3, 4], "Z2": [2, 1, 3, 3, 2, 4],
        "Z3": [3, 2, 1, 3, 4, 3], "Z4": [4, 3, 3, 1, 2, 2],
        "Z5": [3, 4, 2, 2, 1, 3], "Z6": [4, 3, 3, 2, 2, 1],
        "Z7": [2, 3, 1, 3, 2, 3], "Z8": [3, 2, 3, 1, 3, 1],
    }
    cv = {(i, j): cv_righe[j][k] for k, i in enumerate(siti) for j in zone}
    em = {(i, j): em_righe[j][k] for k, i in enumerate(siti) for j in zone}
    x = {i: v[f"x[{i}]"] for i in siti}
    y = {(i, j): v[f"y[{i},{j}]"] for i in siti for j in zone}

    viol = []
    for i in siti:
        for j in zone:
            if y[i, j] < -1e-6:
                viol.append(f"quantita' negativa da {i} a {j}")
            if abs(y[i, j] - round(y[i, j])) > 1e-6:
                viol.append(f"quantita' non intera da {i} a {j}")
    # La domanda di ogni zona deve essere soddisfatta integralmente
    for j in zone:
        tot = sum(y[i, j] for i in siti)
        if abs(tot - d[j]) > 1e-6:
            viol.append(f"domanda della zona {j} non soddisfatta ({tot:g} invece di {d[j]})")
    # Da tre a quattro centri aperti
    aperti = [i for i in siti if x[i] > 0.5]
    if not 3 <= len(aperti) <= 4:
        viol.append(f"centri aperti fuori dalla finestra 3-4 ({len(aperti)})")
    # Almeno un sito nel gruppo Nord (A-C) e uno nel gruppo Sud (D-F)
    if not any(x[i] > 0.5 for i in ["A", "B", "C"]):
        viol.append("nessun sito aperto nel gruppo Nord")
    if not any(x[i] > 0.5 for i in ["D", "E", "F"]):
        viol.append("nessun sito aperto nel gruppo Sud")
    # Ogni centro aperto movimenta almeno 20 unita' e non supera la capacita';
    # un centro chiuso non puo' movimentare nulla
    for i in siti:
        mov = sum(y[i, j] for j in zone)
        if x[i] > 0.5:
            if mov < 20 - 1e-6:
                viol.append(f"il centro aperto {i} movimenta solo {mov:g} unita'")
            if mov > cap[i] + 1e-6:
                viol.append(f"capacita' del centro {i} superata ({mov:g} > {cap[i]})")
        elif mov > 1e-6:
            viol.append(f"il centro chiuso {i} movimenta {mov:g} unita'")
    # Emissioni complessive
    emissioni = sum(em[i, j] * y[i, j] for i in siti for j in zone)
    if emissioni > 470 + 1e-6:
        viol.append(f"emissioni complessive {emissioni:g} oltre il limite di 470")

    obj = sum(cf[i] * x[i] for i in siti) + sum(cv[i, j] * y[i, j] for i in siti for j in zone)
    return obj, viol


# --------------------------------------------------------------------- H02
def verifica_H02():
    v = leggi_sol(QUI / "H02" / "H02.sol")
    prod = ["A", "B", "C"]
    per = [1, 2, 3, 4]
    dom = {"A": [8, 12, 10, 14], "B": [10, 8, 14, 12], "C": [6, 9, 7, 11]}
    cp = {"A": [9, 11, 10, 12], "B": [8, 9, 11, 10], "C": [13, 12, 14, 11]}
    setup = {"A": 45, "B": 40, "C": 50}
    hold = {"A": 2, "B": 3, "C": 2}
    ore = {"A": 2, "B": 3, "C": 4}
    lotmin = {"A": 4, "B": 4, "C": 3}
    cap = {1: 90, 2: 95, 3: 90, 4: 100}
    scorta_iniziale = {"A": 0, "B": 0, "C": 6}

    x = {(i, j): v[f"x[{i},{j}]"] for i in prod for j in per}
    y = {(i, j): v[f"y[{i},{j}]"] for i in prod for j in [0] + per}
    de = {(i, j): v[f"delta[{i},{j}]"] for i in prod for j in per}

    viol = []
    for i in prod:
        for j in per:
            if x[i, j] < -1e-6:
                viol.append(f"produzione negativa di {i} in T{j}")
            if y[i, j] < -1e-6:
                viol.append(f"scorta negativa (arretrato) di {i} a fine T{j}")
            for nome, val in (("produzione", x[i, j]), ("scorta", y[i, j])):
                if abs(val - round(val)) > 1e-6:
                    viol.append(f"{nome} non intera di {i} in T{j}")
    # Scorte iniziali dichiarate dal testo
    for i in prod:
        if abs(y[i, 0] - scorta_iniziale[i]) > 1e-6:
            viol.append(f"scorta iniziale di {i} pari a {y[i, 0]:g} invece di {scorta_iniziale[i]}")
    # Bilancio: produzione corrente + scorta precedente = domanda + scorta finale
    for i in prod:
        for j in per:
            sinistra = x[i, j] + y[i, j - 1]
            destra = dom[i][j - 1] + y[i, j]
            if abs(sinistra - destra) > 1e-6:
                viol.append(f"bilancio violato per {i} in T{j}")
    # Tutte le scorte finali devono essere nulle
    for i in prod:
        if abs(y[i, 4]) > 1e-6:
            viol.append(f"scorta finale di {i} non nulla ({y[i, 4]:g})")
    # La scorta totale non puo' superare 20 unita'
    for j in per:
        tot = sum(y[i, j] for i in prod)
        if tot > 20 + 1e-6:
            viol.append(f"scorta totale in T{j} pari a {tot:g}, oltre il limite di 20")
    # Al massimo due articoli attivati per periodo, e coerenza fra setup e produzione
    for j in per:
        attivi = sum(1 for i in prod if x[i, j] > 1e-6)
        if attivi > 2:
            viol.append(f"in T{j} sono attivati {attivi} articoli, oltre il limite di 2")
        for i in prod:
            if x[i, j] > 1e-6 and de[i, j] < 0.5:
                viol.append(f"{i} e' prodotto in T{j} senza setup dichiarato")
            if x[i, j] > 1e-6 and x[i, j] < lotmin[i] - 1e-6:
                viol.append(f"lotto minimo di {i} non rispettato in T{j} ({x[i, j]:g})")
    # Capacita' oraria
    for j in per:
        impiegate = sum(ore[i] * x[i, j] for i in prod)
        if impiegate > cap[j] + 1e-6:
            viol.append(f"capacita' di T{j} superata ({impiegate:g} > {cap[j]})")

    obj = sum(
        cp[i][j - 1] * x[i, j] + setup[i] * de[i, j] + hold[i] * y[i, j]
        for i in prod for j in per
    )
    return obj, viol


# --------------------------------------------------------------------- H03
def verifica_H03():
    v = leggi_sol(QUI / "H03" / "H03.sol")
    dip = [1, 2, 3, 4, 5, 6, 7, 8]
    gio = [1, 2, 3, 4, 5, 6, 7]
    d = dict(zip(gio, [4, 3, 4, 4, 5, 3, 3]))
    tab = {
        1: [9, 9, 10, 9, 11, 14, None],
        2: [10, 9, 9, 10, 10, None, 14],
        3: [9, 10, 9, 9, 12, 12, 13],
        4: [7, None, 7, 8, 8, 11, 11],
        5: [8, 7, 8, None, 9, 10, 12],
        6: [None, 8, 8, 7, 8, 12, 10],
        7: [8, 8, 7, 9, 7, 11, None],
        8: [9, 7, 8, 8, 7, 10, 11],
    }
    x = {(i, j): v[f"x[{i},{j}]"] for i in dip for j in gio}

    viol = []
    # Copertura della domanda giornaliera
    for j in gio:
        presenti = sum(x[i, j] for i in dip)
        if presenti < d[j] - 1e-6:
            viol.append(f"giorno {j}: {presenti:g} addetti invece dei {d[j]} richiesti")
    # Almeno un senior fra E1, E2, E3 ogni giorno
    for j in gio:
        if sum(x[i, j] for i in [1, 2, 3]) < 1 - 1e-6:
            viol.append(f"giorno {j}: nessun senior in servizio")
    # Da tre a cinque giorni per dipendente
    for i in dip:
        lavorati = sum(x[i, j] for j in gio)
        if not 3 - 1e-6 <= lavorati <= 5 + 1e-6:
            viol.append(f"E{i} lavora {lavorati:g} giorni, fuori dalla finestra 3-5")
    # Divieto di quattro giorni consecutivi
    for i in dip:
        for inizio in [1, 2, 3, 4]:
            finestra = sum(x[i, j] for j in range(inizio, inizio + 4))
            if finestra > 3 + 1e-6:
                viol.append(f"E{i} lavora quattro giorni consecutivi da {inizio}")
    # Specialisti E7/E8 presenti giovedi' e venerdi'
    for j, nome in ((4, "giovedi'"), (5, "venerdi'")):
        if x[7, j] + x[8, j] < 1 - 1e-6:
            viol.append(f"nessuno specialista presente {nome}")
    # E1 ed E2 al massimo un giorno del fine settimana
    for i in [1, 2]:
        if x[i, 6] + x[i, 7] > 1 + 1e-6:
            viol.append(f"E{i} lavora entrambi i giorni del fine settimana")
    # Indisponibilita' dichiarate dalla tabella
    for i in dip:
        for j in gio:
            if tab[i][j - 1] is None and x[i, j] > 0.5:
                viol.append(f"E{i} assegnato al giorno {j}, in cui e' indisponibile")

    obj = sum((tab[i][j - 1] or 0) * x[i, j] for i in dip for j in gio)
    return obj, viol


# --------------------------------------------------------------------- H04
def verifica_H04():
    v = leggi_sol(QUI / "H04" / "H04.sol")
    tipi = ["Piccolo", "Medio", "Grande"]
    rotte = ["R1", "R2", "R3", "R4"]
    dom = dict(zip(rotte, [42, 55, 38, 64]))
    cap = dict(zip(tipi, [8, 14, 20]))
    disp = dict(zip(tipi, [10, 9, 6]))
    emis = dict(zip(tipi, [5, 8, 11]))
    costo_righe = {"R1": [45, 62, 82], "R2": [52, 68, 88],
                   "R3": [40, 58, 79], "R4": [60, 77, 96]}
    costo = {(i, j): costo_righe[j][k] for k, i in enumerate(tipi) for j in rotte}
    x = {(i, j): v[f"x[{i},{j}]"] for i in tipi for j in rotte}

    viol = []
    for i in tipi:
        for j in rotte:
            if x[i, j] < -1e-6:
                viol.append(f"numero di viaggi negativo per {i} su {j}")
            if abs(x[i, j] - round(x[i, j])) > 1e-6:
                viol.append(f"numero di viaggi non intero per {i} su {j}")
    # La capacita' complessiva assegnata a ogni rotta deve coprirne la domanda
    for j in rotte:
        offerta = sum(cap[i] * x[i, j] for i in tipi)
        if offerta < dom[j] - 1e-6:
            viol.append(f"rotta {j}: capacita' {offerta:g} inferiore alla domanda {dom[j]}")
    # Su ogni rotta al massimo due tipi di veicolo
    for j in rotte:
        usati = sum(1 for i in tipi if x[i, j] > 1e-6)
        if usati > 2:
            viol.append(f"rotta {j}: {usati} tipi di veicolo, oltre il limite di 2")
    # Sulla rotta R4 almeno un veicolo grande
    if x["Grande", "R4"] < 1 - 1e-6:
        viol.append("nessun veicolo grande impiegato sulla rotta R4")
    # Disponibilita' di ciascun tipo, condivisa fra le rotte
    for i in tipi:
        usati = sum(x[i, j] for j in rotte)
        if usati > disp[i] + 1e-6:
            viol.append(f"disponibilita' del tipo {i} superata ({usati:g} > {disp[i]})")
    # Emissioni totali
    emissioni = sum(emis[i] * x[i, j] for i in tipi for j in rotte)
    if emissioni > 145 + 1e-6:
        viol.append(f"emissioni totali {emissioni:g} oltre il limite di 145")

    obj = sum(costo[i, j] * x[i, j] for i in tipi for j in rotte)
    return obj, viol


# --------------------------------------------------------------------- H05
def verifica_H05():
    v = leggi_sol(QUI / "H05" / "H05.sol")
    prog = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    dati = {
        "A": (42, 18, 12, 10, 4, 5), "B": (35, 20, 18, 14, 4, 4),
        "C": (48, 25, 20, 18, 5, 6), "D": (31, 15, 14, 12, 3, 3),
        "E": (40, 22, 16, 15, 4, 4), "F": (28, 14, 12, 10, 3, 2),
        "G": (55, 30, 25, 22, 6, 7), "H": (37, 20, 18, 16, 4, 5),
        "I": (33, 17, 15, 12, 3, 3), "J": (50, 27, 21, 18, 5, 6),
        "K": (46, 24, 19, 17, 5, 5), "L": (29, 16, 13, 11, 3, 3),
    }
    x = {i: v[f"x[{i}]"] for i in prog}
    scelti = [i for i in prog if x[i] > 0.5]

    viol = []
    # Budget annuali
    for k, (etichetta, limite) in enumerate(
        [("primo anno", 110), ("secondo anno", 100), ("terzo anno", 90)], start=1
    ):
        speso = sum(dati[i][k] for i in scelti)
        if speso > limite + 1e-6:
            viol.append(f"budget del {etichetta} superato ({speso} > {limite})")
    # Personale e rischio
    personale = sum(dati[i][4] for i in scelti)
    if personale > 28 + 1e-6:
        viol.append(f"limite di personale superato ({personale} > 28)")
    rischio = sum(dati[i][5] for i in scelti)
    if rischio > 32 + 1e-6:
        viol.append(f"rischio complessivo superato ({rischio} > 32)")
    # Prerequisiti: G richiede B, J richiede E, K richiede C
    for richiedente, richiesto in [("G", "B"), ("J", "E"), ("K", "C")]:
        if x[richiedente] > 0.5 and x[richiesto] < 0.5:
            viol.append(f"{richiedente} e' scelto senza il prerequisito {richiesto}")
    # Incompatibilita' D-H e F-L
    for a, b in [("D", "H"), ("F", "L")]:
        if x[a] > 0.5 and x[b] > 0.5:
            viol.append(f"i progetti incompatibili {a} e {b} sono entrambi scelti")
    # Almeno due digitali fra A, C, G, J e almeno un sostenibile fra E, H, K
    digitali = sum(1 for i in ["A", "C", "G", "J"] if x[i] > 0.5)
    if digitali < 2:
        viol.append(f"solo {digitali} progetti digitali, ne servono almeno 2")
    sostenibili = sum(1 for i in ["E", "H", "K"] if x[i] > 0.5)
    if sostenibili < 1:
        viol.append("nessun progetto sostenibile scelto")
    # Al massimo otto progetti
    if len(scelti) > 8:
        viol.append(f"{len(scelti)} progetti scelti, oltre il limite di 8")

    # Le sinergie sono ricalcolate dalle sole decisioni x, senza usare z_AC e z_EK
    sin = 0
    if x["A"] > 0.5 and x["C"] > 0.5:
        sin += 12
    if x["E"] > 0.5 and x["K"] > 0.5:
        sin += 10
    obj = sum(dati[i][0] for i in scelti) + sin
    return obj, viol


# --------------------------------------------------------------------- H06
def verifica_H06():
    v = leggi_sol(QUI / "H06" / "H06.sol")
    lavori = ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
    #          durata  disponibilita'  scadenza  peso
    dati = {
        "J1": (5, 0, 9, 4), "J2": (7, 0, 17, 3), "J3": (4, 2, 12, 5),
        "J4": (6, 3, 22, 2), "J5": (3, 5, 15, 6), "J6": (8, 0, 28, 2),
        "J7": (5, 6, 25, 4),
    }
    S = {i: v[f"S[{i}]"] for i in lavori}

    viol = []
    # Disponibilita': nessun lavoro puo' iniziare prima della sua data
    for i in lavori:
        if S[i] < dati[i][1] - 1e-6:
            viol.append(f"{i} inizia in {S[i]:.0f}, prima della disponibilita'"
                        f" {dati[i][1]}")
    # Non sovrapposizione su una sola macchina: gli intervalli devono essere disgiunti
    for a, i in enumerate(lavori):
        for j in lavori[a + 1:]:
            fine_i, fine_j = S[i] + dati[i][0], S[j] + dati[j][0]
            if S[i] < fine_j - 1e-6 and S[j] < fine_i - 1e-6:
                viol.append(f"{i} e {j} si sovrappongono"
                            f" ([{S[i]:.0f},{fine_i:.0f}) e [{S[j]:.0f},{fine_j:.0f}))")
    # Precedenze: J1 prima di J2, J3 prima di J5
    for prima, dopo in [("J1", "J2"), ("J3", "J5")]:
        if S[prima] + dati[prima][0] > S[dopo] + 1e-6:
            viol.append(f"{prima} non termina prima dell'inizio di {dopo}")

    # I ritardi sono ricalcolati come max(0, completamento - scadenza)
    obj = sum(dati[i][3] * max(0.0, S[i] + dati[i][0] - dati[i][2]) for i in lavori)
    return obj, viol


# --------------------------------------------------------------------- H07
def verifica_H07():
    v = leggi_sol(QUI / "H07" / "H07.sol")
    comp = ["C1", "C2", "C3"]
    forn = ["A", "B", "C", "D", "E", "F"]
    domanda = {"C1": 80, "C2": 70, "C3": 60}
    #          costo fisso  capacita'  rischio
    dati = {
        "A": (120, 100, 2), "B": (140, 110, 3), "C": (100, 90, 1),
        "D": (150, 120, 4), "E": (90, 80, 2), "F": (110, 95, 3),
    }
    cu = {
        ("C1", "A"): 9, ("C2", "A"): 12, ("C3", "A"): 11,
        ("C1", "B"): 10, ("C2", "B"): 9, ("C3", "B"): 12,
        ("C1", "C"): 11, ("C2", "C"): 10, ("C3", "C"): 9,
        ("C1", "D"): None, ("C2", "D"): 11, ("C3", "D"): 10,
        ("C1", "E"): 12, ("C2", "E"): 8, ("C3", "E"): None,
        ("C1", "F"): 10, ("C2", "F"): None, ("C3", "F"): 8,
    }
    qual = {
        ("C1", "A"): 96, ("C2", "A"): 94, ("C3", "A"): 95,
        ("C1", "B"): 93, ("C2", "B"): 97, ("C3", "B"): 92,
        ("C1", "C"): 98, ("C2", "C"): 95, ("C3", "C"): 96,
        ("C1", "D"): None, ("C2", "D"): 94, ("C3", "D"): 93,
        ("C1", "E"): 97, ("C2", "E"): 98, ("C3", "E"): None,
        ("C1", "F"): 94, ("C2", "F"): None, ("C3", "F"): 98,
    }
    x = {(i, j): v[f"x[{i},{j}]"] for i in comp for j in forn}

    viol = []
    # Domanda esatta di ciascun componente
    for i in comp:
        tot = sum(x[i, j] for j in forn)
        if abs(tot - domanda[i]) > 1e-6:
            viol.append(f"{i}: acquistate {tot:.0f} unita' invece di {domanda[i]}")
    # Componenti non fornibili (celle "-")
    for (i, j), c in cu.items():
        if c is None and x[i, j] > 1e-6:
            viol.append(f"{x[i, j]:.0f} unita' di {i} da {j}, che non lo fornisce")
    # Multisourcing: almeno due fornitori per componente, almeno 10 unita' ciascuno
    for i in comp:
        usati = [j for j in forn if x[i, j] > 1e-6]
        if len(usati) < 2:
            viol.append(f"{i} proviene da {len(usati)} fornitore/i, ne servono almeno 2")
        for j in usati:
            if x[i, j] < 10 - 1e-6:
                viol.append(f"{i} da {j}: {x[i, j]:.0f} unita', sotto il minimo di 10")
    # Capacita' complessiva sui tre componenti
    for j in forn:
        tot = sum(x[i, j] for i in comp)
        if tot > dati[j][1] + 1e-6:
            viol.append(f"capacita' di {j} superata ({tot:.0f} > {dati[j][1]})")
    # Qualita' media di ciascun componente
    for i in comp:
        num = sum(qual[i, j] * x[i, j] for j in forn if qual[i, j] is not None)
        media = num / domanda[i]
        if media < 95 - 1e-6:
            viol.append(f"qualita' media di {i} pari a {media:.3f}, sotto 95")
    # Fornitori attivati: al massimo quattro, almeno uno fra A e B
    attivi = [j for j in forn if any(x[i, j] > 1e-6 for i in comp)]
    if len(attivi) > 4:
        viol.append(f"{len(attivi)} fornitori attivati, oltre il limite di 4")
    if not ({"A", "B"} & set(attivi)):
        viol.append("nessun fornitore attivato fra A e B")
    # Rischio totale
    rischio = sum(dati[j][2] * x[i, j] for i in comp for j in forn)
    if rischio > 580 + 1e-6:
        viol.append(f"rischio totale {rischio:.0f}, oltre il limite di 580")

    obj = sum(dati[j][0] for j in attivi) + sum(
        cu[i, j] * x[i, j] for i in comp for j in forn if cu[i, j] is not None
    )
    return obj, viol


# --------------------------------------------------------------------- H08
def verifica_H08():
    v = leggi_sol(QUI / "H08" / "H08.sol")
    staz = ["A", "B", "C", "D", "E", "F", "G", "H"]
    #          costo fisso  capacita'
    dati = {
        "A": (35, 42), "B": (32, 44), "C": (40, 46), "D": (30, 40),
        "E": (38, 45), "F": (33, 43), "G": (36, 44), "H": (31, 42),
    }
    zone = [f"Z{k}" for k in range(1, 13)]
    domanda = {"Z1": 8, "Z2": 7, "Z3": 10, "Z4": 6, "Z5": 9, "Z6": 8,
               "Z7": 7, "Z8": 11, "Z9": 6, "Z10": 9, "Z11": 8, "Z12": 7}
    ragg = {
        "Z1": {"A": 3, "B": 5}, "Z2": {"A": 6, "B": 8, "C": 10},
        "Z3": {"B": 11, "C": 4, "D": 6}, "Z4": {"C": 7, "D": 9},
        "Z5": {"A": 6, "D": 3, "E": 5}, "Z6": {"B": 11, "E": 8, "F": 10},
        "Z7": {"C": 7, "F": 4, "G": 6, "H": 8}, "Z8": {"D": 3, "G": 9, "H": 11},
        "Z9": {"E": 8, "F": 10, "H": 5}, "Z10": {"F": 4, "G": 6, "H": 8},
        "Z11": {"A": 6, "E": 5, "H": 11}, "Z12": {"B": 11, "G": 3, "H": 5},
    }
    y = {i: v[f"y[{i}]"] for i in staz}
    x = {(i, j): v[f"x[{i},{j}]"] for j in zone for i in ragg[j]}
    aperte = [i for i in staz if y[i] > 0.5]

    viol = []
    # Esattamente quattro stazioni aperte
    if len(aperte) != 4:
        viol.append(f"{len(aperte)} stazioni aperte invece di 4")
    # Ogni zona assegnata a una sola stazione, raggiungibile e aperta
    for j in zone:
        assegnate = [i for i in ragg[j] if x[i, j] > 0.5]
        if len(assegnate) != 1:
            viol.append(f"{j} assegnata a {len(assegnate)} stazioni invece di 1")
        for i in assegnate:
            if y[i] < 0.5:
                viol.append(f"{j} assegnata alla stazione chiusa {i}")
    # Capacita' delle stazioni
    for i in staz:
        carico = sum(domanda[j] * x[i, j] for j in zone if i in ragg[j])
        if carico > dati[i][1] * y[i] + 1e-6:
            viol.append(f"capacita' di {i} superata ({carico:.0f} > {dati[i][1]})")
    # Almeno una stazione per gruppo
    if not any(y[i] > 0.5 for i in ["A", "B", "C", "D"]):
        viol.append("nessuna stazione aperta nel gruppo Ovest (A-D)")
    if not any(y[i] > 0.5 for i in ["E", "F", "G", "H"]):
        viol.append("nessuna stazione aperta nel gruppo Est (E-H)")
    # Backup delle zone critiche: almeno due stazioni raggiungibili aperte
    for j in ["Z3", "Z8", "Z11"]:
        n = sum(1 for i in ragg[j] if y[i] > 0.5)
        if n < 2:
            viol.append(f"zona critica {j}: solo {n} stazioni raggiungibili aperte")

    obj = sum(dati[i][0] for i in aperte) + sum(
        domanda[j] * ragg[j][i] * x[i, j] for j in zone for i in ragg[j]
    )
    return obj, viol


# --------------------------------------------------------------------- H09
def verifica_H09():
    v = leggi_sol(QUI / "H09" / "H09.sol")
    prod = ["A", "B", "C"]
    periodi = [1, 2, 3, 4, 5, 6]
    domanda = {
        "A": {1: 12, 2: 18, 3: 14, 4: 20, 5: 16, 6: 19},
        "B": {1: 10, 2: 9, 3: 15, 4: 12, 5: 17, 6: 14},
        "C": {1: 8, 2: 11, 3: 10, 4: 13, 5: 9, 6: 15},
    }
    cu = {
        "A": {1: 7, 2: 8, 3: 9, 4: 7, 5: 10, 6: 8},
        "B": {1: 9, 2: 8, 3: 8, 4: 10, 5: 7, 6: 9},
        "C": {1: 11, 2: 10, 3: 12, 4: 9, 5: 11, 6: 8},
    }
    #          setup  holding  ore/unita'  lotto minimo
    dati = {"A": (35, 2, 2, 5), "B": (40, 2, 3, 4), "C": (45, 3, 4, 3)}
    cap = {1: 120, 2: 115, 3: 125, 4: 110, 5: 120, 6: 115}

    x = {(i, t): v[f"x[{i},{t}]"] for i in prod for t in periodi}
    s = {(i, t): v[f"s[{i},{t}]"] for i in prod for t in periodi}
    o = {t: v[f"o[{t}]"] for t in periodi}

    viol = []
    # Bilancio con scorte iniziali nulle e nessun arretrato
    for i in prod:
        for t in periodi:
            precedente = s[i, t - 1] if t > 1 else 0.0
            if abs(x[i, t] + precedente - domanda[i][t] - s[i, t]) > 1e-6:
                viol.append(f"bilancio violato per {i} in T{t}")
            if s[i, t] < -1e-6:
                viol.append(f"scorta negativa (arretrato) per {i} in T{t}")
    # Scorta finale di almeno 2 unita' per prodotto
    for i in prod:
        if s[i, 6] < 2 - 1e-6:
            viol.append(f"scorta finale di {i} pari a {s[i, 6]:.0f}, sotto 2")
    # Scorta totale di fine periodo
    for t in periodi:
        tot = sum(s[i, t] for i in prod)
        if tot > 40 + 1e-6:
            viol.append(f"scorta totale in T{t} pari a {tot:.0f}, oltre 40")
    # Capacita' e straordinario
    for t in periodi:
        ore = sum(dati[i][2] * x[i, t] for i in prod)
        if o[t] < -1e-6 or o[t] > 20 + 1e-6:
            viol.append(f"straordinario in T{t} pari a {o[t]:.2f}, fuori da [0, 20]")
        if ore > cap[t] + o[t] + 1e-6:
            viol.append(f"capacita' in T{t} superata ({ore:.1f} >"
                        f" {cap[t]} + {o[t]:.2f})")
    # Lotto minimo e numero di attivazioni, ricalcolate dalle sole quantita' prodotte
    for t in periodi:
        attivi = [i for i in prod if x[i, t] > 1e-6]
        limite = 3 if t == 1 else 2
        if len(attivi) > limite:
            viol.append(f"T{t}: {len(attivi)} prodotti attivati, oltre il limite"
                        f" di {limite}")
        for i in attivi:
            if x[i, t] < dati[i][3] - 1e-6:
                viol.append(f"{i} in T{t}: {x[i, t]:.0f} unita', sotto il lotto"
                            f" minimo di {dati[i][3]}")

    obj = (
        sum(cu[i][t] * x[i, t] for i in prod for t in periodi)
        + sum(dati[i][0] for i in prod for t in periodi if x[i, t] > 1e-6)
        + sum(dati[i][1] * s[i, t] for i in prod for t in periodi)
        + 18 * sum(o[t] for t in periodi)
    )
    return obj, viol


# --------------------------------------------------------------------- H10
def verifica_H10():
    v = leggi_sol(QUI / "H10" / "H10.sol")
    archi = ["SA", "SB", "AB", "AC", "BC", "BD", "CD", "CT", "DT"]
    #          costo fisso  capacita'
    dati = {
        "SA": (55, 35), "SB": (50, 35), "AB": (18, 15), "AC": (38, 30),
        "BC": (22, 25), "BD": (35, 25), "CD": (20, 20), "CT": (48, 35),
        "DT": (44, 35),
    }
    cu = {
        ("SA", "K1"): 2, ("SA", "K2"): 3, ("SB", "K1"): 3, ("SB", "K2"): 2,
        ("AB", "K1"): 1, ("AB", "K2"): 2, ("AC", "K1"): 2, ("AC", "K2"): 3,
        ("BC", "K1"): 2, ("BC", "K2"): 1, ("BD", "K1"): 3, ("BD", "K2"): 2,
        ("CD", "K1"): 1, ("CD", "K2"): 2, ("CT", "K1"): 3, ("CT", "K2"): 2,
        ("DT", "K1"): 2, ("DT", "K2"): 3,
    }
    prodotti = ["K1", "K2"]
    domanda = {"K1": 28, "K2": 22}
    entranti = {"A": ["SA"], "B": ["SB", "AB"], "C": ["AC", "BC"], "D": ["BD", "CD"]}
    uscenti = {"A": ["AB", "AC"], "B": ["BC", "BD"], "C": ["CD", "CT"], "D": ["DT"]}

    x = {(a, k): v[f"x[{a},{k}]"] for a in archi for k in prodotti}
    y = {a: v[f"y[{a}]"] for a in archi}
    attivi = [a for a in archi if y[a] > 0.5]

    viol = []
    # Domanda soddisfatta in uscita da S e in ingresso a T
    for k in prodotti:
        uscita = x["SA", k] + x["SB", k]
        if abs(uscita - domanda[k]) > 1e-6:
            viol.append(f"{k}: {uscita:.0f} unita' in uscita da S invece"
                        f" di {domanda[k]}")
        ingresso = x["CT", k] + x["DT", k]
        if abs(ingresso - domanda[k]) > 1e-6:
            viol.append(f"{k}: {ingresso:.0f} unita' in ingresso a T invece"
                        f" di {domanda[k]}")
    # Conservazione del flusso nei nodi intermedi
    for nodo in ["A", "B", "C", "D"]:
        for k in prodotti:
            dentro = sum(x[a, k] for a in entranti[nodo])
            fuori = sum(x[a, k] for a in uscenti[nodo])
            if abs(dentro - fuori) > 1e-6:
                viol.append(f"conservazione violata nel nodo {nodo} per {k}"
                            f" ({dentro:.0f} entranti, {fuori:.0f} uscenti)")
    # Capacita' condivisa fra i due prodotti, solo su archi attivati
    for a in archi:
        flusso = x[a, "K1"] + x[a, "K2"]
        if flusso > 1e-6 and y[a] < 0.5:
            viol.append(f"flusso di {flusso:.0f} unita' sull'arco non attivo {a}")
        if flusso > dati[a][1] * y[a] + 1e-6:
            viol.append(f"capacita' dell'arco {a} superata"
                        f" ({flusso:.0f} > {dati[a][1]})")
    # Resilienza: entrambi gli archi in uscita da S devono essere attivi
    for a in ["SA", "SB"]:
        if y[a] < 0.5:
            viol.append(f"arco {a} in uscita da S non attivato")
    # Al massimo sette archi complessivi
    if len(attivi) > 7:
        viol.append(f"{len(attivi)} archi attivati, oltre il limite di 7")

    obj = sum(dati[a][0] for a in attivi) + sum(
        cu[a, k] * x[a, k] for a in archi for k in prodotti
    )
    return obj, viol


# ----------------------------------------------------------------- REPORT
if __name__ == "__main__":
    noti = ottimi_noti()
    verifiche = {
        "M01": verifica_M01,
        "M02": verifica_M02,
        "M03": verifica_M03,
        "M04": verifica_M04,
        "M05": verifica_M05,
        "M06": verifica_M06,
        "M07": verifica_M07,
        "M08": verifica_M08,
        "M09": verifica_M09,
        "M10": verifica_M10,
        "H01": verifica_H01,
        "H02": verifica_H02,
        "H03": verifica_H03,
        "H04": verifica_H04,
        "H05": verifica_H05,
        "H06": verifica_H06,
        "H07": verifica_H07,
        "H08": verifica_H08,
        "H09": verifica_H09,
        "H10": verifica_H10,
    }

    print("=" * 78)
    print("VERIFICA A POSTERIORI DELLE SOLUZIONI - SCENARIO A (M01-M10, H01-H10)")
    print("=" * 78)
    print(f"{'ID':<5}{'obj verificato':>16}{'ottimo noto':>14}{'ammissibilita':>18}"
          f"{'esito':>14}")
    print("-" * 78)

    dettagli = []
    for pid, funzione in verifiche.items():
        obj, viol = funzione()
        noto = noti[pid]
        ok = (not viol) and abs(obj - noto) < 1e-6
        print(f"{pid:<5}{obj:>16.6g}{noto:>14.6g}{esito(viol):>18}"
              f"{('CORRETTO' if ok else 'NON CORRETTO'):>14}")
        if viol:
            dettagli.append((pid, viol))

    print("-" * 78)
    if dettagli:
        print()
        print("Violazioni rilevate nel problema originale:")
        for pid, viol in dettagli:
            print(f"  {pid}:")
            for m in viol:
                print(f"    - {m}")
    else:
        print("Nessuna violazione rilevata.")
    print("=" * 78)
