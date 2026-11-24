#!/usr/bin/env python3
"""Estrae ed esegue in modo prudente il codice di una risposta LLM."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ALLOWED_IMPORTS = {"gurobipy", "json", "math", "itertools"}
FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "input", "__import__"}


def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python|py)\s*\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if len(blocks) != 1:
        raise ValueError(f"Atteso un solo blocco Python, trovati {len(blocks)}")
    return blocks[0].strip() + "\n"


def static_check(code: str) -> None:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"Import non consentito: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if not node.module or node.module.split(".")[0] not in ALLOWED_IMPORTS:
                raise ValueError(f"Import non consentito: {node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            raise ValueError(f"Chiamata non consentita: {node.func.id}")


def parse_solution(stdout: str) -> dict:
    lines = [line[len("SOLUTION_JSON="):] for line in stdout.splitlines() if line.startswith("SOLUTION_JSON=")]
    if len(lines) != 1:
        raise ValueError(f"Attesa una sola riga SOLUTION_JSON, trovate {len(lines)}")
    value = json.loads(lines[0])
    if not isinstance(value, dict):
        raise ValueError("SOLUTION_JSON non contiene un oggetto JSON")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--approve", action="store_true", help="esegue senza richiesta interattiva")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    text = (run_dir / "response.txt").read_text(encoding="utf-8")
    code = extract_code(text)
    static_check(code)
    code_path = run_dir / "generated.py"
    code_path.write_text(code, encoding="utf-8")

    if not args.approve:
        print(f"Codice estratto in {code_path}")
        answer = input("Dopo averlo controllato, digitare ESEGUI per procedere: ")
        if answer != "ESEGUI":
            print("Esecuzione annullata.")
            return

    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "GRB_LICENSE_FILE": os.environ.get("GRB_LICENSE_FILE", str(Path.home() / "gurobi.lic")),
        "PYTHONIOENCODING": "utf-8",
    }
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-I", str(code_path)], cwd=run_dir, env=env,
            capture_output=True, text=True, timeout=args.timeout,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        proc = None
        timed_out = True
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    elapsed = time.perf_counter() - t0

    if proc is not None:
        stdout, stderr = proc.stdout, proc.stderr
        returncode = proc.returncode
    else:
        returncode = None
    execution = {
        "returncode": returncode, "timed_out": timed_out,
        "elapsed_seconds": elapsed, "stdout": stdout, "stderr": stderr,
    }
    (run_dir / "execution.json").write_text(
        json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if timed_out:
        raise TimeoutError(f"Esecuzione interrotta dopo {args.timeout} secondi")
    if returncode != 0:
        raise RuntimeError(f"Il codice è terminato con exit code {returncode}; vedere execution.json")
    candidate = parse_solution(stdout)
    (run_dir / "candidate_solution.json").write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Soluzione candidata salvata in {run_dir / 'candidate_solution.json'}")


if __name__ == "__main__":
    main()

