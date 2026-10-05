from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum

from .router import IntentKind


class ActionSource(str, Enum):
    KEYBOARD = "keyboard"
    VOICE = "voice"
    BRAIN = "brain"
    SYSTEM = "system"


class RiskLevel(IntEnum):
    READ = 10
    WRITE = 20
    DESTRUCTIVE = 30


@dataclass(frozen=True)
class ActionSpec:
    name: str
    risk: RiskLevel
    voice_allowed: bool = False
    brain_allowed: bool = False
    requires_confirmation: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


ACTION_SPECS: dict[IntentKind, ActionSpec] = {
    IntentKind.SEARCH: ActionSpec("obsidian.search", RiskLevel.READ, voice_allowed=True),
    IntentKind.READ: ActionSpec("obsidian.read", RiskLevel.READ, voice_allowed=True),
    IntentKind.OPEN: ActionSpec("obsidian.open", RiskLevel.READ, voice_allowed=True),
    IntentKind.APPEND: ActionSpec("obsidian.append", RiskLevel.WRITE, voice_allowed=True),
    IntentKind.WRITE: ActionSpec("obsidian.overwrite", RiskLevel.WRITE, voice_allowed=False),
}


class PermissionPolicy:
    """Central authorization policy for local actions.

    Brain output is denied execution by default. Voice is opt-in per action. Any
    destructive action requires explicit confirmation even for keyboard/system
    sources unless a future policy deliberately changes that behavior.
    """

    def evaluate(
        self,
        spec: ActionSpec,
        *,
        source: ActionSource,
        confirmed: bool = False,
    ) -> PolicyDecision:
        if source == ActionSource.BRAIN and not spec.brain_allowed:
            return PolicyDecision(False, "El cerebro puede proponer acciones, pero no ejecutarlas.")

        if source == ActionSource.VOICE and not spec.voice_allowed:
            return PolicyDecision(False, f"La acción {spec.name} no está permitida por voz.")

        if spec.risk >= RiskLevel.DESTRUCTIVE and not confirmed:
            return PolicyDecision(False, f"La acción {spec.name} requiere confirmación explícita.")

        if spec.requires_confirmation and not confirmed:
            return PolicyDecision(False, f"La acción {spec.name} requiere confirmación explícita.")

        return PolicyDecision(True, "permitido")


DEFAULT_POLICY = PermissionPolicy()


def action_spec_for_intent(kind: IntentKind) -> ActionSpec | None:
    return ACTION_SPECS.get(kind)


def permission_matrix() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for kind, spec in ACTION_SPECS.items():
        rows.append(
            {
                "intent": kind.value,
                "action": spec.name,
                "risk": spec.risk.name.lower(),
                "keyboard": "yes",
                "voice": "yes" if spec.voice_allowed else "no",
                "brain": "yes" if spec.brain_allowed else "no",
                "confirmation": "yes" if spec.requires_confirmation or spec.risk >= RiskLevel.DESTRUCTIVE else "no",
            }
        )
    return rows
