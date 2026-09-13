# Architecture rule

This focused rule is subordinate to the canonical contract in [AGENTS.md](../AGENTS.md)
and is concerned only with architecture decisions and boundaries.

## Responsibility

- Treat `.planning/sdd-composy/context/codebase.json` and the context documents as
  evidence about the repository, not as architectural intent.
- Record architecture, interfaces, migrations, and boundary changes in the approved
  TECHSPEC or task artifacts before implementation.
- Reuse established modules and conventions identified by `sdd-map`; do not create a
  parallel structure to avoid an existing boundary.
- Escalate when a change requires an architectural decision, migration, destructive
  operation, or scope expansion beyond the approved artifact.

This rule does not define lifecycle gates or test commands; those remain in
`workflow.md`, `AGENTS.md`, and the repository's detected command contract.

