---
description: Delegate a task to the OpenCode CLI (flexible provider/model routing), then critically review the resulting diff
argument-hint: "[--read-only] <task description>"
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep
---

# /pwdev-code:opencode — Delegate to OpenCode

## Role
Orchestrator: sends the task to the external OpenCode CLI via the
standardized delegation script, then performs a MANDATORY critical review.
Best for: tasks that need a specific model/provider or provider flexibility.
Protocol details: `${CLAUDE_PLUGIN_ROOT}/references/delegation.md`

## Model selection
Precedence: `.planning/config.json` → `external_models.opencode.model`
(passed as `--model`) > env `OPENCODE_MODEL` (respected natively by the CLI)
> OpenCode's configured default. List available models: `opencode models`.

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
"${CLAUDE_PLUGIN_ROOT}/scripts/run-agent.sh" opencode <write|read> "<task>"
```
If this is the FIRST external CLI run in this session → require explicit
confirmation before executing. Never proceed silently.

### STEP 3 — Run
Execute the command via Bash with a tool timeout ≥ the script timeout + 60s
(default 600s; override via `external_models.opencode.timeout_s`).
- exit 127 → OpenCode not installed
  (`curl -fsSL https://opencode.ai/install | bash` or `npm i -g opencode-ai`,
  then run `opencode` once to configure the provider); STOP.
- exit 124 → report the timeout; suggest raising
  `external_models.opencode.timeout_s`.
- exit 4 → another write delegation is running; wait for it.
- Output copy (when `.planning/` exists): `.planning/delegation/<ts>-opencode.md`

### STEP 4 — MANDATORY Review Protocol (never skip, even on exit 0)
1. `git status --short` — list every touched file.
2. `git diff --stat`, then read the FULL `git diff` (per-file if large).
3. Scope check: flag any file outside the task scope; flag ANY touch of
   `.env*`, secrets, lockfiles not implied by the task, or CI configs.
4. Run the project's relevant test suite yourself.
5. Critical evaluation with YOUR OWN judgment — do not rubber-stamp the
   agent's summary.
6. NEVER commit or push. If the result is bad, PROPOSE (do not execute
   without confirmation) `git checkout -- <files>` / `git clean -n`.

### STEP 5 — Report ({{LANG}})
```
📋 Delegation Complete — opencode (mode: write|read, model: [resolved or default])

  Files changed: [N] ([list])
  Tests: [pass/fail/not run — what you ran]
  Out-of-scope changes: [none | list]
  Verdict: [APPROVED FOR COMMIT | NEEDS ADJUSTMENTS | RECOMMEND REVERT]
  Output copy: .planning/delegation/<ts>-opencode.md
```

## Prohibitions
- ❌ NEVER commit or push delegated changes yourself
- ❌ NEVER run two write-mode delegations simultaneously
- ❌ NEVER skip STEP 4, even when the agent reports success
- ❌ NEVER revert without human confirmation
- ❌ NEVER run the script without showing the exact command (and confirming
  on the first external run of the session)
