# Permission kernel

Rupert v0.8 centralizes execution authorization. Parsers, voice, LLMs and future skills do not decide their own permissions.

## Sources

- `keyboard`: explicit deterministic commands typed by the user.
- `voice`: commands produced by speech recognition.
- `brain`: proposals/output from a local or online LLM.
- `system`: reserved for explicitly controlled internal automation.

## Risk levels

- `READ`: observations and non-destructive UI actions.
- `WRITE`: creates or modifies data.
- `DESTRUCTIVE`: deletes, resets, replaces, irreversibly changes or otherwise carries elevated risk.

## Current Obsidian matrix

| Action | Risk | Keyboard | Voice | Brain |
| --- | --- | --- | --- | --- |
| Search notes | read | yes | yes | no |
| Read note | read | yes | yes | no |
| Open note | read | yes | yes | no |
| Append to note | write | yes | yes | no |
| Overwrite note | write | yes | no | no |

A future destructive action requires explicit confirmation. Confirmation never grants an LLM direct execution authority: `brain` remains denied unless an individual future capability is deliberately redesigned and reviewed.

## Design rule

```text
input / proposal
      ↓
   parser
      ↓
 action spec
      ↓
permission policy
   │       │
 deny     allow
           ↓
        handler
```

The handler is never supposed to be reached before the policy decision.

## Why voice differs from keyboard

Speech recognition is probabilistic. Rupert therefore allows useful low-risk/write-limited voice actions such as appending a note, but blocks full note overwrite. More sensitive future voice actions should require an explicit confirmation interaction.

## Why the brain is denied

LLM output is untrusted reasoning, not authorization. A model may propose an action, but Rupert must convert the proposal into a known action, show/validate permissions, and only then execute through the deterministic layer.
