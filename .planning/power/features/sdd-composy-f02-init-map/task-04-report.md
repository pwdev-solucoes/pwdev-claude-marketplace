# F02 Task 04 — Init skill and Claude adapter

## STATUS

PASS

## Scope

Added the portable `sdd-init` skill, Codex `openai.yaml` metadata, and the
thin Claude `/sdd-composy:init` adapter. The skill routes initialization to
Task 03's `scripts/sdd_init.py` `inspect|plan|apply|verify` contract, preserves
exact conflict plan tokens, delegates safety and atomic publication to the
helper, and explicitly excludes secrets and fleet environment files.

Added structural tests for skill discovery, Codex metadata, helper routing,
secret-read boundaries, Claude argument pass-through, and command thinness.
The discovery helper recognizes the intentional `sdd-init` skill → `init`
command naming convention.

## Verification

`python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_runtime` —
45 tests passed.

The new adapter tests were run before implementation and failed on the missing
skill, metadata, and command as expected; they pass after implementation.

No environment, credential, token, private-key, certificate, or fleet
environment files were read.
