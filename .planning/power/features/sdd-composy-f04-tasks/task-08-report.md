# Task 08 report — Sync skill and adapter

Implemented the portable `sdd-sync` skill and Claude/Codex entry points.

## Delivered

- `plugins/sdd-composy/skills/sdd-sync/SKILL.md`
  - routes all work through `sdd_sync.py inspect|plan|apply`;
  - keeps inspection and planning read-only;
  - requires explicit authority and the exact `CONFIRM-SDD-SYNC` token for apply;
  - documents conflict, stale-plan, malformed-input, confinement, and atomic-write guards;
  - remains runtime-neutral and avoids duplicating helper policy.
- `plugins/sdd-composy/skills/sdd-sync/agents/openai.yaml`
  - exposes `$sdd-sync` to Codex.
- `plugins/sdd-composy/commands/sync.md`
  - thin `/sdd-composy:sync` Claude adapter forwarding arguments and context.
- `tests/test_sdd_composy.py`
  - structural coverage for skill discoverability, operation routing, runtime neutrality,
    explicit approval language, and thin adapter boundaries.
- `tests/test_sdd_composy_tasks.py`
  - focused CLI coverage for loading a plan JSON, successful guarded apply, and
    rejection of an invalid token or authority.

## Validation

Failing-first structural run before implementation:

```text
FAILED (failures=1, errors=1)
```

Focused structural test after implementation:

```text
Ran 2 tests in 0.001s

OK
```

Full SDD Composy suite:

```text
Ran 115 tests in 3.665s

OK
```

Diff hygiene:

```text
git diff --check
```

completed with no output/errors.

No commit was created.
