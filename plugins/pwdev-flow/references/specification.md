# Central specification contract

Design produces `.planning/flow/phases/<slug>/spec.md`, the authoritative feature contract. Architecture decisions also go to `decisions.md` with decision, rationale, rejected alternatives, consequences, and reversibility.

## Required sections

Use these exact eight sections:

1. **Persona and stack context** — repository stack, required expertise, applicable governance, active skills, and relevant memories.
2. **Objective** — one to three measurable statements describing what must exist when complete.
3. **Inputs and business rules** — entities, data, interfaces, invariants, permissions, failure behavior, and edge cases.
4. **Output format and file boundaries** — public interfaces, file ownership, naming, compatibility, and explicitly allowed scope.
5. **Quality criteria** — test levels, lint or type checks, security, accessibility, observability, performance, and maintainability requirements.
6. **Stop conditions** — concrete situations in which implementation must stop rather than guess.
7. **Prohibitions** — forbidden behavior, out-of-scope changes, secret handling, Git policy, and compatibility constraints.
8. **Definition of done** — verifiable checklist with exact commands or inspections and expected evidence.

## Design procedure

1. Read approved discovery artifacts and current repository governance.
2. Select only relevant active memories and identify contradictions.
3. Inspect existing architecture and prefer compatible patterns over new abstractions.
4. For each consequential choice, compare viable approaches, recommend one, and obtain user approval.
5. Define component boundaries, data flow, failures, migrations, compatibility, and verification.
6. Write the full specification and decisions; scan for ambiguous language and missing evidence.

## Gate

The user approves the specification and architecture decisions before planning. Rejection returns to design. A conflict with approved requirements returns to discovery rather than silently rewriting the requirement.
