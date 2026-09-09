---
type: TASK_REVIEW
okf_version: "0.2"
status: CHANGES_REQUESTED
generated_by: /root/f05_task08_review
verified_by: /root/f05_task08_review
source: task-08-brief.md
---

# Task 08 — review

## Verification

Command: `python3 -m unittest tests.test_sdd_composy_quality tests.test_sdd_composy_tasks`

Result: `Ran 68 tests ... OK`.

The existing tests cover the documented skill/adapter, source immutability, basic manifest
validation, HTML escaping, confinement, optional-PDF failure, and the guarded lifecycle
transition. The task is not approved because the runtime contract is incomplete.

## Findings

### Important — the advertised build/export CLI is not implemented

`commands/evidence.md` advertises `[build|verify|export]`, and `SKILL.md` routes all three
operations through `sdd_evidence.py`, but `sdd_evidence.py:main()` registers only the
`verify` subcommand. A user invoking the required build or export route receives an argparse
error, so the produced skill is not operational end-to-end. Add thin CLI handlers for
`build`, `verify`, and `export` (including the explicit PDF behavior), with confined input
and output paths and deterministic JSON/result exit codes. Add tests that exercise the CLI
routes rather than only calling Python functions.

### Important — generated manifests do not satisfy the published schema

`schemas/evidence-manifest.schema.json` requires `generated_at`, but `build()` neither
requires nor supplies it and `_validate()` does not check it. Consequently a manifest built
by the new skill can fail its own schema contract. Define the timestamp contract (stable
RFC3339/UTC generation or an explicit caller-supplied value), validate it, and test the
result against the schema/required fields.

### Minor — discovery is documentation-only

The skill says discovery finds existing evidence, but there is no discover operation or
helper; only the rebuild function exists. This can be acceptable if discovery is intentionally
performed by the caller, but the skill/command should state the exact discovery behavior or
provide a read-only discovery route so the advertised workflow is unambiguous.

## Disposition

CHANGES_REQUESTED. Re-review after the CLI and schema contract are implemented and covered by
fresh tests. No lifecycle guard bypass was observed in `sdd_tasks.py`.
