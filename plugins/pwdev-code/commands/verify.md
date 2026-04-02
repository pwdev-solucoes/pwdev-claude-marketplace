---
description: Run the verification phase to validate implementation against the spec
---

# /pwdev-code:verify — Verification Phase

## Agent
Assume the persona of `.claude/agents/agent-verifier.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
Read: `CLAUDE.md` (section 16), `.planning/phases/{active-phase-slug}/spec.md` (sections 2, 5, 7, 8).

## Skills
Read active skills → add specific checklists to the verification.

## Entry Gate
```bash
ls .planning/phases/*/execution/*-summary.md >/dev/null 2>&1 || { echo "❌ No summaries. Run /pwdev-code:execute first."; exit 1; }
```

**Recommended:** Run `/pwdev-code:review` before verify. The review phase (code review + QA audit) catches bugs and coverage gaps that the spec-based verification does not cover. If code-review.md or qa-report.md exist, incorporate their findings into the verification.

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Goal-Backward Setup
Extract truths that must exist:
- spec.md section 2 (objective) → functional truths
- spec.md section 5 (quality) → technical truths
- spec.md section 8 (DoD) → final checklist
- Active skills → additional checklist

### STEP 2 — Automated Validation
```bash
# Lint, Type-check, Unit tests, E2E, Security scan
# (project commands detected from CLAUDE.md section 17)
```

### STEP 3 — Validate ACs (task by task)
Read each execution/*-summary.md. Re-verify each AC with real evidence.

### STEP 4 — Verify Prohibitions
spec.md section 7 + skill anti-patterns → none violated?

### STEP 5 — DoD Check
Each DoD item (section 8) → true with evidence?

### STEP 6 — Verdict
| ✅ APPROVED | ⚠️ CAVEATS | ❌ REJECTED |
Generate `.planning/phases/{active-phase-slug}/verify/verify.md`

### STEP 7 — Fix Plans (if rejected)
Generate `.planning/phases/{active-phase-slug}/verify/fix-{PP}.md` in task Markdown format.

### STEP 8 — Present
✅: "Approved! Feature is ready."
⚠️: "Caveats: [list]. Fix or accept?"
❌: "Fix plans generated: /pwdev-code:execute --plan=fix-01"

## Prohibitions (command-level)
- ❌ NEVER fix code directly (generate fix plans instead)
- ❌ NEVER approve with a critical AC failing
- ❌ NEVER fabricate evidence
