#!/usr/bin/env python3
"""Esegue in ordine le dieci prove Cmem/C0 e si arresta al primo handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
CAP5_CODE = ROOT / "esperimenti_cap5"
DATASET = ROOT / "dataset_cap7"
MODEL_KEY = "deepseek-v4-flash"

sys.path.insert(0, str(CAP5_CODE))
import scenario_c_core as core  # noqa: E402
from cap7_aliases import remap_cap7_candidate  # noqa: E402


# Riferimenti immutabili alle funzioni originali: configure_core viene richiamata
# più volte e non deve impilare wrapper appartenenti a condizioni precedenti.
BASE_CALL_OPENROUTER = core.call_openrouter
BASE_NEW_STATE = core.new_state
BASE_FINALIZE_PROBLEM = core.finalize_problem
BASE_LOAD_CONFIG = core.load_config
BASE_AUDIT_CANDIDATE = core.audit_candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_protocol() -> dict:
    path = HERE / "protocol.json"
    if not path.exists():
        raise FileNotFoundError("Eseguire prima esperimenti_cap7/freeze_protocol.py")
    return json.loads(path.read_text(encoding="utf-8"))


def schedule_rows() -> list[dict]:
    with (HERE / "schedule.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def condition_root(condition: str) -> Path:
    if condition not in {"Cmem", "C0"}:
        raise ValueError(condition)
    return HERE / "conditions" / condition


def memory_file(condition: str) -> Path:
    return condition_root(condition) / "memory" / f"{MODEL_KEY}.json"


def configure_core(condition: str, protocol: dict) -> None:
    """Adatta il runner già verificato del Capitolo 5 al dataset del Capitolo 7."""
    root = condition_root(condition)
    core.DATASET_ROOT = DATASET
    core.GROUND_TRUTH_PATH = DATASET / "ground_truth.json"
    core.PROBLEMS_PATH = DATASET / "problems.jsonl"
    core.SCENARIO_ROOT = root
    core.INITIAL_SYSTEM_PATH = HERE / "system_prompt_cap7.txt"

    def frozen_model_config(model_name: str) -> dict:
        config = dict(BASE_LOAD_CONFIG(model_name))
        config["reasoning_effort"] = protocol["model_configuration"]["reasoning_effort"]
        config["max_output_tokens"] = int(
            protocol["model_configuration"]["max_output_tokens"]
        )
        return config

    def retrieve_all(model_name: str, problem: dict, scenario_root: Path = root) -> dict:
        memory = core.load_memory(model_name, scenario_root)
        return {
            "model": model_name,
            "problem_id": problem["id"],
            "retrieved_at_utc": core.utc_now(),
            "semantic": list(memory.get("semantic", [])),
            "episodic": list(memory.get("episodic", [])),
            "semantic_count_total": len(memory.get("semantic", [])),
            "episodic_count_total": len(memory.get("episodic", [])),
            "retrieval_policy": "full_frozen_snapshot",
            "condition": condition,
        }

    def render_with_ids(retrieval: dict) -> str:
        lines = [
            "MEMORIA DELLA PIPELINE (gli elementi sono correzioni precedenti, non soluzioni del problema corrente):"
        ]
        if not retrieval.get("semantic") and not retrieval.get("episodic"):
            lines.append("- Memoria vuota: nessuna correzione precedente disponibile.")
        for item in retrieval.get("semantic", []):
            lines.append(f"- Principio [{item['id']}]: {item['principle']}")
        for item in retrieval.get("episodic", []):
            lines.append(
                f"- Episodio [{item['id']}]: dominio={item.get('domain', '')}; "
                f"errore={item.get('failure_class', '')}; "
                f"correzione={item.get('correction_summary', '')}"
            )
        lines.append(
            "Nel campo memory_items_used di TRACEABILITY_JSON indica soltanto gli ID effettivamente applicati."
        )
        return "\n".join(lines)

    # Durante l'ablation gli interventi vengono registrati ma non modificano la memoria.
    def do_not_commit_memory(model_name: str, state: dict, scenario_root: Path = root) -> None:
        state["memory_update_suppressed"] = True

    def audit_with_cap7_aliases(record: dict, candidate: dict):
        remapped, cap7_aliases = remap_cap7_candidate(record["id"], candidate)
        algebraic, independent, legacy_aliases = BASE_AUDIT_CANDIDATE(record, remapped)
        return algebraic, independent, {**cap7_aliases, **legacy_aliases}

    def tagged_call(model_name: str, system: str, user_prompt: str, attempt_dir: Path, metadata: dict):
        metadata = dict(metadata)
        metadata.update({"chapter": 7, "condition": condition, "memory_frozen": True})
        return BASE_CALL_OPENROUTER(model_name, system, user_prompt, attempt_dir, metadata)

    def tagged_new_state(model_name: str, problem: dict, sequence: int, retrieval: dict) -> dict:
        state = BASE_NEW_STATE(model_name, problem, sequence, retrieval)
        state.update({"chapter": 7, "condition": condition, "memory_frozen": True})
        return state

    def tagged_finalize(run_dir: Path, state: dict, correct: bool, final_attempt: dict | None, scenario_root: Path = root):
        result = BASE_FINALIZE_PROBLEM(run_dir, state, correct, final_attempt, scenario_root)
        result.update({"chapter": 7, "condition": condition, "memory_frozen": True})
        core.save_json(run_dir / "final.json", result)
        core.save_state(run_dir, state)
        return result

    core.retrieve_memory = retrieve_all
    core.render_memory_context = render_with_ids
    core.commit_memory = do_not_commit_memory
    core.audit_candidate = audit_with_cap7_aliases
    core.load_config = frozen_model_config
    core.call_openrouter = tagged_call
    core.new_state = tagged_new_state
    core.finalize_problem = tagged_finalize

    expected = protocol["memory_sha256"][condition]
    actual = sha256(memory_file(condition))
    if actual != expected:
        raise RuntimeError(f"La memoria {condition} è cambiata: atteso {expected}, trovato {actual}")


def row_run_dir(row: dict) -> Path:
    return core.problem_dir(
        row["model"], int(row["pair_sequence"]), row["problem_id"], condition_root(row["condition"])
    )


def row_status(row: dict) -> str:
    run_dir = row_run_dir(row)
    final = core.load_json(run_dir / "final.json")
    if final:
        return "COMPLETED" if final.get("correct") else "COMPLETED_FAILURE"
    state = core.load_json(run_dir / "state.json")
    return str((state or {}).get("status", "PENDING"))


def print_status(rows: list[dict]) -> None:
    completed = 0
    for row in rows:
        status = row_status(row)
        completed += int(status.startswith("COMPLETED"))
        print(
            f"{int(row['global_order']):02d}/10  {row['problem_id']}  {row['condition']:<4}  {status}"
        )
    print(f"Completate: {completed}/10")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--max-runs", type=int, default=10)
    args = parser.parse_args()

    protocol = load_protocol()
    rows = schedule_rows()
    if args.status:
        print_status(rows)
        return

    advanced = 0
    for row in rows:
        status = row_status(row)
        if status.startswith("COMPLETED"):
            continue
        if advanced >= args.max_runs:
            break
        condition = row["condition"]
        configure_core(condition, protocol)
        before = sha256(memory_file(condition))
        result = core.advance_problem(
            row["model"],
            row["problem_id"],
            int(row["pair_sequence"]),
            scenario_root=condition_root(condition),
        )
        after = sha256(memory_file(condition))
        if before != after or after != protocol["memory_sha256"][condition]:
            raise RuntimeError(f"La memoria {condition} è stata modificata durante la prova")

        if result["status"] == "AWAITING_HANDOFF":
            print(f"HANDOFF RICHIESTO — {row['problem_id']} {condition}")
            print(result["handoff_dir"])
            print("La campagna è sospesa prima della prova successiva.")
            raise SystemExit(4)

        final = result.get("final") or {}
        print(
            f"[{row['global_order']}/10] {row['problem_id']} {condition}: "
            f"{'CORRETTO' if final.get('correct') else 'NON CORRETTO'}; "
            f"tentativi={final.get('attempt_count')}; handoff={final.get('handoff_count')}"
        )
        advanced += 1

    print_status(rows)


if __name__ == "__main__":
    main()
