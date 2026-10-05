from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WhisperCppConfig:
    executable: Path
    model: Path
    language: str = "auto"


def default_runtime_root() -> Path:
    return Path(os.getenv("RUPERT_RUNTIME", ".runtime")).resolve()


def detect_whisper_executable() -> Path | None:
    explicit = os.getenv("WHISPER_CPP_EXE")
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.exists():
            return p

    runtime = default_runtime_root()
    candidates = [
        runtime / "vendors" / "whisper.cpp" / "build" / "bin" / "Release" / "whisper-cli.exe",
        runtime / "vendors" / "whisper.cpp" / "build" / "bin" / "whisper-cli.exe",
        runtime / "vendors" / "whisper.cpp" / "build" / "bin" / "whisper-cli",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    for name in ("whisper-cli", "whisper-cli.exe", "main", "main.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def detect_model() -> Path | None:
    explicit = os.getenv("WHISPER_MODEL")
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.exists():
            return p
    runtime = default_runtime_root()
    candidates = [
        runtime / "models" / "whisper" / "ggml-base.bin",
        runtime / "models" / "whisper" / "ggml-small.bin",
        runtime / "vendors" / "whisper.cpp" / "models" / "ggml-base.bin",
    ]
    return next((p for p in candidates if p.exists()), None)


def voice_doctor() -> int:
    exe = detect_whisper_executable()
    model = detect_model()
    print("Rupert Voice")
    print("============")
    print(f"[{'OK' if exe else '--'}] whisper.cpp" + (f" -> {exe}" if exe else ""))
    print(f"[{'OK' if model else '--'}] whisper model" + (f" -> {model}" if model else ""))
    if not exe:
        print("\nEjecuta: .\\scripts\\setup-whisper.ps1")
    if exe and not model:
        print("\nEjecuta: .\\scripts\\setup-whisper.ps1 -SkipBuild")
    return 0 if exe and model else 1


def transcribe_file(audio_path: str | Path, *, language: str = "auto") -> str:
    audio = Path(audio_path).expanduser().resolve()
    if not audio.exists():
        raise FileNotFoundError(audio)
    exe = detect_whisper_executable()
    model = detect_model()
    if not exe:
        raise RuntimeError("whisper.cpp no está instalado. Ejecuta scripts/setup-whisper.ps1")
    if not model:
        raise RuntimeError("No encuentro un modelo Whisper. Ejecuta scripts/setup-whisper.ps1")

    cmd = [str(exe), "-m", str(model), "-f", str(audio), "-nt", "-np"]
    if language and language != "auto":
        cmd += ["-l", language]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or f"whisper.cpp terminó con {proc.returncode}")
    return proc.stdout.strip()
