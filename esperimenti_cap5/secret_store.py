"""Lettura delle chiavi da variabili d'ambiente o dal Portachiavi di macOS."""

from __future__ import annotations

import getpass
import os
import subprocess

KEYS = {
    "openrouter": ("OPENROUTER_API_KEY", "tesi-cap5-openrouter"),
    "openai": ("OPENAI_API_KEY", "tesi-cap5-openai"),
    "anthropic": ("ANTHROPIC_API_KEY", "tesi-cap5-anthropic"),
    "deepseek": ("DEEPSEEK_API_KEY", "tesi-cap5-deepseek"),
}


def get_api_key(provider: str, required: bool = True) -> str | None:
    env_name, service = KEYS[provider]
    if value := os.environ.get(env_name):
        return value
    proc = subprocess.run(
        ["security", "find-generic-password", "-a", getpass.getuser(), "-s", service, "-w"],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    if required:
        raise RuntimeError(
            f"Chiave {env_name} assente. Eseguire prima: python3 configure_keys.py"
        )
    return None
