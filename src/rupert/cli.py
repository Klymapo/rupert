from __future__ import annotations

import argparse
import os
import shutil
import sys

from . import __version__
from .config import load_local_env
from .obsidian_bridge import DEFAULT_BASE_URL, ObsidianClient, doctor as obsidian_doctor
from .shell import run_shell
from .voice import transcribe_file, voice_doctor


def make_client() -> ObsidianClient:
    return ObsidianClient(
        os.getenv("OBSIDIAN_BASE_URL", DEFAULT_BASE_URL),
        os.getenv("OBSIDIAN_API_KEY"),
    )


def local_doctor() -> int:
    print(f"Rupert {__version__}")
    print("===================")
    for command in ("git", "python", "cmake", "ffmpeg", "ollama"):
        path = shutil.which(command)
        print(f"[{'OK' if path else '--'}] {command}" + (f" -> {path}" if path else ""))
    print(f"[{'OK' if os.getenv('OBSIDIAN_API_KEY') else '--'}] OBSIDIAN_API_KEY")
    print("\nObsidian:")
    try:
        return obsidian_doctor(make_client())
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rupert", description="Rupert — local-first assistant hub")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Diagnóstico local + Obsidian")
    sub.add_parser("shell", help="Shell local de órdenes sin LLM")
    sub.add_parser("voice-doctor", help="Diagnóstico de whisper.cpp + modelo")
    tr = sub.add_parser("transcribe", help="Transcribe un archivo de audio local con whisper.cpp")
    tr.add_argument("file")
    tr.add_argument("--language", "-l", default="auto")
    obs = sub.add_parser("obsidian", help="Comandos directos de Obsidian")
    obs.add_argument("args", nargs=argparse.REMAINDER)
    return p


def main() -> int:
    load_local_env()
    args = build_parser().parse_args()
    if args.command == "doctor":
        return local_doctor()
    if args.command == "shell":
        return run_shell(make_client())
    if args.command == "voice-doctor":
        return voice_doctor()
    if args.command == "transcribe":
        try:
            print(transcribe_file(args.file, language=args.language))
            return 0
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "obsidian":
        from .obsidian_bridge import main as obsidian_main
        old = sys.argv
        try:
            sys.argv = ["rupert obsidian", *args.args]
            return obsidian_main()
        finally:
            sys.argv = old
    return 2
