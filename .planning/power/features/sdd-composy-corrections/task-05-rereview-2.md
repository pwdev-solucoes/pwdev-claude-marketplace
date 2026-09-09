# Task 05 — re-review round 2

Review range: `0b2d6e2..fe571e8`
Date: 2026-09-09
Reviewer mode: independent, read-only apart from this report

## Scope and ruling

The prior two Important findings were rechecked against the updated report and
`review-0b2d6e2..fe571e8.diff`. The prior Compose/teardown Critical remains
`DEFERRED_BY_RULING` to Task 06; `teardown.sh` is outside this correction and the
finding is not counted as fixed here. The prior Minor remains closed and was not
reopened.

## Reproduced checks

### Draft 2020-12 constraint classes

The updated dependency-free validator now follows the used Draft 2020-12 subset:
`$ref`, nested `additionalProperties: false`, strict integer typing that rejects
booleans, regex `pattern`, and conditional `if`/`then`. The adversarial test
fixture supplies one invalid member for each class (nested owner property,
boolean port, bad task-id pattern, relative worktree pattern, and terminal status
without terminal fields). Each is rejected, while the valid fixture is accepted.

Command:

    python3 -m unittest tests.test_sdd_composy_fleet_runner tests.test_sdd_composy -v

Result: **PASS**, 66 tests.

### v1 migration isolation, preservation, and atomicity

The migration regression creates a real independent `git worktree add` member
with the exact legacy branch, refuses ordinary runner execution until explicit
migration, rejects unsafe evidence, and rejects a central-checkout record using
`worktree_path: .` and the root branch. For each terminal state, migration
accepts the registered independent member, binds the canonical worktree, keeps
unknown `x-owner-note` data, validates the v2 result, and changes the member
inode through atomic replacement. The implementation also requires the resolved
member worktree to differ from the repository root and verifies the registered
worktree/branch pair.

## Findings

1. **Draft validation — ADDRESSED.** The requested adversarial constraint
   classes are now rejected and covered by a focused regression.
2. **Real v1 migration — ADDRESSED.** Migration is exercised against an actual
   independent registered worktree, rejects the initiating checkout, preserves
   unknown fields, and demonstrates atomic replacement.
3. **Compose/teardown — DEFERRED_BY_RULING.** Still assigned to Task 06 and not
   reopened here.
4. **Prior Minor — NOT REOPENED.**

## SPEC

**PASS for the authorized Task 05 correction scope.** Both outstanding Important
findings are addressed. The deferred Task 06 contract remains an explicit
acceptance dependency for the overall fleet work.

## QUALITY

**PASS.** Focused runner/schema verification passed 66 tests, including fresh
negative Draft checks and real-worktree migration checks. No additional finding
was identified in the reviewed correction diff.

## REVIEW

**ACCEPTED — 2 ADDRESSED, 1 DEFERRED_BY_RULING, Minor not reopened.** Task 05
may proceed subject to Task 06 independently resolving the deferred
Compose/teardown finding before fleet acceptance.
