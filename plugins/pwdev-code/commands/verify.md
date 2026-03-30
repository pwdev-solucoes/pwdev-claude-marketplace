---
description: Run the verification phase to validate implementation against the spec
---

# /pwdev-code:verify — Verification Phase

## Agent
Assume the persona of `.claude/agents/agent-verifier.md`.

## References
Read: `CLAUDE.md` (section 16), `.planning/SPEC.md` (sections 2, 5, 7, 8).

## Skills
Read active skills → add specific checklists to the verification.

## Entry Gate
```bash
ls .planning/phases/*-SUMMARY.md >/dev/null 2>&1 || { echo "❌ No SUMMARYs. Run /pwdev-code:execute first."; exit 1; }
```

**Recommended:** Run `/pwdev-code:review` before verify. The review phase (code review + QA audit) catches bugs and coverage gaps that the spec-based verification does not cover. If CODE-REVIEW.md or QA-REPORT.md exist, incorporate their findings into the verification.

## Flow

### STEP 1 — Goal-Backward Setup
Extract truths that must exist:
- SPEC.md section 2 (objective) → functional truths
- SPEC.md section 5 (quality) → technical truths
- SPEC.md section 8 (DoD) → final checklist
- Active skills → additional checklist

### STEP 2 — Automated Validation
```bash
# Lint, Type-check, Unit tests, E2E, Security scan
# (project commands detected from CLAUDE.md section 17)
```

### STEP 3 — Validate ACs (task by task)
Read each SUMMARY.md. Re-verify each AC with real evidence.

### STEP 4 — Verify Prohibitions
SPEC.md section 7 + skill anti-patterns → none violated?

### STEP 5 — DoD Check
Each DoD item (section 8) → true with evidence?

### STEP 6 — Verdict
| ✅ APPROVED | ⚠️ CAVEATS | ❌ REJECTED |
Generate `.planning/phases/{NN}-VERIFY.md`

### STEP 7 — Fix Plans (if rejected)
Generate `.planning/phases/{NN}-FIX-{PP}-PLAN.md` in task Markdown format.

### STEP 8 — Present
✅: "Approved! Feature is ready."
⚠️: "Caveats: [list]. Fix or accept?"
❌: "Fix plans generated: /pwdev-code:execute --plan=[NN]-FIX-01"

## Prohibitions (command-level)
- ❌ NEVER fix code directly (generate fix plans instead)
- ❌ NEVER approve with a critical AC failing
- ❌ NEVER fabricate evidence
