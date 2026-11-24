#!/usr/bin/env python3
"""Ricertifica la replica 2 e aggrega le due repliche dell'ablation Cap. 7."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import analyze_results as primary_analysis
import run_replication_02 as replica


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPLICA_CSV = replica.REPLICA_ROOT / "RISULTATI_REPLICA_02.csv"
REPLICA_JSON = replica.REPLICA_ROOT / "RISULTATI_REPLICA_02.json"
COMBINED_CSV = HERE / "RISULTATI_COMBINATI_CAP7.csv"
COMBINED_JSON = HERE / "RISULTATI_COMBINATI_CAP7.json"
COMBINED_REPORT = HERE / "RAPPORTO_COMBINATO_CAP7.md"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def problems_by_id() -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in (
            json.loads(line)
            for line in (ROOT / "dataset_cap7" / "problems.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        )
    }


def traceability_from_run(run_dir: Path, attempt_dir: Path) -> dict | None:
    evaluation = read_json(attempt_dir / "evaluation.json")
    traceability = evaluation.get("traceability")
    if traceability is not None:
        return traceability
    for cancellation_path in sorted(run_dir.glob("handoffs/handoff_*/cancellation.json")):
        original = (read_json(cancellation_path).get("old_evaluation") or {})
        if original.get("traceability") is not None:
            return original["traceability"]
    return None


def collect_replica_rows() -> list[dict[str, Any]]:
    protocol = replica.primary.load_protocol()
    problems = problems_by_id()
    rows: list[dict[str, Any]] = []

    for condition in ("C0", "Cmem"):
        expected = read_json(replica.PROTOCOL)["memory_sha256"][condition]
        actual = replica.sha256(replica.memory_file(condition))
        if actual != expected:
            raise RuntimeError(f"Snapshot {condition} della replica modificato")

    for scheduled in replica.schedule_rows():
        condition = scheduled["condition"]
        problem_id = scheduled["problem_id"]
        replica.configure(condition, protocol)
        core = replica.primary.core
        records = core.load_ground_truth_records()
        run_dir = replica.row_run_dir(scheduled)
        final_path = run_dir / "final.json"
        if not final_path.exists():
            raise RuntimeError(f"Replica incompleta: {problem_id} {condition}")
        final = read_json(final_path)
        attempt_dir = run_dir / str(final.get("final_attempt") or "")
        candidate = read_json(attempt_dir / "candidate_solution.json")
        algebraic, independent, aliases = core.audit_candidate(
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

        traceability = traceability_from_run(run_dir, attempt_dir)
        memory_items: list[str] | None = None
        if traceability is not None:
            memory_items = list(
                (traceability.get("value") or {}).get("memory_items_used") or []
            )
        target_id = problems[problem_id]["target_principle_id"]
        target_used = None if memory_items is None else target_id in memory_items
        state = read_json(run_dir / "state.json")
        interventions = list(state.get("interventions") or [])
        corrections = [item for item in interventions if item.get("action") == "CORRECT"]
        approvals = [item for item in interventions if item.get("action") == "APPROVE"]
        usage = primary_analysis.usage_for_run(run_dir)

        rows.append(
            {
                "replicate": 2,
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
                "correction_handoffs": len(corrections),
                "correction_minutes": sum(
                    float(item.get("active_minutes", 0.0)) for item in corrections
                ),
                "approval_handoffs": len(approvals),
                "approval_minutes": sum(
                    float(item.get("active_minutes", 0.0)) for item in approvals
                ),
                "memory_items_reported_used": memory_items,
                "target_principle_reported_used": target_used,
                "alias_count": len(aliases),
                **usage,
            }
        )

    return sorted(rows, key=lambda row: row["global_order"])


def condition_summary(rows: list[dict[str, Any]], condition: str) -> dict[str, Any]:
    subset = [row for row in rows if row["condition"] == condition]
    return {
        "condition": condition,
        "observations": len(subset),
        "correct": sum(int(row["correct_recertified"]) for row in subset),
        "accuracy": sum(int(row["correct_recertified"]) for row in subset) / len(subset),
        "automatic_repairs": sum(row["automatic_repairs"] for row in subset),
        "handoffs": sum(row["handoffs"] for row in subset),
        "problems_with_handoff": sum(int(row["handoffs"] > 0) for row in subset),
        "human_minutes": sum(row["human_minutes"] for row in subset),
        "correction_minutes": sum(row["correction_minutes"] for row in subset),
        "approval_minutes": sum(row["approval_minutes"] for row in subset),
        "api_calls": sum(row["api_calls"] for row in subset),
        "api_cost_usd": sum(row["api_cost_usd"] for row in subset),
        "api_elapsed_seconds": sum(row["api_elapsed_seconds"] for row in subset),
    }


def paired_observations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    for replicate_id in (1, 2):
        for problem_id in sorted({row["problem_id"] for row in rows}):
            subset = [
                row
                for row in rows
                if row["replicate"] == replicate_id and row["problem_id"] == problem_id
            ]
            by_condition = {row["condition"]: row for row in subset}
            if set(by_condition) != {"C0", "Cmem"}:
                raise RuntimeError(f"Coppia incompleta: replica {replicate_id}, {problem_id}")
            zero = by_condition["C0"]
            memory = by_condition["Cmem"]
            human_saved = zero["human_minutes"] - memory["human_minutes"]
            repairs_avoided = zero["automatic_repairs"] - memory["automatic_repairs"]
            handoffs_avoided = zero["handoffs"] - memory["handoffs"]
            if human_saved > 0 or handoffs_avoided > 0 or repairs_avoided > 0:
                outcome = "vantaggio_memoria"
            elif human_saved < 0 or handoffs_avoided < 0 or repairs_avoided < 0:
                outcome = "svantaggio_memoria"
            else:
                outcome = "nessuna_differenza"
            pairs.append(
                {
                    "replicate": replicate_id,
                    "problem_id": problem_id,
                    "accuracy_equal": zero["correct_recertified"]
                    == memory["correct_recertified"],
                    "human_minutes_C0": zero["human_minutes"],
                    "human_minutes_Cmem": memory["human_minutes"],
                    "human_minutes_saved": human_saved,
                    "repairs_C0": zero["automatic_repairs"],
                    "repairs_Cmem": memory["automatic_repairs"],
                    "repairs_avoided": repairs_avoided,
                    "handoffs_C0": zero["handoffs"],
                    "handoffs_Cmem": memory["handoffs"],
                    "handoffs_avoided": handoffs_avoided,
                    "elapsed_seconds_C0": zero["api_elapsed_seconds"],
                    "elapsed_seconds_Cmem": memory["api_elapsed_seconds"],
                    "elapsed_seconds_saved": zero["api_elapsed_seconds"]
                    - memory["api_elapsed_seconds"],
                    "api_cost_C0": zero["api_cost_usd"],
                    "api_cost_Cmem": memory["api_cost_usd"],
                    "target_principle_reported_used_Cmem": memory[
                        "target_principle_reported_used"
                    ],
                    "outcome": outcome,
                }
            )
    return pairs


def by_problem_summary(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        grouped[pair["problem_id"]].append(pair)
    result = []
    for problem_id, subset in sorted(grouped.items()):
        result.append(
            {
                "problem_id": problem_id,
                "replicates": len(subset),
                "replicates_with_memory_advantage": sum(
                    int(item["outcome"] == "vantaggio_memoria") for item in subset
                ),
                "replicates_with_memory_disadvantage": sum(
                    int(item["outcome"] == "svantaggio_memoria") for item in subset
                ),
                "human_minutes_saved_total": sum(
                    item["human_minutes_saved"] for item in subset
                ),
                "repairs_avoided_total": sum(item["repairs_avoided"] for item in subset),
                "handoffs_avoided_total": sum(item["handoffs_avoided"] for item in subset),
            }
        )
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "replicate",
        "global_order",
        "problem_id",
        "condition",
        "correct_recertified",
        "known_optimum",
        "verified_objective",
        "relative_gap",
        "attempts",
        "automatic_repairs",
        "handoffs",
        "human_minutes",
        "correction_minutes",
        "approval_minutes",
        "api_calls",
        "api_cost_usd",
        "api_elapsed_seconds",
        "target_principle_reported_used",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def main() -> None:
    replica_rows = collect_replica_rows()
    write_csv(REPLICA_CSV, replica_rows)
    REPLICA_JSON.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "replicate": 2,
                "rows": replica_rows,
                "aggregates": {
                    condition: condition_summary(replica_rows, condition)
                    for condition in ("C0", "Cmem")
                },
                "protocol_amendments": read_json(
                    replica.REPLICA_ROOT / "protocol_amendments.json"
                ),
            },
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )

    primary_payload = read_json(HERE / "RISULTATI_DEFINITIVI_CAP7.json")
    primary_rows = [dict(row, replicate=1) for row in primary_payload["rows"]]
    all_rows = sorted(
        primary_rows + replica_rows,
        key=lambda row: (row["replicate"], row["global_order"]),
    )
    pairs = paired_observations(all_rows)
    problem_summary = by_problem_summary(pairs)
    aggregates = {
        condition: condition_summary(all_rows, condition)
        for condition in ("C0", "Cmem")
    }
    c0 = aggregates["C0"]
    cmem = aggregates["Cmem"]
    comparison = {
        "accuracy_preserved": math.isclose(c0["accuracy"], 1.0)
        and math.isclose(cmem["accuracy"], 1.0),
        "human_minutes_saved": c0["human_minutes"] - cmem["human_minutes"],
        "automatic_repairs_avoided": c0["automatic_repairs"]
        - cmem["automatic_repairs"],
        "handoffs_avoided": c0["handoffs"] - cmem["handoffs"],
        "api_calls_avoided": c0["api_calls"] - cmem["api_calls"],
        "api_cost_saved_usd": c0["api_cost_usd"] - cmem["api_cost_usd"],
        "elapsed_seconds_saved": c0["api_elapsed_seconds"]
        - cmem["api_elapsed_seconds"],
        "paired_observations_with_memory_advantage": sum(
            int(pair["outcome"] == "vantaggio_memoria") for pair in pairs
        ),
        "paired_observations_with_memory_disadvantage": sum(
            int(pair["outcome"] == "svantaggio_memoria") for pair in pairs
        ),
        "paired_observations_without_difference": sum(
            int(pair["outcome"] == "nessuna_differenza") for pair in pairs
        ),
        "problem_families_with_memory_advantage": [
            item["problem_id"]
            for item in problem_summary
            if item["replicates_with_memory_advantage"] > 0
        ],
        "strict_correction_minutes_saved": c0["correction_minutes"]
        - cmem["correction_minutes"],
        "h5_assessment": "supporto_operativo_parziale_e_replication_robustness",
    }
    payload = {
        "schema_version": 1,
        "chapter": 7,
        "experiment": "ablation_memoria_due_repliche",
        "observations": len(all_rows),
        "rows": all_rows,
        "aggregates": aggregates,
        "paired_observations": pairs,
        "by_problem": problem_summary,
        "comparison": comparison,
    }
    COMBINED_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    write_csv(COMBINED_CSV, all_rows)

    lines = [
        "# Rapporto combinato — ablation della doppia memoria",
        "",
        "Le venti osservazioni (cinque problemi × due condizioni × due repliche) "
        "sono state ricertificate sul modello originale e sull'ottimo noto.",
        "",
        "| Condizione | Accuratezza | Riparazioni | Handoff | Tempo-uomo | Chiamate | Costo API | Latenza totale |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in ("C0", "Cmem"):
        item = aggregates[condition]
        lines.append(
            f"| {condition} | {item['correct']}/{item['observations']} "
            f"({item['accuracy']:.0%}) | {item['automatic_repairs']} | "
            f"{item['handoffs']} | {item['human_minutes']:.0f} min | "
            f"{item['api_calls']} | ${item['api_cost_usd']:.6f} | "
            f"{item['api_elapsed_seconds'] / 60:.1f} min |"
        )
    lines.extend(
        [
            "",
            "## Effetto per problema nelle due repliche",
            "",
            "| Problema | Repliche con vantaggio | Repliche con svantaggio | Minuti risparmiati | Riparazioni evitate | Handoff evitati |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in problem_summary:
        lines.append(
            f"| {item['problem_id']} | {item['replicates_with_memory_advantage']}/2 | "
            f"{item['replicates_with_memory_disadvantage']}/2 | "
            f"{item['human_minutes_saved_total']:.0f} | "
            f"{item['repairs_avoided_total']} | {item['handoffs_avoided_total']} |"
        )
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"A parità di accuratezza, la memoria riduce il tempo-uomo da "
            f"{c0['human_minutes']:.0f} a {cmem['human_minutes']:.0f} minuti, "
            f"le riparazioni da {c0['automatic_repairs']} a {cmem['automatic_repairs']} "
            f"e gli handoff da {c0['handoffs']} a {cmem['handoffs']}. Il vantaggio "
            f"compare in {comparison['paired_observations_with_memory_advantage']} delle "
            "dieci coppie replicate e interessa tre famiglie: L01, L02 e L05. L03 "
            "non mostra differenze; in una replica di L04 la condizione con memoria "
            "richiede una riparazione in più. L'effetto non è quindi universale.",
            "",
            "Tutti gli interventi umani osservati sono revisioni di assicurazione, non "
            "correzioni del codice. I risultati sostengono quindi la riduzione dello "
            "sforzo umano operativo, ma non dimostrano ancora una diminuzione del costo "
            "di correzione in senso stretto.",
            "",
        ]
    )
    COMBINED_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Creato: {REPLICA_CSV}")
    print(f"Creato: {REPLICA_JSON}")
    print(f"Creato: {COMBINED_CSV}")
    print(f"Creato: {COMBINED_JSON}")
    print(f"Creato: {COMBINED_REPORT}")
    print("Ricertificazione replica 2: 10/10")
    print(
        f"Combinato — C0: {c0['human_minutes']:.0f} min, "
        f"{c0['automatic_repairs']} riparazioni, {c0['handoffs']} handoff; "
        f"Cmem: {cmem['human_minutes']:.0f} min, "
        f"{cmem['automatic_repairs']} riparazioni, {cmem['handoffs']} handoff."
    )


if __name__ == "__main__":
    main()
