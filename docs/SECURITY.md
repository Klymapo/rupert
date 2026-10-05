# Security model

Rupert is designed so the repository can be backed up without backing up secrets or private runtime data.

## Never commit

- `.env`
- Obsidian API keys
- model weights
- recordings
- logs that may contain note contents
- vault contents, unless intentionally stored in a separate private repository

## Obsidian

Prefer binding the Local REST API HTTP endpoint to `127.0.0.1` only. Do not expose port 27123 to the LAN or Internet.

## GitHub

A private repository is recommended while Rupert contains personal automation code. Secrets belong in local environment variables or `.env`, never Git history.
