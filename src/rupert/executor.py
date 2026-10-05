from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .obsidian_bridge import ObsidianClient
from .permissions import (
    DEFAULT_POLICY,
    ActionSource,
    PermissionPolicy,
    action_spec_for_intent,
)
from .router import Intent, IntentKind, parse_intent


HELP_TEXT = """Comandos locales ($0):
  buscar <texto>
  leer <ruta.md>
  abrir <ruta.md>
  añadir <ruta.md> :: <texto>
  escribir <ruta.md> :: <texto>
  ayuda
  salir
"""


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    message: str
    payload: Any = None
    should_exit: bool = False


def execute_intent(
    client: ObsidianClient,
    intent: Intent,
    *,
    source: ActionSource = ActionSource.KEYBOARD,
    confirmed: bool = False,
    policy: PermissionPolicy = DEFAULT_POLICY,
) -> ExecutionResult:
    if intent.kind == IntentKind.EXIT:
        return ExecutionResult(True, "Hasta luego.", should_exit=True)
    if intent.kind == IntentKind.HELP:
        return ExecutionResult(True, HELP_TEXT)

    spec = action_spec_for_intent(intent.kind)
    if spec is not None:
        decision = policy.evaluate(spec, source=source, confirmed=confirmed)
        if not decision.allowed:
            return ExecutionResult(False, decision.reason)

    if intent.kind == IntentKind.SEARCH:
        payload = client.search(intent.target)
        count = len(payload) if isinstance(payload, list) else None
        message = f"Encontré {count} resultado{'s' if count != 1 else ''}." if count is not None else "Búsqueda terminada."
        return ExecutionResult(True, message, payload)
    if intent.kind == IntentKind.READ:
        payload = client.read(intent.target)
        return ExecutionResult(True, f"Leí {intent.target}.", payload)
    if intent.kind == IntentKind.OPEN:
        client.open_note(intent.target)
        return ExecutionResult(True, f"Abrí {intent.target}.")
    if intent.kind == IntentKind.APPEND:
        client.append(intent.target, intent.content)
        return ExecutionResult(True, f"Añadí el contenido a {intent.target}.")
    if intent.kind == IntentKind.WRITE:
        client.write(intent.target, intent.content)
        return ExecutionResult(True, f"Escribí {intent.target}.")
    return ExecutionResult(False, "No entendí esa orden local.")


def execute_text(
    client: ObsidianClient,
    text: str,
    *,
    source: ActionSource = ActionSource.KEYBOARD,
    confirmed: bool = False,
    policy: PermissionPolicy = DEFAULT_POLICY,
) -> ExecutionResult:
    return execute_intent(
        client,
        parse_intent(text),
        source=source,
        confirmed=confirmed,
        policy=policy,
    )
