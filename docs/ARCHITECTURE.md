# Architecture

Rupert is local-first and low-cost. GitHub stores source code and reproducible configuration; runtime data stays on the machine.

## Layers

1. Memory: Obsidian + Local REST API/MCP.
2. Hub: Python routing, deterministic execution and permission boundaries.
3. Audio input: optional `sounddevice` push-to-talk recorder.
4. STT: `whisper.cpp`, fully local.
5. TTS: optional Piper backend, fully local. Kokoro can be added later behind the same boundary.
6. Brain adapters: optional local LLM or optional online reasoning backend.
7. Skills: Git/GitHub, Godot, Blender and other explicitly enabled tools.

## v0.4 flow

```text
keyboard                         microphone
   │                                 │
   │                          push-to-talk WAV
   │                                 │
   │                           whisper.cpp
   │                                 │
   └──────────────┬──────────────────┘
                  ↓
              transcript
                  ↓
          deterministic router
                  ↓
          shared command executor
             │             │
             ↓             ↓
       Obsidian REST    response text
             │             │
             ↓        optional Piper
           vault            │
                            ↓
                         speakers
```

The executor is shared by keyboard and voice. Simple commands do not require an LLM.

## Runtime directories

`.runtime/` is intentionally ignored by Git and may contain:

- downloaded model weights;
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
- treat transcripts as untrusted input before executing future system-level skills.
