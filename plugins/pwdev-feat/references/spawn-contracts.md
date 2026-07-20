# Spawn Contracts — canonical subagent prompts

Harness rules that apply to EVERY spawn:

1. **Self-contained prompt.** The subagent gets everything it needs inside the
   prompt (full plan content) or as explicit file paths to read. It never
   depends on conversation history.
2. **Artifacts are the contract.** The subagent writes its full output to
   `.planning/feat/...` files. Its chat reply is a short status block
   (≤10 lines). The orchestrator reads the status and NEVER pastes full
   reports back into its own context.
3. **Model.** Resolve per `references/model-profiles.md` (override key
   `feat-executor`) and pass via the Task tool `model` parameter.
4. **Language.** Always include `LANGUAGE: {{lang}}`.

---

## executor (`subagent_type: "pwdev-feat:executor"`)

```
MODE: IMPLEMENT | REPORT

ACTION PLAN (full content of .planning/feat/features/{slug}/plan.md):
{...}

PROJECT CONVENTIONS — read yourself: CLAUDE.md (root), especially Stack,
Commands, and Golden Rules sections.
CODEBASE CONTEXT — read yourself: .planning/feat/codebase.md (if it exists).
EXISTING FILES — read every path in the plan's "Existing Files to Read".

RELEVANT MEMORY — curated project knowledge; treat as binding constraints:
{≤3 entries: [type] name — description → read .planning/memory/{file}.md}
{omit this whole block when there is no match or no .planning/memory/MEMORY.md}

LANGUAGE: {lang}

OUTPUT CONTRACT:
IMPLEMENT mode:
1. Execute the plan steps in order; verify EVERY quality criterion with real
   command evidence; commit ONLY files listed in the plan's Output Format
   table (Conventional Commits, message from the plan's Commit section).
2. Write .planning/feat/features/{slug}/plan.done.md (execution report).
REPORT mode (review plans / report-only plans):
1. Do NOT modify or commit ANY project file.
2. Write findings to .planning/feat/features/{slug}/report.md and a short
   .planning/feat/features/{slug}/plan.done.md (Status + report path).
Both modes — reply with AT MOST 10 lines:
   STATUS: COMPLETE | CAVEATS | FAILED | NEEDS_ADVICE | STOPPED:<condition>
   REPORT: <path to plan.done.md>
   COMMIT: <hash or none>
   NOTE: <1 line>
```

On `NEEDS_ADVICE` (IMPLEMENT mode only) the executor writes
`.planning/feat/features/{slug}/advice-request.md` first (Blocking Question,
Context, Options Considered, Work Done So Far, Files Involved), does NOT
commit, and replies instead:

```
STATUS: NEEDS_ADVICE
QUESTION: <the decision, 1 line>
REQUEST: .planning/feat/features/{slug}/advice-request.md
COMMIT: none
NOTE: <1 line — what was done / working tree state>
```

On retry after FAILED, append:

```
PREVIOUS ATTEMPT FAILED WITH:
{error/status note from the failed run}
Do not repeat the same approach blindly — diagnose first.
```

On re-spawn after the advisor answered a `NEEDS_ADVICE`, append:

```
ADVICE — a senior advisor resolved your NEEDS_ADVICE question:
DECISION: {RECOMMENDATION line from the advisor's reply}
KEY POINTS:
{up to 3 KEY POINTS lines}
Full rationale: read {advice file path}
Follow this direction. Do NOT emit NEEDS_ADVICE again for this plan —
if still blocked, reply STOPPED:<specific blocker>.
```

---

## advisor (`subagent_type: "pwdev-feat:advisor"`)

```
ADVICE REQUEST (full content of .planning/feat/features/{slug}/advice-request.md):
{...}

PLAN EXCERPTS (.planning/feat/features/{slug}/plan.md):
### §1 Persona & Stack
{...}
### §2 Objective
{...}
### §7 Prohibitions
{...}

RELEVANT MEMORY: {≤3 entries from .planning/memory/MEMORY.md — omit if none}

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Investigate read-only (Read/Grep/Glob/Bash). Pick ONE direction — never "it depends".
2. Write .planning/feat/features/{slug}/advice.md (Decision, Rationale, Rejected Options, Risks).
3. Reply with AT MOST 10 lines: RECOMMENDATION, CONFIDENCE (high|medium|low), ADVICE path, KEY POINTS (≤3).
```

Model: resolve per `references/model-profiles.md` (override key `feat-advisor`).

## Mode rule (used by /pwdev-feat:exec and the executor)

- Plan header `> **Type:** review` → **MODE: REPORT**.
- Otherwise, if the plan's Output Format table lists NO code files to
  create/modify (report-only plan, e.g. a test audit) → **MODE: REPORT**.
- Else → **MODE: IMPLEMENT**. Test plans that create test files are
  IMPLEMENT — tests are code and must be committed.
