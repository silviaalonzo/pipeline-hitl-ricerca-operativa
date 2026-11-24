#!/usr/bin/env python3
"""Esegue la sequenza congelata dello Scenario B con checkpoint per ogni run."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
ERRORS = HERE / "batch_errors.jsonl"
PROGRESS = HERE / "batch_progress.json"


def run_dir(row: dict) -> Path:
    return HERE / "runs" / "B" / row["model"] / row["problem_id"] / f"run_{int(row['replicate']):02d}"


def completed(row: dict) -> bool:
    return (run_dir(row) / "validation.json").exists()


def log_error(row: dict, stage: str, attempt: int, message: str) -> None:
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sequence": int(row["sequence"]),
        "model": row["model"],
        "problem_id": row["problem_id"],
        "replicate": int(row["replicate"]),
        "stage": stage,
        "attempt": attempt,
        "message": message[-4000:],
    }
    with ERRORS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def call(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=HERE, text=True, capture_output=True, timeout=timeout)


def api_call(row: dict) -> bool:
    for attempt in range(1, 4):
        cmd = [
            PYTHON, "run_scenario_b.py", "--model", row["model"],
            "--problem", row["problem_id"], "--run", str(row["replicate"]), "--overwrite",
        ]
        try:
            result = call(cmd, timeout=900)
        except subprocess.TimeoutExpired as exc:
            log_error(row, "api", attempt, f"timeout: {exc}")
            result = None
        if result is not None and result.returncode == 0:
            print(result.stdout.strip(), flush=True)
            return True
        message = "" if result is None else (result.stderr or result.stdout)
        log_error(row, "api", attempt, message)
        if attempt < 3:
            time.sleep(15 * attempt)
    return False


def execute_and_validate(row: dict) -> bool:
    directory = run_dir(row)
    execution = call([PYTHON, "execute_response.py", "--run-dir", str(directory), "--approve"], timeout=360)
    if execution.returncode != 0:
        log_error(row, "execution", 1, execution.stderr or execution.stdout)
        return False
    validation = call([PYTHON, "validate_candidate.py", "--run-dir", str(directory)], timeout=60)
    if validation.returncode != 0:
        log_error(row, "validation", 1, validation.stderr or validation.stdout)
        return False
    return True


def refresh_results() -> None:
    subprocess.run([PYTHON, "audit_scenario_b.py"], cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def save_progress(schedule: list[dict], current_sequence: int | None = None) -> None:
    done = sum(completed(row) for row in schedule)
    payload = {
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "completed": done,
        "total": len(schedule),
        "current_sequence": current_sequence,
        "remaining": len(schedule) - done,
    }
    PROGRESS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    schedule_path = HERE / "batch_schedule.csv"
    if not schedule_path.exists() or not (HERE / "protocol_manifest.json").exists():
        raise FileNotFoundError("Eseguire prima freeze_protocol.py")
    with schedule_path.open(encoding="utf-8") as handle:
        schedule = list(csv.DictReader(handle))

    save_progress(schedule)
    for row in schedule:
        if completed(row):
            continue
        seq = int(row["sequence"])
        print(
            f"[{seq}/{len(schedule)}] {row['model']} {row['problem_id']} run {row['replicate']}",
            flush=True,
        )
        save_progress(schedule, seq)
        if not (run_dir(row) / "response.json").exists() and not api_call(row):
            print("  API fallita dopo 3 tentativi; run lasciato in sospeso", flush=True)
            continue
        if execute_and_validate(row):
            print("  completato", flush=True)
        else:
            print("  output non validabile automaticamente; registrato per revisione", flush=True)
        refresh_results()
        save_progress(schedule, seq)

    refresh_results()
    save_progress(schedule)
    remaining = sum(not completed(row) for row in schedule)
    print(f"Batch terminato; run senza validation.json: {remaining}", flush=True)
    sys.exit(0 if remaining == 0 else 3)


if __name__ == "__main__":
    main()
