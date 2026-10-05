from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .brain import BrainReply, OllamaBackend
from .executor import ExecutionResult, execute_intent
from .obsidian_bridge import ObsidianClient
from .router import IntentKind, parse_intent


class Reasoner(Protocol):
    def chat(self, text: str) -> BrainReply: ...


class TurnMode(str, Enum):
    LOCAL = "local"
    BRAIN = "brain"


@dataclass(frozen=True)
class AssistantTurn:
    mode: TurnMode
    message: str
    payload: object | None = None
    should_exit: bool = False


class AssistantEngine:
    """Route known commands locally and unknown language to a text-only brain."""

    def __init__(self, client: ObsidianClient, brain: Reasoner | None = None):
        self.client = client
        self.brain = brain or OllamaBackend()

    def handle(self, text: str) -> AssistantTurn:
        intent = parse_intent(text)
        if intent.kind != IntentKind.UNKNOWN:
            result: ExecutionResult = execute_intent(self.client, intent)
            return AssistantTurn(
                TurnMode.LOCAL,
                result.message,
                payload=result.payload,
                should_exit=result.should_exit,
            )

        reply = self.brain.chat(text.strip())
        return AssistantTurn(TurnMode.BRAIN, reply.text)


def _show_payload(payload: object) -> None:
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload)


def run_assistant_shell(client: ObsidianClient, brain: Reasoner | None = None) -> int:
    """Interactive single-entry Rupert console.

    Known deterministic commands execute locally. Everything else is sent to the
    configured reasoning backend and returned as text only.
    """
    engine = AssistantEngine(client, brain=brain)
    print("Rupert v0.7 — consola híbrida")
    print("Comandos conocidos se ejecutan localmente; conversación usa el cerebro configurado.")
    print("Escribe 'ayuda' para comandos locales o 'salir' para terminar.")

    while True:
        try:
            text = input("rupert> ")
            turn = engine.handle(text)
            if turn.payload is not None:
                _show_payload(turn.payload)
            else:
                prefix = "Rupert" if turn.mode == TurnMode.BRAIN else "Local"
                print(f"{prefix}: {turn.message}")
            if turn.should_exit:
                return 0
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        except RuntimeError as exc:
            print(f"❌ {exc}")
