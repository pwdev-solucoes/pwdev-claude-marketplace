# F02 Task 03 — Review

## SPEC

PASS with a verification caveat. The helper is repository-bound, renders only
the approved templates, refuses destination symlinks and known path conflicts,
creates `.claude -> .agents` only after preflight, records the OKF actor/index,
preserves existing files, and uses same-directory temporary files plus a hard
link for no-overwrite publication. The plan digest is stable across clock
changes because it hashes the action/conflict set rather than generated content,
so an exact token emitted by `plan` remains usable later.

## QUALITY

CHANGES_REQUESTED. `python3 -m unittest tests.test_sdd_composy_runtime` passes
all 11 tests, but the runtime contract is under-tested and `verify` accepts a
malformed index actor declaration. A direct temporary-repository check produced
`ok: true` for an index containing `notby: human:test`; the implementation uses
`f"by: {actor}" in text` rather than parsing frontmatter and checking the exact
`generated.by`/actor field. `verify` also checks only one of the four rules and
does not verify that `.claude` is the required relative symlink. These gaps can
report a repository as initialized when its governance contract is incomplete
or actor provenance is invalid.

The tests also do not exercise a destination-directory conflict (the current
“directory conflict” case is only the `.agents` compatibility directory), a
successful apply using a saved conflict plan token after the timestamp changes,
parent-symlink rejection, or failure/cleanup behavior after a mid-apply write
error.

## FINDINGS

### P1 — `verify` can approve malformed actor provenance

`plugins/sdd-composy/scripts/sdd_init.py:238-242` determines `index_ok` by
substring search. An index containing `notby: human:test` (or an unrelated body
line containing `by: human:test`) passes verification even though it does not
declare the required OKF actor metadata. The command also requires only
`00-sdd-composy.md`, so missing or malformed `architecture.md`, `testing.md`, or
`workflow.md` is not detected.

Parse the reserved index frontmatter and require exact `type: Index`,
`okf_version: "0.2"`, and `generated.by == actor` (plus a valid generated
timestamp if that is part of the OKF contract). Verify all four installed rule
files and that `.claude` is a non-dangling symlink whose target is exactly
`.agents`. Add negative tests for malformed actor fields, missing rules, and an
incorrect `.claude` target.

### P2 — Runtime safety claims lack regression coverage

The implementation has the intended conservative primitives, but the focused
tests do not protect several stated acceptance criteria: a real destination
directory conflict, saved-token application after a clock tick, unsafe symlink
parents, and partial-write cleanup on an injected publication failure. Add
temporary-repository tests for these cases so later changes cannot silently
weaken repository-boundary, token, or atomic-publication behavior.

## REVIEW

`CHANGES_REQUESTED`

The clean-init, idempotence, conflict, and unsafe-destination scenarios are
covered and pass. Do not treat Task 03 as fully approved until `verify` enforces
the exact OKF/actor contract and the missing safety regressions are covered.

HEAD was not moved and no commit was created.
