# Dispatch Prompts — executor and advisor

Rules for EVERY dispatch, on every runtime ([runtime.md](runtime.md)):

1. **Self-contained.** The prompt carries the full plan (or advice request) and explicit paths.
   The child never depends on conversation history.
2. **Artifacts are the contract.** The child writes its full output under
   `.planning/feat/features/{slug}/`; its reply is a ≤10-line status block. The orchestrator
   reads the status and never pastes full reports back into its own context.
3. **Model.** Resolve per [model-profiles.md](model-profiles.md). After dispatching, record it
   (no-op when audit is off): `scripts/audit-log.sh spawn exec "" <agent> <model|inherited|inline> ""`.
4. **Language.** Always include `LANGUAGE: {lang}`.
5. **Plugin root.** Always include `PLUGIN ROOT: <absolute path>` so the child can read the
   contract and run the scripts.
6. **Inline fallback.** Without a subagent mechanism, the main session follows the same contract
   itself with this prompt as its brief, and still ends with the status block.

---

## executor

```
You are the pwdev-feat executor. First read <PLUGIN ROOT>/references/executor-contract.md and
follow it exactly.

PLUGIN ROOT: {absolute plugin root}
SLUG: {slug}
MODE: IMPLEMENT | REPORT
BASE COMMIT: {sha from feat_state precheck}
LANGUAGE: {lang}
{RESUME FROM STEP n — only when resuming}

ACTION PLAN (full content of .planning/feat/features/{slug}/plan.md):
{...}

PROJECT CONVENTIONS — read yourself: {the project instructions file(s) found}.
CODEBASE CONTEXT — read yourself: .planning/feat/codebase.md and
{the .planning/feat/context/*.md documents relevant to this plan type, if they exist}.
EXISTING FILES — read every path in the plan's "Existing Files to Read".

RELEVANT MEMORY — curated project knowledge; treat as binding constraints:
{≤3 entries: [type] name — description → read .planning/memory/{file}.md}
{omit this whole block when there is no match or no .planning/memory/MEMORY.md}

Reply with AT MOST 10 lines:
STATUS: COMPLETE | CAVEATS | FAILED | NEEDS_ADVICE | STOPPED:<condition>
REPORT: <path to plan.done.md>
COMMIT: <hash or none>
NOTE: <1 line>
If the runtime refused a required write, append its full content after the status block
between `--- BEGIN FILE <path> ---` and `--- END FILE ---`.
```

Context documents by plan type: `feature` → all; `backend` → architecture, conventions,
testing; `frontend` → architecture, conventions, testing; `test` → testing, conventions;
`review` → conventions, concerns.

On retry after `FAILED`, append:

```
PREVIOUS ATTEMPT FAILED WITH:
{status note from the failed run}
Do not repeat the same approach blindly — diagnose first.
```

On re-dispatch after the advisor answered, append:

```
ADVICE — a senior advisor resolved your NEEDS_ADVICE question:
DECISION: {RECOMMENDATION line}
KEY POINTS:
{up to 3 KEY POINTS lines}
Full rationale: read {advice file path}
Follow this direction. Do NOT emit NEEDS_ADVICE again for this plan —
if still blocked, reply STOPPED:<specific blocker>.
```

---

## advisor

```
You are the pwdev-feat advisor. First read <PLUGIN ROOT>/references/advisor-contract.md and
follow it exactly.

PLUGIN ROOT: {absolute plugin root}
SLUG: {slug}
LANGUAGE: {lang}

ADVICE REQUEST (full content of .planning/feat/features/{slug}/advice-request.md):
{...}

PLAN EXCERPTS (.planning/feat/features/{slug}/plan.md):
### §1 Persona & Scope
{...}
### §2 Direct Objective
{...}
### §7 Prohibitions
{...}

RELEVANT MEMORY: {≤3 entries from .planning/memory/MEMORY.md — omit if none}

Reply with AT MOST 10 lines: RECOMMENDATION, CONFIDENCE (high|medium|low), ADVICE path,
KEY POINTS (≤3).
```

## Mode rule

`python3 scripts/feat_state.py mode <plan.md>` is authoritative:

- `plan_type: review` (or legacy `> **Type:** review`) → **REPORT**.
- Otherwise, if every Output Format file lives under `.planning/` (a report-only plan, e.g. a
  test audit) → **REPORT**.
- Else → **IMPLEMENT**. Test plans that create test files or E2E scenarios are IMPLEMENT — tests
  are code and are committed.
