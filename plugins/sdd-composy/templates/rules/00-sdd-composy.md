# SDD Composy rule index

This rule set is subordinate to the canonical contract in [AGENTS.md](../AGENTS.md).
Read that file first; it owns repository-wide governance, safety, artifacts, gates,
and commands.

## Discovery and precedence

- This file is the entry point for the rules installed in `.agents/rules/`.
- The concern-specific files are `architecture.md`, `testing.md`, and `workflow.md`.
- When a rule conflicts with `AGENTS.md`, follow `AGENTS.md` and report the conflict.
- Apply only the concern-specific rule relevant to the current change; do not copy its
  policy into another rule or create a runtime-specific variant.

## Shared boundary

## Responsibility

This rule's responsibility is rule discovery and precedence across the focused files.
Rules describe how to interpret the canonical contract. They do not authorize scope
expansion, replace human approvals, or turn an observed map finding into architecture.
