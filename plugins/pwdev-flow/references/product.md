# Product planning contract

Product planning creates a problem-first PRD and decomposes an approved PRD into a traceable roadmap. Do not plan implementation before the product contract is approved.

## PRD

Store `.planning/flow/product/prd.md` with:

1. context and problem statement;
2. target users and jobs;
3. goals with measurable outcomes;
4. non-goals;
5. scope and business rules;
6. user journeys and user stories;
7. functional requirements;
8. non-functional requirements;
9. risks, assumptions, dependencies, and open questions;
10. acceptance and release evidence.

Interview one decision at a time, inspect existing product context, distinguish facts from assumptions, and keep implementation choices out of requirements unless they are genuine constraints.

Present the PRD for explicit approval before roadmap generation.

## Roadmap hierarchy

Decompose approved work as `Phase → Epic → Feature → Task` under `.planning/flow/product/roadmap/`.

- Phase: a delivery boundary with measurable user value.
- Epic: a coherent capability within one phase.
- Feature: an independently demonstrable behavior.
- Task: an implementation-sized unit that later feeds discovery and design.

Every node records its ID, parent, source PRD requirement IDs, objective, acceptance outcome, dependencies, risks, estimate range, and status. Preserve full traceability upward and do not create orphan tasks.

## Gate

Roadmap generation may be performed inline. When the user explicitly requests parallel agent work, a worker may draft the hierarchy, but the primary conversation presents it for approval. Approved roadmap items still pass through feature discovery, design, and planning before execution.
