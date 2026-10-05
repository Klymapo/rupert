from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class BrainError(RuntimeError):
    pass


SYSTEM_PROMPT = """You are Rupert's local reasoning backend.
You may explain, summarize, brainstorm, classify, and propose next steps.
You do NOT have authority to execute commands, modify files, call tools, or claim that an action was performed.
If the user asks for an action, describe the proposed action in plain text. Rupert's deterministic executor and permission layer decide whether anything is actually executed.
Reply in the user's language unless asked otherwise.
"""


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://127.0.0.1:11434"
    model: str = ""
    timeout: float = 120.0
    allow_remote: bool = False

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
            model=os.getenv("OLLAMA_MODEL", "").strip(),
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "120")),
            allow_remote=os.getenv("RUPERT_ALLOW_REMOTE_BRAIN", "0").strip().casefold() in {"1", "true", "yes"},
        )

    def validate(self, *, require_model: bool = True) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("OLLAMA_BASE_URL no es una URL HTTP(S) válida")
        if self.timeout <= 0:
            raise ValueError("OLLAMA_TIMEOUT debe ser positivo")
        if require_model and not self.model:
            raise ValueError("Define OLLAMA_MODEL en .env")
        if not self.allow_remote and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError(
                "Por seguridad Rupert sólo usa un cerebro local. "
                "Define RUPERT_ALLOW_REMOTE_BRAIN=1 únicamente si quieres permitir un servidor remoto."
            )


@dataclass(frozen=True)
class BrainReply:
    text: str
    model: str
    done: bool = True


Requester = Callable[[Request, float], bytes]


def _stdlib_requester(request: Request, timeout: float) -> bytes:
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URL is validated by config
            return response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace") if exc.fp else str(exc)
        raise BrainError(f"Ollama respondió HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise BrainError(f"No pude conectar con Ollama: {exc.reason}") from exc


class OllamaBackend:
    def __init__(self, config: OllamaConfig | None = None, *, requester: Requester | None = None):
        self.config = config or OllamaConfig.from_env()
        self.requester = requester or _stdlib_requester

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        require_model: bool = False,
    ) -> dict[str, Any]:
        self.config.validate(require_model=require_model)
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.config.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        raw = self.requester(request, self.config.timeout)
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BrainError("Ollama devolvió una respuesta JSON inválida") from exc
        if not isinstance(decoded, dict):
            raise BrainError("Ollama devolvió un formato inesperado")
        if decoded.get("error"):
            raise BrainError(str(decoded["error"]))
        return decoded

    def list_models(self) -> list[str]:
        payload = self._request_json("GET", "/api/tags", require_model=False)
        models = payload.get("models", [])
        if not isinstance(models, list):
            return []
        names: list[str] = []
        for model in models:
            if isinstance(model, dict) and model.get("name"):
                names.append(str(model["name"]))
        return names

    def chat(self, text: str, *, system_prompt: str = SYSTEM_PROMPT) -> BrainReply:
        if not text.strip():
            raise ValueError("La consulta al cerebro está vacía")
        payload = self._request_json(
            "POST",
            "/api/chat",
            {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text.strip()},
                ],
                "stream": False,
            },
            require_model=True,
        )
        message = payload.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise BrainError("Ollama no devolvió message.content")
        return BrainReply(
            text=message["content"].strip(),
            model=str(payload.get("model") or self.config.model),
            done=bool(payload.get("done", True)),
        )


def brain_doctor(config: OllamaConfig | None = None, *, requester: Requester | None = None) -> int:
    cfg = config or OllamaConfig.from_env()
    print("Rupert Brain")
    print("============")
    try:
        cfg.validate(require_model=False)
    except ValueError as exc:
        print(f"❌ configuración: {exc}")
        return 1

    print(f"[OK] endpoint -> {cfg.base_url}")
    print(f"[{'OK' if cfg.model else '--'}] model -> {cfg.model or '(sin configurar)'}")
    backend = OllamaBackend(cfg, requester=requester)
    try:
        models = backend.list_models()
    except BrainError as exc:
        print(f"[--] Ollama -> {exc}")
        return 1

    print(f"[OK] Ollama responde; modelos locales: {len(models)}")
    if models:
        for name in models[:8]:
            marker = "*" if name == cfg.model else "-"
            print(f"  {marker} {name}")
    if cfg.model and cfg.model not in models:
        print(f"⚠️ OLLAMA_MODEL={cfg.model} no aparece entre los modelos instalados")
        return 1
    if not cfg.model:
        print("\nDefine OLLAMA_MODEL en .env después de elegir/descargar un modelo local.")
        return 1
    return 0
