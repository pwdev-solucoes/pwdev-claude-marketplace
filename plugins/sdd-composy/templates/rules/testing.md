# Testing rule

This focused rule is subordinate to the canonical contract in [AGENTS.md](../AGENTS.md)
and is concerned only with verification and evidence.

## Responsibility

- Run the smallest relevant command after a change, then the complete applicable suite
  before claiming completion.
- Prefer deterministic, repository-native tests and preserve fresh output as evidence
  in the applicable report or verification artifact.
- Distinguish a test failure from an environment failure; neither is evidence of
  success.
- Verify the behavior at the boundary it changes, including safety and idempotence
  when initialization or synchronization is involved.
- Do not weaken an assertion, delete a failing test, or infer approval from coverage,
  confidence, or artifact existence.

This rule does not choose architecture or reorder lifecycle gates; those concerns are
owned by `architecture.md`, `workflow.md`, and `AGENTS.md`.

