# Architecture

Rupert is **cloud-first, phone-first and low-cost**. The public GitHub repository contains code and reproducible infrastructure. Private runtime state lives in authenticated cloud services.

## Primary v0.10 topology

```text
Phone / PWA (GitHub Pages)
        │
        │ Supabase Auth JWT
        ▼
Supabase Edge Functions
   │               │
   │               └── Cloudflare Workers AI
   │                   ├── text reasoning
   │                   └── Whisper ASR
   │
   ├── Postgres + Row Level Security
   ├── private Storage
   └── audit trail
```

The laptop is not part of the critical path.

## Layers

1. **Client** — installable PWA in `web/`, optimized for phone use.
2. **Identity** — Supabase Auth.
3. **Private memory** — Supabase Postgres protected by RLS.
4. **Cloud router** — authenticated Supabase Edge Function.
5. **Voice** — mobile MediaRecorder + authenticated ASR Edge Function.
6. **Reasoning** — optional Cloudflare Workers AI adapter.
7. **Audit** — `rupert_audit` records permitted/failed cloud operations.
8. **Optional workers** — future laptop/desktop nodes for Blender, Godot, files or local GPU jobs.

## Routing rule

```text
request
  │
  ├── known deterministic command
  │       ↓
  │   authenticated RLS-scoped handler
  │       ↓
  │   memory result
  │
  └── unknown natural language
          ↓
      reasoning backend
          ↓
      text response only
```

Unknown natural language never receives an execution channel.

## v0.10 deterministic cloud skills

```text
buscar <texto>                  → memory.search   READ
leer <título>                   → memory.read     READ
añadir <título> :: <contenido>  → memory.append   WRITE
```

There is deliberately no cloud delete/overwrite/system command in v0.10.

## Trust boundaries

### Public GitHub

Allowed:

- source code;
- PWA static assets;
- tests;
- workflows;
- migrations;
- templates and documentation.

Forbidden:

- Supabase secret/service-role keys;
- Cloudflare API tokens;
- user JWTs/sessions;
- private memory;
- audio recordings;
- personal files.

### PWA

The browser may hold only:

- Supabase project URL;
- publishable/anon client key;
- authenticated user session managed by Supabase JS.

It must never receive provider secrets.

### Edge Functions

The functions validate the caller's JWT and create a user-scoped Supabase client. Normal operations do not use service-role credentials, so RLS stays active inside the function.

Cloudflare credentials are backend-only secrets.

## Data model

- `rupert_memory` — durable notes/context.
- `rupert_messages` — chat history per user/session.
- `rupert_settings` — private per-user settings.
- `rupert_audit` — action/security audit.
- `rupert-private` — non-public Storage bucket with user-folder policies.

## Voice path

```text
phone microphone
      ↓
MediaRecorder
      ↓
authenticated multipart POST
      ↓
rupert-transcribe Edge Function
      ↓
Cloudflare Whisper
      ↓
transcript text
      ↓
normal Rupert router
```

Audio is transient by default. If voice-history storage is added later it must use the private user-scoped bucket explicitly.

## Background wake word

A PWA cannot be trusted to keep its microphone active indefinitely while suspended/backgrounded by the mobile OS. Therefore v0.10 uses push-to-talk.

A future native Android/iOS companion may do only wake-word detection and hand off the command to Rupert Cloud. The cloud architecture does not depend on such a companion.

## Optional desktop worker

Existing local modules remain useful as a future worker process:

```text
Rupert Cloud
    │ outbound authenticated job
    ▼
Desktop worker (optional)
    ├── Godot
    ├── Blender
    ├── local files
    └── local GPU
```

The worker should make an outbound connection and expose no unauthenticated inbound port.

## Cost routing

1. deterministic commands first;
2. reasoning only when needed;
3. transcription only while the user actively records;
4. public GitHub infrastructure for code/UI/CI;
5. private cloud services only for state that cannot safely be public.

## Legacy local stack

The earlier local-first components are preserved as optional adapters, not removed:

- Obsidian Local REST/MCP;
- whisper.cpp;
- Piper;
- openWakeWord;
- Ollama;
- Python permission kernel;
- skill registry.

They can become a desktop worker without forcing normal phone usage to wait for the laptop.
