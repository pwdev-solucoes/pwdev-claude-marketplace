# Task F04-19 — implementation report

Date: 2026-09-13
Branch: `codex/pwdev-qa`

## Scope

Implemented the portable `qa-regression` and `qa-bug` workflow bodies, their thin Claude command
adapters, and focused behavioral coverage in `tests/test_qa_workflows.py`. No product correction,
test execution by the workflows, installation, publication, external effect, or change outside
the authorized task files was performed.

## RED

Command (packaged Python 3.12):

```text
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_qa_workflows.QaWorkflowContractTest.test_regression_and_bug_have_the_complete_portable_contract
```

Observed result before implementation: `FAILED (failures=2)`. Both subtests failed because
`plugins/pwdev-qa/skills/qa-regression/SKILL.md` and
`plugins/pwdev-qa/skills/qa-bug/SKILL.md` were absent. The failures were behavioral assertions,
not import, path-fixture, or environment errors.

## GREEN

Focused workflow suite:

```text
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_qa_workflows
Ran 20 tests in 0.006s
OK
```

All PWDEV QA regression tests:

```text
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -p 'test_qa_*.py'
Ran 162 tests in 10.297s
OK
```

Compilation and diff validation:

```text
/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile tests/test_qa_workflows.py plugins/pwdev-qa/scripts/*.py
exit 0

git diff --check
exit 0
```

## Implemented contract

- Regression selection is impact-ranked and records concrete change, impact, risk, criterion,
  prior-defect, selected-case, and excluded-case IDs with explicit rationale and gaps.
- Bug records target/build/environment, reproduction, expected/observed behavior, evidence,
  independent severity/priority rationales, scope, immutable attempts, and retest state.
- Global `PASS` after a defect retest requires a valid terminal passing attempt with current
  evidence, every applicable criterion `PASS`, and no other current in-scope defect.
- Both workflows select installed applicable `qa-specialist-*` guidance without allowing a
  specialist to expand authorization.
- Both bodies preserve objective, constraints, authorization, and limitations; stored commands
  and report export remain inert. Product corrections and effects require separate explicit
  authorization.
- Claude commands only load the shared portable body, forward `$ARGUMENTS` plus repository
  context, and return the body result unchanged.

## Limitations

- These checks validate deterministic Markdown contracts and adapters; they do not constitute
  the real Claude Code, Codex, or Hermes model smoke required later by F05.
- The repository-wide non-QA baseline was not rerun because this task's approved verification
  scope requires the focused suite and all `test_qa_*` tests. The ledger records seven unrelated
  pre-existing full-suite failures.

## Correction round 1

Review source: `.planning/power/features/pwdev-qa/task-19-review.md`.

### Root cause

The original oracle checked broad vocabulary and a partial ordered relation. It did not encode
the full structural invariants already present in the workflow contracts, so semantically invalid
mutations retained enough nearby words to pass.

### Mutation RED evidence

Before changing the oracle, each reviewed mutation was reproduced in isolation and the original
targeted test incorrectly returned `OK`:

- removing `impact ID` from the regression relation;
- allowing arbitrary logical cases/targets and non-linear `supersedes` history;
- copying severity into priority instead of assessing delivery order independently.

After adding the invariant assertions, each mutation failed its targeted test for the intended
reason:

- `drop-impact-id-edge`: failed the exact ordered
  change→impact→risk→criterion/explicit-none→prior-defect/explicit-none→case assertion;
- `allow-cross-target-branched-retest`: failed the stable logical case, unique/increasing attempt,
  same-target, linear-supersedes, no-branch/cycle assertion;
- `couple-priority-to-severity`: failed the independent product-impact versus delivery-order
  rationale assertion.

The new local `PASS` guard initially failed against the unchanged contract because it did not
state absence of pending work explicitly. The smallest contract clarification now requires valid
terminal retest evidence, all applicable criteria `PASS`, no pending work or limitations, and no
other current in-scope defect.

### Correction GREEN

The focused suite returned `Ran 20 tests ... OK` after all mutations were removed and the guard
was clarified. Packaged Python 3.12 discovery for `test_qa_*.py` returned
`Ran 162 tests in 10.685s ... OK`; `py_compile` for the workflow test and plugin scripts exited
zero using an isolated cache, and `git diff --check` exited zero.
