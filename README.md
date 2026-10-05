# Rupert

**Rupert** is Atatoriz's local-first, low-cost personal assistant hub.

GitHub stores code, reproducible configuration and tests. Secrets, recordings, model weights, Obsidian vault data and private runtime state stay on the machine.

## Current milestone — v0.3

```text
Keyboard / local WAV
        │
        ├── deterministic command router ($0, no LLM)
        │          ↓
        │     Obsidian REST/MCP
        │          ↓
        │       your vault
        │
        └── whisper.cpp ($0, local)
                   ↓
              transcript
```

## Bootstrap

From PowerShell in the repository root:

```powershell
.\scripts\bootstrap.ps1
```

Edit `.env` and set your local Obsidian REST API key. Never commit it.

```powershell
.\.venv\Scripts\rupert.exe doctor
.\.venv\Scripts\rupert.exe shell
```

Example commands:

```text
buscar Theo
leer AlasTheo/Ideas.md
abrir AlasTheo/Ideas.md
añadir AlasTheo/Ideas.md :: Probar a Rupert
salir
```

## Local speech-to-text

Build the pinned whisper.cpp release and download the multilingual `base` model:

```powershell
.\scripts\setup-whisper.ps1
```

Optional NVIDIA CUDA build:

```powershell
.\scripts\setup-whisper.ps1 -Cuda
```

Then:

```powershell
.\.venv\Scripts\rupert.exe voice-doctor
.\.venv\Scripts\rupert.exe transcribe .\sample.wav -l es
```

No audio is uploaded by Rupert.

## Cost / privacy policy

Core target: **$0/month**. Paid APIs are never required by the core. Models, recordings, secrets and the Obsidian vault stay outside Git.

See `docs/ARCHITECTURE.md` and `docs/SECURITY.md`.
