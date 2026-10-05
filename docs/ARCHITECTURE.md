# Architecture

Rupert is local-first and low-cost. GitHub stores source code and reproducible configuration; runtime data stays on the machine.

## Layers

1. Memory: Obsidian + Local REST API/MCP.
2. Hub: Python routing, deterministic execution and permission boundaries.
3. Wake word: optional `openWakeWord` ONNX detector, fully local.
4. Audio input: optional `sounddevice` recorder.
5. STT: `whisper.cpp`, fully local.
6. TTS: optional Piper backend, fully local. Kokoro can be added later behind the same boundary.
7. Brain adapters: optional local LLM or optional online reasoning backend.
8. Skills: Git/GitHub, Godot, Blender and other explicitly enabled tools.

## v0.5 flow

```text
                   microphone
                       │
                       ↓
               openWakeWord (local)
                       │
               activation event only
                       │
             ┌─────────┴─────────┐
             │                   │
         push-to-talk         keyboard
             │                   │
             ↓                   │
        whisper.cpp              │
             │                   │
             └─────────┬─────────┘
                       ↓
                   transcript
                       ↓
             deterministic router
                       ↓
             shared command executor
                │              │
                ↓              ↓
          Obsidian REST     response text
                │              │
                ↓         optional Piper
              vault             │
                                ↓
                             speakers
```

The wake-word detector does not execute commands. In v0.5 it stops after one activation so false-positive behavior can be measured before automatic command capture is enabled.

The executor is shared by keyboard and voice. Simple commands do not require an LLM.

## Runtime directories

`.runtime/` is intentionally ignored by Git and may contain:

- downloaded model weights;
- custom wake-word models;
- cloned/build dependencies such as whisper.cpp;
- temporary microphone recordings;
- generated TTS WAV files.

## Future brain routing

A later brain adapter should only receive commands that the deterministic router cannot safely satisfy. The intended order is:

```text
command
  ↓
local deterministic route available? ── yes → execute locally ($0)
  │
  no
  ↓
local LLM suitable? ──────────────────── yes → local reasoning ($0 API)
  │
  no / user requests stronger reasoning
  ↓
optional online reasoning backend
```

## Security boundaries

- bind local services to `127.0.0.1` by default;
- never commit `.env`, tokens, recordings, model weights or vault contents;
- require explicit confirmation for destructive actions;
- do not expose Obsidian REST/MCP directly to the public Internet;
- treat transcripts as untrusted input before executing future system-level skills;
- treat wake-word detection as activation only, never as authorization.
