---
name: power-brainstorm
description: Use before any creative work - creating a feature, building a component, adding functionality, or changing behavior - to explore intent and design before implementation
---

# Brainstorm Before Building

Read [collaboration](../../references/collaboration.md) and
[artifacts](../../references/artifacts.md) before acting.

## Step 1 — Classify, out loud, before the first question

Say which path this is and why, in one sentence, before you ask anything. The classification
determines how much process follows, so hiding it hides the decision.

| Path | What it is | Where it ends |
|---|---|---|
| **Spike** | A feasibility question. You do not know if something is possible. | A recommendation. Any code is labelled throwaway. |
| **Bounded** | A well-scoped change to a flow that **already exists in this repository**. | Agreement in chat. No spec file, no plan. |
| **Architectural** | New systems, new subsystems, interface changes, anything you cannot fully picture yet. | An approved `spec.md`, then `power-plan`. |

**Bounded means you can read the flow you are about to change.** Understanding what kind of
application it is does not make a change bounded.

**The ratchet.** When torn between two paths, take the heavier one. Hidden complexity found
mid-task moves you up a path; nothing ever moves you down. A bounded change that turns out to
need a new interface becomes architectural at that moment, and you say so.

## Spike

State the question and a two-or-three-sentence probe plan. Get a nod. Investigate the cheapest
way that actually answers it. Report what you found and what you recommend. Say explicitly that
any code written is throwaway.

## Bounded

Ask what you need, one question at a time. Read the existing flow. Present a short design **in
the conversation** — no file. Then **stop**. Implement only after an explicit yes.

## Architectural

1. Explore the context: read the code the change touches, the tests around it, the
   conventions it must match.
2. Ask questions **one at a time**. A numbered list of six gets answered like a form.
3. Present two or three approaches with real trade-offs and a recommendation. "It depends" is
   not a recommendation.
4. Walk the design section by section, taking approval per section, so a disagreement costs one
   section rather than the whole thing.
5. Write `.planning/power/features/<slug>/spec.md`:

   ```markdown
   # <Feature> — Design
   Status: DRAFT
   Source: <requirement or conversation>
   Updated: <ISO date>

   ## Problem
   ## Approach
   ## Decisions
   ## Interfaces
   ## Constraints
   ## Out of scope
   ## Acceptance criteria
   ## Risks
   ```

   Every decision gets Decision / Options / Choice / Why / Trade-off / Reversible. Constraints
   carry **exact values** — timeouts, limits, formats, names — because the plan will copy them
   verbatim and an implementer will only ever see the copy.

6. Self-review the spec before showing it: does it cover the whole problem; does it contain any
   placeholder or "TBD"; is it internally consistent; is anything ambiguous enough that two
   engineers would build different things?
7. **Gate.** Present the spec and wait. On approval, set exactly one `Status: APPROVED` field
   and record the gate in `state.md`.

## The only exit

On the architectural path, the single next skill is `power-plan`. Not an implementation skill,
not a UI skill, not "let me just start the first file". If you find yourself reaching for a
framework, you have skipped the gate.
