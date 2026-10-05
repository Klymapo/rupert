# Rupert

**Rupert** is Atatoriz's local-first, low-cost personal assistant hub.

GitHub stores code, reproducible configuration and tests. Secrets, recordings, model weights, Obsidian vault data and private runtime state stay on the machine.

## Current milestone — v0.4

```text
Keyboard / microphone / local WAV
              │
              ↓
        whisper.cpp ($0)
              │
              ↓
        transcript text
              │
              ↓
 deterministic router ($0, no LLM)
              │
              ↓
         command executor
          │           │
          ↓           ↓
    Obsidian REST   Piper TTS
          │           │
          ↓           ↓
       vault        speakers
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

## Local text-to-speech — Piper

Install the optional local audio/TTS extras and download the default Mexican Spanish voice (`es_MX-ald-medium`):

```powershell
.\scripts\setup-piper.ps1
```

Then:

```powershell
.\.venv\Scripts\rupert.exe tts-doctor
.\.venv\Scripts\rupert.exe speak "Rupert está en línea."
```

Piper is optional; Rupert's core remains dependency-light.

## Push-to-talk

After Whisper and the local audio extras are installed:

```powershell
.\.venv\Scripts\rupert.exe talk
```

Press ENTER to start recording and ENTER again to stop. Rupert transcribes the WAV locally and sends the transcript to the same deterministic command executor used by the keyboard shell.

To make Rupert answer aloud:

```powershell
.\.venv\Scripts\rupert.exe talk --speak
```

For testing the full command pipeline from an existing WAV without a microphone:

```powershell
.\.venv\Scripts\rupert.exe process-audio .\sample.wav --speak
```

No audio is uploaded by Rupert.

## Cost / privacy policy

Core target: **$0/month**. Paid APIs are never required by the core. Models, recordings, secrets and the Obsidian vault stay outside Git.

LLMs are an optional future reasoning backend. Routine commands such as opening, reading, searching or appending notes should stay deterministic and local whenever possible.

See `docs/ARCHITECTURE.md` and `docs/SECURITY.md`.
