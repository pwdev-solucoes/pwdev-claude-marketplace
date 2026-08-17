# Execution contract

Execution implements one approved atomic task at a time. The plan and central specification outrank implementation convenience.

## Before editing

1. Read applicable repository instructions, the full task, linked specification clauses, required context, relevant memory, and current Git status.
2. Confirm allowed files do not overlap unrelated user changes unsafely.
3. Confirm dependencies are complete and verification commands are available.
4. Stop when the plan is stale, ambiguous, or contradicts the repository.

## Task lifecycle

1. Set phase state to `EXECUTING` and identify the task ID.
2. For behavior changes, write the focused failing test and observe the expected failure.
3. Implement only the approved actions and allowed files.
4. Run focused verification, then the relevant broader suite.
5. Inspect the full diff for scope and prohibited behavior.
6. Write `.planning/flow/phases/<slug>/execution/<id>-summary.md` with each acceptance criterion, exact evidence, changed files, deviations, and remaining risk.
7. Return `COMPLETE`, `CAVEATS`, `FAILED`, `NEEDS_ADVICE`, or `STOPPED:<reason>`.

Do not commit, push, create a branch, or rewrite history unless the user explicitly authorizes that action. `auto_commit` remains false by default.

## Advice and blockers

When a material ambiguity, architecture fork, or repeated verification failure has one concrete question:

- stop edits;
- write `<id>-advice-request.md` with question, context, options, work performed, and affected files;
- request a decision in the primary conversation;
- resume only after the decision is recorded in `<id>-advice.md` and, when durable, in memory.

Do not use advice as a way to expand scope. A second unresolved blocker for the same task returns `STOPPED` for human direction.

## Corrections

Review or verification may produce fix tasks. Execute them through the same lifecycle and mark prior review evidence stale. Allow a maximum of two correction cycles for a feature. After the second rejected cycle, stop and present the unresolved truths and attempted evidence.

## Collaboration

Execute inline by default. When the user explicitly requests delegation, follow [collaboration](collaboration.md), assign one writer per atomic task, and independently verify every returned claim before updating state.
