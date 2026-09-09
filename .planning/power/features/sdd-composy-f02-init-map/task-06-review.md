# F02 Task 06 — Review

## SPEC

FAIL. The portable `$sdd-map` skill is discoverable, records the required
observation-only/source-commit/staleness contract, documents all five context
outputs, forbids sensitive-path inspection and manifest execution, and routes
fresh evidence through PRD → STORIES → TECHSPEC → TASKS while returning stale
evidence to MAP. The Claude `/sdd-composy:map` command is a thin pass-through to
that skill and the Codex metadata is present.

One output-path boundary is not enforced consistently by the consumed helper:
the skill says an optional output directory “must remain inside the
repository”, but `build_map()` accepts an external output directory in the
read-only path. Repository-bound validation exists in `write_map()` only. With
an external directory containing `codebase.json`, the read-only path instead
calls `_safe_relative()` and raises `ValueError`; with no prior map it can
return a successful inventory despite the contract. The adapter/skill should
ensure the same repository-bound validation before invoking either mode (and
the helper should reject it consistently).

## QUALITY

PASS for the delivered adapter surface. The structural and runtime suites are
green:

```text
python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_runtime
Ran 52 tests in 1.065s — OK
```

Manual inspection confirms the skill delegates traversal, exclusion,
serialization, and publication to `sdd_map.py`; does not embed runtime-specific
tools or scanner logic; states commands are evidence only; and preserves
staleness and observation-only semantics. The helper invocation against the
worktree emitted `schema: sdd-composy.codebase`, matching source/mapped commit,
and `observation_only: true` without writing repository files. No HEAD move or
commit was performed.

## FINDINGS

### [P1] Read-only `--output-dir` is not repository-bound

`build_map(root, output_dir)` resolves the supplied directory but does not
validate it is beneath `root` before inspecting the prior map. `write_map()`
does enforce `context.relative_to(root.resolve())`, so the boundary differs
between the documented read-only scan and publication. Add one shared
validation path and a focused fixture covering an external output directory in
both modes; the read-only mode must fail cleanly without inspecting outside
the repository.

## REVIEW

`CHANGES_REQUIRED`

HEAD was not moved and no commit was created.
