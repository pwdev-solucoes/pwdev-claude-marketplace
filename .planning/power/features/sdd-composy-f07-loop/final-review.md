# F07 Integrated Review — Autonomous Loop

## Scope

Reviewed the approved F07 plan, ledger, all task reports/reviews, the current
working-tree implementation, loop references/templates/skill/adapters, and the
full test suite. This review was read-only; no source or test files were
modified.

## Verification

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q
Ran 218 tests ... OK

python3 -m unittest tests.test_sdd_composy_loop -q
Ran 26 tests ... OK

python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_tasks -q
Ran 85 tests ... OK

git diff --check
passed
```

## Findings

### Important — orchestrator collapses exact safe-stop reasons

`correction_decision()` distinguishes `destructive_request`, `scope_drift`,
`new_architecture`, `third_rejection`, and `repeated_environment_failure`, but
`orchestrate()` converts every `needs_human` decision to the terminal
`missing_progress` status. The loop skill and F07 plan require the exact stop
reason and the next human action, and the public loop schema has dedicated
terminal states for these safety conditions. An orchestrated destructive,
scope-expanding, architectural, repeated-environment, or third-rejection
result therefore loses the reason at the durable state boundary.

### Important — runtime exceptions are not classified as environment failure

When the runtime engine raises, `orchestrate()` synthesizes a rejected result
but does not preserve the runtime failure as an environment stop classification.
Depending on the previous snapshot, this can enter correction or end as
`missing_progress`, instead of the explicit `environment_failure` safe-stop
required by the plan.

## Disposition

**SPEC/QUALITY: REJECTED pending correction.**

The state machine, durable publication/resume behavior, runtime isolation,
provider adapters, skill disclosure, cancellation, and test coverage are
otherwise coherent and all requested verification commands pass. The two
orchestrator classification gaps must be fixed and covered by integration
tests before F07 can be approved.
