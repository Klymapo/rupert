# Architecture

Rupert is local-first and low-cost. GitHub stores source code and reproducible configuration; runtime data stays on the machine.

## Layers

1. Memory: Obsidian + Local REST API/MCP.
2. Hub: Python routing and permission boundaries.
3. Voice: whisper.cpp for STT; Piper/Kokoro later for TTS.
4. Brain adapters: optional local LLM or optional online reasoning backend.
5. Skills: Git/GitHub, Godot, Blender and other explicitly enabled tools.

## Current flow

```text
text / local WAV
      ↓
    Rupert
   ↙     ↘
router   whisper.cpp
  ↓          ↓
Obsidian  transcript
```

## Security boundaries

- bind local services to 127.0.0.1 by default;
- never commit .env, tokens, recordings, model weights or vault contents;
- require explicit confirmation for destructive actions;
- do not expose Obsidian REST/MCP directly to the public Internet.
