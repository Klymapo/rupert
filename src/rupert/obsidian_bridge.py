#!/usr/bin/env python3
"""Rupert Hub v0.3 — bridge local para Obsidian Local REST API with MCP.

Sin dependencias externas: usa solo la librería estándar de Python.

Variables de entorno:
  OBSIDIAN_API_KEY   Requerida para operaciones del vault.
  OBSIDIAN_BASE_URL  Opcional. Default: http://127.0.0.1:27123

IMPORTANTE: usa HTTP solo si el plugin está ligado a localhost/127.0.0.1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:27123"


def quote_vault_path(path: str, keep_trailing_slash: bool = False) -> str:
    """Codifica cada componente sin convertir los separadores / del vault."""
    trailing = path.endswith("/")
    parts = [urllib.parse.quote(p, safe="") for p in path.strip("/").split("/") if p]
    encoded = "/".join(parts)
    if keep_trailing_slash and (trailing or path == ""):
        encoded += "/"
    return encoded


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    raw: bytes

    @property
    def text(self) -> str:
        return self.raw.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text) if self.raw else None


class ObsidianClient:
    def __init__(self, base_url: str, api_key: str | None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        content_type: str | None = None,
        accept: str | None = None,
        auth: bool = True,
    ) -> Response:
        headers: dict[str, str] = {}
        if auth:
            if not self.api_key:
                raise RuntimeError("Falta OBSIDIAN_API_KEY en las variables de entorno.")
            headers["Authorization"] = f"Bearer {self.api_key}"
        if content_type:
            headers["Content-Type"] = content_type
        if accept:
            headers["Accept"] = accept

        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return Response(r.status, dict(r.headers.items()), r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Obsidian respondió HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"No pude conectar con {self.base_url}. "
                "¿Obsidian está abierto y el servidor HTTP del plugin está habilitado?"
            ) from e

    def status(self) -> Any:
        return self.request("GET", "/").json()

    def list_dir(self, folder: str = "") -> Any:
        encoded = quote_vault_path(folder, keep_trailing_slash=True)
        path = "/vault/" + encoded
        if not path.endswith("/"):
            path += "/"
        return self.request("GET", path).json()

    def read(self, note_path: str) -> str:
        encoded = quote_vault_path(note_path)
        return self.request("GET", f"/vault/{encoded}", accept="text/markdown").text

    def read_metadata(self, note_path: str) -> Any:
        encoded = quote_vault_path(note_path)
        return self.request(
            "GET", f"/vault/{encoded}", accept="application/vnd.olrapi.note+json"
        ).json()

    def write(self, note_path: str, content: str) -> None:
        encoded = quote_vault_path(note_path)
        self.request(
            "PUT",
            f"/vault/{encoded}",
            body=content.encode("utf-8"),
            content_type="text/markdown; charset=utf-8",
        )

    def append(self, note_path: str, content: str) -> None:
        encoded = quote_vault_path(note_path)
        self.request(
            "POST",
            f"/vault/{encoded}",
            body=content.encode("utf-8"),
            content_type="text/markdown; charset=utf-8",
        )

    def search(self, query: str) -> Any:
        q = urllib.parse.urlencode({"query": query})
        return self.request("POST", f"/search/simple/?{q}", body=b"").json()

    def active(self) -> str:
        return self.request("GET", "/active/", accept="text/markdown").text

    def open_note(self, note_path: str) -> None:
        encoded = quote_vault_path(note_path)
        self.request("POST", f"/open/{encoded}", body=b"")


def pretty(value: Any) -> None:
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def doctor(client: ObsidianClient) -> int:
    print("[1/2] Servidor Obsidian...")
    pretty(client.status())
    print("\n[2/2] Autenticación + acceso al vault...")
    pretty(client.list_dir(""))
    print("\n✅ Rupert Hub ↔ Obsidian: conexión correcta.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rupert Hub v0.3 — Obsidian bridge")
    p.add_argument(
        "--base-url",
        default=os.getenv("OBSIDIAN_BASE_URL", DEFAULT_BASE_URL),
        help=f"Servidor Local REST API (default: {DEFAULT_BASE_URL})",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Prueba servidor, API key y acceso al vault")
    sub.add_parser("status", help="Estado del servidor")

    ls = sub.add_parser("list", help="Lista raíz o una carpeta del vault")
    ls.add_argument("folder", nargs="?", default="")

    read = sub.add_parser("read", help="Lee una nota")
    read.add_argument("path")

    meta = sub.add_parser("meta", help="Lee contenido + metadata de una nota")
    meta.add_argument("path")

    search = sub.add_parser("search", help="Busca texto en el vault")
    search.add_argument("query")

    write = sub.add_parser("write", help="Crea o reemplaza una nota")
    write.add_argument("path")
    write.add_argument("content")

    append = sub.add_parser("append", help="Añade contenido al final de una nota")
    append.add_argument("path")
    append.add_argument("content")

    sub.add_parser("active", help="Lee la nota activa en Obsidian")

    op = sub.add_parser("open", help="Abre una nota en Obsidian")
    op.add_argument("path")
    return p


def main() -> int:
    args = build_parser().parse_args()
    client = ObsidianClient(args.base_url, os.getenv("OBSIDIAN_API_KEY"))

    try:
        if args.command == "doctor":
            return doctor(client)
        if args.command == "status":
            pretty(client.status())
        elif args.command == "list":
            pretty(client.list_dir(args.folder))
        elif args.command == "read":
            print(client.read(args.path))
        elif args.command == "meta":
            pretty(client.read_metadata(args.path))
        elif args.command == "search":
            pretty(client.search(args.query))
        elif args.command == "write":
            client.write(args.path, args.content)
            print(f"✅ Escrito: {args.path}")
        elif args.command == "append":
            client.append(args.path, args.content)
            print(f"✅ Añadido: {args.path}")
        elif args.command == "active":
            print(client.active())
        elif args.command == "open":
            client.open_note(args.path)
            print(f"✅ Abierto en Obsidian: {args.path}")
        return 0
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
