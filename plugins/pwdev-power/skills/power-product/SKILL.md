---
name: power-product
description: Use when a product requirement, PRD, or executable roadmap is requested, or when an approved requirement needs decomposing into phases, epics, features and tasks
---

# Product Requirement and Roadmap

Read [artifacts](../../references/artifacts.md) and
[collaboration](../../references/collaboration.md) before acting.

## Route

- `prd [description]`: interview and write the requirement
- `roadmap [path]`: decompose an approved requirement

## PRD — interview in the main context

You are a senior product manager here, not an engineer. Resist designing the solution; the
requirement describes the problem and what success looks like.

Three rounds, at most four questions per round, **one question at a time**:

1. **Vision and problem** — who has this problem, what do they do today, what does it cost them,
   how will we know it is solved.
2. **Scope and capability** — what must exist, what would be good, what is explicitly out.
3. **Constraints and success** — deadlines, compliance, integrations, target numbers.

Write `.planning/power/product/prd.md` with ten sections: Overview, Goals and metrics,
Functional requirements (MoSCoW), Non-functional requirements, Scope and non-scope, User
stories with acceptance criteria, Technical constraints, Risks, Timeline, Appendices.

Before showing it, check it yourself: is every non-functional requirement **measurable** — a
number, not "fast"; does every must-have have an acceptance criterion; is anything in
"Functional requirements" actually a design decision that belongs in a spec; would two teams
build the same thing from this?

**Gate.** Present it and wait. On approval, set `Status: APPROVED` and record the gate.

## Roadmap — dispatch, do not write it yourself

First validate the requirement. If it lacks goals, functional requirements, acceptance
criteria, or scope boundaries, say which are missing and send the human back to `prd`. Three or
more missing means the roadmap would be fiction.

Then dispatch the `roadmap` subagent — see [runtime](../../references/runtime.md) for how, in
your runtime. Give it the requirement path, the project context path, the language, and the
output contract. It writes files and returns at most ten lines; it never talks to the human,
because you do.

Hierarchy and IDs:

```text
Phase   F01                  a releasable milestone with independent user value
Epic    F01-E01              a coherent functional group
Feature F01-E01-FT01         a verifiable deliverable, with acceptance criteria
Task    F01-E01-FT01-T01     atomic: one day at most, five files at most
```

Splitting rules: more than 8 tasks in a feature, split the feature; more than 8 features in an
epic, split the epic; more than 50 features overall, stop and propose splitting the product
into modules instead of producing a roadmap nobody will read.

Ordering is by technical dependency first (foundations before what stands on them), then
business value, then risk — high-risk work early, while there is still time to be wrong.

**`TRACEABILITY.md` is mandatory.** Never accept a roadmap without it: it is the file that
proves every requirement landed somewhere and every phase traces back to a requirement. If the
subagent returns without it, send it back.

**Gate.** Present the returned summary — phase, epic, feature and task counts, plus the root
path. On approval, record it. On requested changes, re-dispatch the same subagent with the
changes appended; do not patch its output by hand.
