# Rupert

**Rupert** is Atatoriz's local-first, low-cost personal assistant hub.

GitHub stores code, reproducible configuration and tests. Secrets, recordings, model weights, Obsidian vault data and private runtime state stay on the machine.

## Current milestone — v0.6

```text
          "Rupert" / keyboard
                  │
        ┌─────────┴──────────┐
        │                    │
 known local command    reasoning request
        │                    │
        ↓                    ↓
 deterministic router    Ollama local
        │                (text only)
        ↓                    │
 command executor            │
   │          │              │
   ↓          ↓              │
Obsidian   Piper TTS ←───────┘

Voice input: openWakeWord → microphone → whisper.cpp → same routing layer
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

Example deterministic commands:

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

```powershell
.\scripts\setup-wakeword.ps1
```

The final activation phrase is **Rupert**, using a custom ONNX model stored outside Git at:

```text
.runtime/models/wakeword/rupert.onnx
```

```powershell
.\.venv\Scripts\rupert.exe wake-doctor
.\.venv\Scripts\rupert.exe wake-monitor
```

See `docs/WAKEWORD.md` for custom-model training. Wake detection is activation, not authorization.

## Optional local brain — Ollama

Rupert can use Ollama for reasoning while keeping execution permissions separate.

Rupert does **not** install Ollama or force a model download. Once Ollama is installed explicitly:

```powershell
.\scripts\setup-ollama.ps1
```

After choosing a model:

```powershell
.\scripts\setup-ollama.ps1 -Model <model-name>
```

Set the same model in `.env`, then:

```powershell
.\.venv\Scripts\rupert.exe brain-doctor
.\.venv\Scripts\rupert.exe ask "Dame tres alternativas para esta idea"
```

`ask` returns text only. The local model cannot directly execute Rupert skills or claim that an action was completed.

See `docs/BRAIN.md` for the permission model.

## Cost / privacy policy

Core target: **$0/month**. Paid APIs are never required by the core. Models, recordings, secrets and the Obsidian vault stay outside Git.

Routine commands such as opening, reading, searching or appending notes remain deterministic and local whenever possible. LLM reasoning is optional and does not replace the permission/executor layer.

See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/WAKEWORD.md`, and `docs/BRAIN.md`.
