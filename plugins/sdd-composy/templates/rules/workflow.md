# Workflow rule

This focused rule is subordinate to the canonical contract in [AGENTS.md](../AGENTS.md)
and is concerned only with lifecycle sequencing and approvals.

## Responsibility

- Follow the canonical lifecycle from `INIT` through `MAP`, product and technical
  artifacts, execution, QA, evidence, review, verification, and `COMPLETE`.
- Require explicit human approval for the gates named by `AGENTS.md`; artifact
  existence or model confidence never substitutes for approval.
- Keep `QUICK` within its five-file limit and escalate before editing when its boundary
  is crossed. Keep `LOOP` bounded and keep `FLEET` limited to independent ready tasks
  in isolated worktrees.
- Return rejected gates to the artifact that owns the decision and reconcile stale
  downstream artifacts before reuse.
- Keep runtime adapters thin: lifecycle meaning and durable state belong to the shared
  artifacts and canonical contract.

This rule does not redefine artifact schemas, safety prohibitions, or test commands;
those remain in `AGENTS.md` and the shared references.

