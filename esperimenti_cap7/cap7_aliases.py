"""Normalizzazione conservativa dei soli nomi di variabile del dataset Cap7."""

from __future__ import annotations

import re

from validate_candidate import canonicalize_variable_name


def alias_name(problem_id: str, raw_name: str) -> str:
    name = canonicalize_variable_name(raw_name)

    if problem_id == "L01":
        match = re.fullmatch(r"(?:open|active)_((?:E|D)\d)", name, flags=re.IGNORECASE)
        if match:
            return f"y_{match.group(1).upper()}"
        match = re.fullmatch(
            r"(?:assign|a)_((?:E|D)\d)_(R\d+)", name, flags=re.IGNORECASE
        )
        if match:
            route = f"R{int(match.group(2)[1:]):02d}"
            return f"x_{match.group(1).upper()}_{route}"
        match = re.fullmatch(r"x_((?:E|D)\d)_R(\d+)", name, flags=re.IGNORECASE)
        if match:
            return f"x_{match.group(1).upper()}_R{int(match.group(2)):02d}"

    if problem_id == "L02":
        match = re.fullmatch(
            r"([xIy])_(P[1-3])_(?:T)?([1-8])", name, flags=re.IGNORECASE
        )
        if match:
            family = "I" if match.group(1).casefold() == "i" else match.group(1).casefold()
            return f"{family}_{match.group(2).upper()}_T{match.group(3)}"
        match = re.fullmatch(
            r"(?:prod(?:uction)?|q)_(P[1-3])_(?:T)?([1-8])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"x_{match.group(1).upper()}_T{match.group(2)}"
        match = re.fullmatch(
            r"(?:inv(?:entory)?|stock|s)_(P[1-3])_(?:T)?([1-8])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"I_{match.group(1).upper()}_T{match.group(2)}"
        match = re.fullmatch(
            r"setup_(P[1-3])_(?:T)?([1-8])", name, flags=re.IGNORECASE
        )
        if match:
            return f"y_{match.group(1).upper()}_T{match.group(2)}"

    if problem_id == "L03":
        # Convenzione alternativa matematicamente equivalente: alcuni modelli
        # usano y[i,j] per l'impiego della coppia e z[i] per l'attivazione del
        # fornitore, mentre la ground truth usa rispettivamente z[i,j] e y[i].
        match = re.fullmatch(
            r"y_(S[1-8])_(C[1-6])", name, flags=re.IGNORECASE
        )
        if match:
            return f"z_{match.group(1).upper()}_{match.group(2).upper()}"
        match = re.fullmatch(r"z_(S[1-8])", name, flags=re.IGNORECASE)
        if match:
            return f"y_{match.group(1).upper()}"
        match = re.fullmatch(
            r"(?:a|open|active)_(S[1-8])", name, flags=re.IGNORECASE
        )
        if match:
            return f"y_{match.group(1).upper()}"
        match = re.fullmatch(
            r"(?:use|assign)_(S[1-8])_(C[1-6])", name, flags=re.IGNORECASE
        )
        if match:
            return f"z_{match.group(1).upper()}_{match.group(2).upper()}"
        match = re.fullmatch(
            r"(?:q|quantity|purchase)_(S[1-8])_(C[1-6])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"x_{match.group(1).upper()}_{match.group(2).upper()}"

    if problem_id == "L04":
        match = re.fullmatch(
            r"([xIy])_([A-E])_(?:T)?([1-6])", name, flags=re.IGNORECASE
        )
        if match:
            family = "I" if match.group(1).casefold() == "i" else match.group(1).casefold()
            return f"{family}_{match.group(2).upper()}_T{match.group(3)}"
        match = re.fullmatch(
            r"(?:prod(?:uction)?)_([A-E])_(?:T)?([1-6])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"x_{match.group(1).upper()}_T{match.group(2)}"
        match = re.fullmatch(
            r"(?:inv(?:entory)?|stock|s)_([A-E])_(?:T)?([1-6])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"I_{match.group(1).upper()}_T{match.group(2)}"
        match = re.fullmatch(
            r"(?:setup)_([A-E])_(?:T)?([1-6])", name, flags=re.IGNORECASE
        )
        if match:
            return f"y_{match.group(1).upper()}_T{match.group(2)}"
        match = re.fullmatch(
            r"(?:o|ot|overtime)_(?:T)?([1-6])", name, flags=re.IGNORECASE
        )
        if match:
            return f"o_T{match.group(1)}"
        match = re.fullmatch(
            r"(?:u|otact|overtime_active|use_overtime)_(?:T)?([1-6])",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"u_T{match.group(1)}"
        match = re.fullmatch(r"z_(?:T)?([1-6])", name, flags=re.IGNORECASE)
        if match:
            return f"u_T{match.group(1)}"

    if problem_id == "L05":
        match = re.fullmatch(r"(?:open|active)_(I(?:1[0-2]|[1-9]))", name, flags=re.IGNORECASE)
        if match:
            return f"y_{match.group(1).upper()}"
        match = re.fullmatch(
            r"(?:assign|a)_(I(?:1[0-2]|[1-9]))_A(\d{1,2})",
            name,
            flags=re.IGNORECASE,
        )
        if match:
            return f"x_{match.group(1).upper()}_A{int(match.group(2)):02d}"
        match = re.fullmatch(
            r"x_(I(?:1[0-2]|[1-9]))_A(\d{1,2})", name, flags=re.IGNORECASE
        )
        if match:
            return f"x_{match.group(1).upper()}_A{int(match.group(2)):02d}"

    return name


def _alias_l04_zero_based(name: str) -> str | None:
    """Traduce la convenzione Python 0..5 nella convenzione T1..T6 di L04."""

    match = re.fullmatch(r"([xIy])_([A-E])_([0-5])", name, flags=re.IGNORECASE)
    if match:
        family = "I" if match.group(1).casefold() == "i" else match.group(1).casefold()
        return f"{family}_{match.group(2).upper()}_T{int(match.group(3)) + 1}"

    match = re.fullmatch(
        r"(?:inv(?:entory)?|stock|s)_([A-E])_([0-5])",
        name,
        flags=re.IGNORECASE,
    )
    if match:
        return f"I_{match.group(1).upper()}_T{int(match.group(2)) + 1}"

    match = re.fullmatch(r"setup_([A-E])_([0-5])", name, flags=re.IGNORECASE)
    if match:
        return f"y_{match.group(1).upper()}_T{int(match.group(2)) + 1}"

    match = re.fullmatch(
        r"(?:o|ot|overtime|straordinario)_([0-5])",
        name,
        flags=re.IGNORECASE,
    )
    if match:
        return f"o_T{int(match.group(1)) + 1}"

    match = re.fullmatch(
        r"(?:u|z|overtime_active|use_overtime|attiva_straordinario)_([0-5])",
        name,
        flags=re.IGNORECASE,
    )
    if match:
        return f"u_T{int(match.group(1)) + 1}"

    return None


def _alias_l02_zero_based(name: str) -> str | None:
    """Traduce prodotti 0..2 e periodi 0..7 nella notazione P1..P3/T1..T8."""

    match = re.fullmatch(r"([xy])_([0-2])_([0-7])", name, flags=re.IGNORECASE)
    if match:
        return (
            f"{match.group(1).casefold()}_P{int(match.group(2)) + 1}"
            f"_T{int(match.group(3)) + 1}"
        )

    match = re.fullmatch(
        r"(?:I|s|inv(?:entory)?|stock)_([0-2])_([0-7])",
        name,
        flags=re.IGNORECASE,
    )
    if match:
        return f"I_P{int(match.group(1)) + 1}_T{int(match.group(2)) + 1}"

    return None


def remap_cap7_candidate(problem_id: str, candidate: dict) -> tuple[dict, dict[str, str]]:
    raw_variables = candidate.get("variables") or {}
    normalized_names = [canonicalize_variable_name(name) for name in raw_variables]
    # La presenza esplicita del periodo 0 identifica senza ambiguità una
    # convenzione zero-based. In quel caso anche gli indici 1..5 devono essere
    # traslati di una posizione, anziché interpretati direttamente come T1..T5.
    l04_zero_based = problem_id == "L04" and any(
        re.fullmatch(
            r"(?:[xIy]_[A-E]|setup_[A-E]|straordinario|attiva_straordinario|o|ot|overtime|u|z)_0",
            name,
            flags=re.IGNORECASE,
        )
        for name in normalized_names
    )
    l02_zero_based = problem_id == "L02" and any(
        re.fullmatch(
            r"(?:[xy]|I|s|inv(?:entory)?|stock)_0_[0-7]",
            name,
            flags=re.IGNORECASE,
        )
        for name in normalized_names
    )

    remapped: dict[str, float] = {}
    mapping: dict[str, str] = {}
    for raw_name, value in raw_variables.items():
        normalized = canonicalize_variable_name(raw_name)
        if l02_zero_based:
            target = _alias_l02_zero_based(normalized) or normalized
        elif l04_zero_based:
            target = _alias_l04_zero_based(normalized) or normalized
        else:
            target = alias_name(problem_id, raw_name)
        if target in remapped and float(remapped[target]) != float(value):
            raise ValueError(f"Alias duplicato con valori diversi: {raw_name} -> {target}")
        remapped[target] = value
        if raw_name != target:
            mapping[raw_name] = target
    result = dict(candidate)
    result["variables"] = remapped
    return result, mapping
