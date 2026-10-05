# Rupert

**Rupert** is Atatoriz's local-first, low-cost personal assistant hub.

GitHub stores code, reproducible configuration and tests. Secrets, recordings, model weights, Obsidian vault data and private runtime state stay on the machine.

## Current milestone — v0.5

```text
          "Rupert"
             │
             ↓
      openWakeWord ($0)
             │
       activation only
             │
             ├──────────────┐
             ↓              │
       microphone        keyboard
             │              │
             ↓              │
      whisper.cpp ($0)      │
             │              │
             └──────┬───────┘
                    ↓
          deterministic router
                    ↓
            command executor
             │              │
             ↓              ↓
       Obsidian REST     Piper TTS
             │              │
             ↓              ↓
           vault         speakers
```

Simple commands do not use an LLM. The core target is **$0/month**.

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

## Local speech-to-text — whisper.cpp

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

## Local text-to-speech — Piper

```powershell
.\scripts\setup-piper.ps1
.\.venv\Scripts\rupert.exe tts-doctor
.\.venv\Scripts\rupert.exe speak "Rupert está en línea."
```

The default voice is Mexican Spanish (`es_MX-ald-medium`).

## Push-to-talk

```powershell
.\.venv\Scripts\rupert.exe talk
```

Press ENTER to start recording and ENTER again to stop. To answer aloud:

```powershell
.\.venv\Scripts\rupert.exe talk --speak
```

## Local wake word — openWakeWord

Install the optional wake-word layer:

```powershell
.\scripts\setup-wakeword.ps1
```

The final activation phrase is **Rupert**, using a custom ONNX model stored outside Git at:

```text
.runtime/models/wakeword/rupert.onnx
```

Diagnostics and one-shot monitoring:

```powershell
.\.venv\Scripts\rupert.exe wake-doctor
.\.venv\Scripts\rupert.exe wake-monitor
```

For an initial smoke test before the custom model exists, the setup script can optionally download openWakeWord's upstream `hey_jarvis` model:

```powershell
.\scripts\setup-wakeword.ps1 -DownloadSmokeModel
```

See `docs/WAKEWORD.md` for custom-model training. v0.5 intentionally stops after wake-word detection; it does not yet auto-execute commands after an activation.

## Cost / privacy policy

Core target: **$0/month**. Paid APIs are never required by the core. Models, recordings, secrets and the Obsidian vault stay outside Git.

LLMs are an optional future reasoning backend. Routine commands such as opening, reading, searching or appending notes should stay deterministic and local whenever possible.

See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, and `docs/WAKEWORD.md`.
