#!/usr/bin/env python3
"""Controlla Gurobi, dataset e presenza delle chiavi API senza mostrarle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gurobipy as gp
import httpx
from gurobipy import GRB

from secret_store import get_api_key

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def check_gurobi() -> None:
    model = gp.Model("setup_check")
    model.Params.OutputFlag = 0
    x = model.addVar(vtype=GRB.BINARY, name="x")
    model.setObjective(x, GRB.MAXIMIZE)
    model.optimize()
    if model.Status != GRB.OPTIMAL or abs(x.X - 1.0) > 1e-9:
        raise RuntimeError("Gurobi non ha risolto correttamente il test minimo")
    print(f"Gurobi: OK — versione {'.'.join(map(str, gp.gurobi.version()))}")


def check_dataset() -> None:
    prompts = sorted((ROOT / "dataset_cap4" / "prompts").glob("[MH][0-9][0-9].md"))
    records = json.loads((ROOT / "dataset_cap4" / "ground_truth.json").read_text(encoding="utf-8"))
    if len(prompts) != 20 or len(records) != 20:
        raise RuntimeError(f"Dataset incompleto: {len(prompts)} prompt, {len(records)} ground truth")
    if {p.stem for p in prompts} != {r["id"] for r in records}:
        raise RuntimeError("Gli ID dei prompt non coincidono con quelli della ground truth")
    print("Dataset: OK — 20 prompt e 20 record di ground truth")


def check_keys() -> bool:
    key = get_api_key("openrouter", required=False)
    if not key:
        print("OpenRouter: chiave assente")
        return False
    response = httpx.get(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    if response.status_code != 200:
        print(f"OpenRouter: chiave presente ma non valida (HTTP {response.status_code})")
        return False
    print("OpenRouter: chiave presente e riconosciuta")
    return True


if __name__ == "__main__":
    check_gurobi()
    check_dataset()
    if not check_keys():
        print("Configurazione incompleta: aggiungere le chiavi API prima delle chiamate ai modelli.")
        sys.exit(2)
    print("Configurazione completa.")
