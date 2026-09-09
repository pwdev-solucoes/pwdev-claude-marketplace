# Task 02 review — round 1

## Verdict

**REJECTED — rollback can delete pre-existing fleet bookkeeping.**

## Verification

Ran `python3 -m unittest tests.test_sdd_composy_fleet -v` — 12 tests passed.
Ran `git diff --check` — passed.

The lock lifetime fix is correct: `fleet_lock` no longer uses a `RETURN` trap,
and both the launch lock and port allocator explicitly unlock after their critical
sections. The concurrent allocator test passes and returns distinct ports.

## Finding

### HIGH — cleanup does not distinguish invocation-owned state from pre-existing state

`state_created=1` is unconditional after `mkdir -p "$state/members"`. On any later
failure (including an existing branch collision or an existing `runtime.env`),
`cleanup` removes `fleet.json` and deletes every `members/*.json` under the fleet
state directory. This can destroy records from a prior successful/recoverable
launch. The same issue exists for a pre-existing `docker-compose.yml` because
`compose_created` is set only after `cp`, but the code does not refuse/record an
existing destination before overwriting it.

Rollback must snapshot ownership before mutation and remove only files created by
this invocation; pre-existing records, runtime files, and Compose files must remain
untouched. Add a regression test that seeds existing member/fleet metadata, then
forces a post-validation failure and asserts byte-for-byte preservation.

## Positive checks

- Port lock lifetime now protects the allocation critical section.
- Concurrent allocator test passes with distinct slots.
- Invalid/occupied ranges, existing runtime refusal, mode `0600`, Compose absence,
  symlink rejection, and generated-state cleanup are covered and passing.
