# Skills

Rupert v0.9 introduces a central skill registry. A skill is an executable capability with:

- a stable name;
- a human-readable description;
- an `ActionSpec` containing risk/permission metadata;
- a handler that performs the action only after the registry authorizes it.

## Execution path

```text
intent
  ↓
skill name
  ↓
SkillRegistry
  ↓
PermissionPolicy
  │
  ├─ deny → no handler call
  │
  └─ allow
       ↓
     handler
       ↓
   SkillResult
```

## Current skills

- `obsidian.search`
- `obsidian.read`
- `obsidian.open`
- `obsidian.append`
- `obsidian.overwrite`

Inspect the live registry:

```powershell
.\.venv\Scripts\rupert.exe skills
```

## Adding a future skill

A future Git/Godot/Blender capability should be registered with an explicit `ActionSpec`. It must not bypass `SkillRegistry.invoke()` merely because its handler is convenient to call directly.

Example design:

```python
spec = ActionSpec(
    "git.status",
    RiskLevel.READ,
    voice_allowed=True,
)
```

A destructive skill should declare `RiskLevel.DESTRUCTIVE`; the policy will require explicit confirmation before its handler can run.

## LLM boundary

The local brain does not receive a registry handle and is not allowed to invoke skills. Future natural-language action proposals must be converted to a known skill request by trusted Rupert code, then evaluated by the permission kernel.
