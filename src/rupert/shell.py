from __future__ import annotations

import json

from .executor import HELP_TEXT, execute_text as execute_command
from .obsidian_bridge import ObsidianClient


HELP = HELP_TEXT + "\nEjemplo:\n  buscar Theo\n  añadir AlasTheo/Ideas.md :: Revisar la escena del crucero\n"


def _show(value) -> None:
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def execute_text(client: ObsidianClient, text: str) -> bool:
    """Execute one text command. Return False when the shell should exit."""
    result = execute_command(client, text)
    if result.payload is not None:
        _show(result.payload)
    else:
        print(result.message)
    return not result.should_exit


def run_shell(client: ObsidianClient) -> int:
    print("Rupert v0.4 — shell sin LLM ($0)")
    print("Escribe 'ayuda' para ver comandos.")
    while True:
        try:
            text = input("rupert> ")
            if not execute_text(client, text):
                return 0
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        except RuntimeError as exc:
            print(f"❌ {exc}")
