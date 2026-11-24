#!/usr/bin/env python3
"""Componenti riproducibili della pipeline HITL dello Scenario C.

Il modulo mantiene separati quattro livelli:

* risposta grezza del modello;
* esecuzione prudente del codice;
* validazione privata contro il modello originale;
* pacchetto pubblico per l'esperto, privo di ottimo e soluzione certificata.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_scenario_b import audit_candidate
from execute_response import extract_code, parse_solution, static_check
from run_scenario_b import load_config
from secret_store import get_api_key


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCENARIO_ROOT = Path(
    os.environ.get("SCENARIO_C_ROOT", str(ROOT / "scenario_c"))
).expanduser().resolve()
DATASET_ROOT = ROOT / "dataset_cap4"
GROUND_TRUTH_PATH = DATASET_ROOT / "ground_truth.json"
PROBLEMS_PATH = DATASET_ROOT / "problems.jsonl"
INITIAL_SYSTEM_PATH = HERE / "system_prompt_c.txt"
REPAIR_SYSTEM_PATH = HERE / "system_prompt_repair_c.txt"

MAX_SELF_REPAIR = 3
MAX_TRACEABILITY_REPAIR = 1
MIN_TRACEABILITY_MAPPINGS = 4
SOLVER_TIMEOUT_SECONDS = 300
GAP_TOLERANCE = 1e-3


class RoutingIdentityError(RuntimeError):
    """Il gateway ha usato un modello o un provider fuori dalla configurazione."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def model_slug(model_name: str) -> str:
    return model_name.replace("/", "_").replace(" ", "_")


def json_safe(value: Any) -> Any:
    """Converte i valori non JSON (in particolare ±inf/NaN dei validatori)."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(json_safe(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_problems() -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in PROBLEMS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["id"]: row for row in rows}


def load_ground_truth_records() -> dict[str, dict]:
    return {
        row["id"]: row
        for row in json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    }


def model_identity_matches(requested: str, actual: str | None) -> bool:
    """Accetta l'ID richiesto e la sua revisione esplicita, non modelli diversi."""
    if actual == requested:
        return True
    return bool(
        requested == "deepseek/deepseek-v4-flash"
        and actual
        and actual.startswith(requested + "-")
    )


def prompt_for(problem_id: str) -> str:
    path = DATASET_ROOT / "prompts" / f"{problem_id}.md"
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def empty_memory(model_name: str) -> dict:
    return {
        "schema_version": 1,
        "model": model_name,
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "episodic": [],
        "semantic": [],
    }


def memory_path(model_name: str, scenario_root: Path = SCENARIO_ROOT) -> Path:
    return scenario_root / "memory" / f"{model_slug(model_name)}.json"


def load_memory(model_name: str, scenario_root: Path = SCENARIO_ROOT) -> dict:
    path = memory_path(model_name, scenario_root)
    memory = load_json(path)
    if memory is None:
        memory = empty_memory(model_name)
        save_json(path, memory)
    if memory.get("model") != model_name:
        raise ValueError(f"Memoria associata al modello errato: {path}")
    return memory


def retrieve_memory(
    model_name: str,
    problem: dict,
    scenario_root: Path = SCENARIO_ROOT,
) -> dict:
    """Recupera principi e pochi episodi pertinenti senza usare la ground truth."""
    memory = load_memory(model_name, scenario_root)
    domain = str(problem.get("domain", "")).casefold()
    model_class = str(problem.get("model_class", "")).casefold()

    def score(item: dict) -> tuple[int, str]:
        tags = {str(tag).casefold() for tag in item.get("tags", [])}
        value = 0
        if domain and domain in tags:
            value += 3
        if model_class and model_class in tags:
            value += 2
        if not tags:
            value += 1
        return value, str(item.get("created_at_utc", ""))

    semantic_ranked = sorted(memory.get("semantic", []), key=score, reverse=True)
    semantic = [item for item in semantic_ranked if score(item)[0] > 0][:8]

    episodic_ranked = sorted(memory.get("episodic", []), key=score, reverse=True)
    episodic = [item for item in episodic_ranked if score(item)[0] > 0][:2]
    return {
        "model": model_name,
        "problem_id": problem["id"],
        "retrieved_at_utc": utc_now(),
        "semantic": semantic,
        "episodic": episodic,
        "semantic_count_total": len(memory.get("semantic", [])),
        "episodic_count_total": len(memory.get("episodic", [])),
    }


def render_memory_context(retrieval: dict) -> str:
    lines = [
        "MEMORIA DELLA PIPELINE (usa solo gli elementi pertinenti; non sono soluzioni del problema corrente):"
    ]
    if not retrieval.get("semantic") and not retrieval.get("episodic"):
        lines.append("- Memoria vuota: nessuna correzione precedente disponibile.")
        return "\n".join(lines)
    for item in retrieval.get("semantic", []):
        lines.append(f"- Principio: {item['principle']}")
    for item in retrieval.get("episodic", []):
        lines.append(
            "- Episodio precedente: "
            f"dominio={item.get('domain', '')}; errore={item.get('failure_class', '')}; "
            f"correzione={item.get('correction_summary', '')}"
        )
    return "\n".join(lines)


def build_initial_prompt(problem_text: str, retrieval: dict) -> str:
    return (
        f"{problem_text.rstrip()}\n\n"
        "---\n"
        f"{render_memory_context(retrieval)}\n\n"
        "Applica la checklist di tracciabilità richiesta dal messaggio di sistema e poi produci la formulazione "
        "e il codice completo. Non usare dati diversi da quelli presenti nella traccia."
    )


def build_traceability_repair_prompt(
    problem_text: str,
    retrieval: dict,
    traceability: dict,
) -> str:
    errors = traceability.get("errors") or ["riga TRACEABILITY_JSON assente o incompleta"]
    return (
        f"{problem_text.rstrip()}\n\n"
        "---\n"
        f"{render_memory_context(retrieval)}\n\n"
        "CONTROLLO AUTOMATICO DELLA TRACCIABILITÀ NON SUPERATO:\n"
        + "\n".join(f"- {error}" for error in errors)
        + "\n\nRigenera l'intera risposta nel formato richiesto dal messaggio di sistema. "
        "La prima riga deve essere un solo TRACEABILITY_JSON valido; se la traccia è completa, "
        f"requirements_mapped deve contenere almeno {MIN_TRACEABILITY_MAPPINGS} corrispondenze "
        "concrete nella forma «requisito -> elemento del modello». Produci nuovamente anche "
        "formulazione, codice completo e sintesi, senza aggiungere dati alla traccia."
    )


def compact(text: str, limit: int = 16000) -> str:
    value = text.strip()
    if len(value) <= limit:
        return value
    return value[: limit // 2] + "\n...[contenuto abbreviato]...\n" + value[-limit // 2 :]


def build_repair_prompt(
    problem_text: str,
    retrieval: dict,
    failure: dict,
    previous_code: str,
    cycle: int,
) -> str:
    category = failure.get("failure_class", "errore_non_classificato")
    detail = compact(str(failure.get("detail", "")), 8000)
    if category == "output_troncato_o_senza_codice":
        code_section = "La risposta precedente non ha prodotto codice estraibile. Non ripeterne le spiegazioni."
    else:
        code_section = f"CODICE PRECEDENTE:\n```python\n{compact(previous_code, 18000)}\n```"
    return (
        f"TRACCIA ORIGINALE:\n{problem_text.rstrip()}\n\n"
        f"{render_memory_context(retrieval)}\n\n"
        f"CICLO DI SELF-REPAIR {cycle}/{MAX_SELF_REPAIR}\n"
        f"Categoria: {category}\nDettaglio verificabile:\n{detail}\n\n"
        f"{code_section}\n\n"
        "Correggi soltanto ciò che impedisce l'esecuzione o la soluzione del modello. "
        "Restituisci esclusivamente il singolo blocco Python richiesto."
    )


def build_expert_prompt(
    problem_text: str,
    retrieval: dict,
    failure: dict,
    previous_code: str,
    expert_response: dict,
) -> str:
    return (
        f"TRACCIA ORIGINALE:\n{problem_text.rstrip()}\n\n"
        f"{render_memory_context(retrieval)}\n\n"
        "ISTRUZIONE DELL'ESPERTO UMANO:\n"
        f"{expert_response['expert_instruction'].strip()}\n\n"
        "ERRORE CHE HA ATTIVATO L'HANDOFF:\n"
        f"{compact(str(failure.get('detail', '')), 8000)}\n\n"
        "CODICE PRECEDENTE (se disponibile):\n"
        f"```python\n{compact(previous_code, 18000)}\n```\n\n"
        "Applica esattamente la correzione indicata dall'esperto e restituisci esclusivamente il codice completo."
    )


def call_openrouter(
    model_name: str,
    system: str,
    user_prompt: str,
    attempt_dir: Path,
    metadata: dict,
) -> tuple[str, dict]:
    """Esegue una chiamata idempotente e separa i retry di trasporto dai self-repair."""
    response_path = attempt_dir / "response.json"
    text_path = attempt_dir / "response.txt"
    if response_path.exists() and text_path.exists():
        return text_path.read_text(encoding="utf-8").rstrip("\n"), load_json(response_path)

    from openai import OpenAI

    config = load_config(model_name)
    attempt_dir.mkdir(parents=True, exist_ok=True)
    request = {
        "scenario": "C",
        "model_key": model_name,
        "provider": config["provider"],
        "model": config["model"],
        "configuration": config,
        "created_at_utc": utc_now(),
        "metadata": metadata,
        "system_prompt": system,
        "user_prompt": user_prompt,
    }
    save_json(attempt_dir / "request.json", request)

    client = OpenAI(
        api_key=get_api_key("openrouter"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/tesi-cap5",
            "X-Title": "Tesi HITL OR - Scenario C",
        },
    )
    transport_errors = []
    for transport_attempt in range(1, 4):
        started = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=config["max_output_tokens"],
                extra_body={
                    "reasoning": {"effort": config["reasoning_effort"], "exclude": False},
                    "provider": {
                        "only": [config["upstream_provider"]],
                        "allow_fallbacks": False,
                        "require_parameters": True,
                    },
                },
            )
            elapsed = time.perf_counter() - started
            raw = response.model_dump(mode="json")
            raw["_experiment"] = {
                "elapsed_seconds": elapsed,
                "completed_at_utc": utc_now(),
                "transport_attempt": transport_attempt,
            }
            raw["_routing_request"] = {
                "gateway": "openrouter",
                "requested_model": config["model"],
                "required_provider": config["upstream_provider"],
                "allow_fallbacks": False,
                "require_parameters": True,
            }
            actual_model = raw.get("model")
            actual_provider = str(raw.get("provider", "")).casefold()
            if not model_identity_matches(config["model"], actual_model):
                save_json(attempt_dir / f"rejected_response_{transport_attempt}.json", raw)
                raise RoutingIdentityError(f"Modello effettivo inatteso: {actual_model}")
            if actual_provider != str(config["upstream_provider"]).casefold():
                save_json(attempt_dir / f"rejected_response_{transport_attempt}.json", raw)
                raise RoutingIdentityError(f"Provider effettivo inatteso: {raw.get('provider')}")
            raw["_routing_request"]["actual_model"] = actual_model
            raw["_routing_request"]["resolved_revision"] = actual_model != config["model"]
            text = response.choices[0].message.content or ""
            save_json(response_path, raw)
            text_path.write_text(text + "\n", encoding="utf-8")
            if transport_errors:
                save_json(attempt_dir / "transport_errors.json", transport_errors)
            return text, raw
        except RoutingIdentityError as exc:
            transport_errors.append(
                {
                    "attempt": transport_attempt,
                    "at_utc": utc_now(),
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            save_json(attempt_dir / "transport_errors.json", transport_errors)
            raise
        except Exception as exc:  # i retry di rete non devono diventare errori del modello
            transport_errors.append(
                {
                    "attempt": transport_attempt,
                    "at_utc": utc_now(),
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            save_json(attempt_dir / "transport_errors.json", transport_errors)
            if transport_attempt == 3:
                raise
            time.sleep(10 * transport_attempt)
    raise AssertionError("Flusso di retry non raggiungibile")


def parse_traceability(text: str) -> dict:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("TRACEABILITY_JSON=")
    ]
    if not lines:
        return {
            "present": False,
            "valid": False,
            "complete_ready": False,
            "needs_expert": False,
            "errors": ["riga TRACEABILITY_JSON assente"],
        }
    if len(lines) != 1:
        return {
            "present": True,
            "valid": False,
            "complete_ready": False,
            "needs_expert": False,
            "errors": [f"attesa una sola riga TRACEABILITY_JSON, trovate {len(lines)}"],
        }

    raw = lines[0].split("=", 1)[1].strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "present": True,
            "valid": False,
            "complete_ready": False,
            "needs_expert": False,
            "errors": [f"JSON non valido: {exc}"],
        }
    if not isinstance(value, dict):
        return {
            "present": True,
            "valid": False,
            "complete_ready": False,
            "needs_expert": False,
            "errors": ["TRACEABILITY_JSON deve contenere un oggetto JSON"],
        }

    errors = []
    required = {"status", "unresolved", "undefined_symbols", "requirements_mapped"}
    missing = sorted(required - set(value))
    if missing:
        errors.append("campi obbligatori mancanti: " + ", ".join(missing))
    status = str(value.get("status", "")).upper()
    if status not in {"READY", "NEEDS_EXPERT"}:
        errors.append("status deve essere READY oppure NEEDS_EXPERT")
    for field in ("unresolved", "undefined_symbols", "requirements_mapped"):
        if field in value and not isinstance(value[field], list):
            errors.append(f"{field} deve essere una lista")

    unresolved = value.get("unresolved") if isinstance(value.get("unresolved"), list) else []
    undefined = (
        value.get("undefined_symbols")
        if isinstance(value.get("undefined_symbols"), list)
        else []
    )
    mappings = (
        value.get("requirements_mapped")
        if isinstance(value.get("requirements_mapped"), list)
        else []
    )
    needs_expert = status == "NEEDS_EXPERT" or bool(unresolved or undefined)
    mapping_errors = [
        item
        for item in mappings
        if not isinstance(item, str) or not item.strip() or "->" not in item
    ]
    if status == "READY" and len(mappings) < MIN_TRACEABILITY_MAPPINGS:
        errors.append(
            f"requirements_mapped contiene {len(mappings)} elementi; ne servono almeno "
            f"{MIN_TRACEABILITY_MAPPINGS}"
        )
    if status == "READY" and mapping_errors:
        errors.append(
            "ogni elemento di requirements_mapped deve essere una stringa non vuota con '->'"
        )
    valid = not errors
    complete_ready = bool(valid and status == "READY" and not needs_expert)
    return {
        "present": True,
        "valid": valid,
        "complete_ready": complete_ready,
        "value": value,
        "needs_expert": needs_expert,
        "errors": errors,
    }


def response_is_empty_truncation(text: str, raw_response: dict) -> bool:
    finish_reason = ((raw_response.get("choices") or [{}])[0]).get("finish_reason") or ""
    return finish_reason == "length" and not text.strip()


def automatic_repair_count(state: dict) -> int:
    return sum(
        1
        for attempt in state.get("attempts", [])
        if attempt.get("kind") in {"TRACEABILITY_REPAIR", "AUTO_REPAIR"}
    )


def stage_two_assurance_required(problem: dict, state: dict, evaluation: dict) -> bool:
    return bool(
        evaluation.get("success")
        and str(problem.get("difficulty", "")).casefold() == "elevata"
        and automatic_repair_count(state) > 0
        and not state.get("stage_2_assurance_completed", False)
    )


def execute_code(code: str, attempt_dir: Path, timeout: int = SOLVER_TIMEOUT_SECONDS) -> dict:
    code_path = attempt_dir / "generated.py"
    code_path.write_text(code, encoding="utf-8")
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "GRB_LICENSE_FILE": os.environ.get("GRB_LICENSE_FILE", str(Path.home() / "gurobi.lic")),
        "PYTHONIOENCODING": "utf-8",
    }
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(code_path)],
            cwd=attempt_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        execution = {
            "returncode": proc.returncode,
            "timed_out": False,
            "elapsed_seconds": time.perf_counter() - started,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        execution = {
            "returncode": None,
            "timed_out": True,
            "elapsed_seconds": time.perf_counter() - started,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }
    save_json(attempt_dir / "execution.json", execution)
    return execution


def definitive_validation(problem_id: str, candidate: dict) -> tuple[dict, dict]:
    record = load_ground_truth_records()[problem_id]
    algebraic, independent, aliases = audit_candidate(record, candidate)
    optimum = float(record["solution"]["objective"])
    projected_objective = independent.get("projected_objective")
    relative_gap = None
    if projected_objective is not None:
        relative_gap = abs(float(projected_objective) - optimum) / max(1.0, abs(optimum))
    status_optimal = str(candidate.get("status", "")).upper() == "OPTIMAL"
    unknown_nonzero = independent.get("unknown_nonzero") or []
    decision_correct = bool(
        status_optimal
        and independent.get("projected_feasible")
        and relative_gap is not None
        and relative_gap <= GAP_TOLERANCE
        and not unknown_nonzero
        and not independent.get("duplicates")
    )
    declared = candidate.get("objective")
    declared_delta = None
    if declared is not None and projected_objective is not None:
        try:
            declared_delta = abs(float(declared) - float(projected_objective))
        except (TypeError, ValueError):
            pass
    declared_corrected = bool(decision_correct and (declared_delta is None or declared_delta > 1e-6))
    private = {
        "problem_id": problem_id,
        "validated_at_utc": utc_now(),
        "correct": decision_correct,
        "status_optimal": status_optimal,
        "known_optimum": optimum,
        "projected_feasible": independent.get("projected_feasible"),
        "projected_objective": projected_objective,
        "relative_gap": relative_gap,
        "gap_tolerance": GAP_TOLERANCE,
        "declared_objective": declared,
        "declared_objective_delta": declared_delta,
        "declared_objective_corrected_automatically": declared_corrected,
        "unknown_nonzero_variables": unknown_nonzero,
        "aliases": aliases,
        "auxiliary_variables_completed": independent.get("auxiliary_variables_completed") or [],
        "algebraic": algebraic,
        "independent": independent,
    }
    public = {
        "problem_id": problem_id,
        "correct": decision_correct,
        "candidate_status": candidate.get("status"),
        "feasible_in_original_problem": bool(independent.get("projected_feasible")),
        "gap_within_tolerance": bool(relative_gap is not None and relative_gap <= GAP_TOLERANCE),
        "declared_objective_corrected_automatically": declared_corrected,
        "max_constraint_violation": algebraic.get("max_violation"),
        "constraint_violations": algebraic.get("constraint_violations") or [],
        "bound_violations": algebraic.get("bound_violations") or [],
        "integrality_violations": algebraic.get("integrality_violations") or [],
        "unknown_nonzero_variables": unknown_nonzero,
        "missing_variables_assumed_zero": algebraic.get("missing_variables_assumed_zero") or [],
    }
    return private, public


def evaluate_response(
    problem_id: str,
    text: str,
    raw_response: dict,
    attempt_dir: Path,
) -> dict:
    finish_reason = ((raw_response.get("choices") or [{}])[0]).get("finish_reason") or ""
    try:
        code = extract_code(text)
    except (ValueError, SyntaxError) as exc:
        category = "output_troncato_o_senza_codice" if finish_reason == "length" else "codice_non_estratto"
        result = {
            "success": False,
            "repairable": True,
            "stage": 3,
            "failure_class": category,
            "detail": str(exc),
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result
    try:
        static_check(code)
    except (ValueError, SyntaxError) as exc:
        result = {
            "success": False,
            "repairable": True,
            "stage": 3,
            "failure_class": "controllo_statico_fallito",
            "detail": str(exc),
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result

    execution = execute_code(code, attempt_dir)
    if execution["timed_out"]:
        result = {
            "success": False,
            "repairable": True,
            "stage": 3,
            "failure_class": "timeout_solver",
            "detail": f"Esecuzione interrotta dopo {SOLVER_TIMEOUT_SECONDS} secondi",
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result
    if execution["returncode"] != 0:
        result = {
            "success": False,
            "repairable": True,
            "stage": 3,
            "failure_class": "errore_di_esecuzione",
            "detail": compact(execution.get("stderr") or execution.get("stdout") or "", 10000),
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result
    try:
        candidate = parse_solution(execution.get("stdout") or "")
    except (ValueError, json.JSONDecodeError) as exc:
        result = {
            "success": False,
            "repairable": True,
            "stage": 3,
            "failure_class": "soluzione_non_leggibile",
            "detail": str(exc),
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result
    save_json(attempt_dir / "candidate_solution.json", candidate)

    if str(candidate.get("status", "")).upper() != "OPTIMAL":
        result = {
            "success": False,
            "repairable": True,
            "stage": 2,
            "failure_class": "solver_senza_soluzione_ottima",
            "detail": f"Il codice ha restituito stato {candidate.get('status')}",
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result

    try:
        private, public = definitive_validation(problem_id, candidate)
    except Exception as exc:
        result = {
            "success": False,
            "repairable": False,
            "stage": 4,
            "failure_class": "validazione_non_completata",
            "detail": f"{type(exc).__name__}: {exc}",
            "finish_reason": finish_reason,
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result
    save_json(attempt_dir / "validation_private.json", private)
    save_json(attempt_dir / "validation_public.json", public)
    if private["correct"]:
        result = {
            "success": True,
            "repairable": False,
            "stage": 4,
            "failure_class": "corretta",
            "detail": "Soluzione ammissibile e gap entro tolleranza",
            "finish_reason": finish_reason,
            "declared_objective_corrected_automatically": private[
                "declared_objective_corrected_automatically"
            ],
        }
        save_json(attempt_dir / "evaluation.json", result)
        return result

    reasons = []
    if not public["feasible_in_original_problem"]:
        reasons.append("la soluzione viola almeno un requisito del problema originale")
    if not public["gap_within_tolerance"]:
        reasons.append("il gap supera la soglia dello 0,1%")
    if public["unknown_nonzero_variables"]:
        reasons.append("sono presenti variabili operative non riconosciute")
    result = {
        "success": False,
        "repairable": False,
        "stage": 4,
        "failure_class": "validazione_indipendente_fallita",
        "detail": "; ".join(reasons) or "la soluzione non supera la validazione indipendente",
        "finish_reason": finish_reason,
        "validation_public": public,
    }
    save_json(attempt_dir / "evaluation.json", result)
    return result


def problem_dir(
    model_name: str,
    sequence: int,
    problem_id: str,
    scenario_root: Path = SCENARIO_ROOT,
) -> Path:
    return scenario_root / "runs" / model_slug(model_name) / f"{sequence:02d}_{problem_id}"


def state_path(run_dir: Path) -> Path:
    return run_dir / "state.json"


def previous_code(run_dir: Path, state: dict) -> str:
    if not state.get("attempts"):
        return ""
    path = run_dir / state["attempts"][-1]["directory"] / "generated.py"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def new_state(model_name: str, problem: dict, sequence: int, retrieval: dict) -> dict:
    return {
        "schema_version": 2,
        "scenario": "C",
        "model": model_name,
        "problem_id": problem["id"],
        "problem_sequence": sequence,
        "domain": problem.get("domain"),
        "difficulty": problem.get("difficulty"),
        "model_class": problem.get("model_class"),
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "status": "RUNNING",
        "auto_repair_count_current_cycle": 0,
        "traceability_repair_count": 0,
        "stage_2_assurance_completed": False,
        "attempts": [],
        "interventions": [],
        "memory_retrieval": retrieval,
        "pending_handoff": None,
    }


def save_state(run_dir: Path, state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    save_json(state_path(run_dir), state)


def safe_validation_for_packet(attempt_dir: Path) -> dict | None:
    return load_json(attempt_dir / "validation_public.json")


def attempt_history_for_packet(run_dir: Path, state: dict) -> list[dict]:
    """Riassume gli output automatici senza esporre ground truth o ragionamenti interni."""
    history = []
    for attempt in state.get("attempts", []):
        attempt_dir = run_dir / attempt["directory"]
        raw = load_json(attempt_dir / "response.json", {})
        choice = (raw.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = raw.get("usage") or {}
        token_details = usage.get("completion_tokens_details") or {}
        evaluation = attempt.get("evaluation") or {}
        history.append(
            {
                "attempt_number": attempt["number"],
                "attempt_kind": attempt["kind"],
                "finish_reason": choice.get("finish_reason"),
                "content_characters": len(message.get("content") or ""),
                "completion_tokens": usage.get("completion_tokens") or 0,
                "reasoning_tokens": token_details.get("reasoning_tokens") or 0,
                "code_extracted": (attempt_dir / "generated.py").exists(),
                "failure_class": evaluation.get("failure_class"),
                "failure_detail": evaluation.get("detail", ""),
            }
        )
    return history


def automatic_handoff_diagnosis(
    history: list[dict], failure: dict, response_excerpt: str = ""
) -> str:
    if failure.get("handoff_mode") == "ASSURANCE_REVIEW":
        return (
            "Il problema è di difficoltà elevata e la soluzione ha richiesto almeno una "
            "riparazione automatica. Prima dell'accettazione, il protocollo richiede una revisione "
            "umana del modello e del codice rispetto alla traccia, senza mostrare la ground truth."
        )
    if history and all(
        item.get("finish_reason") == "length"
        and item.get("content_characters") == 0
        and not item.get("code_extracted")
        for item in history
    ):
        return (
            "Tutti i tentativi hanno esaurito il limite di output nel ragionamento interno: "
            "il modello non ha emesso contenuto finale né codice eseguibile. L'handoff riguarda "
            "quindi la capacità di concludere la risposta, non un errore matematico già osservabile."
        )
    if response_excerpt.strip() and any(
        item.get("failure_class") == "codice_non_estratto" for item in history
    ):
        return (
            "Almeno un tentativo ha emesso una risposta non vuota, ma il parser non ha trovato "
            "l'unico blocco Python richiesto dal protocollo. La risposta più recente disponibile "
            "è riportata nel pacchetto: l'esperto può verificare se si tratta di solo formato o di "
            "un errore sostanziale del modello."
        )
    if failure.get("stage") == 4:
        return (
            "Il codice è stato eseguito, ma la soluzione non ha superato la validazione indipendente. "
            "Esaminare le violazioni e il codice riportati nel pacchetto."
        )
    return str(failure.get("detail", "Errore non ulteriormente diagnosticato"))


def create_handoff(
    run_dir: Path,
    state: dict,
    problem_text: str,
    failure: dict,
) -> Path:
    # Un handoff tecnico può essere annullato senza diventare un intervento.
    # In quel caso la numerazione non può basarsi soltanto sugli interventi
    # registrati, altrimenti una successiva revisione sovrascriverebbe la
    # cartella del falso allarme. Si prosegue dal massimo identificativo già
    # presente, preservando integralmente la traccia di audit.
    existing_numbers = []
    for path in (run_dir / "handoffs").glob("handoff_*"):
        try:
            existing_numbers.append(int(path.name.rsplit("_", 1)[1]))
        except (IndexError, ValueError):
            continue
    number = max([len(state.get("interventions", [])), *existing_numbers], default=0) + 1
    handoff_dir = run_dir / "handoffs" / f"handoff_{number:02d}"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    last_attempt = state["attempts"][-1]
    attempt_dir = run_dir / last_attempt["directory"]
    code = (attempt_dir / "generated.py").read_text(encoding="utf-8") if (attempt_dir / "generated.py").exists() else ""
    response_excerpt = ""
    response_source_attempt = None
    for previous_attempt in reversed(state.get("attempts", [])):
        candidate_path = run_dir / previous_attempt["directory"] / "response.txt"
        if not candidate_path.exists():
            continue
        candidate_text = candidate_path.read_text(encoding="utf-8")
        if candidate_text.strip():
            response_excerpt = candidate_text
            response_source_attempt = previous_attempt["number"]
            break
    attempt_history = attempt_history_for_packet(run_dir, state)
    handoff_mode = failure.get("handoff_mode", "CORRECTION")
    assurance_review = handoff_mode == "ASSURANCE_REVIEW"
    packet = {
        "schema_version": 2,
        "created_at_utc": utc_now(),
        "model": state["model"],
        "problem_id": state["problem_id"],
        "problem_sequence": state["problem_sequence"],
        "handoff_number": number,
        "stage": int(failure["stage"]),
        "failure_class": failure["failure_class"],
        "failure_detail": failure.get("detail", ""),
        "handoff_mode": handoff_mode,
        "allowed_actions": (
            ["APPROVE", "CORRECT", "ACCEPT_FAILURE"]
            if assurance_review
            else ["CORRECT", "ACCEPT_FAILURE"]
        ),
        "automatic_repairs_exhausted": state.get("auto_repair_count_current_cycle", 0),
        "problem_prompt": problem_text,
        "last_code": code,
        "last_response_excerpt": compact(response_excerpt, 12000),
        "response_source_attempt": response_source_attempt,
        "validation": None if assurance_review else safe_validation_for_packet(attempt_dir),
        "attempt_history": attempt_history,
        "automatic_diagnosis": automatic_handoff_diagnosis(
            attempt_history, failure, response_excerpt
        ),
        "ground_truth_disclosed": False,
    }
    save_json(handoff_dir / "packet.json", packet)
    md = [
        f"# Handoff {number} — {state['problem_id']} / {state['model']}",
        "",
        f"- **Stadio:** {packet['stage']}",
        f"- **Categoria:** {packet['failure_class']}",
        f"- **Tipo di handoff:** {packet['handoff_mode']}",
        f"- **Dettaglio:** {packet['failure_detail']}",
        f"- **Cicli automatici già usati:** {packet['automatic_repairs_exhausted']}",
        "- **Ground truth mostrata:** no",
        "",
        "## Diagnosi automatica",
        "",
        packet["automatic_diagnosis"],
        "",
        "| Tentativo | Tipo | Fine | Caratteri finali | Token di ragionamento | Codice estratto | Esito |",
        "| ---: | --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in attempt_history:
        md.append(
            f"| {item['attempt_number']} | {item['attempt_kind']} | {item['finish_reason']} | "
            f"{item['content_characters']} | {item['reasoning_tokens']} | "
            f"{'sì' if item['code_extracted'] else 'no'} | {item['failure_class']} |"
        )
    md.extend([
        "",
        "## Traccia",
        "",
        problem_text.strip(),
        "",
    ])
    if packet["validation"]:
        md.extend([
            "## Esito pubblico della validazione",
            "",
            "```json",
            json.dumps(packet["validation"], ensure_ascii=False, indent=2),
            "```",
            "",
        ])
    if code:
        md.extend(["## Codice da esaminare", "", "```python", code.rstrip(), "```", ""])
    else:
        source_label = (
            f" (tentativo {packet['response_source_attempt']})"
            if packet.get("response_source_attempt") is not None
            else ""
        )
        md.extend([
            f"## Ultima risposta non vuota disponibile{source_label}",
            "",
            "```python",
            packet["last_response_excerpt"].rstrip(),
            "```",
            "",
        ])
    if assurance_review:
        md.extend([
            "## Checklist di revisione dello Stadio 2",
            "",
            "Verificare il codice rispetto alla traccia, senza consultare la ground truth:",
            "",
            "1. variabili decisionali e relativi domini;",
            "2. funzione obiettivo e verso di ottimizzazione;",
            "3. corrispondenza tra ogni requisito della traccia e almeno un vincolo;",
            "4. coefficienti, indici e unità di misura;",
            "5. vincoli impliciti necessari alla corretta interpretazione del problema.",
            "",
            "Registrare i minuti effettivi e scegliere APPROVE se non emerge alcun errore, "
            "CORRECT se serve una modifica, oppure ACCEPT_FAILURE se il problema non viene corretto.",
        ])
    else:
        md.extend([
            "## Cosa deve fornire l'esperto",
            "",
            "1. I minuti di lavoro attivo.",
            "2. Un'istruzione precisa con la correzione da applicare.",
            "3. Una breve sintesi della correzione.",
            "4. Facoltativamente, un principio generale da salvare nella Memoria Semantica.",
        ])
    (handoff_dir / "packet.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    save_json(
        handoff_dir / "expert_response.json",
        {
            "status": "PENDING",
            "action": "APPROVE" if assurance_review else "CORRECT",
            "active_minutes": None,
            "expert_instruction": "",
            "correction_summary": "",
            "semantic_principle": "",
            "submitted_at_utc": None,
        },
    )
    state["status"] = "AWAITING_HANDOFF"
    state["pending_handoff"] = str(handoff_dir.relative_to(run_dir))
    save_state(run_dir, state)
    return handoff_dir


def expert_response_ready(path: Path) -> tuple[bool, str]:
    response = load_json(path)
    if not response or response.get("status") != "SUBMITTED":
        return False, "Risposta dell'esperto non ancora inviata"
    packet = load_json(path.parent / "packet.json", {})
    allowed_actions = set(packet.get("allowed_actions") or ["CORRECT", "ACCEPT_FAILURE"])
    if response.get("action") not in allowed_actions:
        return False, "action non ammessa per questo tipo di handoff"
    try:
        minutes = float(response.get("active_minutes"))
    except (TypeError, ValueError):
        return False, "active_minutes deve essere numerico"
    if minutes <= 0:
        return False, "active_minutes deve essere maggiore di zero"
    if response["action"] == "CORRECT" and not str(response.get("expert_instruction", "")).strip():
        return False, "manca expert_instruction"
    if not str(response.get("correction_summary", "")).strip():
        return False, "manca correction_summary"
    return True, "OK"


def commit_memory(
    model_name: str,
    state: dict,
    scenario_root: Path = SCENARIO_ROOT,
) -> None:
    memory = load_memory(model_name, scenario_root)
    changed = False
    for intervention in state.get("interventions", []):
        if intervention.get("memory_committed") or intervention.get("action") != "CORRECT":
            continue
        episode_id = f"{state['problem_id']}-H{intervention['handoff_number']:02d}"
        episode = {
            "id": episode_id,
            "created_at_utc": utc_now(),
            "problem_id": state["problem_id"],
            "domain": state.get("domain", ""),
            "model_class": state.get("model_class", ""),
            "stage": intervention["stage"],
            "failure_class": intervention["failure_class"],
            "correction_summary": intervention["correction_summary"],
            "expert_instruction": intervention["expert_instruction"],
            "active_minutes": intervention["active_minutes"],
            "tags": [
                state.get("domain", ""),
                state.get("model_class", ""),
                f"stadio-{intervention['stage']}",
                intervention["failure_class"],
            ],
        }
        memory["episodic"].append(episode)
        principle = str(intervention.get("semantic_principle", "")).strip()
        if principle and principle not in {item.get("principle") for item in memory["semantic"]}:
            memory["semantic"].append(
                {
                    "id": f"S-{len(memory['semantic']) + 1:03d}",
                    "created_at_utc": utc_now(),
                    "source_episode": episode_id,
                    "principle": principle,
                    "tags": episode["tags"],
                }
            )
        intervention["memory_committed"] = True
        changed = True
    if changed:
        memory["updated_at_utc"] = utc_now()
        save_json(memory_path(model_name, scenario_root), memory)


def finalize_problem(
    run_dir: Path,
    state: dict,
    correct: bool,
    final_attempt: dict | None,
    scenario_root: Path = SCENARIO_ROOT,
) -> dict:
    if correct:
        commit_memory(state["model"], state, scenario_root)
    human_minutes = sum(float(x.get("active_minutes", 0)) for x in state.get("interventions", []))
    traceability_repairs = sum(
        1 for x in state.get("attempts", []) if x["kind"] == "TRACEABILITY_REPAIR"
    )
    code_repairs = sum(1 for x in state.get("attempts", []) if x["kind"] == "AUTO_REPAIR")
    automatic_repairs = traceability_repairs + code_repairs
    result = {
        "scenario": "C",
        "model": state["model"],
        "problem_id": state["problem_id"],
        "problem_sequence": state["problem_sequence"],
        "completed_at_utc": utc_now(),
        "correct": bool(correct),
        "pass": bool(final_attempt and final_attempt.get("evaluation", {}).get("success")),
        "final_attempt": None if final_attempt is None else final_attempt["directory"],
        "attempt_count": len(state.get("attempts", [])),
        "automatic_repair_count": automatic_repairs,
        "traceability_repair_count": traceability_repairs,
        "code_repair_count": code_repairs,
        "handoff_count": len(state.get("interventions", [])),
        "human_minutes": human_minutes,
        "handoff_stages": [x["stage"] for x in state.get("interventions", [])],
        "memory_semantic_retrieved": len(state["memory_retrieval"].get("semantic", [])),
        "memory_episodic_retrieved": len(state["memory_retrieval"].get("episodic", [])),
    }
    save_json(run_dir / "final.json", result)
    state["status"] = "COMPLETED" if correct else "COMPLETED_FAILURE"
    state["pending_handoff"] = None
    save_state(run_dir, state)
    return result


def advance_problem(
    model_name: str,
    problem_id: str,
    sequence: int,
    scenario_root: Path = SCENARIO_ROOT,
) -> dict:
    problems = load_problems()
    problem = problems[problem_id]
    problem_text = prompt_for(problem_id)
    run_dir = problem_dir(model_name, sequence, problem_id, scenario_root)
    run_dir.mkdir(parents=True, exist_ok=True)
    state = load_json(state_path(run_dir))
    if state is None:
        retrieval = retrieve_memory(model_name, problem, scenario_root)
        state = new_state(model_name, problem, sequence, retrieval)
        save_json(run_dir / "memory_retrieval.json", retrieval)
        save_state(run_dir, state)
    if state["status"] in {"COMPLETED", "COMPLETED_FAILURE"}:
        return {"status": state["status"], "run_dir": str(run_dir), "final": load_json(run_dir / "final.json")}

    next_kind = "INITIAL"
    system = INITIAL_SYSTEM_PATH.read_text(encoding="utf-8")
    prompt = build_initial_prompt(problem_text, state["memory_retrieval"])

    if state["status"] == "AWAITING_HANDOFF":
        handoff_dir = run_dir / state["pending_handoff"]
        response_path = handoff_dir / "expert_response.json"
        ready, message = expert_response_ready(response_path)
        if not ready:
            return {
                "status": "AWAITING_HANDOFF",
                "run_dir": str(run_dir),
                "handoff_dir": str(handoff_dir),
                "message": message,
            }
        response = load_json(response_path)
        packet = load_json(handoff_dir / "packet.json")
        intervention = {
            "handoff_number": packet["handoff_number"],
            "stage": packet["stage"],
            "failure_class": packet["failure_class"],
            "handoff_mode": packet.get("handoff_mode", "CORRECTION"),
            "active_minutes": float(response["active_minutes"]),
            "action": response["action"],
            "expert_instruction": response.get("expert_instruction", ""),
            "correction_summary": response["correction_summary"],
            "semantic_principle": response.get("semantic_principle", ""),
            "submitted_at_utc": response.get("submitted_at_utc") or utc_now(),
            "memory_committed": False,
        }
        state["interventions"].append(intervention)
        state["pending_handoff"] = None
        state["auto_repair_count_current_cycle"] = 0
        if packet.get("handoff_mode") == "ASSURANCE_REVIEW":
            state["stage_2_assurance_completed"] = True
        if response["action"] == "APPROVE":
            final_attempt = state["attempts"][-1] if state.get("attempts") else None
            if not final_attempt or not final_attempt.get("evaluation", {}).get("success"):
                raise RuntimeError(
                    "APPROVE è ammesso soltanto dopo una soluzione automatica già validata"
                )
            save_state(run_dir, state)
            final = finalize_problem(run_dir, state, True, final_attempt, scenario_root)
            return {"status": "COMPLETED", "run_dir": str(run_dir), "final": final}
        if response["action"] == "ACCEPT_FAILURE":
            save_state(run_dir, state)
            final = finalize_problem(run_dir, state, False, None, scenario_root)
            return {"status": "COMPLETED_FAILURE", "run_dir": str(run_dir), "final": final}
        previous_failure = {
            "stage": packet["stage"],
            "failure_class": packet["failure_class"],
            "detail": packet.get("failure_detail", ""),
        }
        prompt = build_expert_prompt(
            problem_text,
            state["memory_retrieval"],
            previous_failure,
            previous_code(run_dir, state),
            response,
        )
        system = REPAIR_SYSTEM_PATH.read_text(encoding="utf-8")
        next_kind = "EXPERT_CORRECTION"
        state["status"] = "RUNNING"
        save_state(run_dir, state)

    while True:
        attempt_number = len(state["attempts"])
        attempt_dir = run_dir / f"attempt_{attempt_number:02d}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "problem_id": problem_id,
            "problem_sequence": sequence,
            "attempt_number": attempt_number,
            "attempt_kind": next_kind,
            "auto_repair_count_current_cycle": state["auto_repair_count_current_cycle"],
        }
        text, raw = call_openrouter(model_name, system, prompt, attempt_dir, metadata)

        traceability = (
            parse_traceability(text)
            if next_kind in {"INITIAL", "TRACEABILITY_REPAIR"}
            and not response_is_empty_truncation(text, raw)
            else None
        )
        if traceability and traceability.get("needs_expert"):
            evaluation = {
                "success": False,
                "repairable": False,
                "stage": 1,
                "failure_class": "ambiguita_o_dati_mancanti",
                "detail": json.dumps(traceability.get("value", {}), ensure_ascii=False),
                "traceability": traceability,
            }
            save_json(attempt_dir / "evaluation.json", evaluation)
        elif traceability and not traceability.get("complete_ready"):
            evaluation = {
                "success": False,
                "repairable": state.get("traceability_repair_count", 0)
                < MAX_TRACEABILITY_REPAIR,
                "stage": 1,
                "failure_class": "tracciabilita_assente_o_non_valida",
                "detail": "; ".join(traceability.get("errors") or []),
                "traceability": traceability,
            }
            save_json(attempt_dir / "evaluation.json", evaluation)
        else:
            evaluation = evaluate_response(problem_id, text, raw, attempt_dir)
            if traceability is not None:
                evaluation["traceability"] = traceability
                save_json(attempt_dir / "evaluation.json", evaluation)
        attempt_record = {
            "number": attempt_number,
            "kind": next_kind,
            "directory": attempt_dir.name,
            "created_at_utc": utc_now(),
            "evaluation": evaluation,
        }
        state["attempts"].append(attempt_record)
        save_state(run_dir, state)

        if evaluation["success"] and stage_two_assurance_required(problem, state, evaluation):
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
            handoff_dir = create_handoff(run_dir, state, problem_text, review_request)
            return {
                "status": "AWAITING_HANDOFF",
                "run_dir": str(run_dir),
                "handoff_dir": str(handoff_dir),
                "message": "Revisione umana di assicurazione richiesta allo Stadio 2",
            }

        if evaluation["success"]:
            final = finalize_problem(run_dir, state, True, attempt_record, scenario_root)
            return {"status": "COMPLETED", "run_dir": str(run_dir), "final": final}

        if (
            evaluation.get("stage") == 1
            and evaluation.get("failure_class") == "tracciabilita_assente_o_non_valida"
            and state.get("traceability_repair_count", 0) < MAX_TRACEABILITY_REPAIR
        ):
            state["traceability_repair_count"] = (
                state.get("traceability_repair_count", 0) + 1
            )
            save_state(run_dir, state)
            prompt = build_traceability_repair_prompt(
                problem_text,
                state["memory_retrieval"],
                evaluation.get("traceability") or {},
            )
            system = INITIAL_SYSTEM_PATH.read_text(encoding="utf-8")
            next_kind = "TRACEABILITY_REPAIR"
            continue

        if evaluation.get("repairable") and state["auto_repair_count_current_cycle"] < MAX_SELF_REPAIR:
            state["auto_repair_count_current_cycle"] += 1
            save_state(run_dir, state)
            prompt = build_repair_prompt(
                problem_text,
                state["memory_retrieval"],
                evaluation,
                previous_code(run_dir, state),
                state["auto_repair_count_current_cycle"],
            )
            system = REPAIR_SYSTEM_PATH.read_text(encoding="utf-8")
            next_kind = "AUTO_REPAIR"
            continue

        handoff_dir = create_handoff(run_dir, state, problem_text, evaluation)
        return {
            "status": "AWAITING_HANDOFF",
            "run_dir": str(run_dir),
            "handoff_dir": str(handoff_dir),
            "message": "La pipeline richiede l'intervento dell'esperto",
        }


def api_usage_for_attempt(attempt_dir: Path) -> dict:
    response = load_json(attempt_dir / "response.json", {})
    usage = response.get("usage") or {}
    details = usage.get("completion_tokens_details") or {}
    return {
        "prompt_tokens": usage.get("prompt_tokens") or 0,
        "completion_tokens": usage.get("completion_tokens") or 0,
        "reasoning_tokens": details.get("reasoning_tokens") or 0,
        "total_tokens": usage.get("total_tokens") or 0,
        "api_cost_usd": usage.get("cost") or 0.0,
        "response_seconds": (response.get("_experiment") or {}).get("elapsed_seconds") or 0.0,
    }
