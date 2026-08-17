# Discovery contract

Discovery turns a feature idea into approved requirements without choosing implementation prematurely.

## Inputs

- user problem or feature description;
- applicable repository instructions;
- current product and project context;
- relevant active memories;
- read-only inspection of the existing stack and behavior.

## Interview

Ask one focused question at a time. Resolve, at minimum:

1. user or actor and the problem being solved;
2. measurable outcome;
3. in-scope and out-of-scope behavior;
4. business rules and failure cases;
5. affected interfaces and data;
6. compatibility, security, performance, and accessibility constraints;
7. acceptance evidence.

Do not ask for information that repository inspection can answer. When answers conflict, name the conflict and request a decision instead of merging incompatible assumptions.

## Research

Inspect the codebase before external research. Record observed stack, existing patterns, relevant dependencies, domain vocabulary, and concrete pitfalls. Browse current primary sources only when a version, standard, or external system may have changed.

Research may run concurrently with the interview only when the user explicitly requested parallel agent work. Research remains read-only and never makes architecture decisions.

## Outputs

Write under `.planning/flow/context/` when artifact persistence is authorized:

- `project.md` — repository purpose, architecture, conventions, commands, boundaries;
- `requirements.md` — problem, actors, scope, rules, acceptance criteria, open questions;
- `domain.md` — vocabulary and domain invariants;
- `stack.md` — observed technologies and versions;
- `pitfalls.md` — evidence-backed risks and failure modes.

## Gate

Present a concise requirements summary and unresolved questions. Set the discovery gate to `APPROVED` only after the user accepts the requirements. An unresolved material question yields `BLOCKED`; design must not start from guessed requirements.
