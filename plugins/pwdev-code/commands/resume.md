---
description: Resume a previous session by reading persisted state and recommending next action
---

# /pwdev-code:resume — Resume Session

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Read persisted state
```bash
cat .planning/state.md
cat .planning/product/roadmap/roadmap.md 2>/dev/null
ls -la .planning/phases/ 2>/dev/null
```

### STEP 2 — Identify resumption point
- Last completed phase
- Last completed task
- Next pending action
- Registered blockers

### STEP 3 — Verify integrity
```bash
git status --short
grep -rl "Status: in progress" .planning/phases/*/execution/*.md 2>/dev/null
ls .planning/phases/*/spec.md 2>/dev/null && echo "✅ spec.md present" || echo "❌ spec.md missing"
```

### STEP 4 — Present
```markdown
## 🔄 Resuming session

**Last state:** [date]
**Phase:** [current]
**Last completed task:** [ID]
**Next action:** [ID or command]

### Integrity
- spec.md: [✅|❌]
- Uncommitted code: [yes/no]
- Tasks in progress: [list]

### Recommendation
👉 [recommended action]

Proceed? (y/n)
```

If uncommitted code → warn and ask: commit or discard.
If inconsistency → suggest /pwdev-code:review then /pwdev-code:verify.
