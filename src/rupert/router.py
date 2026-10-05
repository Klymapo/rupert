from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntentKind(str, Enum):
    HELP = "help"
    SEARCH = "search"
    READ = "read"
    OPEN = "open"
    APPEND = "append"
    WRITE = "write"
    EXIT = "exit"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Intent:
    kind: IntentKind
    target: str = ""
    content: str = ""


def _strip_prefix(text: str, prefixes: tuple[str, ...]) -> str | None:
    lowered = text.casefold()
    for prefix in prefixes:
        if lowered.startswith(prefix.casefold()):
            return text[len(prefix):].strip()
    return None


def parse_intent(text: str) -> Intent:
    raw = text.strip()
    if not raw:
        return Intent(IntentKind.UNKNOWN)

    if raw.casefold() in {"salir", "exit", "quit", "adiós", "adios"}:
        return Intent(IntentKind.EXIT)
    if raw.casefold() in {"ayuda", "help", "?"}:
        return Intent(IntentKind.HELP)

    rest = _strip_prefix(raw, ("buscar ", "busca ", "search "))
    if rest is not None:
        return Intent(IntentKind.SEARCH, target=rest)

    rest = _strip_prefix(raw, ("leer ", "lee ", "read "))
    if rest is not None:
        return Intent(IntentKind.READ, target=rest)

    rest = _strip_prefix(raw, ("abrir ", "abre ", "open "))
    if rest is not None:
        return Intent(IntentKind.OPEN, target=rest)

    for prefixes, kind in [
        (("añadir ", "agregar ", "append "), IntentKind.APPEND),
        (("escribir ", "crear ", "write "), IntentKind.WRITE),
    ]:
        rest = _strip_prefix(raw, prefixes)
        if rest is not None:
            if "::" not in rest:
                return Intent(IntentKind.UNKNOWN, target=rest)
            target, content = rest.split("::", 1)
            return Intent(kind, target=target.strip(), content=content.strip())

    return Intent(IntentKind.UNKNOWN, target=raw)
