# Local brain

Rupert can use a local Ollama server as an **optional reasoning backend**. This layer is for conversation, explanation, classification, brainstorming and planning. It is not an execution authority.

## Security model

The local brain is deliberately separated from Rupert's deterministic executor.

```text
user text
   │
   ├─ known deterministic command ──→ executor ──→ allowed local action
   │
   └─ reasoning request ─────────────→ Ollama ────→ text reply only
```

The model cannot directly call Obsidian, Git, Godot, Blender, PowerShell or other skills. Future integrations may allow the brain to *propose* a structured action, but the permission/executor layer must validate it before execution.

## Endpoint

Default:

```text
http://127.0.0.1:11434
```

Rupert rejects non-loopback Ollama endpoints by default. Remote endpoints require an explicit opt-in:

```dotenv
RUPERT_ALLOW_REMOTE_BRAIN=1
```

Do not enable this merely to make an error disappear. The default exists to keep private context and inference local.

## Configuration

```dotenv
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=
OLLAMA_TIMEOUT=120
RUPERT_ALLOW_REMOTE_BRAIN=0
```

No model is pinned yet. Model selection should be made after measuring the actual laptop VRAM/RAM and desired latency. This prevents Rupert from silently downloading several gigabytes that may be a bad fit for the machine.

## Setup

Rupert does not silently install Ollama. Once Ollama is installed explicitly:

```powershell
.\scripts\setup-ollama.ps1
```

After choosing a model:

```powershell
.\scripts\setup-ollama.ps1 -Model <model-name>
```

Then set the same name in `.env`:

```dotenv
OLLAMA_MODEL=<model-name>
```

Check connectivity:

```powershell
.\.venv\Scripts\rupert.exe brain-doctor
```

Ask the local model something without executing any action:

```powershell
.\.venv\Scripts\rupert.exe ask "Resume esta idea en tres puntos"
```

## API design

The Ollama adapter uses Python's standard library and calls:

- `GET /api/tags` for diagnostics/model discovery;
- `POST /api/chat` with `stream: false` for chat.

No additional Python HTTP SDK is required.

## Future routing

A later milestone can route commands the deterministic parser does not understand to the brain for interpretation. Even then, the brain should return a proposal, not execute anything itself.
