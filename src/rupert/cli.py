from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

from . import __version__
from .assistant import run_assistant_shell
from .brain import BrainError, OllamaBackend, brain_doctor
from .config import load_local_env
from .obsidian_bridge import DEFAULT_BASE_URL, ObsidianClient, doctor as obsidian_doctor
from .pipeline import process_audio_file, push_to_talk
from .shell import run_shell
from .skills import build_obsidian_registry
from .tts import speak, tts_doctor
from .voice import transcribe_file, voice_doctor
from .wakeword import (
    WakeWordConfig,
    WakeWordDependencyError,
    WakeWordDetector,
    wait_for_activation,
    wake_doctor,
)


def make_client() -> ObsidianClient:
    return ObsidianClient(
        os.getenv("OBSIDIAN_BASE_URL", DEFAULT_BASE_URL),
        os.getenv("OBSIDIAN_API_KEY"),
    )


def _show_payload(value) -> None:
    if value is None:
        return
    if isinstance(value, (dict, list)):
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def _show_turn(turn) -> None:
    print(f"📝 {turn.transcript}")
    _show_payload(turn.result.payload)
    print(f"Rupert: {turn.result.message}")


def local_doctor() -> int:
    print(f"Rupert {__version__}")
    print("===================")
    for command in ("git", "python", "cmake", "ffmpeg", "ffplay", "ollama"):
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
    sub.add_parser("chat", help="Consola única: comandos locales + razonamiento Ollama")
    sub.add_parser("skills", help="Lista skills registradas y su política")
    sub.add_parser("voice-doctor", help="Diagnóstico de whisper.cpp + modelo")
    sub.add_parser("tts-doctor", help="Diagnóstico de Piper + voz local")
    sub.add_parser("wake-doctor", help="Diagnóstico de openWakeWord + modelo Rupert")
    sub.add_parser("wake-monitor", help="Escucha hasta detectar una activación y se detiene")
    sub.add_parser("brain-doctor", help="Diagnóstico del cerebro local Ollama")

    ask = sub.add_parser("ask", help="Consulta al cerebro local sin ejecutar acciones")
    ask.add_argument("text")

    tr = sub.add_parser("transcribe", help="Transcribe un archivo de audio local con whisper.cpp")
    tr.add_argument("file")
    tr.add_argument("--language", "-l", default="auto")

    pa = sub.add_parser("process-audio", help="Transcribe un WAV y ejecuta la orden local")
    pa.add_argument("file")
    pa.add_argument("--language", "-l", default="es")
    pa.add_argument("--speak", action="store_true", help="Responder por voz con Piper")
    pa.add_argument("--tts-cuda", action="store_true")

    talk = sub.add_parser("talk", help="Push-to-talk: ENTER inicia / ENTER detiene")
    talk.add_argument("--language", "-l", default="es")
    talk.add_argument("--speak", action="store_true", help="Responder por voz con Piper")
    talk.add_argument("--tts-cuda", action="store_true")

    say = sub.add_parser("speak", help="Habla texto localmente con Piper")
    say.add_argument("text")
    say.add_argument("--cuda", action="store_true")

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
    if args.command == "chat":
        return run_assistant_shell(make_client())
    if args.command == "skills":
        _show_payload(build_obsidian_registry(make_client()).describe())
        return 0
    if args.command == "voice-doctor":
        return voice_doctor()
    if args.command == "tts-doctor":
        return tts_doctor()
    if args.command == "wake-doctor":
        return wake_doctor()
    if args.command == "brain-doctor":
        return brain_doctor()
    if args.command == "ask":
        try:
            reply = OllamaBackend().chat(args.text)
            print(reply.text)
            return 0
        except (BrainError, ValueError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "wake-monitor":
        try:
            cfg = WakeWordConfig.from_env()
            detector = WakeWordDetector(cfg)
            print(f"👂 Escuchando wake word con umbral {cfg.threshold:.2f}. Ctrl+C cancela.")
            score = wait_for_activation(detector)
            print(f"✅ Wake word detectado. Score={score:.3f}")
            return 0
        except KeyboardInterrupt:
            print("\nCancelado.")
            return 130
        except (FileNotFoundError, ValueError, WakeWordDependencyError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "transcribe":
        try:
            print(transcribe_file(args.file, language=args.language))
            return 0
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "process-audio":
        try:
            turn = process_audio_file(
                make_client(),
                args.file,
                language=args.language,
                speak_response=args.speak,
                tts_cuda=args.tts_cuda,
            )
            _show_turn(turn)
            return 0 if turn.result.ok else 2
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "talk":
        try:
            turn = push_to_talk(
                make_client(),
                language=args.language,
                speak_response=args.speak,
                tts_cuda=args.tts_cuda,
            )
            _show_turn(turn)
            return 0 if turn.result.ok else 2
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
    if args.command == "speak":
        try:
            speak(args.text, cuda=args.cuda)
            return 0
        except RuntimeError as exc:
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
