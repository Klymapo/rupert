from __future__ import annotations

import json

from .obsidian_bridge import ObsidianClient
from .router import IntentKind, parse_intent


HELP = """Comandos locales ($0):
  buscar <texto>
  leer <ruta.md>
  abrir <ruta.md>
  añadir <ruta.md> :: <texto>
  escribir <ruta.md> :: <texto>
  ayuda
  salir

Ejemplo:
  buscar Theo
  añadir AlasTheo/Ideas.md :: Revisar la escena del crucero
"""


def _show(value) -> None:
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def execute_text(client: ObsidianClient, text: str) -> bool:
    """Execute one text command. Return False when the shell should exit."""
    intent = parse_intent(text)
    if intent.kind == IntentKind.EXIT:
        return False
    if intent.kind == IntentKind.HELP:
        print(HELP)
    elif intent.kind == IntentKind.SEARCH:
        _show(client.search(intent.target))
    elif intent.kind == IntentKind.READ:
        print(client.read(intent.target))
    elif intent.kind == IntentKind.OPEN:
        client.open_note(intent.target)
        print(f"✅ Abierto: {intent.target}")
    elif intent.kind == IntentKind.APPEND:
        client.append(intent.target, intent.content)
        print(f"✅ Añadido: {intent.target}")
    elif intent.kind == IntentKind.WRITE:
        client.write(intent.target, intent.content)
        print(f"✅ Escrito: {intent.target}")
    else:
        print("No entendí esa orden local. Escribe 'ayuda'.")
    return True


def run_shell(client: ObsidianClient) -> int:
    print("Rupert v0.3 — shell sin LLM ($0)")
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
