# Architecture

Rupert is local-first and low-cost. GitHub stores source code and reproducible configuration; runtime data stays on the machine.

## Layers

1. Memory: Obsidian + Local REST API/MCP.
2. Hub: Python routing, deterministic execution and permission boundaries.
3. Wake word: optional `openWakeWord` ONNX detector, fully local.
4. Audio input: optional `sounddevice` recorder.
5. STT: `whisper.cpp`, fully local.
6. TTS: optional Piper backend, fully local. Kokoro can be added later behind the same boundary.
7. Brain: optional local Ollama reasoning backend, text-only in v0.6.
8. Skills: Git/GitHub, Godot, Blender and other explicitly enabled tools.

## v0.6 flow

```text
microphone                                  keyboard
    │                                          │
openWakeWord                                   │
    │                                          │
whisper.cpp                                    │
    │                                          │
    └──────────────────────┬───────────────────┘
                           ↓
                      input text
                           │
             ┌─────────────┴─────────────┐
             │                           │
       known deterministic         reasoning request
            intent                       │
             │                           ↓
             ↓                       Ollama local
     permission/executor             text reply only
        │          │                      │
        ↓          ↓                      │
  Obsidian REST  future skills            │
        │                                 │
        ↓                                 │
      vault                         optional Piper
                                          │
                                          ↓
                                       speakers
```

The local brain is **not** in the execution path. It may explain or propose an action, but it cannot directly invoke Rupert skills. Execution stays behind the deterministic parser, permission rules and executor.

The wake-word detector is activation only, never authorization.

## Runtime directories

`.runtime/` is intentionally ignored by Git and may contain:

- downloaded model weights;
- custom wake-word models;
- cloned/build dependencies such as whisper.cpp;
- temporary microphone recordings;
- generated TTS WAV files.

Ollama manages its own local model store outside this repository.

## Reasoning routing

Current v0.6 keeps reasoning explicit through `rupert ask`. A later milestone may route unknown text to a brain adapter for interpretation, but the brain must return a proposal rather than execute it.

Target policy:

```text
request
  ↓
known deterministic route? ─────────────── yes → execute locally ($0)
  │
  no
  ↓
reasoning needed? ──────────────────────── yes → local Ollama ($0 API)
  │                                                │
  no                                               ↓
  │                                           text/proposal
  ↓                                                │
answer/error                              permission validation
                                                   │
                                     explicit execution only if allowed
```

## Network boundaries

- Obsidian REST/MCP defaults to loopback.
- Ollama defaults to `http://127.0.0.1:11434`.
- Rupert rejects a non-loopback brain endpoint unless `RUPERT_ALLOW_REMOTE_BRAIN=1` is explicitly configured.

## Security boundaries

- bind local services to `127.0.0.1` by default;
- never commit `.env`, tokens, recordings, model weights or vault contents;
- require explicit confirmation for destructive actions;
- do not expose Obsidian REST/MCP directly to the public Internet;
- treat transcripts as untrusted input before executing system-level skills;
- treat wake-word detection as activation only, never as authorization;
- treat LLM output as untrusted advice/proposals, never as implicit permission to act.
