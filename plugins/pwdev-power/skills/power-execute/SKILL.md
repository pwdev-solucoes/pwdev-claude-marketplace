---
name: power-execute
description: Use when an approved plan needs executing task by task in this session, with a fresh implementer per task and review between tasks
---

# Execute a Plan, Task by Task

Read [collaboration](../../references/collaboration.md), [runtime](../../references/runtime.md),
[model-profiles](../../references/model-profiles.md), and [safety](../../references/safety.md)
before acting.

You are the controller. You dispatch, you adjudicate, you record. **You do not implement and
you do not fix.** The moment you edit code yourself, every discipline below stops applying to
that edit.

## Setup

1. Ensure isolation with `pwdev-power:power-worktree`.
2. `../../scripts/power-workspace.sh <slug>` prints the working directory and creates `ledger.md`.
3. **Read the ledger.** Its first line names its plan. Tasks marked `Task NN: complete` are
   done — do not dispatch them again. A ledger belonging to a different plan is not yours;
   ignore it.

   This check exists because the most expensive observed failure is a controller that lost its
   place and re-dispatched a whole sequence of finished tasks.

4. **Pre-flight scan**, before Task 01. Produce a table with one row per pair of tasks that
   share a file or an interface — what one produces against what the other consumes — and one
   row per task confirming its own text agrees with itself. Record every ruling you make in the
   ledger. "The scan is clean" without those rows is not a scan you ran.

## Model selection

- **Codex** inherits host or session model and reasoning-effort settings by default. Override only
  for an explicit user instruction, repository governance rule, configuration, or approved
  profile, after confirming a supported model-and-effort combination on that host.
- **Claude Code** keeps explicit model routing on every dispatch. Apply the configured profile and
  the task's declared `Complexity` per [model-profiles](../../references/model-profiles.md), using
  a model the runtime supports.
- **Hermes Agent** follows [hermes-tools](../../references/hermes-tools.md) and the runtime mapping.
  Use its documented Kanban route or run inline when per-dispatch selection is unavailable; never
  invent model, provider, or effort parameters.

## The loop, per task

### 1. Dispatch

Record `BASE=$(git rev-parse HEAD)` first. Generate the brief with
`../../scripts/task-brief.sh <plan> <N>`.

The dispatch prompt has exactly six parts:

1. One line placing the task in the project.
2. The brief path — "read this first; these are your requirements, with exact values".
3. The context paths, when they exist: `.planning/power/context/project.md` for conventions and
   `stack.md` for versions. **Paths, not contents** — pasting a map into every brief costs the
   same context the map was written to save.
4. Interfaces and decisions from earlier tasks that this one consumes.
5. Your resolution of any ambiguity you found in the scan.
6. The report path to write.

Exact values live in the brief, not in the prompt. **Never** make the child read the whole
plan. **Never** paste accumulated conversation history — a dispatch that is 99% history is a
dispatch that buried its own instructions.

One implementer at a time. Never parallelize them: they share a working tree.

### 2. Read the status

| Status | Do |
|---|---|
| `DONE` | Build the review package and review. |
| `DONE_WITH_CONCERNS` | Read the report first, then review. |
| `NEEDS_CONTEXT` | Supply exactly what was missing and re-dispatch. |
| `BLOCKED` | Choose one: more context, a more capable model, split the task, or a ruling that the plan is defective. |

Never re-dispatch the same model against the same failure with nothing changed.

### 3. Review

`../../scripts/review-package.sh <workspace> <BASE> <HEAD>` builds the diff file. Dispatch
`task-reviewer` with three paths — brief, report, package — plus the plan's `Global
Constraints` block **quoted verbatim**. Demand both verdicts: spec compliance and task quality.

Never tell the reviewer what not to flag, and never cap severity in advance. Both are
pre-judging, and both produce a review that agrees with you by construction.

### 4. Fix loop

Enter it on a spec `FAIL`, any Critical or Important finding, or a ⚠️ you confirmed is real.

Two things leave immediately:

- **Minor** findings go to the ledger as `Task NN: minor (deferred): …` and never enter the
  loop.
- A finding that the **plan itself mandated** requires a **ruling** from you, recorded in the
  ledger, before anything is changed.

Then, at most **five rounds**. Each round is one fix dispatch plus one re-review scoped to the
findings:

- **Rounds 1–3**: resume the original implementer, which still has the context.
- **Rounds 4–5**: a fresh implementer, framed as "a previous implementer tried N times; here is
  where it stands". On Claude Code, escalate one tier as the profile requires. On Codex, escalate
  only under an explicit override. On Hermes Agent, use only the route documented by its mapping.
  In every case, the target choice must be supported by that runtime.

The re-review gives a per-finding verdict: ADDRESSED or NOT ADDRESSED. **Never fix it
yourself.**

### 5. The breaker

At round five with findings still open, stop dispatching and adjudicate each one:

| Finding is | Do |
|---|---|
| Wrong or contestable | park it with a ruling saying why |
| Real, but nothing depends on it | park it with a ruling |
| Real and load-bearing | decide the smallest change that unblocks it, and carry it into the next dispatch |

Every adjudication is a ledger entry. Silently dropping a finding is not allowed. Adjudicating
*before* the cap is pre-judging under another name.

### 6. Complete

`Task NN: complete (commits <base7>..<head7>, review clean)`.

## Final review

After the last task, build one package over the whole branch — `git merge-base <base-branch>
HEAD` to HEAD — and review it using `pwdev-power:power-review`. Claude Code uses its most capable
supported model for this review. Codex inherits host or session settings unless an explicit
routing policy calls for a supported higher-tier model-and-effort combination. Hermes Agent
follows its tool mapping. Point the review at the deferred-minor and parked lines in the ledger.

If it finds anything: **one** fix dispatch with the complete list, then exactly **one** scoped
re-review. There is no second wave.

## Waiting

While you have local work, do it. When genuinely idle, wait in bounded stretches with a
one-line status between them. Never poll in a tight loop; never wait silently forever.

## Finish

Collect **every** `Ruling:` line from the ledger into your final message, in order, each with
what it costs if it was wrong. A ruling that dies with the workspace was a decision taken in
secret.

Then hand off to `pwdev-power:power-verify`.
