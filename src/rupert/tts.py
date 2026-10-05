from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_PIPER_VOICE = "es_MX-ald-medium"


def piper_data_dir() -> Path:
    explicit = os.getenv("PIPER_DATA_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    runtime = Path(os.getenv("RUPERT_RUNTIME", ".runtime")).resolve()
    return runtime / "models" / "piper"


def piper_voice() -> str:
    return os.getenv("PIPER_VOICE", DEFAULT_PIPER_VOICE)


def piper_available() -> bool:
    return importlib.util.find_spec("piper") is not None


def tts_doctor() -> int:
    installed = piper_available()
    ffplay = shutil.which("ffplay")
    data_dir = piper_data_dir()
    voice = piper_voice()
    model = data_dir / f"{voice}.onnx"
    config = data_dir / f"{voice}.onnx.json"

    print("Rupert TTS")
    print("==========")
    print(f"[{'OK' if installed else '--'}] piper-tts")
    print(f"[{'OK' if ffplay else '--'}] ffplay" + (f" -> {ffplay}" if ffplay else ""))
    print(f"[{'OK' if model.exists() else '--'}] voice model -> {model}")
    print(f"[{'OK' if config.exists() else '--'}] voice config -> {config}")
    if not installed or not model.exists() or not config.exists():
        print("\nEjecuta: .\\scripts\\setup-piper.ps1")
    return 0 if installed and model.exists() and config.exists() else 1


def speak(text: str, *, voice: str | None = None, cuda: bool = False) -> None:
    """Speak text locally with Piper. Piper/voice files remain outside Git."""
    if not text.strip():
        return
    if not piper_available():
        raise RuntimeError("piper-tts no está instalado. Ejecuta scripts/setup-piper.ps1")

    selected_voice = voice or piper_voice()
    data_dir = piper_data_dir()
    cmd = [
        sys.executable,
        "-m",
        "piper",
        "-m",
        selected_voice,
        "--data-dir",
        str(data_dir),
    ]
    if cuda:
        cmd.append("--cuda")
    cmd += ["--", text]

    proc = subprocess.run(cmd, check=False, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or f"Piper terminó con {proc.returncode}")
