---
description: Execute planned tasks by delegating to the executor subagent
argument-hint: "[--plan=PP | --wave=N | --fix]"
---

# /pwdev-code:execute — Execute Phase

## Role (orchestrator — you do NOT implement; the executor subagent does)

You coordinate the execution loop: pick the next task, spawn a fresh
`pwdev-code:executor` subagent for it with a self-contained prompt, collect
its short status, update `state.md`, and move on. Each task runs in a fresh
context — this is the Fresh Context Model, for real.

## Entry Gate
```bash
[ -d ".planning/phases/" ] || { echo "❌ No phases folder. Run /pwdev-code:design first."; exit 1; }
ls .planning/phases/*/plans/*.md >/dev/null 2>&1 || { echo "❌ No plans found. Run /pwdev-code:plan first."; exit 1; }
```

If `.planning/state.md` contains `review_gate: BLOCKED` and you are NOT
running `--fix` → warn that review found critical findings and they should be
addressed first.

## Flow

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 0.5 — Uncommitted Work Check
```bash
git status --short 2>/dev/null
```
If uncommitted code is detected → warn the human before spawning anything:
- PT-BR: `⚠️ Codigo nao commitado detectado. Deseja commitar antes de continuar? (s/n)`
- EN: `⚠️ Uncommitted code detected. Commit before continuing? (y/n)`

(Older versions generated an `executor-context.md` for stale sessions —
no longer needed: every spawn is fresh and self-contained by design.)

### STEP 1 — Build the Work Queue
```bash
cat .planning/state.md
ls .planning/phases/*/plans/*.md
```
- Normal mode: pending plans, grouped by their `Wave:` header, respecting
  `Depends on:`. Honor `--plan=PP` / `--wave=N` filters.
- **`--fix` mode:** the queue is `.planning/phases/{slug}/verify/fix-*.md`.
  Read `fix_iteration` from `state.md` (default 0). If `fix_iteration >= 2`
  → STOP: present both verify reports' diff to the human and escalate —
  do not loop forever. Otherwise increment it in `state.md`.

### STEP 2 — Execution Loop (per task, wave by wave)

For each task of the current wave, in order:

**2.1 Prepare the spawn prompt** — follow the **executor** template in
`${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md`:
- Full content of the task file (or fix plan)
- spec.md §1 (Persona), §6 (Stop Conditions), §7 (Prohibitions) — pasted in
- Active skills paths (from spec §1)
- "Required Context" paths from the task
- `LANGUAGE: {lang}`

**2.2 Spawn** via the Task tool:
- `subagent_type`: `pwdev-code:executor`
- `model`: resolve per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`

**2.3 Collect the status reply** (≤10 lines). Read ONLY the status — do not
open the summary file unless the status demands it.

**2.4 React:**
- `COMPLETE` / `CAVEATS` → update `state.md` (position + status), next task.
- `STOPPED:<condition>` → present the condition to the human, wait for
  decision before continuing.
- `FAILED` → re-spawn ONCE with the failure note appended to the prompt
  (see "retry" block in spawn-contracts). If it fails again → STOP the loop
  and report to the human with both status notes.

**2.5 Wave checkpoint:** when a wave completes, note it in `state.md` before
starting the next wave.

> Tasks within a wave are independent by contract, but run them sequentially —
> parallel executors would race on git commits. (Future evolution: parallel
> waves with `isolation: worktree` executors, at the cost of merge semantics.)

### STEP 3 — Persistence
The executor writes `execution/{PP}-summary.md` itself. After each task,
update `.planning/state.md` (position + status).
After all tasks in a plan:
→ "Plan {PP} complete. Next plan or /pwdev-code:review?"

### STEP 4 — Transition
```
✅ Phase execution complete.
📁 Summaries in .planning/phases/{active-phase-slug}/execution/
👉 Next: /pwdev-code:review (code review + QA audit)
   Then: /pwdev-code:verify (spec verification)
```
In `--fix` mode:
```
✅ Fix iteration {N}/2 executed.
👉 Next: /pwdev-code:verify (re-verification)
```

## Prohibitions (command-level)
- ❌ NEVER implement code yourself — always spawn the executor
- ❌ NEVER paste a summary file's content into your context — status lines only
- ❌ NEVER execute a task without an approved plan
- ❌ NEVER ignore a `STOPPED:` condition from the executor
- ❌ NEVER exceed 2 fix iterations — escalate to the human
- ❌ NEVER continue to verify with tasks neither completed nor explicitly paused
