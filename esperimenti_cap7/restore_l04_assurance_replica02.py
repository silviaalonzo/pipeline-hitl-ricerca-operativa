#!/usr/bin/env python3
"""Ripristina la revisione di assicurazione saltata su L04-Cmem/replica 2."""

from __future__ import annotations

import json

import run_replication_02 as replica


def main() -> None:
    protocol = replica.primary.load_protocol()
    replica.configure("Cmem", protocol)
    core = replica.primary.core
    row = next(
        item
        for item in replica.schedule_rows()
        if item["condition"] == "Cmem" and item["problem_id"] == "L04"
    )
    run_dir = replica.row_run_dir(row)
    state = core.load_json(run_dir / "state.json")
    if not state or state.get("status") != "COMPLETED":
        raise RuntimeError("L04-Cmem non è nello stato COMPLETED atteso")
    if core.automatic_repair_count(state) < 1:
        raise RuntimeError("Non risultano riparazioni automatiche da sottoporre a revisione")
    if state.get("stage_2_assurance_completed"):
        raise RuntimeError("La revisione di assicurazione risulta già completata")

    final_path = run_dir / "final.json"
    archived_final = run_dir / "final_pre_assurance.json"
    if not final_path.exists() or archived_final.exists():
        raise RuntimeError("Stato inatteso dei file finali")
    final_path.replace(archived_final)

    state["status"] = "RUNNING"
    state["pending_handoff"] = None
    core.save_state(run_dir, state)
    review_request = {
        "success": False,
        "repairable": False,
        "stage": 2,
        "failure_class": "revisione_di_assicurazione_post_riparazione",
        "detail": (
            "Problema di difficoltà elevata risolto dopo almeno una riparazione "
            "automatica: il protocollo richiede una revisione umana prima dell'accettazione."
        ),
        "handoff_mode": "ASSURANCE_REVIEW",
    }
    handoff_dir = core.create_handoff(
        run_dir,
        state,
        core.prompt_for("L04"),
        review_request,
    )

    amendments_path = replica.REPLICA_ROOT / "protocol_amendments.json"
    amendments = json.loads(amendments_path.read_text(encoding="utf-8"))
    amendments.append(
        {
            "recorded_at_utc": core.utc_now(),
            "replicate": 2,
            "condition": "Cmem",
            "problem_id": "L04",
            "reason": (
                "L'annullamento del falso handoff sugli alias aveva finalizzato direttamente "
                "una soluzione ottenuta dopo riparazione automatica, saltando la revisione "
                "di assicurazione prevista per i problemi di difficoltà elevata."
            ),
            "action": "restore_required_stage_2_assurance_review",
            "previous_final_preserved_as": "final_pre_assurance.json",
            "handoff_dir": str(handoff_dir.relative_to(replica.REPLICA_ROOT)),
        }
    )
    amendments_path.write_text(
        json.dumps(amendments, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(handoff_dir)


if __name__ == "__main__":
    main()
