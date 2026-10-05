from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


class WakeWordDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class WakeWordConfig:
    model: Path
    threshold: float = 0.5
    chunk_size: int = 1280
    samplerate: int = 16000
    framework: str = "onnx"

    @classmethod
    def from_env(cls) -> "WakeWordConfig":
        runtime = Path(os.getenv("RUPERT_RUNTIME", ".runtime")).resolve()
        model = Path(
            os.getenv("WAKEWORD_MODEL", str(runtime / "models" / "wakeword" / "rupert.onnx"))
        ).expanduser().resolve()
        threshold = float(os.getenv("WAKEWORD_THRESHOLD", "0.5"))
        framework = os.getenv("WAKEWORD_FRAMEWORK", "onnx").strip().lower()
        chunk_size = int(os.getenv("WAKEWORD_CHUNK_SIZE", "1280"))
        return cls(model=model, threshold=threshold, framework=framework, chunk_size=chunk_size)

    def validate(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("WAKEWORD_THRESHOLD debe estar entre 0 y 1")
        if self.chunk_size <= 0:
            raise ValueError("WAKEWORD_CHUNK_SIZE debe ser positivo")
        if self.samplerate != 16000:
            raise ValueError("openWakeWord espera audio a 16 kHz")
        if self.framework not in {"onnx", "tflite"}:
            raise ValueError("WAKEWORD_FRAMEWORK debe ser onnx o tflite")


def openwakeword_available() -> bool:
    return importlib.util.find_spec("openwakeword") is not None


def sounddevice_available() -> bool:
    return importlib.util.find_spec("sounddevice") is not None


def _load_model(config: WakeWordConfig):
    if not openwakeword_available():
        raise WakeWordDependencyError(
            "Falta openwakeword. Instala Rupert con: pip install -e .[wake]"
        )
    from openwakeword.model import Model  # type: ignore

    return Model(
        wakeword_models=[str(config.model)],
        inference_framework=config.framework,
    )


def _prediction_score(prediction: Any) -> float:
    if not isinstance(prediction, dict) or not prediction:
        return 0.0

    values: list[float] = []
    for value in prediction.values():
        try:
            values.append(float(value))
            continue
        except (TypeError, ValueError):
            pass
        try:
            values.append(max(float(v) for v in value))
        except (TypeError, ValueError):
            continue
    return max(values, default=0.0)


class WakeWordDetector:
    def __init__(self, config: WakeWordConfig, *, model: Any | None = None):
        config.validate()
        if not config.model.exists() and model is None:
            raise FileNotFoundError(config.model)
        self.config = config
        self.model = model if model is not None else _load_model(config)

    def score_pcm16(self, pcm: bytes) -> float:
        try:
            import numpy as np
        except ImportError as exc:  # pragma: no cover - openwakeword installs numpy transitively
            raise WakeWordDependencyError("Falta numpy para procesar el wake word") from exc
        samples = np.frombuffer(pcm, dtype=np.int16)
        return _prediction_score(self.model.predict(samples))

    def detected_pcm16(self, pcm: bytes) -> tuple[bool, float]:
        score = self.score_pcm16(pcm)
        return score >= self.config.threshold, score


def wake_doctor(config: WakeWordConfig | None = None) -> int:
    cfg = config or WakeWordConfig.from_env()
    try:
        cfg.validate()
        valid_config = True
    except ValueError as exc:
        valid_config = False
        print(f"❌ configuración: {exc}")

    oww = openwakeword_available()
    sd = sounddevice_available()
    model = cfg.model.exists()

    print("Rupert Wake Word")
    print("================")
    print(f"[{'OK' if oww else '--'}] openwakeword 0.6.x")
    print(f"[{'OK' if sd else '--'}] sounddevice")
    print(f"[{'OK' if model else '--'}] model -> {cfg.model}")
    print(f"[{'OK' if valid_config else '--'}] threshold -> {cfg.threshold}")
    print(f"[{'OK' if cfg.framework == 'onnx' else '--'}] framework -> {cfg.framework}")

    if not oww or not sd:
        print("\nEjecuta: .\\scripts\\setup-wakeword.ps1")
    if not model:
        print("\nFalta el modelo personalizado de 'Rupert'. Consulta docs/WAKEWORD.md")
    return 0 if oww and sd and model and valid_config else 1


def wait_for_activation(
    detector: WakeWordDetector,
    *,
    stream_factory: Callable[..., Any] | None = None,
) -> float:
    """Block until one wake-word activation and return its score."""
    if stream_factory is None:
        if not sounddevice_available():
            raise WakeWordDependencyError(
                "Falta sounddevice. Instala Rupert con: pip install -e .[wake]"
            )
        import sounddevice as sd  # type: ignore

        stream_factory = sd.RawInputStream

    cfg = detector.config
    with stream_factory(
        samplerate=cfg.samplerate,
        channels=1,
        dtype="int16",
        blocksize=cfg.chunk_size,
    ) as stream:
        while True:
            data, overflowed = stream.read(cfg.chunk_size)
            if overflowed:
                print("⚠️ wake-word: audio overflow")
            detected, score = detector.detected_pcm16(bytes(data))
            if detected:
                return score
