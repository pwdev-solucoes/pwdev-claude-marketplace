# Spawn Contracts — canonical subagent prompts

Harness rules that apply to EVERY spawn:

1. **Self-contained prompt.** The subagent gets everything it needs *inside the prompt* (full task content, spec excerpts) or as explicit file paths to read. It never depends on conversation history.
2. **Artifacts are the contract.** The subagent writes its full output to `.planning/...` files. Its chat reply to the orchestrator is a short status block (≤10 lines). The orchestrator reads the status, updates `state.md`, and NEVER pastes full reports back into its own context — only paths + status.
3. **Model.** Resolve per `references/model-profiles.md` and pass via the Task tool `model` parameter.
4. **Language.** Always include `LANGUAGE: {{lang}}` — subagents write user-facing artifacts in that language.
5. **Parallelism.** When two subagents are independent (code-reviewer + qa), issue both Task calls in a SINGLE message so they run concurrently.

---

## executor (`subagent_type: "pwdev-code:executor"`)

```
TASK (full content of .planning/phases/{slug}/plans/{PP}-{task-slug}.md — or verify/fix-{NN}.md when fixing):
{...}

SPEC EXCERPTS (.planning/phases/{slug}/spec.md):
### §1 Persona
{...}
### §6 Stop Conditions
{...}
### §7 Prohibitions
{...}

ACTIVE SKILLS — read these files before implementing:
{one path per line, e.g. .claude/skills/{name}/SKILL.md}

REQUIRED CONTEXT — read these files yourself:
{paths from the task's "Required Context" section}

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Implement, verify, and commit atomically (Conventional Commits; only files in the task scope).
2. Write .planning/phases/{slug}/execution/{PP}-summary.md — every AC with real command evidence.
3. Reply with AT MOST 10 lines:
   STATUS: COMPLETE | CAVEATS | FAILED | STOPPED:<condition>
   SUMMARY: <path>
   COMMIT: <hash or none>
   NOTE: <1 line>
```

On retry after FAILED, append:

```
PREVIOUS ATTEMPT FAILED WITH:
{error/status note from the failed run}
Do not repeat the same approach blindly — diagnose first.
```

---

## code-reviewer (`subagent_type: "pwdev-code:code-reviewer"`)

```
REVIEW SCOPE:
{file list or diff range, e.g. "git diff HEAD~3" or explicit paths}

SPEC EXCERPTS (.planning/phases/{slug}/spec.md):
### §1 Persona
### §5 Quality Criteria
### §7 Prohibitions
{...}

PROJECT CONVENTIONS: read CLAUDE.md section 12 (Repository Conventions).

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Write .planning/phases/{slug}/review/code-review.md (verdict: APPROVED | CHANGES REQUESTED | BLOCKED, findings table with severity).
2. Reply with AT MOST 10 lines: VERDICT, report path, counts by severity (critical/major/minor).
```

---

## qa (`subagent_type: "pwdev-code:qa"`)

```
SPEC EXCERPTS (.planning/phases/{slug}/spec.md):
### §2 Objective
### §5 Quality Criteria
### §8 Definition of Done
{...}

EXECUTION SUMMARIES — read:
{paths to .planning/phases/{slug}/execution/*-summary.md}

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Run the real test suite; trace requirement → test; propose skeletons for gaps.
2. Write .planning/phases/{slug}/review/qa-report.md (verdict: ADEQUATE | GAPS FOUND | INSUFFICIENT).
3. Reply with AT MOST 10 lines: VERDICT, report path, suite result, gap count.
```

---

## verifier (`subagent_type: "pwdev-code:verifier"`)

```
YOUR GOAL IS TO REFUTE COMPLETION, NOT CONFIRM IT.

SPEC (full sections 2, 3, 5, 6, 7, 8 of .planning/phases/{slug}/spec.md):
{...}

EXECUTION SUMMARIES — read (and DISTRUST: re-run their evidence):
{paths}

PRIOR REVIEW REPORTS (if they exist) — read:
{paths to review/code-review.md, review/qa-report.md}

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Build the truth list; for each truth, run the command most likely to DISPROVE it.
2. Write .planning/phases/{slug}/verify/verify.md (verdict: APPROVED | WITH CAVEATS | REJECTED).
3. If REJECTED: write .planning/phases/{slug}/verify/fix-{NN}.md in task format (one per plan).
4. Reply with AT MOST 10 lines: VERDICT, verify path, ACs passed/total, fix plans generated.
```

---

## researcher (`subagent_type: "pwdev-code:researcher"`)

```
FEATURE UNDER DISCOVERY: {description from interview round 1}
DETECTED STACK: {summary from init/discover step 1}
INVESTIGATE: {paths / topics}

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Write .planning/context/domain.md, .planning/context/stack.md, .planning/context/pitfalls.md.
2. Reply with AT MOST 3 lines: STATUS + the three paths.
```

---

## roadmap (`subagent_type: "pwdev-code:roadmap"`)

```
PRD (full content of .planning/product/prd.md):
{...}

PROJECT CONTEXT — read: .planning/context/project.md (if it exists)

LANGUAGE: {lang}

OUTPUT CONTRACT:
1. Write the multi-file roadmap under .planning/product/roadmap/ (ROADMAP, TRACEABILITY, RISKS, METRICS, ROLLOUT, VALIDATION + phase folders, hierarchy Phase→Epic→Feature→Task, IDs F01-E01-FT01-T01).
2. Reply with AT MOST 10 lines: counts (phases/epics/features/tasks) + root path.
```
