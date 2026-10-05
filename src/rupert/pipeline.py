from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .audio import record_push_to_talk
from .executor import ExecutionResult, execute_intent
from .obsidian_bridge import ObsidianClient
from .router import IntentKind, parse_intent
from .tts import speak
from .voice import transcribe_file


@dataclass(frozen=True)
class VoiceTurn:
    transcript: str
    result: ExecutionResult


def default_audio_path() -> Path:
    runtime = Path(os.getenv("RUPERT_RUNTIME", ".runtime")).resolve()
    return runtime / "audio" / "push-to-talk.wav"


def process_transcript(client: ObsidianClient, transcript: str) -> VoiceTurn:
    cleaned = transcript.strip()
    intent = parse_intent(cleaned)
    if intent.kind == IntentKind.WRITE:
        result = ExecutionResult(
            False,
            "Por voz no sobrescribo notas completas. Usa el teclado o una confirmación explícita.",
        )
    else:
        result = execute_intent(client, intent)
    return VoiceTurn(cleaned, result)


def process_audio_file(
    client: ObsidianClient,
    audio_path: str | Path,
    *,
    language: str = "es",
    speak_response: bool = False,
    tts_cuda: bool = False,
) -> VoiceTurn:
    transcript = transcribe_file(audio_path, language=language)
    turn = process_transcript(client, transcript)
    if speak_response:
        speak(turn.result.message, cuda=tts_cuda)
    return turn


def push_to_talk(
    client: ObsidianClient,
    *,
    output_path: str | Path | None = None,
    language: str = "es",
    speak_response: bool = False,
    tts_cuda: bool = False,
) -> VoiceTurn:
    audio = record_push_to_talk(output_path or default_audio_path())
    return process_audio_file(
        client,
        audio,
        language=language,
        speak_response=speak_response,
        tts_cuda=tts_cuda,
    )
