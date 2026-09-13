# Task 10 — Protected-content boundary for interactive fleet runtimes

## Root cause

`plugins/sdd-composy/scripts/fleet/interactive-run.sh` validated canonical task-contract
filenames before dispatch, but its provider-facing prompt stated only lifecycle approval and
evidence rules. It did not explicitly prohibit an interactive runtime from discovering or
reading `runtime.env`, `.env*`, credentials, tokens, secrets, private keys, certificates, or
other protected environment files. The real `hermes:tmux` observation exposed that missing
instruction boundary before native human approval.

## Change

- Added an explicit provider-facing prohibition against discovering, locating, opening,
  reading, printing, copying, or inspecting protected content.
- Restricted the runtime to the already-sanitized fleet member, task contract, and LOOP
  context supplied by the launcher.
- Required the runtime to stop and request human direction if protected content appears
  necessary.
- Kept isolated `sdd-loop`, all `loop-engine-*` scripts, adapter command vectors, prompt-file
  creation/cleanup, UI ownership, and recovery resources unchanged.

## TDD evidence

The focused regression test was observed failing before the production change, passing after
the change, failing again when the fix was temporarily reverted, and passing after restoration.
It reconstructs the exact generated prompt, proves an unrecognized preflight sentinel is not
interpolated, and verifies the same protected-content boundary reaches the Codex, Hermes, and
Claude interactive adapter command boundaries before any provider execution.

## Verification

- Focused regression:
  `python3 -m unittest tests.test_sdd_composy_fleet.FleetLaunchTest.test_interactive_prompt_delivers_exact_protected_content_boundary_to_every_adapter`
  — 1 passed.
- Fleet suite: `python3 -m unittest tests.test_sdd_composy_fleet` — 68 passed. The first
  sandboxed run was blocked only because tmux could not create its temporary socket; the
  identical suite passed outside that sandbox restriction.
- Canonical full suite:
  `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 442 passed in 200.236s
  on the clean committed head during independent review.

No provider, cmux workspace, tmux session, real fleet run, retry, fallback, protected file,
`--human-approved`, teardown, merge, or preserved recovery resource was accessed or changed.
