# F04 Task 05 — Review

## SPEC

FAIL. The portable skill and Claude command are present, runtime-neutral, and
the adapter is thin. The documented operation surface is not implemented in
full: `SKILL.md` promises a read-only `verify` operation (routing to the
helper when available, or performing equivalent validation), but
`scripts/sdd_tasks.py` has no `verify` parser or implementation. The CLI
therefore rejects the operation and the skill has no equivalent gate-check
path. The implemented `list`, `next`, and `show` paths are read-only, while
`import` and lifecycle operations route through the shared helper and its
atomic writer.

## QUALITY

PASS with a coverage gap. Structural and task suites pass:
`python3 -m unittest tests/test_sdd_composy.py tests/test_sdd_composy_tasks.py`
(59 tests). They cover discoverability, thin routing, runtime neutrality,
stable IDs, dependency/lifecycle guards, evidence, confinement, unknown-field
preservation, and atomic replacement. They do not exercise the promised
`verify` route end-to-end, nor assert that a command invocation cannot mutate
state without the skill-level approval gate.

## FINDINGS

1. **[BLOCKER] The documented `verify` operation is missing.** Add a
   read-only `verify <state>` implementation to `sdd_tasks.py` (or remove the
   operation from the skill and contract). It must inspect fresh tests, QA,
   review, verification, and trace evidence and report whether completion is
   permitted without changing the projection. Add CLI and negative/positive
   tests.
2. **[MAJOR] No integration test proves the approval boundary.** The skill
   instructs the agent to request explicit human approval immediately before
   `start`, `block`, and `transition`, but the route tests only inspect text.
   Add a contract-level test or documented invocation protocol demonstrating
   that read-only operations are callable without approval and mutations are
   gated by explicit approval rather than inferred from metadata.

## REVIEW

`REJECTED`

The adapter and most task contracts are sound and all focused tests pass, but
the advertised operation surface is incomplete because `verify` cannot run.
No HEAD movement or commit was performed.
