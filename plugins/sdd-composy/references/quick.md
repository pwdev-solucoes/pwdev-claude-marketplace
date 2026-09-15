# Quick path

`$sdd-quick` is a bounded entry path, not a second lifecycle. It consumes an
objective, acceptance criteria, a closed allowed-file list, and known verification
commands, then creates a `Q-*` contract and a normal `TASK-*` record.

## Eligibility gate

Before editing, all conditions must hold:

- at most five implementation files (tests and generated evidence are tracked separately);
- precise objective and acceptance criteria;
- no architecture or schema decision, migration, destructive operation, scope expansion,
  or unknown verification;
- known failing-test and final verification commands;
- no forbidden prompt/output dumps, environment variables, secrets, models, or private paths.

Failure of any condition makes the gate return `ESCALATE` (reported as `ESCALATED`); stop before editing and continue through
the standard SDD flow. Never silently widen the quick scope.

## Execution contract

1. Inspect instructions and working-tree changes; protect unrelated edits.
2. Write the `QUICK_CONTRACT` and register the normal task: render `task-<id>.md` from
   `templates/task.md` and run `sdd_tasks.py import`; gate evidence goes through
   `sdd_tasks.py evidence`.
3. Run a failing test before implementation (TDD), then make only the allowed change.
4. Run focused and broader verification, review the complete diff, and collect evidence.
5. After each represented action succeeds, append semantic events with `sdd_trace.py record`;
   never edit or repair `trace.json` directly.
6. Write `QUICK_REPORT`, verify the evidence links and trace, and publish a verified verdict.

The plan-bound confirmation token `CONFIRM-SDD-SYNC-…` is required only for synchronization
operations; quick mode never bypasses that boundary. Quick reports and contracts use
OKF v0.2 and are linked from the feature bundle index.

## Evidence and escalation

The report must identify the failing test, changed-file count, acceptance evidence,
review, verification, trace event, and final verdict. Missing, stale, or contradictory
evidence is not completion. Escalate to a normal task when the scope changes, the
five-file limit is exceeded, a forbidden category appears, verification becomes
unknown, or review cannot establish the acceptance criteria.
