#!/usr/bin/env python3
"""Controlli pre-esecuzione senza chiamare il modello."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import gurobipy as gp
import httpx
from gurobipy import GRB


ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
DATASET = ROOT / "dataset_cap7"
CAP5_CODE = ROOT / "esperimenti_cap5"
sys.path.insert(0, str(CAP5_CODE))

import scenario_c_core as core  # noqa: E402
from run_scenario_b import load_config  # noqa: E402
from secret_store import get_api_key  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def check_gurobi() -> None:
    model = gp.Model("cap7_setup_check")
    model.Params.OutputFlag = 0
    x = model.addVar(vtype=GRB.BINARY, name="x")
    model.setObjective(x, GRB.MAXIMIZE)
    model.optimize()
    if model.Status != GRB.OPTIMAL or abs(x.X - 1) > 1e-9:
        raise RuntimeError("Gurobi non supera il test minimo")
    print(f"Gurobi: OK — {'.'.join(map(str, gp.gurobi.version()))}")


def check_key() -> None:
    key = get_api_key("openrouter", required=False)
    if not key:
        raise RuntimeError("Chiave OpenRouter assente")
    response = httpx.get(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    response.raise_for_status()
    print("OpenRouter: chiave riconosciuta")


def check_dataset_and_validator() -> None:
    records = json.loads((DATASET / "ground_truth.json").read_text(encoding="utf-8"))
    public_records = [
        json.loads(line)
        for line in (DATASET / "problems.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    prompts = sorted((DATASET / "prompts").glob("L[0-9][0-9].md"))
    if len(records) != 5 or len(public_records) != 5 or len(prompts) != 5:
        raise AssertionError("Attesi cinque prompt e cinque record di ground truth")
    if {row.get("dataset_version") for row in public_records} != {"definitivo_v2"}:
        raise AssertionError("Versione del dataset inattesa")
    verification = json.loads(
        (DATASET / "verification_report.json").read_text(encoding="utf-8")
    )
    if (
        not verification.get("certified")
        or verification.get("problem_count") != 5
        or any(
            row.get("status") != "OPTIMAL" or float(row.get("mip_gap", 1.0)) != 0.0
            for row in verification.get("problems", [])
        )
    ):
        raise AssertionError("La certificazione indipendente del dataset non è valida")
    target_audit = json.loads(
        (DATASET / "target_pattern_audit.json").read_text(encoding="utf-8")
    )
    if len(target_audit) != 5 or not all(
        row.get("target_is_consequential") for row in target_audit
    ):
        raise AssertionError("L'audit dei pattern bersaglio non è valido")
    core.DATASET_ROOT = DATASET
    core.GROUND_TRUTH_PATH = DATASET / "ground_truth.json"
    core.PROBLEMS_PATH = DATASET / "problems.jsonl"
    for record in records:
        candidate = {
            "status": "OPTIMAL",
            "objective": record["solution"]["objective"],
            "variables": record["solution"]["variables"],
        }
        private, _ = core.definitive_validation(record["id"], candidate)
        if not private["correct"]:
            raise AssertionError(f"Il validatore respinge la ground truth di {record['id']}")
        text = (DATASET / "prompts" / f"{record['id']}.md").read_text(encoding="utf-8")
        if record["source_problem"] in text or record["target_principle_id"] in text:
            raise AssertionError(f"Informazione riservata presente nel prompt {record['id']}")
    print("Dataset e validatore: OK — cinque ground truth accettate")


def check_protocol_and_memory() -> None:
    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    if protocol.get("dataset_version") != "definitivo_v2":
        raise AssertionError("Il protocollo non punta al dataset definitivo v2")
    for relative_path, expected in protocol.get("artifact_sha256", {}).items():
        path = ROOT / relative_path
        if not path.exists() or sha256(path) != expected:
            raise AssertionError(f"Artefatto modificato dopo il congelamento: {relative_path}")
    for condition in ("Cmem", "C0"):
        path = HERE / "conditions" / condition / "memory" / "deepseek-v4-flash.json"
        if sha256(path) != protocol["memory_sha256"][condition]:
            raise AssertionError(f"Hash della memoria {condition} non valido")
        memory = json.loads(path.read_text(encoding="utf-8"))
        expected = 5 if condition == "Cmem" else 0
        if len(memory["semantic"]) != expected or len(memory["episodic"]) != expected:
            raise AssertionError(f"Contenuto della memoria {condition} inatteso")
    config = load_config("deepseek-v4-flash")
    if config["model"] != "deepseek/deepseek-v4-flash" or config["upstream_provider"] != "deepseek":
        raise AssertionError("Configurazione DeepSeek diversa da quella congelata nel Capitolo 5")
    if protocol["model_configuration"]["reasoning_effort"] != "high":
        raise AssertionError("Reasoning effort diverso da high")
    if int(protocol["model_configuration"]["max_output_tokens"]) != 64000:
        raise AssertionError("Il limite ufficiale del Capitolo 7 deve essere 64.000 token")
    print("Protocollo e memorie: OK — snapshot separati e congelati")


if __name__ == "__main__":
    check_gurobi()
    check_dataset_and_validator()
    check_protocol_and_memory()
    check_key()
    print("Configurazione del Capitolo 7 completa.")
