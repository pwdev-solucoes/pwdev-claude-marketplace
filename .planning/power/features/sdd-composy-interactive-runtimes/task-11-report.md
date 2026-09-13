# Task 11 — Native LOOP approval boundary

## Root cause

The interactive fleet prompt said that native approval prompts belonged to the human operator,
but it did not explicitly distinguish lifecycle approval from the contract/hash authorization,
runtime/UI authorization, directory trust, hook trust, or fleet launch/resume command. A real
Codex session therefore inferred approval from those earlier actions and attempted to mutate
`README.md` before the native LOOP approval gate.

## Change

- Declared every earlier authorization and trust decision insufficient for lifecycle approval.
- Required the runtime to ask the human operator explicitly and wait before any mutation, write,
  edit, potentially mutating test, or lifecycle continuation.
- Prohibited invoking, passing, simulating, or inferring `--human-approved`.
- Required zero mutation when approval is unavailable or times out.
- Restricted pre-approval reads to the already-sanitized named member, task contract, and LOOP
  context.
- Left LOOP creation/binding, isolated-loop behavior, adapters, UI ownership, and recovery
  resources unchanged.

## TDD evidence

The focused regression was observed failing before the production change, passing after it,
failing again when the production fix was temporarily reverted, and passing after restoration.
It reconstructs the generated prompt, verifies exact argv boundaries for Codex, Hermes, and
Claude, rejects `--human-approved` as an argv element, and proves an unrelated sensitive field
is not interpolated.

## Verification

- Focused prompt regressions: 2 passed.
- Fleet suite: 69 passed outside the sandbox restriction required for temporary tmux sockets.
- `bash -n plugins/sdd-composy/scripts/fleet/interactive-run.sh`: passed.
- `git diff --check`: passed.
- Canonical SDD Composy suite on isolated committed code:
  `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — 443 passed in
  272.412s.

No real provider, UI, consumed session, protected file, fleet resource, merge, or retry was
accessed or changed.
