#!/usr/bin/env python3
"""Ricertifica e aggrega i risultati ufficiali dell'ablation del Capitolo 7."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_ablation as runner  # noqa: E402


DETAIL_CSV = HERE / "RISULTATI_DEFINITIVI_CAP7.csv"
SUMMARY_JSON = HERE / "RISULTATI_DEFINITIVI_CAP7.json"
REPORT_MD = HERE / "RAPPORTO_DEFINITIVO_CAP7.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pct_change(old: float, new: float) -> float | None:
    if math.isclose(old, 0.0):
        return None
    return (old - new) / old


def usage_for_run(run_dir: Path) -> dict[str, Any]:
    responses = [read_json(path) for path in sorted(run_dir.glob("attempt_*/response.json"))]
    providers = sorted({str(item.get("provider", "")) for item in responses})
    models = sorted(
        {
            str((item.get("_routing_request") or {}).get("actual_model", ""))
            for item in responses
        }
    )
    finishes = Counter(
        str(((item.get("choices") or [{}])[0]).get("finish_reason", ""))
        for item in responses
    )
    return {
        "api_calls": len(responses),
        "prompt_tokens": sum(int((item.get("usage") or {}).get("prompt_tokens", 0)) for item in responses),
        "completion_tokens": sum(
            int((item.get("usage") or {}).get("completion_tokens", 0)) for item in responses
        ),
        "reasoning_tokens": sum(
            int(
                (((item.get("usage") or {}).get("completion_tokens_details") or {}).get(
                    "reasoning_tokens", 0
                ))
            )
            for item in responses
        ),
        "total_tokens": sum(int((item.get("usage") or {}).get("total_tokens", 0)) for item in responses),
        "api_cost_usd": sum(float((item.get("usage") or {}).get("cost", 0.0)) for item in responses),
        "api_elapsed_seconds": sum(
            float((item.get("_experiment") or {}).get("elapsed_seconds", 0.0)) for item in responses
        ),
        "providers": providers,
        "actual_models": models,
        "finish_reasons": dict(sorted(finishes.items())),
    }


def aggregate(rows: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    subset = [row for row in rows if row["condition"] == condition]
    return {
        "condition": condition,
        "problems": len(subset),
        "correct": sum(int(row["correct_recertified"]) for row in subset),
        "accuracy": sum(int(row["correct_recertified"]) for row in subset) / len(subset),
        "automatic_repairs": sum(row["automatic_repairs"] for row in subset),
        "problems_with_handoff": sum(int(row["handoffs"] > 0) for row in subset),
        "handoffs": sum(row["handoffs"] for row in subset),
        "stage_2_handoffs": sum(row["handoff_stages"].count(2) for row in subset),
        "handoff_rate": sum(int(row["handoffs"] > 0) for row in subset) / len(subset),
        "human_minutes": sum(row["human_minutes"] for row in subset),
        "mean_human_minutes_per_problem": sum(row["human_minutes"] for row in subset) / len(subset),
        "correction_handoffs": sum(row["correction_handoffs"] for row in subset),
        "correction_minutes": sum(row["correction_minutes"] for row in subset),
        "approval_handoffs": sum(row["approval_handoffs"] for row in subset),
        "approval_minutes": sum(row["approval_minutes"] for row in subset),
        "api_calls": sum(row["api_calls"] for row in subset),
        "prompt_tokens": sum(row["prompt_tokens"] for row in subset),
        "completion_tokens": sum(row["completion_tokens"] for row in subset),
        "reasoning_tokens": sum(row["reasoning_tokens"] for row in subset),
        "total_tokens": sum(row["total_tokens"] for row in subset),
        "api_cost_usd": sum(row["api_cost_usd"] for row in subset),
        "api_elapsed_seconds": sum(row["api_elapsed_seconds"] for row in subset),
        "target_principle_reported_used": sum(
            int(row["target_principle_reported_used"] is True) for row in subset
        ),
        "target_principle_usage_observable": sum(
            int(row["target_principle_reported_used"] is not None) for row in subset
        ),
    }


def main() -> None:
    protocol = runner.load_protocol()
    schedule = runner.schedule_rows()
    problems = {
        item["id"]: item
        for item in (
            json.loads(line)
            for line in (ROOT / "dataset_cap7" / "problems.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        )
    }

    for condition in ("C0", "Cmem"):
        actual_hash = sha256(runner.memory_file(condition))
        expected_hash = protocol["memory_sha256"][condition]
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Memoria {condition} modificata: atteso {expected_hash}, trovato {actual_hash}"
            )

    rows: list[dict[str, Any]] = []
    for scheduled in schedule:
        condition = scheduled["condition"]
        problem_id = scheduled["problem_id"]
        runner.configure_core(condition, protocol)
        records = runner.core.load_ground_truth_records()
        run_dir = runner.row_run_dir(scheduled)
        final_path = run_dir / "final.json"
        if not final_path.exists():
            raise RuntimeError(f"Prova incompleta: {problem_id} {condition}")
        final = read_json(final_path)
        final_attempt = str(final.get("final_attempt") or "")
        if not final_attempt:
            raise RuntimeError(f"Tentativo finale assente: {problem_id} {condition}")
        attempt_dir = run_dir / final_attempt
        candidate = read_json(attempt_dir / "candidate_solution.json")
        algebraic, independent, aliases = runner.core.audit_candidate(
            records[problem_id], candidate
        )
        optimum = float(records[problem_id]["solution"]["objective"])
        objective = float(independent["projected_objective"])
        gap = abs(objective - optimum) / max(1.0, abs(optimum))
        correct = bool(
            algebraic.get("correct")
            and independent.get("projected_correct")
            and gap <= 0.001
        )
        if not correct:
            raise RuntimeError(f"Ricertificazione fallita: {problem_id} {condition}")

        evaluation = read_json(attempt_dir / "evaluation.json")
        traceability = evaluation.get("traceability")
        if traceability is None:
            # Una normalizzazione documentata degli alias può rivalidare la
            # soluzione e sostituire l'evaluation finale. La dichiarazione
            # originale sull'uso della memoria resta conservata nel file di
            # cancellazione del falso handoff e va recuperata per l'analisi.
            for cancellation_path in sorted(
                run_dir.glob("handoffs/handoff_*/cancellation.json")
            ):
                cancellation = read_json(cancellation_path)
                original = cancellation.get("old_evaluation") or {}
                if original.get("traceability") is not None:
                    traceability = original["traceability"]
                    break
        memory_items: list[str] | None = None
        if traceability is not None:
            memory_items = list((traceability.get("value") or {}).get("memory_items_used") or [])
        target_id = problems[problem_id]["target_principle_id"]
        target_used = None if memory_items is None else target_id in memory_items
        state = read_json(run_dir / "state.json")
        interventions = list(state.get("interventions") or [])
        correction_interventions = [
            item for item in interventions if item.get("action") == "CORRECT"
        ]
        approval_interventions = [
            item for item in interventions if item.get("action") == "APPROVE"
        ]
        usage = usage_for_run(run_dir)

        row = {
            "global_order": int(scheduled["global_order"]),
            "pair_sequence": int(scheduled["pair_sequence"]),
            "problem_id": problem_id,
            "source_problem": problems[problem_id]["source_problem"],
            "target_principle_id": target_id,
            "condition": condition,
            "correct_recertified": correct,
            "known_optimum": optimum,
            "verified_objective": objective,
            "relative_gap": gap,
            "attempts": int(final["attempt_count"]),
            "automatic_repairs": int(final["automatic_repair_count"]),
            "handoffs": int(final["handoff_count"]),
            "handoff_stages": list(final.get("handoff_stages") or []),
            "human_minutes": float(final["human_minutes"]),
            "interventions": interventions,
            "correction_handoffs": len(correction_interventions),
            "correction_minutes": sum(
                float(item.get("active_minutes", 0.0)) for item in correction_interventions
            ),
            "approval_handoffs": len(approval_interventions),
            "approval_minutes": sum(
                float(item.get("active_minutes", 0.0)) for item in approval_interventions
            ),
            "memory_items_reported_used": memory_items,
            "target_principle_reported_used": target_used,
            "alias_count": len(aliases),
            **usage,
        }
        rows.append(row)

    rows.sort(key=lambda item: item["global_order"])
    aggregates = {condition: aggregate(rows, condition) for condition in ("C0", "Cmem")}
    c0 = aggregates["C0"]
    cmem = aggregates["Cmem"]

    paired = []
    for problem_id in sorted(problems):
        by_condition = {
            row["condition"]: row for row in rows if row["problem_id"] == problem_id
        }
        zero = by_condition["C0"]
        memory = by_condition["Cmem"]
        paired.append(
            {
                "problem_id": problem_id,
                "target_principle_id": problems[problem_id]["target_principle_id"],
                "accuracy_equal": zero["correct_recertified"] == memory["correct_recertified"],
                "human_minutes_C0": zero["human_minutes"],
                "human_minutes_Cmem": memory["human_minutes"],
                "human_minutes_saved": zero["human_minutes"] - memory["human_minutes"],
                "correction_minutes_C0": zero["correction_minutes"],
                "correction_minutes_Cmem": memory["correction_minutes"],
                "approval_minutes_C0": zero["approval_minutes"],
                "approval_minutes_Cmem": memory["approval_minutes"],
                "repairs_C0": zero["automatic_repairs"],
                "repairs_Cmem": memory["automatic_repairs"],
                "repairs_avoided": zero["automatic_repairs"] - memory["automatic_repairs"],
                "api_cost_C0": zero["api_cost_usd"],
                "api_cost_Cmem": memory["api_cost_usd"],
                "api_cost_saved": zero["api_cost_usd"] - memory["api_cost_usd"],
                "elapsed_seconds_C0": zero["api_elapsed_seconds"],
                "elapsed_seconds_Cmem": memory["api_elapsed_seconds"],
                "elapsed_seconds_saved": zero["api_elapsed_seconds"]
                - memory["api_elapsed_seconds"],
                "target_principle_reported_used_Cmem": memory[
                    "target_principle_reported_used"
                ],
            }
        )

    target_pair_uses = sum(
        int(pair["target_principle_reported_used_Cmem"] is True)
        for pair in paired
    )
    accuracy_preserved = c0["accuracy"] == cmem["accuracy"] == 1.0
    human_minutes_saved = c0["human_minutes"] - cmem["human_minutes"]
    repairs_avoided = c0["automatic_repairs"] - cmem["automatic_repairs"]
    correction_minutes_saved = (
        c0["correction_minutes"] - cmem["correction_minutes"]
    )
    h5_assessment = (
        "supporto_parziale_esplorativo"
        if accuracy_preserved and human_minutes_saved > 0 and repairs_avoided > 0
        else "non_supportata_nel_campione"
    )
    h5_rationale = [
        f"L'accuratezza resta pari al {c0['accuracy']:.0%} in entrambe le condizioni.",
        (
            f"La memoria riduce il tempo-uomo da {c0['human_minutes']:.0f} a "
            f"{cmem['human_minutes']:.0f} minuti e le riparazioni automatiche da "
            f"{c0['automatic_repairs']} a {cmem['automatic_repairs']}."
        ),
        (
            f"Gli handoff passano da {c0['handoffs']} a {cmem['handoffs']}; la differenza "
            "si concentra su L01, dove C0 richiede un self-repair e una revisione umana, "
            "mentre Cmem conclude al primo tentativo dichiarando l'uso del principio S-001."
        ),
        (
            f"Il costo umano di correzione in senso stretto diminuisce di "
            f"{correction_minutes_saved:.0f} minuti: l'intervento su L01/C0 è una revisione "
            "di approvazione, non una modifica del codice."
        ),
        (
            f"Il principio bersaglio è dichiarato esplicitamente in {target_pair_uses} "
            "coppie Cmem su cinque; nei casi rivalidati dopo la normalizzazione degli alias "
            "la dichiarazione è recuperata dalla valutazione originale conservata nel log."
        ),
        (
            "Con cinque coppie e una sola esecuzione per condizione, il risultato costituisce "
            "un supporto esplorativo al vantaggio operativo della memoria, ma non una prova "
            "conclusiva della riduzione del costo di correzione definita da H5."
        ),
    ]

    comparison = {
        "accuracy_preserved": accuracy_preserved,
        "human_minutes_saved": human_minutes_saved,
        "human_time_reduction_fraction": pct_change(
            c0["human_minutes"], cmem["human_minutes"]
        ),
        "automatic_repairs_avoided": repairs_avoided,
        "automatic_repair_reduction_fraction": pct_change(
            c0["automatic_repairs"], cmem["automatic_repairs"]
        ),
        "api_calls_avoided": c0["api_calls"] - cmem["api_calls"],
        "api_cost_saved_usd": c0["api_cost_usd"] - cmem["api_cost_usd"],
        "api_cost_reduction_fraction": pct_change(
            c0["api_cost_usd"], cmem["api_cost_usd"]
        ),
        "elapsed_seconds_saved": c0["api_elapsed_seconds"]
        - cmem["api_elapsed_seconds"],
        "elapsed_reduction_fraction": pct_change(
            c0["api_elapsed_seconds"], cmem["api_elapsed_seconds"]
        ),
        "handoff_incidence_changed": c0["problems_with_handoff"]
        != cmem["problems_with_handoff"],
        "correction_cost_changed": c0["correction_minutes"]
        != cmem["correction_minutes"],
        "correction_minutes_saved": correction_minutes_saved,
        "target_principle_used_pairs": target_pair_uses,
        "informative_pairs_for_human_time": sum(
            int(not math.isclose(pair["human_minutes_saved"], 0.0)) for pair in paired
        ),
        "h5_assessment": h5_assessment,
        "h5_rationale": h5_rationale,
    }

    result = {
        "schema_version": 1,
        "chapter": 7,
        "experiment": "ablation_memoria_accumulata_vs_memoria_vuota",
        "protocol_sha256": sha256(HERE / "protocol.json"),
        "schedule_sha256": sha256(HERE / "schedule.csv"),
        "memory_sha256_verified": {
            condition: sha256(runner.memory_file(condition))
            for condition in ("C0", "Cmem")
        },
        "rows": rows,
        "aggregates": aggregates,
        "paired_comparison": paired,
        "comparison": comparison,
        "protocol_amendments": read_json(HERE / "protocol_amendments.json"),
    }
    SUMMARY_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    scalar_fields = [
        "global_order",
        "pair_sequence",
        "problem_id",
        "source_problem",
        "target_principle_id",
        "condition",
        "correct_recertified",
        "known_optimum",
        "verified_objective",
        "relative_gap",
        "attempts",
        "automatic_repairs",
        "handoffs",
        "human_minutes",
        "correction_handoffs",
        "correction_minutes",
        "approval_handoffs",
        "approval_minutes",
        "api_calls",
        "prompt_tokens",
        "completion_tokens",
        "reasoning_tokens",
        "total_tokens",
        "api_cost_usd",
        "api_elapsed_seconds",
        "target_principle_reported_used",
    ]
    with DETAIL_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=scalar_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in scalar_fields})

    report_lines = [
        "# Rapporto definitivo — ablation della doppia memoria",
        "",
        "Tutte le dieci soluzioni sono state ricertificate sul modello originale e sull'ottimo noto.",
        "Le memorie sono rimaste identiche agli snapshot congelati prima della campagna.",
        "",
        "| Condizione | Accuratezza | Riparazioni | Handoff | Tempo-uomo | Correzione | Chiamate | Costo API |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in ("C0", "Cmem"):
        item = aggregates[condition]
        report_lines.append(
            f"| {condition} | {item['correct']}/{item['problems']} "
            f"({item['accuracy']:.0%}) | {item['automatic_repairs']} | {item['handoffs']} | "
            f"{item['human_minutes']:.0f} min | {item['correction_minutes']:.0f} min | "
            f"{item['api_calls']} | ${item['api_cost_usd']:.6f} |"
        )
    report_lines.extend(
        [
            "",
            "## Confronto appaiato",
            "",
            "| Problema | Tempo C0 | Tempo Cmem | Correzione C0/Cmem | Riparazioni C0 | Riparazioni Cmem | Principio bersaglio dichiarato |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for pair in paired:
        used = pair["target_principle_reported_used_Cmem"]
        label = "non osservabile" if used is None else ("sì" if used else "no")
        report_lines.append(
            f"| {pair['problem_id']} | {pair['human_minutes_C0']:.0f} min | "
            f"{pair['human_minutes_Cmem']:.0f} min | "
            f"{pair['correction_minutes_C0']:.0f}/{pair['correction_minutes_Cmem']:.0f} min | "
            f"{pair['repairs_C0']} | "
            f"{pair['repairs_Cmem']} | {label} |"
        )
    report_lines.extend(
        [
            "",
            "## Valutazione di H5",
            "",
            "H5 riceve un supporto parziale ed esplorativo. A parità di accuratezza, la memoria "
            f"riduce il tempo-uomo totale da {c0['human_minutes']:.0f} a "
            f"{cmem['human_minutes']:.0f} minuti, le riparazioni automatiche da "
            f"{c0['automatic_repairs']} a {cmem['automatic_repairs']} e gli handoff da "
            f"{c0['handoffs']} a {cmem['handoffs']}. La differenza è concentrata su L01: "
            "senza memoria il primo output richiede un self-repair e una revisione umana, "
            "mentre con memoria il problema viene chiuso al primo tentativo dichiarando l'uso "
            "del principio bersaglio S-001. L'intervento evitato è tuttavia una revisione di "
            "approvazione e non una correzione del codice; con cinque coppie e una sola esecuzione "
            "per condizione, il risultato documenta il vantaggio operativo della memoria ma non "
            "costituisce una prova conclusiva della riduzione del costo di correzione in senso stretto.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Creato: {DETAIL_CSV}")
    print(f"Creato: {SUMMARY_JSON}")
    print(f"Creato: {REPORT_MD}")
    print("Ricertificazione: 10/10")
    print(
        f"Tempo-uomo C0={c0['human_minutes']:.0f} min; "
        f"Cmem={cmem['human_minutes']:.0f} min"
    )


if __name__ == "__main__":
    main()
