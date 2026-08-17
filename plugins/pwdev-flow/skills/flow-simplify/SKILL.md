---
name: flow-simplify
description: Analyze a completed phase diff for high-confidence behavior-preserving simplifications and apply only explicitly approved proposals. Use after execution and before review to reduce duplication, dead code, needless complexity, or avoidable inefficiency.
---

# Simplify without changing behavior

Read [execution](../../references/execution.md), [collaboration](../../references/collaboration.md), [memory](../../references/memory.md), [artifacts](../../references/artifacts.md), and [safety](../../references/safety.md).

## MODE: ANALYZE

1. Resolve an explicit diff or current phase execution scope.
2. Read quality criteria, prohibitions, repository conventions, relevant memories, tests, and the full diff.
3. Do not edit code in ANALYZE mode.
4. Propose only changes with at least 80% confidence that preserve observable behavior:
   - reuse an existing abstraction;
   - remove proven dead or duplicate code;
   - flatten needless control flow or indirection;
   - remove avoidable work with equivalent semantics.
5. Exclude bug fixes, behavior changes, speculative abstractions, broad rewrites, and style-only churn.
6. Write `simplify-proposals.md` with ID, confidence, kind, files, before/after sketch, evidence, risk, and verification command.
7. Present proposals by ID and stop. MODE: APPLY requires explicit approval; never analyze and apply in one uninterrupted step.

## MODE: APPLY

1. Require explicit approval listing proposal IDs. Ignore unapproved proposals.
2. Re-read the current diff and stop if proposal assumptions are stale.
3. Apply one approved proposal at a time within its declared files.
4. Run its focused verification immediately. On failure, restore only that proposal's edits when they can be isolated safely; otherwise stop and request direction.
5. Run the broader affected suite after all successful proposals.
6. Append applied, skipped, and evidence results to `simplify-proposals.md`.
7. Mark prior review evidence stale and set `REVIEW_REQUIRED`.

Work inline by default. Use a worker only when the user explicitly requests delegation, and keep ANALYZE and APPLY as separate approval-gated actions.

Do not commit or change unrelated files. Return mode, proposal or application counts, report path, verification evidence, and next action.
