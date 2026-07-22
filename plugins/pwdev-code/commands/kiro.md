---
description: Delegate an agentic implementation task to the Kiro CLI (headless mode), then critically review the resulting diff
argument-hint: "[--read-only] <task description>"
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep
---

# /pwdev-code:kiro — Delegate to Kiro CLI

## Role
Orchestrator: sends the task to the external Kiro CLI (headless mode) via
the standardized delegation script, then performs a MANDATORY critical
review. Best for: agentic/spec-driven implementation and AWS-stack tasks.
Protocol details: `${CLAUDE_PLUGIN_ROOT}/references/delegation.md`

## CLI notes
- Binary: `kiro-cli` — invoked as `kiro-cli chat --no-interactive "<prompt>"`.
- In **write** mode the script adds `--trust-all-tools` (required for Kiro to
  edit files headlessly). In **read** mode it is omitted: read-only tools are
  trusted by default and mutations get rejected — a natural read-only guard.
- Headless auth: set `KIRO_API_KEY` to skip the browser login flow
  (docs: https://kiro.dev/docs/cli/headless/).

## Input
$ARGUMENTS: the task description. `--read-only` → MODE=read (default: write).

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Preflight
- Parse $ARGUMENTS: strip `--read-only` (→ MODE=read); the remainder is the
  task. Empty task → show usage and STOP.
- `git status --porcelain` — if the tree is dirty in write mode, warn the
  user that delegation results will be hard to attribute; offer to continue
  or abort.
- Record baseline: `git rev-parse HEAD` and `git status --short`.

### STEP 2 — Human Confirmation (same rule as review.md STEP 3.5)
Show the EXACT command that will run:
```
"${CLAUDE_PLUGIN_ROOT}/scripts/run-agent.sh" kiro <write|read> "<task>"
```
If this is the FIRST external CLI run in this session → require explicit
confirmation before executing. Never proceed silently.

### STEP 3 — Run
Execute the command via Bash with a tool timeout ≥ the script timeout + 60s
(default 600s; agentic runs are slow — consider
`external_models.kiro.timeout_s: 900`).
- exit 127 → Kiro CLI not installed (official installer at
  https://kiro.dev, then authenticate once or set `KIRO_API_KEY`); STOP.
- exit 124 → report the timeout; suggest raising
  `external_models.kiro.timeout_s`.
- exit 4 → another write delegation is running; wait for it.
- Output copy (when `.planning/` exists): `.planning/delegation/<ts>-kiro.md`

### STEP 4 — MANDATORY Review Protocol (never skip, even on exit 0)
1. `git status --short` — list every touched file.
2. `git diff --stat`, then read the FULL `git diff` (per-file if large).
3. Scope check: flag any file outside the task scope; flag ANY touch of
   `.env*`, secrets, lockfiles not implied by the task, or CI configs.
4. Run the project's relevant test suite yourself — do not trust the
   agent's claim.
5. Critical evaluation with YOUR OWN judgment — do not rubber-stamp the
   agent's summary.
6. NEVER commit or push. If the result is bad, PROPOSE (do not execute
   without confirmation) `git checkout -- <files>` / `git clean -n`.

### STEP 5 — Report ({{LANG}})
```
📋 Delegation Complete — kiro (mode: write|read)

  Files changed: [N] ([list])
  Tests: [pass/fail/not run — what you ran]
  Out-of-scope changes: [none | list]
  Verdict: [APPROVED FOR COMMIT | NEEDS ADJUSTMENTS | RECOMMEND REVERT]
  Output copy: .planning/delegation/<ts>-kiro.md
```

## Prohibitions
- ❌ NEVER commit or push delegated changes yourself
- ❌ NEVER run two write-mode delegations simultaneously
- ❌ NEVER skip STEP 4, even when the agent reports success
- ❌ NEVER revert without human confirmation
- ❌ NEVER run the script without showing the exact command (and confirming
  on the first external run of the session)
