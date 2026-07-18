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
   STATUS: COMPLETE | CAVEATS | FAILED | STOPPED:<condition>
   REPORT: <path to plan.done.md>
   COMMIT: <hash or none>
   NOTE: <1 line>
```

On retry after FAILED, append:

```
PREVIOUS ATTEMPT FAILED WITH:
{error/status note from the failed run}
Do not repeat the same approach blindly — diagnose first.
```

## Mode rule (used by /pwdev-feat:exec and the executor)

- Plan header `> **Type:** review` → **MODE: REPORT**.
- Otherwise, if the plan's Output Format table lists NO code files to
  create/modify (report-only plan, e.g. a test audit) → **MODE: REPORT**.
- Else → **MODE: IMPLEMENT**. Test plans that create test files are
  IMPLEMENT — tests are code and must be committed.
