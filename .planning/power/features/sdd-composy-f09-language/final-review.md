# F09 final integrated review — language-aware artifacts

## Scope

Read-only integrated review of the F09 specification, plan, task reports and
reviews, implementation diff, tests, documentation, and marketplace compatibility.

## Contract verification

- `/sdd-composy:init` is the only entry point that returns language choices when
  no preference exists; it returns `pt-BR` and `en-US` without writing artifacts.
- Explicit language selection is validated and persisted atomically under the
  confined `.planning/sdd-composy/config.json` path.
- Invalid language values return `invalid_language` without mutating existing
  configuration or generating artifacts.
- Downstream consumers do not prompt. Before initialization they return
  `{"status":"not_initialized","next_action":"run_init"}`; after initialization
  they consume the persisted language.
- Consumer-side explicit resolution is read-only and cannot overwrite the
  persisted workspace preference.
- Human-facing artifact prose is routable to `pt-BR` or `en-US`; schemas, IDs,
  keys, filenames, lifecycle values, and command names remain English.
- Claude Code and Codex documentation expose the same portable contract.
- Existing SDD Composy runtime callers and marketplace registrations remain
  compatible.

## Verification

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -q
Ran 279 tests in 11.423s
OK

python3 -m unittest discover -s tests -p '*marketplace*.py' -q
Ran 8 tests in 0.018s
OK

git diff --check
passed
```

## Disposition

SPEC: APPROVED

QUALITY: APPROVED

No critical, important, or unresolved correctness findings remain. F09 is ready
to proceed to the project finish/commit step.
