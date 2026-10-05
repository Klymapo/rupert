from __future__ import annotations

import wave
from pathlib import Path
from typing import Callable


class AudioDependencyError(RuntimeError):
    pass


def _load_sounddevice():
    try:
        import sounddevice as sd  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on local optional install
        raise AudioDependencyError(
            "Falta sounddevice. Instala Rupert con el extra de voz: pip install -e .[voice]"
        ) from exc
    return sd


def record_push_to_talk(
    output_path: str | Path,
    *,
    samplerate: int = 16000,
    channels: int = 1,
    prompt: Callable[[str], str] = input,
) -> Path:
    """Record PCM16 WAV between two ENTER presses.

    Uses sounddevice only at runtime so the core package stays dependency-free.
    """
    if samplerate <= 0:
        raise ValueError("samplerate debe ser positivo")
    if channels <= 0:
        raise ValueError("channels debe ser positivo")

    sd = _load_sounddevice()
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[bytes] = []

    def callback(indata, frames, time_info, status) -> None:  # noqa: ANN001
        del frames, time_info
        if status:
            print(f"⚠️ audio: {status}")
        chunks.append(bytes(indata))

    prompt("Pulsa ENTER para empezar a hablar...")
    with sd.RawInputStream(
        samplerate=samplerate,
        channels=channels,
        dtype="int16",
        callback=callback,
    ):
        prompt("🎙️ Grabando. Pulsa ENTER para detener...")

    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(samplerate)
        wav.writeframes(b"".join(chunks))

    return output
