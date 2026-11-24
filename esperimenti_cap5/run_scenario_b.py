#!/usr/bin/env python3
"""Invia una singola prova dello Scenario B e salva la risposta grezza."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

from secret_store import get_api_key


def load_config(model_name: str) -> dict:
    configs = json.loads((HERE / "models.json").read_text(encoding="utf-8"))
    if model_name not in configs:
        raise KeyError(f"Modello non configurato: {model_name}")
    return configs[model_name]


def call_openrouter(config: dict, system: str, prompt: str) -> tuple[str, dict]:
    from openai import OpenAI

    client = OpenAI(
        api_key=get_api_key("openrouter"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/tesi-cap5",
            "X-Title": "Tesi HITL OR - Scenario B",
        },
    )
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=config["max_output_tokens"],
        extra_body={
            "reasoning": {
                "effort": config["reasoning_effort"],
                "exclude": False,
            },
            "provider": {
                "only": [config["upstream_provider"]],
                "allow_fallbacks": False,
                "require_parameters": True,
            },
        },
    )
    raw = response.model_dump(mode="json")
    raw["_routing_request"] = {
        "gateway": "openrouter",
        "requested_model": config["model"],
        "required_provider": config["upstream_provider"],
        "allow_fallbacks": False,
        "require_parameters": True,
    }
    return response.choices[0].message.content or "", raw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--run", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    config = load_config(args.model)
    prompt_path = ROOT / "dataset_cap4" / "prompts" / f"{args.problem}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(prompt_path)

    system = (HERE / "system_prompt.txt").read_text(encoding="utf-8")
    prompt = prompt_path.read_text(encoding="utf-8")
    run_dir = HERE / "runs" / "B" / args.model / args.problem / f"run_{args.run:02d}"
    if run_dir.exists() and not args.overwrite:
        raise FileExistsError(f"Esecuzione già presente: {run_dir}; usare --overwrite solo se giustificato")
    run_dir.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc)
    request_record = {
        "scenario": "B", "provider": config["provider"], "model": config["model"],
        "problem_id": args.problem, "replicate": args.run,
        "started_at_utc": started.isoformat(), "configuration": config,
        "system_prompt": system, "problem_prompt": prompt,
    }
    (run_dir / "request.json").write_text(
        json.dumps(request_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    t0 = time.perf_counter()
    text, raw = call_openrouter(config, system, prompt)
    elapsed = time.perf_counter() - t0

    raw["_experiment"] = {"elapsed_seconds": elapsed, "completed_at_utc": datetime.now(timezone.utc).isoformat()}
    (run_dir / "response.json").write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (run_dir / "response.txt").write_text(text + "\n", encoding="utf-8")
    print(f"Risposta salvata in {run_dir}")
    print(f"Latenza: {elapsed:.2f} s")


if __name__ == "__main__":
    main()
