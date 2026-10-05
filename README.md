# Rupert

**Rupert** is Atatoriz's local-first, low-cost personal assistant hub.

GitHub stores code, reproducible configuration and tests. Secrets, recordings, model weights, Obsidian vault data and private runtime state stay on the machine.

## Current milestone — v0.9

```text
text / voice transcript
        │
        ↓
deterministic parser ── unknown ──→ Ollama local (text only)
        │
   known intent
        ↓
   skill registry
        ↓
 permission kernel
   │          │
 deny       allow
              ↓
           handler
              ↓
         SkillResult
```

The rule is simple: **reasoning is not authorization, and permissions are checked before a skill handler runs.**

The core target is **$0/month**.

## Bootstrap

```powershell
.\scripts\bootstrap.ps1
```

Edit `.env` and set your local Obsidian REST API key. Never commit it.

### Deterministic shell

```powershell
.\.venv\Scripts\rupert.exe shell
```

### Unified Rupert console

Once the optional Ollama brain is configured:

```powershell
.\.venv\Scripts\rupert.exe chat
```

Known commands execute deterministically. Natural-language reasoning goes to Ollama and returns text only.

## Skills

Obsidian is now implemented through the common skill registry:

- `obsidian.search`
- `obsidian.read`
- `obsidian.open`
- `obsidian.append`
- `obsidian.overwrite`

Inspect registered skills and risk metadata:

```powershell
.\.venv\Scripts\rupert.exe skills
```

Future Git/Godot/Blender capabilities will plug into this same registry instead of bypassing permissions. See `docs/SKILLS.md`.

## Permission kernel

Current policy distinguishes the source of an action (`keyboard`, `voice`, `brain`, `system`) and its risk (`read`, `write`, `destructive`).

- voice may search/read/open notes and append text;
- voice may **not** overwrite an entire note;
- an LLM may propose actions but may **not** execute them;
- destructive future actions require explicit confirmation.

See `docs/PERMISSIONS.md`.

## Local speech-to-text — whisper.cpp

```powershell
.\scripts\setup-whisper.ps1
```

Optional NVIDIA CUDA build:

```powershell
.\scripts\setup-whisper.ps1 -Cuda
```

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

Default voice: Mexican Spanish (`es_MX-ald-medium`).

## Push-to-talk

```powershell
.\.venv\Scripts\rupert.exe talk
.\.venv\Scripts\rupert.exe talk --speak
```

## Local wake word — openWakeWord

```powershell
.\scripts\setup-wakeword.ps1
```

The final activation phrase is **Rupert**, using a custom ONNX model stored outside Git at `.runtime/models/wakeword/rupert.onnx`.

```powershell
.\.venv\Scripts\rupert.exe wake-doctor
.\.venv\Scripts\rupert.exe wake-monitor
```

See `docs/WAKEWORD.md`. Wake detection is activation, not authorization.

## Optional local brain — Ollama

Rupert does **not** install Ollama or force a model download.

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
.\.venv\Scripts\rupert.exe chat
```

See `docs/BRAIN.md`.

## Cost / privacy policy

Core target: **$0/month**. Paid APIs are never required by the core. Models, recordings, secrets and the Obsidian vault stay outside Git.

Routine commands remain deterministic whenever possible. LLM reasoning is optional and never replaces the registry/permission/executor layer.

See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/WAKEWORD.md`, `docs/BRAIN.md`, `docs/PERMISSIONS.md`, and `docs/SKILLS.md`.
