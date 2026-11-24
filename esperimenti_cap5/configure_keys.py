#!/usr/bin/env python3
"""Salva le chiavi API nel Portachiavi di macOS senza scriverle su disco."""

from __future__ import annotations

import getpass
import subprocess

import httpx

from secret_store import KEYS


def store(provider: str) -> None:
    env_name, service = KEYS[provider]
    value = getpass.getpass(f"Incolla {env_name} (i caratteri non saranno mostrati): ").strip()
    if not value:
        print(f"{provider}: operazione saltata")
        return
    if provider == "openrouter":
        response = httpx.get(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {value}"},
            timeout=30,
        )
        if response.status_code != 200:
            print(
                f"openrouter: chiave rifiutata (HTTP {response.status_code}); "
                "non è stata salvata"
            )
            return
    subprocess.run(
        [
            "security", "add-generic-password", "-U", "-a", getpass.getuser(),
            "-s", service, "-w", value,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"{provider}: chiave salvata nel Portachiavi")


if __name__ == "__main__":
    print("La chiave viene salvata nel Portachiavi di macOS e non nei file della tesi.")
    store("openrouter")
