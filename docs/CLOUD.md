# Rupert Cloud Core v0.10

Rupert is now **cloud-first and phone-first**. The public GitHub repository contains code, tests, workflows and static web assets only. Private user state belongs in Supabase and provider secrets belong in backend secret stores.

## Topology

```text
Android / iPhone PWA (GitHub Pages)
        |
        | Supabase Auth JWT
        v
Supabase Edge Functions
   |            |
   |            +--> Cloudflare Workers AI (optional reasoning + ASR)
   |
   +--> Postgres + RLS
   +--> private Storage bucket
```

The laptop is optional. It can later be registered as a worker for Blender/Godot/GPU tasks, but Rupert's normal chat, memory and voice path does not require it to be online.

## Security model

1. `Klymapo/rupert` may stay public.
2. Never commit `.env`, Supabase secret keys, Cloudflare API tokens, auth sessions, recordings or personal memory.
3. The web client only needs a Supabase project URL and **publishable/anon client key**. These are client credentials and are protected by Auth + Row Level Security.
4. Edge Functions validate the user JWT with `auth.getUser()` and use the caller-scoped Supabase client.
5. Normal functions do not use a service-role key.
6. Cloudflare credentials live only as Supabase function secrets.
7. Unknown natural language goes to the reasoning backend as text only. It has no skill/execution channel.
8. Destructive actions are intentionally absent from the cloud MVP.

## Database

Migration: `supabase/migrations/20261005_001_rupert_cloud_core.sql`

Tables:

- `rupert_memory`: durable personal memory/notes.
- `rupert_messages`: conversation history by session.
- `rupert_settings`: private per-user configuration.
- `rupert_audit`: action/security audit trail.

Every table has RLS. A private Storage bucket, `rupert-private`, is scoped by the first path segment equal to the authenticated user's UUID.

## Deterministic commands

The cloud Edge Function preserves Rupert's low-cost rule. It recognizes these without an LLM:

```text
buscar <texto>
leer <título>
añadir <título> :: <contenido>
```

Everything else is treated as reasoning-only text and may be sent to Cloudflare Workers AI if configured.

Notably, v0.10 has no cloud command for overwrite/delete/send/purchase/system execution.

## PWA

Static app: `web/`

The user can configure it from the phone by entering:

- Supabase Project URL
- Supabase publishable/anon key

These values are stored only in that browser's `localStorage`. Do not enter service-role keys or Cloudflare tokens in the PWA.

Authentication starts with Supabase email OTP / magic link. Passkeys/WebAuthn can be enabled as a later hardening step once the Supabase project is connected and tested.

The microphone button records only while the page is in the foreground. The recording is submitted directly to the authenticated transcription Edge Function and is not stored by default.

## Cloudflare Workers AI

Expected Supabase Edge Function secrets:

```text
CF_ACCOUNT_ID
CF_API_TOKEN
CF_TEXT_MODEL=@cf/meta/llama-3.1-8b-instruct
CF_ASR_MODEL=@cf/openai/whisper-large-v3-turbo
```

The public PWA never receives these values.

Reasoning endpoint used by `rupert`:

```text
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}
```

The transcription function sends base64 audio to the same Workers AI run API.

## GitHub Pages

`.github/workflows/pages.yml` packages the `web/` folder and deploys it using GitHub Pages when `main` changes.

GitHub Pages may need to be enabled once in repository Settings → Pages → Source: GitHub Actions. This is a repository setting, not a laptop requirement.

## Supabase deployment

Once the Supabase plugin/account is connected, the intended deployment order is:

1. create or select a Supabase project;
2. apply the migration;
3. deploy `rupert` and `rupert-transcribe` functions;
4. configure Auth redirect URL for the GitHub Pages address;
5. add Cloudflare secrets to Edge Functions;
6. paste the Supabase URL + publishable key into the Rupert PWA on the phone;
7. sign in and test deterministic memory commands before enabling AI.

## What remains local-only

Nothing in the normal v0.10 path requires a laptop. Future optional workers may provide capabilities such as:

- Blender rendering;
- Godot headless tests/screenshots;
- large local GPU models;
- access to files that exist only on a specific computer.

Those workers should connect outward to Rupert Cloud and remain off by default.
