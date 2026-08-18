# PWDEV Power

Disciplined spec-driven development that runs on **Claude Code, Codex, and Hermes Agent**, with
isolated autonomous fleets on **cmux**.

---

## Why this exists

Coding agents fail in predictable ways. They start writing before anyone agreed what to build.
They write the test after the code, so it tests what was built rather than what was needed. They
fix the symptom they can see instead of the cause they cannot. They say "done" without running
anything. And when they work in parallel, they quietly overwrite each other.

Each of those has a known countermeasure, and none of them is complicated. What is hard is
applying them under pressure, in the middle of a task, when skipping one feels productive.

`pwdev-power` encodes those countermeasures as skills the agent must invoke, and puts a human at
every gate that matters. It combines three things that usually live apart:

- **Speed.** Planning happens inline, in the conversation, not behind a subagent that cannot talk
  to you. A small change costs one command.
- **A product layer.** A requirement, then a `Phase → Epic → Feature → Task` roadmap with real
  traceability, so a large effort has a spine.
- **Engineering discipline.** A brainstorming gate before any code, plans whose exact values
  travel to the engineer who implements them, execution with a durable ledger and a bounded fix
  loop, and verification that tries to *refute* completion rather than confirm it.

### Three rules that survive every rationalization

1. **No production code without a failing test first** — and the red must be *observed*, not
   assumed. A test that never failed proves nothing when it passes.
2. **No fix without root cause investigation first.** Three failed fixes means the architecture is
   the suspect, not the line you keep editing.
3. **No success claim without running the command and reading its output.** Evidence, then
   assertion — never the reverse.

---

## The mental model

**Skills are the single source of truth.** Fourteen skills describe the work. Each runtime gets a
thin adapter over them and nothing more: slash commands on Claude Code, `$power-*` on Codex, a
native plugin on Hermes. There is no second implementation to drift.

**Gates belong to humans.** A gate is a point where the agent stops, shows you something, and
waits. Approval is *recorded* — never inferred from silence, and never granted by the agent to
its own work. Nothing is approved merely because a file exists.

**Status contracts are short.** A subagent writes its report to a file and returns at most ten
lines. The orchestrator reads the status and the path — never the report's contents. That single
rule is what keeps a long feature affordable instead of drowning the main context.

**The ledger is on disk.** Execution progress and every judgement call live in `ledger.md`, whose
first line binds it to its plan. A controller that loses its place reads the ledger instead of
re-dispatching finished tasks.

---

## Install

### Claude Code

```bash
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-power
```

Verify: `/pwdev-power:init` should offer to set up a workspace.

### Codex

The plugin declares `"skills": "./skills/"`, so Codex discovers them itself. Invoke with
`$power-<name>`, for example `$power-plan`.

Subagents require this in `~/.codex/config.toml`:

```toml
[features]
multi_agent = true
```

### Hermes Agent

```bash
# global install
hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable

# or, working inside a checkout, load the skills repo-local
hermes skills trust .
hermes skills list | grep power-
```

Verify: `hermes plugins doctor plugins/pwdev-power` should report registration passing, and a new
session should already know the `power` skill without being told.

### For the fleet (optional)

The fleet needs **cmux running** and `jq`, `git`, `python3`, and `docker` on `PATH`. Everything
else in the plugin works without cmux.

```bash
cmux ping                    # must answer before any fleet command
```

If the CLI is not on your `PATH` (common on macOS, where it lives inside the app bundle), set:

```bash
export PWDEV_POWER_CMUX_BIN=/Applications/cmux.app/Contents/Resources/bin/cmux
```

---

## Command reference

| Command | Arguments | What it does |
|---|---|---|
| `/pwdev-power:init` | — | Sets up `.planning/power/`, detects the stack, reports the runtime surface |
| `/pwdev-power:product` | `prd [description] \| roadmap [path]` | Interviews for a requirement, or decomposes an approved one |
| `/pwdev-power:plan` | `<feature description>` | Brainstorms, designs, and decomposes into tasks |
| `/pwdev-power:exec` | `<feature-slug>` | Executes an approved plan task by task |
| `/pwdev-power:verify` | `<feature-slug> [--strict]` | Adversarial verification, then integration |
| `/pwdev-power:quick` | `<bounded task>` | A small understood change, no plan file |
| `/pwdev-power:fleet` | `<slug...> [--via-kanban] \| --status \| --teardown <slug> [--merge]` | Approved phases, unattended and in parallel |

Skills also trigger on their own — you do not have to name `power-tdd` for it to apply when code
is being written.

---

# Scenarios

Each scenario below is a complete path, with what you type, what happens, and where you stop.

---

## Scenario A — A new product, from nothing

The full path. Use it when you are starting something substantial and nobody has written the
requirement yet.

### A1. Set up

```
/pwdev-power:init
```

It detects before it asks: is this a git repository, greenfield or brownfield, what stack (read
from `package.json`, `pyproject.toml`, `go.mod`, and friends — including the *real* test and lint
commands), and which of cmux, Hermes, `jq` and `sqlite3` are available.

Then at most three questions: language, model profile (`economy` / `balanced` / `performance`),
and whether to enable the audit trail.

**Produces:** `.planning/power/config.json` and `.planning/power/state.md`.

### A2. Write the requirement

```
/pwdev-power:product prd "a booking system for municipal health clinics"
```

Three rounds, at most four questions per round, **asked one at a time** — a numbered list of six
questions gets answered like a form, and forms get answered shallowly.

1. Vision and problem — who has it, what they do today, what it costs them.
2. Scope and capability — must, should, out.
3. Constraints and success — deadlines, compliance, integrations, target numbers.

It then writes a ten-section requirement and checks its own work before showing you: is every
non-functional requirement *measurable* (a number, not "fast"), does every must-have have an
acceptance criterion, is anything in "functional requirements" actually a design decision that
belongs in a spec.

🚦 **GATE.** It shows you the requirement and waits. On approval it sets `Status: APPROVED`.

**Produces:** `.planning/power/product/prd.md`

### A3. Decompose into a roadmap

```
/pwdev-power:product roadmap
```

First it validates the requirement. If goals, functional requirements, acceptance criteria or
scope boundaries are missing, it sends you back — three or more missing means the roadmap would
be fiction.

Then it dispatches the `roadmap` subagent, which writes files and returns ten lines. Ordering is
by technical dependency first, then business value, then risk — high-risk work early, while being
wrong is still cheap.

🚦 **GATE.** You see counts and the root path. Ask for changes and it re-dispatches; it does not
hand-patch the output.

**Produces:**

```text
.planning/power/product/roadmap/
├── ROADMAP.md          index
├── TRACEABILITY.md     requirement ↔ roadmap, both ways — mandatory
├── RISKS.md · METRICS.md · ROLLOUT.md
└── F01-<slug>/
    ├── PHASE.md · CHECKLIST-F01.md
    └── F01-E01-<slug>/
        ├── EPIC.md
        └── F01-E01-FT01-<slug>.md
```

A roadmap without `TRACEABILITY.md` is refused. It is the file that proves every requirement
landed somewhere and every phase traces back to one.

### A4. Plan the first phase

```
/pwdev-power:plan "F01-E01 — clinic and room registry"
```

**It classifies out loud before asking anything** — spike, bounded, or architectural — because
the classification decides how much process follows, and hiding it hides the decision.

For a new subsystem this is *architectural*: it explores the code, asks one question at a time,
offers two or three approaches with real trade-offs **and a recommendation**, then walks the
design section by section so a disagreement costs one section instead of the whole thing.

🚦 **GATE 1.** The spec. On approval, exactly one `Status: APPROVED` field.

Then it decomposes. The plan is written for an engineer who joins at one task, has none of your
context, and will never see the other tasks:

```markdown
## Global Constraints
- Request timeout: 2500ms
- Page size: 50 items maximum

## File Structure
...

## Task 01 — clinic model and migration
Complexity: low
Files: src/models/clinic.ts, migrations/001_clinics.sql
Interfaces:
  Produces: `findClinic(id: string): Promise<Clinic | null>`
Steps:
- [ ] Write a failing test for finding a clinic by id
- [ ] Run it, watch it fail for the missing function
- [ ] Implement findClinic
- [ ] Run it, watch it pass
- [ ] Commit
```

`Global Constraints` is copied **verbatim** from the spec, never summarized — the reviewer checks
against this block, so a paraphrase here becomes a wrong verdict there. The `Interfaces:` block is
how an implementer that sees one task discovers what its neighbours expect.

🚦 **GATE 2.** The task map — id, name, complexity, files.

**Produces:** `spec.md` and `plan.md` under `.planning/power/features/<slug>/`

### A5. Execute

```
/pwdev-power:exec clinic-registry
```

What happens, per task:

1. **Pre-flight scan** (once, before Task 01) — a table with one row per pair of tasks sharing a
   file or an interface, and one row per task confirming its own text agrees with itself.
2. **Dispatch** — a fresh implementer with the brief path, the interfaces it consumes, and the
   report path. Never the whole plan, never accumulated conversation.
3. **Report** — `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
4. **Review** — a fresh reviewer gets the brief, the report, the diff, and the constraints
   verbatim, and returns two independent verdicts: spec compliance *and* task quality.
5. **Fix loop, if needed** — at most **five rounds**. Rounds 1–3 resume the original implementer,
   which still has the context; rounds 4–5 use a fresh one, a model tier up. Minor findings are
   deferred to the ledger and never enter the loop.
6. **Complete** — `Task NN: complete (commits abc1234..def5678, review clean)`.

At the end you get every `Ruling:` line from the ledger, in order, each with what it costs if it
was wrong. A judgement call that dies with the workspace was a decision taken in secret.

### A6. Verify and integrate

```
/pwdev-power:verify clinic-registry
```

The verifier's instruction is not "check whether this is complete" — it is **"try to refute that
this is complete."** For each stated truth it designs a command that would *fail* if the truth
did not hold, runs it, and records the real output.

It pays particular attention to prohibitions (least tested, most often violated, because nothing
fails when you break one) and to tests that cannot fail (revert the implementation; the test must
go red).

Add `--strict` for two parallel lenses — functional and compliance — where the verdict is the
worse of the two. Something that works but violates a stated prohibition is not approved.

| Verdict | Next |
|---|---|
| `APPROVED` | integrate |
| `CAVEATS` | integrate, with findings surfaced |
| `REJECTED` | a bounded fix plan, then re-verify — at most twice |

Then `power-finish` runs the full suite, and only once it is green shows the menu: merge locally,
push and open a pull request, or leave it. Discarding requires you to type the word `discard`.

---

## Scenario B — A feature in an existing codebase

Skip the product layer entirely.

```
/pwdev-power:init                              # once per repository
/pwdev-power:plan "add CSV export to the patient list"
```

Here the brainstorm will likely classify **bounded**: a well-scoped change to a flow that already
exists and can be read. Bounded means a short design *in the conversation*, no spec file, no plan
— then it stops and waits for an explicit yes before implementing.

If it turns out the change needs a new interface, the classification **moves up** to architectural
mid-conversation and says so. The ratchet only turns one way: hidden complexity raises the path,
nothing ever lowers it.

For architectural, continue exactly as in A4 → A6.

---

## Scenario C — A change of one to three files

```
/pwdev-power:quick "the retry ceiling should be 5, not 3"
```

It reads the actual files (a quick change proposed from memory of a codebase is a guess), shows a
three-line mini-plan, waits for a yes, implements, verifies, and commits.

**It escalates rather than drifting** the moment any of these is true: more than three files, you
cannot name the failure mode, it adds an interface or a migration, it touches auth, payments,
permissions or data deletion, or you are about to write "while I'm here."

Even here TDD applies. "It is only one line" is the most common way a missing test never gets
written.

**Produces:** `.planning/power/quick/<date>-<slug>/{contract,report}.md` — two short files, so
that a pattern of quick changes to the same area becomes visible evidence that the area needs a
real plan.

---

## Scenario D — Something is broken

You do not need a command. Describing a bug triggers `power-debug`, which refuses to propose a fix
before it has a cause.

```
The booking endpoint returns 500 for clinics created today.
```

1. **Root cause** — read the *entire* error; reproduce it consistently; check what changed
   recently. In a multi-component system, **instrument every boundary before proposing anything**
   and run once to learn *where* it breaks. Trace the data backwards from wrong to right.
2. **Pattern analysis** — find something in this codebase that works the same way, read it
   completely, and list every difference. The irrelevant-looking one is frequently the answer.
3. **One hypothesis at a time**, written down, with the smallest test that would disprove it. If
   it was wrong, form a *new* one — do not stack another fix on the last attempt.
4. **Fix** — failing test first, root cause once, no "while I'm here", then verify.

**After three failed fixes it stops** and brings the architecture to you. Continuing costs more
than asking.

---

## Scenario E — Review arrived

```
Here's the review from the PR: <paste>
```

`power-review` runs READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT.

It verifies each finding against the codebase before acting — reviewers are sometimes wrong about
what the code does, especially external ones — and if **any** finding is unclear it stops and asks
before implementing **any** of them, because findings interact.

There is no performative agreement. No "You're absolutely right!", no thanks. Disagreement with a
technical reason is a normal, expected outcome.

To request a review of your own work, it builds the reviewer's context deliberately — requirements,
diff, constraints — rather than handing over the session history, and never tells the reviewer
what not to flag.

---

## Scenario F — Several phases at once, unattended

For approved phases that do not overlap. Each member gets its own worktree, Docker stack and cmux
workspace.

### F1. Preconditions

- cmux running (`cmux ping` answers)
- Each slug has `spec.md` with **exactly one** `Status: APPROVED` field, plus `plan.md`
- A named current branch — not detached HEAD

### F2. Launch

```
/pwdev-power:fleet clinic-registry booking-rules
```

It shows the exact command shape for your runtime and **requires you to acknowledge the dangerous
flag** before anything launches:

| Runtime | Vector |
|---|---|
| Claude Code | `claude -p --dangerously-skip-permissions --no-session-persistence --output-format json` |
| Codex | `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <schema> --output-last-message <file>` |
| Hermes | `hermes -z <prompt> --in <worktree> --yolo --accept-hooks` |

If two slugs mention the same repository paths you get an advisory warning naming them. It does
not block — plausible overlap is common and only you know whether it matters here.

Each member then runs `plan → execute → review → verify` on its own, committing per stage.

### F3. Watch

Status lives in the **cmux sidebar** — amber while running, green on done, red when a member needs
you, plus a notification. There is no pane to watch.

```
/pwdev-power:fleet --status
```

gives a one-shot table: slug, runtime, stage, status, ports, and a short message. It never prints
worktree paths, logs or prompts.

Ports come from the first free slot — member 0 gets `3000`/`5432`, member 1 gets `3010`/`5442` —
and are published on loopback only.

### F4. When a member is rejected

`verify` returning `REJECTED` starts a correction cycle: `execute-fix → review-fix → verify`. At
most **two** cycles, so ten provider invocations worst case. A third rejection becomes
`NEEDS_HUMAN` — it never becomes an approval by attrition.

### F5. Tear down

```
/pwdev-power:fleet --teardown clinic-registry
```

Stops the stack, closes the cmux workspace it created, removes the member record, and
**preserves the branch and the worktree** — a member that failed is evidence. The database volume
is kept and reported with the command to remove it.

```
/pwdev-power:fleet --teardown clinic-registry --merge
```

Merges into the base branch. Refused for any member that is not `DONE`, and the terminal status is
re-validated first.

---

## Scenario G — Let Hermes orchestrate the fleet

Requires the `hermes` CLI. Approved phases become cards on the Hermes Kanban board and its
dispatcher runs them.

```
/pwdev-power:fleet clinic-registry booking-rules --via-kanban
```

Under the hood, and always previewed first:

```bash
scripts/kanban-bridge.sh preview clinic-registry     # prints the exact commands; creates nothing
scripts/kanban-bridge.sh create  clinic-registry     # creates the cards, records the task ids
hermes kanban dispatch --dry-run --json              # shows what would spawn
hermes kanban daemon --interval 60                   # or dispatch for real
scripts/kanban-bridge.sh mirror                      # board state → cmux sidebar
```

The mapping:

| pwdev-power | `hermes kanban` |
|---|---|
| Approved phase | `create --workspace worktree:<path>` |
| Correction cap | `--max-retries 2` |
| Member timeout | `--max-runtime 2h` (SIGTERM → SIGKILL → re-queue) |
| Dependencies | `--parent <id>`, `kanban link` |
| Human gate | `request-review` / `request-changes` |

**The idempotency key carries the spec hash.** Relaunching the same approved phase returns the
*same* card instead of duplicating it; an edited spec produces a different key and therefore a
genuinely new card.

**Read `references/kanban.md` before using this route.** On it, the correction cap becomes the
dispatcher's `--max-retries`, and the human gate becomes `request-review` on the card. What does
*not* change owner is the contract hashes — the board cannot tell an edited spec from an approved
one, so this plugin keeps checking.

---

## Scenario H — Working in Codex

Same skills, different invocation.

```
$power-plan add CSV export to the patient list
$power-execute clinic-registry
```

Codex-specific behaviour the skills already account for:

- Subagents spawn with `fork_turns: "none"`. The default `"all"` copies the entire transcript into
  the child, which defeats the point of a fresh context.
- Every spawn sets **both** `model` and `reasoning_effort` — setting only `model` silently resets
  effort to that model's default.
- Fix rounds 1–3 use `followup_task` to reach the implementer that already has the context, rather
  than spawning a fresh one.
- `wait_agent` is an event subscription, not a poll: one wait with a 5–10 minute timeout, not
  eight short ones.

To run a fleet from Codex, use `codex-fleet-up.sh`. Your runtime is bound at launch and a runner
with a different adapter refuses to start.

---

## Scenario I — Working in Hermes

The bootstrap loads on the first turn of a session, so the agent already knows the skills exist.

```
skill_view("pwdev-power:power-plan")
skill_view("pwdev-power:power-tdd")
```

If a namespaced lookup returns "not found", the bootstrap prints the absolute skills directory for
`read_file` as a fallback.

Headless, for scripts and CI:

```bash
hermes -z "load pwdev-power:power-quick and bump the retry ceiling to 5" --in .
```

Two Hermes specifics worth knowing:

- **Subagent context is explicit** via `delegate_task(goal=…, context=…, toolsets=[…])`. There is
  no transcript to suppress, which matches this plugin's rule of handing a child its brief rather
  than accumulated history.
- **There is no post-compaction hook.** See *Known limits*.

---

## Scenario J — Turn on the audit trail

Off by default. It takes three things, and creating the database is the act that turns it on:

```bash
# 1. opt in
jq '.audit = true' .planning/power/config.json > tmp && mv tmp .planning/power/config.json

# 2. sqlite3 must be installed
command -v sqlite3

# 3. create the database — nothing is recorded until this exists
mkdir -p .planning/power/audit
sqlite3 .planning/power/audit/pwdev-audit.db "SELECT 1;"
```

Query it directly:

```bash
sqlite3 -header -column .planning/power/audit/pwdev-audit.db \
  "SELECT timestamp, phase, action, target FROM events ORDER BY id DESC LIMIT 20;"

# every gate result
sqlite3 .planning/power/audit/pwdev-audit.db \
  "SELECT timestamp, phase, action FROM events WHERE action LIKE 'gate_%';"
```

**Model names and prompts never enter the trail.** Any key containing `model` or `prompt` is
rejected before the write, so a dispatch records a *tier* (`tier=mid`), not a model name. Targets
are stored relative to the repository root; absolute paths are rejected. Audit is best-effort by
construction and always exits 0 — a failed record must never change the lifecycle result it was
describing.

---

## What lands on disk

```text
.planning/power/
├── config.json                     language, model profile, audit, fleet, kanban
├── state.md                        status, last gate, correction cycles, next valid action
├── product/
│   ├── prd.md
│   └── roadmap/                    ROADMAP, TRACEABILITY, RISKS, METRICS, ROLLOUT + phases
├── features/<slug>/
│   ├── spec.md                     the approved design
│   ├── plan.md                     global constraints + per-task interfaces
│   ├── ledger.md                   progress + every Ruling:
│   ├── task-01-brief.md            what the implementer actually reads
│   ├── task-01-report.md           what it did, with real command output
│   ├── task-01-review.md           two verdicts and findings
│   ├── verdict.md                  verification evidence
│   └── fix-01.md                   bounded correction tasks, on rejection
├── quick/<date>-<slug>/            contract + report
├── fleet/<slug>.json               runtime, worktree, ports, contract hashes, cmux workspace id
├── fleet-status.json               per-worktree: stage, status, verdict, correction cycles
└── audit/pwdev-audit.db            opt-in
```

Markdown is a human-readable contract; JSON is configuration and operational bookkeeping. Task IDs
are two digits and stay stable from plan through execution and correction — a fix for task 03 is
always about task 03.

---

## Every gate, in one table

| Gate | Who decides | Recorded in |
|---|---|---|
| Requirement approved | you | `state.md` + `Status:` in `prd.md` |
| Roadmap accepted | you | `state.md` |
| Design approved | you | `state.md` + exactly one `Status: APPROVED` in `spec.md` |
| Plan approved | you | `state.md` |
| Task review | the reviewer subagent | `task-NN-review.md` |
| Verification verdict | the verifier, then you on `REJECTED` | `verdict.md` |
| Fleet launch | you, by acknowledging the vector | the member record |
| Branch integration | you, from a three-option menu | — |

"Exactly one `Status: APPROVED`" is deliberate. A document with a second one inside an example
block is ambiguous, and ambiguity here means launching unapproved work.

---

## How the fleet stays safe

- **The privileged command exists in exactly one adapter per runtime.** Nothing else in the plugin
  may build a provider command or add a permission flag. Tests run all three adapters and compare
  the real argv: `claude` never carries `--yolo`, `hermes` never carries a `--dangerously` flag.
- **The runtime is fixed before any mutation.** It is chosen by the launcher, written into the
  member record, and a runner whose adapter disagrees refuses to start. No config value,
  environment variable or argument can turn one vector into another.
- **Contracts are hashed at launch** — the exact approved working-tree bytes, not `HEAD` bytes,
  because an approved spec is frequently not committed yet. The hashes are re-checked before and
  after every stage, so editing a spec mid-flight stops the member instead of quietly changing
  what it is building.
- **The provider leads its own process group.** Reaping a successful provider does not release
  ownership: the whole descendant group must be proven gone before validating a result,
  committing, or advancing — it may have left dev servers or child containers alive.
- **A stage must produce work.** Well-formed JSON describing work nobody did is caught by asking
  git whether HEAD moved or the feature directory is dirty.
- **Generated runtime files never reach the branch.** The environment file is written under
  `umask 077` *before* the content lands, and a generated `.gitignore` keeps it and the raw
  provider output out of what `git add -A` would carry into your base branch on merge.
- **The fleet never steals focus** and closes only cmux workspaces whose identifier it recorded.

---

## Troubleshooting

| What you see | What it means | What to do |
|---|---|---|
| `cmux: no socket at …` | cmux is not running | Start cmux. Only the fleet needs it. |
| `cmux: CLI not found` | Not on `PATH` | `export PWDEV_POWER_CMUX_BIN=/Applications/cmux.app/Contents/Resources/bin/cmux` |
| `spec must carry exactly one 'Status: APPROVED' field (found 2)` | A second approval line, often inside an example block | Leave one real approval field |
| `no .planning/power/config.json; run init first` | No workspace | `/pwdev-power:init` |
| `detached HEAD; check out a named branch first` | Every phase binds to a branch | Check out a branch |
| `registered fleet member does not match canonical Git worktree registration` | You are the wrong runtime for this member, or the worktree moved | Use the launcher matching the member's `runtime` field |
| `approved fleet contracts do not match the bound member` | Someone edited the spec or plan after launch | Restore the approved bytes, or tear down and relaunch |
| `invalid structured result for <stage>` | The provider answered with prose | The raw answer is kept as `<stage>-<time>.invalid.json` in `fleet-results/` |
| `fleet member is already running` | A runner lock is held | Check for a live runner before removing anything |
| `provider ownership is unresolved; retaining runner lock` | A process group could not be proven gone | **Deliberate.** Look for orphaned processes before relaunching |
| `verification rejected after two correction cycles` | The cap held | Read `verdict.md`; the loop will not try a third time |
| `fleet allocation is already locked` | A concurrent launch | Wait for it, or remove `.planning/power/fleet/.lock` if no launch is running |
| Skills stop triggering on Hermes | The session compacted over turn one | Start a new session — see *Known limits* |

A member that failed keeps its branch and worktree. Investigate there; do not relaunch over it.

---

## Known limits

- **Hermes has no post-compaction hook.** A long session that compacts over its first turn loses
  the bootstrap. Start a fresh session if skills stop triggering — this cannot be fixed from
  inside the plugin. Claude Code re-injects on `startup|clear|compact`; Codex discovers skills
  natively and needs no injection.
- **Per-dispatch model selection on Hermes is not established.** `delegate_task` is not documented
  as taking a model. Until it is, route through the Kanban card's `--model`/`--provider`, or run
  inline — never invent a parameter to satisfy the rule that models be explicit. See
  `references/hermes-tools.md`.
- **The fleet requires cmux.** There is no tmux fallback by design.
- **Audit requires `sqlite3`** and stays off until the database file exists.
- **The compose template assumes Postgres.** Without a `Dockerfile` only the database comes up,
  which is intentional — the `app` service cannot build.
- **`unittest discover` does not work in this tree.** One form raises `ImportError`, the other runs
  zero tests silently. Name the modules.

---

## Contributing

```bash
python3 -m unittest tests.test_pwdev_power tests.test_power_hermes    # 59 tests
claude plugin validate plugins/pwdev-power
hermes plugins doctor --ci plugins/pwdev-power
```

The reference contracts in `references/` are the specification; skills read them rather than
restating them. If you change behaviour, change the reference and the test together.

Two conventions worth knowing before editing a skill:

- **A skill's `description` states only when to trigger, never what the skill does.** A description
  that summarises the workflow gets followed *instead of* the skill being read.
- **No `@`-links between skills.** They force an immediate load and burn context nobody chose to
  spend. Use the namespaced name and relative markdown links.

---

## License

Apache-2.0. See [LICENSE](./LICENSE).
