from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .obsidian_bridge import ObsidianClient
from .permissions import DEFAULT_POLICY, ActionSource, PermissionPolicy
from .router import Intent, IntentKind, parse_intent
from .skills import SkillRegistry, build_obsidian_registry, skill_name_for_intent


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
    registry: SkillRegistry | None = None,
) -> ExecutionResult:
    if intent.kind == IntentKind.EXIT:
        return ExecutionResult(True, "Hasta luego.", should_exit=True)
    if intent.kind == IntentKind.HELP:
        return ExecutionResult(True, HELP_TEXT)

    skill_name = skill_name_for_intent(intent.kind)
    if skill_name is None:
        return ExecutionResult(False, "No entendí esa orden local.")

    active_registry = registry or build_obsidian_registry(client, policy=policy)
    result = active_registry.invoke(
        skill_name,
        source=source,
        confirmed=confirmed,
        target=intent.target,
        content=intent.content,
    )
    return ExecutionResult(result.ok, result.message, result.payload)


def execute_text(
    client: ObsidianClient,
    text: str,
    *,
    source: ActionSource = ActionSource.KEYBOARD,
    confirmed: bool = False,
    policy: PermissionPolicy = DEFAULT_POLICY,
    registry: SkillRegistry | None = None,
) -> ExecutionResult:
    return execute_intent(
        client,
        parse_intent(text),
        source=source,
        confirmed=confirmed,
        policy=policy,
        registry=registry,
    )
