#!/usr/bin/env python3
"""Rivalida le soluzioni dello Scenario B normalizzando solo alias di variabili.

Il validatore originale viene conservato immutato. Questo passaggio post-hoc
non modifica valori o output dei modelli: traduce esclusivamente nomi
semanticamente equivalenti (per esempio ``x_A`` e ``y_A`` nel set covering)
nei nomi della ground truth. I risultati sono salvati in file ``*_v2``.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

from validate_candidate import canonicalize_variable_name, load_ground_truth, validate


HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs" / "B"
DETAILS_V1 = HERE / "results_detailed.csv"
DETAILS_V2 = HERE / "results_detailed_v2.csv"
SUMMARY_V2 = HERE / "results_summary_v2.csv"


DAY_MAP = {"1": "Lun", "2": "Mar", "3": "Mer", "4": "Gio", "5": "Ven", "6": "Sab", "7": "Dom"}
SIZE_MAP = {
    "P": "Piccolo", "S": "Piccolo",
    "M": "Medio",
    "G": "Grande", "L": "Grande",
}
ARCS_M10 = {"SA": "S_A", "SB": "S_B", "AB": "A_B", "AC": "A_C", "BC": "B_C", "BT": "B_T", "CT": "C_T"}
ARCS_H10 = {
    "SA": "S_A", "SB": "S_B", "AB": "A_B", "AC": "A_C", "BC": "B_C",
    "BD": "B_D", "CD": "C_D", "CT": "C_T", "DT": "D_T",
}


def alias_name(problem_id: str, raw_name: str) -> str:
    """Restituisce il nome equivalente nella convenzione della ground truth."""
    name = canonicalize_variable_name(raw_name)

    if problem_id == "H01":
        site_opening = re.fullmatch(r"x_([A-F])", name)
        if site_opening:
            return f"y_{site_opening.group(1)}"
        shipment = re.fullmatch(r"y_([A-F])_(Z[1-8])", name)
        if shipment:
            return f"x_{shipment.group(2)}_{shipment.group(1)}"

    if problem_id == "M05":
        match = re.fullmatch(r"P(\d+)", name)
        if match:
            return f"x_P{match.group(1)}"
        match = re.fullmatch(r"x_?(\d+)", name)
        if match:
            return f"x_P{match.group(1)}"

    if problem_id == "M06":
        match = re.fullmatch(r"[xy]_(?:J)?(\d+)_(A|B)", name)
        if match:
            return f"x_J{match.group(1)}_{match.group(2)}"
        if name in {"C", "C_max", "Cmax", "makespan"}:
            return "Cmax"

    if problem_id == "M04" and name in {
        "Van", "Autocarro", "Refrigerato", "Elettrico", "Bilico"
    }:
        return f"x_{name}"

    if problem_id == "M08":
        match = re.fullmatch(r"x_([A-H])", name)
        if match:
            return f"y_{match.group(1)}"

    if problem_id == "M09":
        match = re.fullmatch(r"x_?(\d+)", name)
        if match:
            return f"q_{match.group(1)}"
        match = re.fullmatch(r"([yI])_?(\d+)", name)
        if match:
            return f"{match.group(1)}_{match.group(2)}"

    if problem_id == "M10":
        compact = re.fullmatch(r"([xy])_?([SABCT]{2})", name)
        if compact and compact.group(2) in ARCS_M10:
            family = "f" if compact.group(1) == "x" else "y"
            return f"{family}_{ARCS_M10[compact.group(2)]}"
        expanded = re.fullmatch(r"([xy])_([SABCT])_([SABCT])", name)
        if expanded:
            family = "f" if expanded.group(1) == "x" else "y"
            return f"{family}_{expanded.group(2)}_{expanded.group(3)}"

    if problem_id == "H02":
        name = re.sub(r"_T([1-4])$", r"_\1", name)
        if name.startswith("Inv_"):
            name = "I_" + name[4:]
        inventory = re.fullmatch(r"s_([ABC])_([0-4])", name)
        if inventory:
            name = f"I_{inventory.group(1)}_{inventory.group(2)}"
        return name

    if problem_id == "H03":
        numeric = re.fullmatch(r"x_([1-8])_([1-7])", name)
        if numeric:
            return f"x_E{numeric.group(1)}_{DAY_MAP[numeric.group(2)]}"
        match = re.fullmatch(r"x_(E\d+)_(\d)", name)
        if match and match.group(2) in DAY_MAP:
            return f"x_{match.group(1)}_{DAY_MAP[match.group(2)]}"

    if problem_id == "H04":
        match = re.fullmatch(r"([xyz])_(R\d+)_([PSMGL])", name)
        if match:
            family = "y" if match.group(1) == "z" else match.group(1)
            return f"{family}_{match.group(2)}_{SIZE_MAP[match.group(3)]}"
        activation = re.fullmatch(r"z_(R\d+)_(Piccolo|Medio|Grande)", name)
        if activation:
            return f"y_{activation.group(1)}_{activation.group(2)}"

    if problem_id == "H05":
        # La binaria che attiva una sinergia è ausiliaria: y_A_C, y_AC e z_AC
        # rappresentano la stessa quantità, così come le varianti per E-K.
        compact_synergy = name.replace("_", "")
        if compact_synergy == "yAC":
            return "z_AC"
        if compact_synergy == "yEK":
            return "z_EK"

    if problem_id == "H06":
        match = re.fullmatch(r"([SCT])_?(?:J)?(\d+)", name)
        if match:
            return f"{match.group(1)}_J{match.group(2)}"
        match = re.fullmatch(r"[xyo]_(?:J)?(\d+)_(?:J)?(\d+)", name)
        if match:
            return f"o_J{match.group(1)}_J{match.group(2)}"

    if problem_id == "H07":
        pair_activation = re.fullmatch(r"y_([A-F])_(C[1-3])", name)
        if pair_activation:
            return f"z_{pair_activation.group(1)}_{pair_activation.group(2)}"
        supplier_activation = re.fullmatch(r"z_([A-F])", name)
        if supplier_activation:
            return f"y_{supplier_activation.group(1)}"

    if problem_id == "H09":
        # Il periodo può essere scritto come 1 oppure T1 senza cambiare la variabile.
        name = re.sub(r"_T([1-6])$", r"_\1", name)
        match = re.fullmatch(r"s_([ABC])_(\d+)", name)
        if match:
            return f"I_{match.group(1)}_{match.group(2)}"
        match = re.fullmatch(r"O_(\d+)", name)
        if match:
            return f"o_{match.group(1)}"
        match = re.fullmatch(r"overtime_(?:T)?([1-6])", name, flags=re.IGNORECASE)
        if match:
            return f"o_{match.group(1)}"

    if problem_id == "H10":
        compact_flow = re.fullmatch(r"x_([SABCDT]{2})_(K[12])", name)
        if compact_flow and compact_flow.group(1) in ARCS_H10:
            origin, destination = ARCS_H10[compact_flow.group(1)].split("_")
            return f"f_{compact_flow.group(2)}_{origin}_{destination}"
        compact_activation = re.fullmatch(r"y_([SABCDT]{2})", name)
        if compact_activation and compact_activation.group(1) in ARCS_H10:
            origin, destination = ARCS_H10[compact_activation.group(1)].split("_")
            return f"y_{origin}_{destination}"
        match = re.fullmatch(r"x_([SABCDT])_([SABCDT])_(K[12])", name)
        if match:
            return f"f_{match.group(3)}_{match.group(1)}_{match.group(2)}"
        match = re.fullmatch(r"x_(K[12])_([SABCDT])_([SABCDT])", name)
        if match:
            return f"f_{match.group(1)}_{match.group(2)}_{match.group(3)}"

    return name


def remap_candidate(problem_id: str, candidate: dict) -> tuple[dict, dict[str, str]]:
    remapped: dict[str, object] = {}
    mapping: dict[str, str] = {}
    raw_variables = candidate.get("variables") or {}
    canonical_names = [canonicalize_variable_name(name) for name in raw_variables]
    h02_zero_based = bool(
        problem_id == "H02"
        and any(re.fullmatch(r"[xyIs]_[ABC]_(?:T)?0", name) for name in canonical_names)
        and not any(re.fullmatch(r"[xyIs]_[ABC]_(?:T)?4", name) for name in canonical_names)
    )
    # Nella formulazione dell'esperto di H02, la scorta è indicata con y e la
    # binaria di setup con delta. La presenza della famiglia delta disambigua
    # questa convenzione da quella della ground truth, che usa I e y.
    h02_delta_setup = bool(
        problem_id == "H02"
        and any(re.fullmatch(r"delta_[ABC]_[1-4]", name) for name in canonical_names)
    )
    h06_zero_based = bool(
        problem_id == "H06"
        and any(
            re.fullmatch(r"[SCT]_0", name)
            or re.fullmatch(r"[xyo]_0_[0-6]", name)
            or re.fullmatch(r"[xyo]_[0-6]_0", name)
            for name in canonical_names
        )
        and not any(
            re.fullmatch(r"[SCT]_(?:J)?7", name)
            or re.fullmatch(r"[xyo]_(?:J)?7_(?:J)?[1-7]", name)
            or re.fullmatch(r"[xyo]_(?:J)?[1-7]_(?:J)?7", name)
            for name in canonical_names
        )
    )
    for raw_name, value in raw_variables.items():
        canonical = canonicalize_variable_name(raw_name)
        h06_job_match = (
            re.fullmatch(r"([SCT])_([0-6])", canonical)
            if h06_zero_based
            else None
        )
        h06_order_match = (
            re.fullmatch(r"[xyo]_([0-6])_([0-6])", canonical)
            if h06_zero_based
            else None
        )
        h02_setup_match = (
            re.fullmatch(r"delta_([ABC])_([1-4])", canonical)
            if h02_delta_setup
            else None
        )
        h02_inventory_match = (
            re.fullmatch(r"y_([ABC])_([0-4])", canonical)
            if h02_delta_setup
            else None
        )
        zero_based_match = (
            re.fullmatch(r"([xyIs])_([ABC])_(?:T)?([0-3])", canonical)
            if h02_zero_based and not h02_delta_setup
            else None
        )
        if h06_job_match:
            target = f"{h06_job_match.group(1)}_J{int(h06_job_match.group(2)) + 1}"
        elif h06_order_match:
            target = (
                f"o_J{int(h06_order_match.group(1)) + 1}_"
                f"J{int(h06_order_match.group(2)) + 1}"
            )
        elif h02_setup_match:
            target = f"y_{h02_setup_match.group(1)}_{h02_setup_match.group(2)}"
        elif h02_inventory_match:
            target = f"I_{h02_inventory_match.group(1)}_{h02_inventory_match.group(2)}"
        elif zero_based_match:
            family = "I" if zero_based_match.group(1) == "s" else zero_based_match.group(1)
            target = (
                f"{family}_{zero_based_match.group(2)}_"
                f"{int(zero_based_match.group(3)) + 1}"
            )
        else:
            target = alias_name(problem_id, raw_name)
        if target in remapped and remapped[target] != value:
            raise ValueError(f"Alias duplicato con valori diversi: {raw_name} -> {target}")
        remapped[target] = value
        if raw_name != target:
            mapping[raw_name] = target
    result = dict(candidate)
    result["variables"] = remapped
    return result, mapping


def revalidate_runs() -> None:
    for candidate_path in sorted(RUNS.glob("*/*/run_*/candidate_solution.json")):
        run_dir = candidate_path.parent
        request = json.loads((run_dir / "request.json").read_text(encoding="utf-8"))
        problem_id = request["problem_id"]
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        remapped, aliases = remap_candidate(problem_id, candidate)
        result = validate(load_ground_truth(problem_id), remapped)
        result["validation_version"] = "2.0-alias-normalization"
        result["semantic_aliases"] = aliases
        (run_dir / "validation_v2.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def boolean(value: object) -> bool:
    return str(value).strip().lower() == "true"


def rebuild_tables() -> None:
    import pandas as pd

    with DETAILS_V1.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0])

    for row in rows:
        run_dir = HERE / row["run_directory"]
        v2_path = run_dir / "validation_v2.json"
        if not v2_path.exists():
            continue
        v2 = json.loads(v2_path.read_text(encoding="utf-8"))
        row["feasible"] = str(bool(v2["feasible"]))
        row["recomputed_objective"] = "" if v2["recomputed_objective"] is None else str(v2["recomputed_objective"])
        row["known_optimum"] = str(v2["known_optimum"])
        row["relative_gap"] = "" if v2["relative_gap"] is None else str(v2["relative_gap"])
        row["correct"] = str(bool(v2["correct"]))
        row["max_violation"] = "" if not math.isfinite(v2["max_violation"]) else str(v2["max_violation"])
        row["unknown_variables"] = str(len(v2["unknown_variables"]))

    with DETAILS_V2.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    df = pd.DataFrame(rows)
    for field in ["pass", "feasible", "correct"]:
        df[field] = df[field].map(boolean)
    for field in [
        "relative_gap", "response_seconds", "reasoning_tokens", "total_tokens", "api_cost_usd"
    ]:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    summary = []
    for model, group in df.groupby("requested_model", sort=True):
        valid_gaps = group.loc[group["feasible"], "relative_gap"]
        summary.append({
            "model": model,
            "n_runs": len(group),
            "pass_rate": group["pass"].mean(),
            "feasibility_rate": group["feasible"].mean(),
            "accuracy": group["correct"].mean(),
            "mean_relative_gap_feasible": valid_gaps.mean(),
            "mean_response_seconds": group["response_seconds"].mean(),
            "mean_reasoning_tokens": group["reasoning_tokens"].mean(),
            "mean_total_tokens": group["total_tokens"].mean(),
            "total_api_cost_usd": group["api_cost_usd"].sum(),
            "mean_api_cost_usd": group["api_cost_usd"].mean(),
        })
    pd.DataFrame(summary).to_csv(SUMMARY_V2, index=False)


if __name__ == "__main__":
    raise SystemExit(
        "Script legacy: per evitare di ricreare riepiloghi superati, usa "
        "`python3 audit_scenario_b.py`. L'unico risultato canonico è "
        "RISULTATI_DEFINITIVI_SCENARIO_B.csv."
    )
