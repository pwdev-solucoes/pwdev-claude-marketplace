---
description: Pick the best external coding CLI for the task (codex, opencode, kimi, gemini, or kiro) and delegate with the standard safety protocol
argument-hint: "<task description>"
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep
---

# /pwdev-code:delegate — Smart External Delegation

## Role
Orchestrator: analyzes the task, selects ONE external agent by the selection
matrix, announces the choice, and then follows the standard delegation flow
(confirmation → `run-agent.sh` → mandatory review).
Protocol details: `${CLAUDE_PLUGIN_ROOT}/references/delegation.md`

## Input
$ARGUMENTS: the task description. Empty → show usage and STOP.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Classify the Task & Select the Agent

Selection matrix (canonical copy: `references/delegation.md` §6):

| Task nature | Agent | Default mode |
|-------------|-------|:------------:|
| Objective implementation, bugfix, well-scoped tests | codex | write |
| A specific model/provider was requested, or provider flexibility matters | opencode | write |
| Large repo, extensive refactor, many files | kimi | write |
| Agentic/spec-driven implementation, AWS-stack tasks | kiro | write |
| Analysis, architecture, documentation, review, second opinion | gemini | read |

Tie-breakers: analysis-only → always gemini (read). Implementation with a
model explicitly named by the user → opencode. Otherwise prefer codex for
small scope, kimi for wide scope.

### STEP 2 — Announce the Choice ({{LANG}})
Before executing, state in 1–2 sentences WHICH agent was selected and WHY
(reference the matrix row). Check availability with
`command -v <binary>` (`kiro` → `kiro-cli`):
- Chosen CLI missing → announce and fall back to the next reasonable
  candidate; if none is installed, say so and offer to do the task yourself
  (Claude-only).

### STEP 3 — Delegate (standard flow)
Follow the selected agent's command flow exactly
(`commands/codex.md` / `opencode.md` / `kimi.md` / `gemini.md` / `kiro.md`):
1. Preflight (dirty-tree warning in write mode; record baseline).
2. Human confirmation showing the EXACT command:
   `"${CLAUDE_PLUGIN_ROOT}/scripts/run-agent.sh" <agent> <mode> "<task>"`
   (mandatory on the first external run of the session).
3. Run via Bash (tool timeout ≥ script timeout + 60s); handle exit codes
   127 / 124 / 4 / 3 as in the agent's command.
4. MANDATORY review protocol (`references/delegation.md` §7): full diff,
   scope check, run tests yourself, own critical verdict, never commit/push.
5. Report ({{LANG}}) with files changed, tests, out-of-scope findings,
   verdict, and the output copy path.

### Rules of engagement
- ONE primary agent per task. A second agent may be used ONLY for a
  read-only review of the first agent's diff (e.g. gemini read).
- NEVER two write-mode delegations at once (the script's lock enforces it —
  respect it, don't work around it).
- The final conclusion is ALWAYS yours, not the external agent's.

## Prohibitions
- ❌ NEVER execute before announcing the selected agent and the reason
- ❌ NEVER delegate to more than one write-mode agent for the same task
- ❌ NEVER commit or push delegated changes yourself
- ❌ NEVER skip the mandatory review protocol
- ❌ NEVER run the script without showing the exact command (and confirming
  on the first external run of the session)
