---
description: Analyze the phase diff and apply human-approved high-confidence simplifications via the simplifier subagent
argument-hint: "[files | --diff HEAD~N] (default: diff of the current phase's execution commits)"
---

# /pwdev-code:simplify — Code Simplification Pass

## Role (orchestrator — the simplifier subagent does the work)

Optional quality step between EXECUTE and REVIEW: reuse, dead-code removal,
complexity reduction, efficiency. It is NOT a bug hunt (that is /review's job)
and it never changes behavior. Two passes: ANALYZE (propose) → human approves
by ID → APPLY (implement + refactor commit).

## Entry Gate
```bash
ls .planning/phases/*/execution/*-summary.md >/dev/null 2>&1 || [ -n "$ARGUMENTS" ] || { echo "❌ No execution summaries and no explicit scope. Run /pwdev-code:execute first or pass files/--diff."; exit 1; }
```

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Determine Scope
- `$ARGUMENTS` given → use it (file list or `--diff HEAD~N`).
- Default → the phase's execution commits: read `state.md` for the active
  phase, resolve the commit range since the phase's first execute commit
  (`git log --oneline` + summaries' commit hashes).

### STEP 2 — Gather Spawn Inputs
For the prompts only (do not analyze yourself): spec.md §5 (Quality) and §7
(Prohibitions) of the active phase; RELEVANT MEMORY block per
`${CLAUDE_PLUGIN_ROOT}/references/memory.md` (conventions first);
project verification commands (CLAUDE.md §12/§14).

### STEP 3 — Spawn ANALYZE
Via the Task tool:
- `subagent_type`: `pwdev-code:simplifier`
- `model`: resolve per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`
- prompt: **ANALYZE** template in
  `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md`.

Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event simplify SIMPLIFY simplify_proposed simplify-proposals.md '{"count":N}'`

### STEP 4 — Human Approval by ID
Present the proposals table from the status reply + report path.
Ask: approve **all / none / list of IDs** (e.g. "S1, S3").
- `STATUS: NOTHING_TO_PROPOSE` or 0 approved → end cleanly:
  ```
  ✨ Nothing to simplify (or nothing approved). Code stays as is.
  👉 Next: /pwdev-code:review
  ```

### STEP 5 — Spawn APPLY
Only with >=1 approved ID. Same subagent, **APPLY** template with the full
text of the approved proposals + verification commands.

### STEP 6 — Gate + state.md
- Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event simplify SIMPLIFY simplify_applied simplify-proposals.md '{"applied":N,"skipped":M}'`
- Update `.planning/state.md`:
  ```markdown
  ## Last Simplify
  - Date: [timestamp]
  - Applied: [N] | Skipped: [M]
  - Commit: [hash]
  - review_gate: STALE   # only if N > 0 — review must re-run on the refactor diff
  ```

### Transition (when changes were applied)
```
✅ Simplify: {N} applied, {M} skipped — commit {hash}.
⚠️ Changes applied → review must re-run on the refactor diff.
👉 Next: /pwdev-code:review --diff {refactor-range}
```

## Prohibitions (command-level)
- ❌ NEVER edit code yourself — always spawn the simplifier
- ❌ NEVER apply without explicit human approval by ID
- ❌ NEVER spawn APPLY with zero approved proposals
- ❌ NEVER report bugs here (forward the simplifier's notes to /review)
- ❌ NEVER skip the re-review after changes were applied
