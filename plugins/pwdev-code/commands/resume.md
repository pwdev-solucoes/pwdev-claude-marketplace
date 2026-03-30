---
description: Resume a previous session by reading persisted state and recommending next action
---

# /pwdev-code:resume — Resume Session

## Procedure

### STEP 1 — Read persisted state
```bash
cat .planning/STATE.md
cat .planning/ROADMAP.md 2>/dev/null
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
grep -l "Status: in progress" .planning/phases/*.md 2>/dev/null
[ -f ".planning/SPEC.md" ] && echo "✅ SPEC.md present" || echo "❌ SPEC.md missing"
```

### STEP 4 — Present
```markdown
## 🔄 Resuming session

**Last state:** [date]
**Phase:** [current]
**Last completed task:** [ID]
**Next action:** [ID or command]

### Integrity
- SPEC.md: [✅|❌]
- Uncommitted code: [yes/no]
- Tasks in progress: [list]

### Recommendation
👉 [recommended action]

Proceed? (y/n)
```

If uncommitted code → warn and ask: commit or discard.
If inconsistency → suggest /pwdev-code:review then /pwdev-code:verify.
