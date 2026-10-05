from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .obsidian_bridge import ObsidianClient
from .permissions import (
    ACTION_SPECS,
    DEFAULT_POLICY,
    ActionSource,
    ActionSpec,
    PermissionPolicy,
)
from .router import IntentKind


@dataclass(frozen=True)
class SkillResult:
    ok: bool
    message: str
    payload: Any = None


SkillHandler = Callable[..., SkillResult]


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    description: str
    spec: ActionSpec
    handler: SkillHandler


class SkillRegistry:
    """Registry that enforces policy before invoking any skill handler."""

    def __init__(self, policy: PermissionPolicy = DEFAULT_POLICY):
        self.policy = policy
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, definition: SkillDefinition) -> None:
        if definition.name in self._skills:
            raise ValueError(f"Skill duplicada: {definition.name}")
        if definition.name != definition.spec.name:
            raise ValueError("SkillDefinition.name debe coincidir con ActionSpec.name")
        self._skills[definition.name] = definition

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def names(self) -> list[str]:
        return sorted(self._skills)

    def describe(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for name in self.names():
            definition = self._skills[name]
            spec = definition.spec
            rows.append(
                {
                    "name": name,
                    "description": definition.description,
                    "risk": spec.risk.name.lower(),
                    "voice": "yes" if spec.voice_allowed else "no",
                    "brain": "yes" if spec.brain_allowed else "no",
                    "confirmation": "yes" if spec.requires_confirmation else "no",
                }
            )
        return rows

    def invoke(
        self,
        name: str,
        *,
        source: ActionSource,
        confirmed: bool = False,
        **kwargs: Any,
    ) -> SkillResult:
        definition = self.get(name)
        if definition is None:
            return SkillResult(False, f"Skill desconocida: {name}")

        decision = self.policy.evaluate(
            definition.spec,
            source=source,
            confirmed=confirmed,
        )
        if not decision.allowed:
            return SkillResult(False, decision.reason)

        result = definition.handler(**kwargs)
        if not isinstance(result, SkillResult):
            raise TypeError(f"La skill {name} debe devolver SkillResult")
        return result


INTENT_SKILLS: dict[IntentKind, str] = {
    IntentKind.SEARCH: "obsidian.search",
    IntentKind.READ: "obsidian.read",
    IntentKind.OPEN: "obsidian.open",
    IntentKind.APPEND: "obsidian.append",
    IntentKind.WRITE: "obsidian.overwrite",
}


def skill_name_for_intent(kind: IntentKind) -> str | None:
    return INTENT_SKILLS.get(kind)


def build_obsidian_registry(
    client: ObsidianClient,
    *,
    policy: PermissionPolicy = DEFAULT_POLICY,
) -> SkillRegistry:
    registry = SkillRegistry(policy)

    def search(*, target: str, content: str = "") -> SkillResult:
        del content
        payload = client.search(target)
        count = len(payload) if isinstance(payload, list) else None
        message = (
            f"Encontré {count} resultado{'s' if count != 1 else ''}."
            if count is not None
            else "Búsqueda terminada."
        )
        return SkillResult(True, message, payload)

    def read(*, target: str, content: str = "") -> SkillResult:
        del content
        payload = client.read(target)
        return SkillResult(True, f"Leí {target}.", payload)

    def open_note(*, target: str, content: str = "") -> SkillResult:
        del content
        client.open_note(target)
        return SkillResult(True, f"Abrí {target}.")

    def append(*, target: str, content: str = "") -> SkillResult:
        client.append(target, content)
        return SkillResult(True, f"Añadí el contenido a {target}.")

    def overwrite(*, target: str, content: str = "") -> SkillResult:
        client.write(target, content)
        return SkillResult(True, f"Escribí {target}.")

    handlers: dict[IntentKind, tuple[str, SkillHandler]] = {
        IntentKind.SEARCH: ("Busca texto dentro del vault de Obsidian.", search),
        IntentKind.READ: ("Lee una nota de Obsidian.", read),
        IntentKind.OPEN: ("Abre una nota en la interfaz de Obsidian.", open_note),
        IntentKind.APPEND: ("Añade contenido al final de una nota.", append),
        IntentKind.WRITE: ("Sobrescribe el contenido completo de una nota.", overwrite),
    }

    for kind, (description, handler) in handlers.items():
        spec = ACTION_SPECS[kind]
        registry.register(SkillDefinition(spec.name, description, spec, handler))

    return registry
