---
description: Delegate a read-only analysis or review task to the Gemini CLI (use --write to allow file changes)
argument-hint: "[--write] <analysis request>"
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep
---

# /pwdev-code:gemini — Delegate to Gemini CLI (read-only by default)

## Role
Orchestrator: sends an analysis/review request to the external Gemini CLI
via the standardized delegation script, then verifies and critically
consolidates the findings. Best for: broad-context analysis, architecture
review, documentation, second opinions.
**Default mode is READ-ONLY** — pass `--write` to allow implementation.
Protocol details: `${CLAUDE_PLUGIN_ROOT}/references/delegation.md`

## Model selection
Precedence: `.planning/config.json` → `external_models.gemini.model`
(passed as `--model`) > env `GEMINI_MODEL` (respected natively) > CLI default.

## Input
$ARGUMENTS: the analysis request. `--write` → MODE=write (default: read).

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Preflight
- Parse $ARGUMENTS: strip `--write` (→ MODE=write); the remainder is the
  request. Empty request → show usage and STOP.
- Record baseline: `git rev-parse HEAD` and `git status --porcelain`.

### STEP 2 — Human Confirmation (same rule as review.md STEP 3.5)
Show the EXACT command that will run:
```
"${CLAUDE_PLUGIN_ROOT}/scripts/run-agent.sh" gemini <read|write> "<request>"
```
If this is the FIRST external CLI run in this session → require explicit
confirmation before executing. Never proceed silently.

### STEP 3 — Run
Execute the command via Bash with a tool timeout ≥ the script timeout + 60s
(default 600s; override via `external_models.gemini.timeout_s`).
- exit 127 → Gemini CLI not installed (`npm i -g @google/gemini-cli`, then
  run `gemini` once to authenticate); STOP.
- exit 124 → report the timeout; suggest raising
  `external_models.gemini.timeout_s`.
- exit 3 → **READ-ONLY VIOLATION**: the agent modified files in read mode.
  Alert prominently, show `git status --short`, and propose a revert.
- exit 4 (write mode) → another write delegation is running; wait for it.
- Output copy (when `.planning/` exists): `.planning/delegation/<ts>-gemini.md`

### STEP 4 — MANDATORY Verification Protocol (never skip)

**Read mode:**
1. Verify `git status --porcelain` matches the baseline — the working tree
   must be untouched (the script exits 3 on violation; double-check anyway).
2. Compare Gemini's analysis against the actual code: spot-check the claims
   in the repository — do NOT accept conclusions without evidence.
3. Separate confirmed findings from likely false positives.

**Write mode:** apply the full diff-review protocol
(`references/delegation.md` §7): `git status --short`, full `git diff`,
scope check, run tests yourself, own critical evaluation.

In both modes: NEVER commit or push.

### STEP 5 — Report ({{LANG}})
```
📋 Delegation Complete — gemini (mode: read|write)

  Working tree: [untouched ✅ | VIOLATION ❌ | N files changed (write mode)]
  Confirmed findings: [N] ([summary])
  Possible false positives: [N] ([summary])
  Verdict: [ANALYSIS CONSOLIDATED | APPROVED FOR COMMIT | NEEDS ADJUSTMENTS | RECOMMEND REVERT]
  Output copy: .planning/delegation/<ts>-gemini.md
```

## Prohibitions
- ❌ NEVER commit or push anything
- ❌ NEVER accept external conclusions without checking them against the code
- ❌ NEVER skip the baseline verification in read mode
- ❌ NEVER run two write-mode delegations simultaneously
- ❌ NEVER run the script without showing the exact command (and confirming
  on the first external run of the session)
