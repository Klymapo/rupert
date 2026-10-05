from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_PIPER_VOICE = "es_MX-ald-medium"


def runtime_root() -> Path:
    return Path(os.getenv("RUPERT_RUNTIME", ".runtime")).resolve()


def piper_data_dir() -> Path:
    explicit = os.getenv("PIPER_DATA_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    return runtime_root() / "models" / "piper"


def piper_voice() -> str:
    return os.getenv("PIPER_VOICE", DEFAULT_PIPER_VOICE)


def piper_available() -> bool:
    return importlib.util.find_spec("piper") is not None


def playback_available() -> bool:
    if sys.platform.startswith("win"):
        return True
    if sys.platform == "darwin":
        return shutil.which("afplay") is not None
    return shutil.which("ffplay") is not None


def play_wav(path: str | Path) -> None:
    wav = Path(path).expanduser().resolve()
    if sys.platform.startswith("win"):
        import winsound

        winsound.PlaySound(str(wav), winsound.SND_FILENAME)
        return
    if sys.platform == "darwin":
        player = shutil.which("afplay")
        if not player:
            raise RuntimeError("No encuentro afplay para reproducir audio")
        proc = subprocess.run([player, str(wav)], check=False)
    else:
        player = shutil.which("ffplay")
        if not player:
            raise RuntimeError("No encuentro ffplay para reproducir audio")
        proc = subprocess.run([player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(wav)], check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"El reproductor terminó con {proc.returncode}")


def tts_doctor() -> int:
    installed = piper_available()
    playback = playback_available()
    data_dir = piper_data_dir()
    voice = piper_voice()
    model = data_dir / f"{voice}.onnx"
    config = data_dir / f"{voice}.onnx.json"

    print("Rupert TTS")
    print("==========")
    print(f"[{'OK' if installed else '--'}] piper-tts")
    print(f"[{'OK' if playback else '--'}] audio playback")
    print(f"[{'OK' if model.exists() else '--'}] voice model -> {model}")
    print(f"[{'OK' if config.exists() else '--'}] voice config -> {config}")
    if not installed or not model.exists() or not config.exists():
        print("\nEjecuta: .\\scripts\\setup-piper.ps1")
    return 0 if installed and playback and model.exists() and config.exists() else 1


def synthesize(
    text: str,
    *,
    voice: str | None = None,
    cuda: bool = False,
    output_path: str | Path | None = None,
) -> Path:
    if not text.strip():
        raise ValueError("No hay texto para sintetizar")
    if not piper_available():
        raise RuntimeError("piper-tts no está instalado. Ejecuta scripts/setup-piper.ps1")

    selected_voice = voice or piper_voice()
    data_dir = piper_data_dir()
    output = Path(output_path or (runtime_root() / "audio" / "tts-last.wav")).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "piper",
        "-m",
        selected_voice,
        "--data-dir",
        str(data_dir),
        "-f",
        str(output),
    ]
    if cuda:
        cmd.append("--cuda")
    cmd += ["--", text]

    proc = subprocess.run(cmd, check=False, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or f"Piper terminó con {proc.returncode}")
    if not output.exists():
        raise RuntimeError("Piper terminó sin crear el WAV esperado")
    return output


def speak(text: str, *, voice: str | None = None, cuda: bool = False) -> None:
    """Synthesize and play locally. Voice files and WAVs stay outside Git."""
    if not text.strip():
        return
    wav = synthesize(text, voice=voice, cuda=cuda)
    play_wav(wav)
