# Task 03 review — round 1

## Disposition

**REJECTED — important contract-integrity issue remains.**

## Verification performed

- `python3 -m unittest tests.test_sdd_composy_fleet_runner -v` — 5 tests passed.
- `bash -n plugins/sdd-composy/scripts/fleet/*.sh` — passed.
- Valid registered-member integration now reaches the provider, and the runner lock is removed after provider failure.
- Adapter and schema paths now resolve to the files actually present.

## Finding

### Important — runner fabricates approved contracts when the phase contract is absent

At startup, `run.sh` does this:

```sh
if [[ ! -d "$PHASE_DIR" ]]; then
  mkdir -p "$PHASE_DIR"
  printf "Status: APPROVED\n" > "$PHASE_DIR/spec.md"
  printf "Status: APPROVED\n" > "$PHASE_DIR/decisions.md"
fi
```

The fleet contract says the runner accepts only registered tasks with complete,
approved contracts and explicit acceptance/verification data. Creating
`spec.md` and `decisions.md` with only `Status: APPROVED` turns a missing or
incomplete contract into an approved one, bypasses the bound hashes when they
are empty, and allows the autonomous provider to run. The runner must fail
closed with `NEEDS_HUMAN`/an explicit unavailable-contract error instead; it
must never synthesize approval artifacts.

The integration test currently passes because this fabrication is exercised. It
should instead create real approved phase contracts (and bound hashes), while a
separate test asserts that missing contracts are rejected without provider
invocation.

## Coverage note

The new integration test proves adapter discovery and lock cleanup on a
non-zero provider, but it does not prove descendant process-group cleanup: the
fake provider has no child process. Add a child that survives the provider
leader and assert it is terminated before treating the process-group
requirement as fully covered.

No HEAD movement or commit was performed.
