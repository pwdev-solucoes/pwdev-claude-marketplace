---
description: Run the verification phase to validate implementation against the spec
argument-hint: "[phase-slug]"
---

# /pwdev-code:verify — Verification Phase

## Role (orchestrator — the verifier subagent does the work, adversarially)

The verifier's goal is to REFUTE that the phase is complete, not confirm it.
It re-runs evidence itself and distrusts execution summaries.

## Entry Gate
```bash
ls .planning/phases/*/execution/*-summary.md >/dev/null 2>&1 || { echo "❌ No summaries. Run /pwdev-code:execute first."; exit 1; }
```

If `.planning/state.md` contains `review_gate: BLOCKED` → abort:
```
❌ Review gate is BLOCKED (critical findings open).
Fix them via /pwdev-code:execute + /pwdev-code:review, or explicitly override.
```

**Recommended:** run `/pwdev-code:review` before verify — its reports feed
the verifier (unresolved critical/high findings count as DoD failures).

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Gather Spawn Inputs
Read (for the prompt only): `CLAUDE.md` (section 11 — Verification,
Goal-Backward), spec.md sections 2, 3, 5, 6, 7, 8 (full text), paths of
`execution/*-summary.md`, paths of `review/code-review.md` and
`review/qa-report.md` (if they exist), active skills list. Project
verification commands come from CLAUDE.md sections 12 and 14.

### STEP 2 — Spawn the Verifier (real subagent)
Via the Task tool:
- `subagent_type`: `pwdev-code:verifier`
- `model`: resolve per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`
- prompt: follow the **verifier** template in
  `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md` — full spec sections,
  summary paths (to be distrusted), review report paths, `LANGUAGE: {lang}`,
  and the goal: refute completion.

It writes `verify/verify.md` (+ `verify/fix-{NN}.md` if rejected) and replies
with ≤10 lines.

### STEP 3 — React to the Verdict
Read ONLY the status reply. Update `.planning/state.md` with the verdict.
Log it: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event verify VERIFY gate_passed verify.md '{"verdict":"..."}'`
(use `gate_rejected` on ❌).

### STEP 4 — Present

- ✅ APPROVED: "Approved! Feature is ready." → phase complete.
- ⚠️ WITH CAVEATS: "Caveats: [list]. Fix or accept?"
- ❌ REJECTED: read `fix_iteration` from `state.md` (default 0):
  ```
  ❌ Rejected. Fix plans generated in verify/.
  Fix iteration {N}/2 — next: /pwdev-code:execute --fix
  ```
  If `fix_iteration >= 2` → do NOT suggest another loop; present the diff
  between the two verify reports and escalate to the human.

## Prohibitions (command-level)
- ❌ NEVER verify the code yourself — spawn the verifier
- ❌ NEVER run verify while review_gate is BLOCKED (without explicit override)
- ❌ NEVER fix code directly (fix plans go to the executor)
- ❌ NEVER approve with a critical AC failing
- ❌ NEVER fabricate evidence
- ❌ NEVER loop past 2 fix iterations — escalate
