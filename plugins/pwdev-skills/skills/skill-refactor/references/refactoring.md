---
okf_version: "0.2"
type: protocol
title: "Portable skill refactoring"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
  updated_at: "2026-09-13T20:30:12Z"
sources:
  - resource: "docs/skill-refactoring-guide.md"
    sha256: "b044b3d3246dca295fb93c8e7da094a541b200c262fdc57ad4077fde0c7c60c5"
    context: "Path in the source repository; this reference is a portable adaptation, not a full copy."
  - resource: "https://claude.com/plugins/skill-creator"
  - resource: "https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra"
verified:
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-13T20:30:12Z"
    scope: "references/refactoring.md"
    source: "relative links resolved from each referencing file; grep: lean/guided defined only in this file; no model names outside sources:"
---

# Refactoring protocol

## Contract and preparation

Record the targets, the expected outcome, the executor and target profiles, and the
checks already known. Reuse information the request already gave. Keep authorized
changes separate from suggestions for other skills or environment rules.

Read `SKILL.md` and only the resources relevant to the flow being changed. Preserve
the observed state of the target files, including uncommitted changes, in a new
directory under an artifact location the project allows or the user chose. Copy only
the regular files the target needs. If the target is installed in a cache, is
read-only, or is reached through a symlink, prepare the candidate in a writable
authorized location and report where it is; do not alter the original.

## Behavior-preserving refactoring

1. Make `description` a capability with concrete conditions of use. Keep every
   legitimate trigger, including phrasings that do not name the skill.
2. Keep in the core the objective, the invariants, and the limits that apply before
   any action. A mandatory rule must not depend on a reference the agent might not
   read. Explain the reason behind guidance that needs judgment.
3. Move domain or tool detail into references with explicit reading conditions.
   Group by flow; avoid fragmentation that multiplies lookups.
4. Consolidate repetition into one source of truth. Preserve the name, resources,
   unknown fields, `paths`, integrations, and any metadata the target runtime owns.
5. Turn repetitive procedures into reusable resources only when that is in scope.
   New scripts need real verification; never create one just to shorten the Markdown.
6. Compare before and after against the requirements and run the relevant commands.
   Fix links, routing, and lost behavior before delivering.

The context limit is guidance, not a reduction target. Do not cut requirements to hit
a line count. Preserve the target's language and leave unrelated content alone.

## Optimization rules

Each rule names the measurement that decides it; a rule without a measurement is an
opinion.

1. **Cost per accepted task, not size.** A shorter skill that causes more lookups,
   retries or corrections loses. Decided by `cost_per_success_usd` with the acceptance
   rate inside the limit fixed beforehand.
2. **Layers are paid at different frequencies** — `description` in every conversation,
   the core on every activation, a reference only under its condition. Optimize in that
   order. Decided by `scripts/tokens.py` per layer and load scenario.
3. **Keep, move, remove.** Authorization limits and mandatory formats stay in the core;
   tool procedures move to a conditional reference; a recurring-error explanation moves to
   the `guided` complement; a repeated rule elects one source; "always read X" becomes a
   concrete condition; adjectives become observable criteria; a rule with no purpose is
   tested by removal.
4. **A profile per model is derived from measurement, never from a name.** A/B `lean`
   against `guided` on the same cases for each (runtime, model); the lower cost per
   accepted task within the quality limit wins. Without a measurement, `guided`. Decided
   by `evals/benchmarks/*/summary.json`.
5. **One change at a time.** Ablate against a fixed baseline: a more specific
   description (fewer wrong triggers / lost legitimate requests), references on demand
   (less accumulated input / an omitted essential instruction), removed repetition (same
   adherence with less context / a forgotten condition), guided complement (less rework /
   latency without gain), explicit completion (fewer premature stops / work beyond scope).
   Then validate the combination. Decided by the delta per component.

Triggering, context, limits, full cost and evidence labels are measured as described in
[the evaluation protocol](evaluation.md).

## Profiles

| Profile | Shared core | Additional support | Evidence that selects it |
| --- | --- | --- | --- |
| `lean` | Outcome, invariants, conditional references, verification, completion | Examples only for genuine ambiguity | Lower cost per accepted task than `guided` for that model, acceptance inside the limit |
| `guided` | Exactly the same requirements and permissions | Short sequence, one worked example, a frequent mistake, a checklist | Default without measurement; or `lean` failed the acceptance limit for that model |

A profile is a starting configuration, not a verified ranking or a permission level.
Model families named in a request are that request's routing only; this protocol
defines no per-model default. For mixed consumers, add a guided reference inside the
target skill when needed and put an explicit loading condition in the core. If the
user asks for one profile, add nothing for the others. Record how each selection was
resolved and which measurement, if any, backed it.

Executor profile `guided` follows this sequence:

- List what must remain true after the change.
- Map every moved or removed passage to the rule that replaces it.
- Edit the description and the core, then adjust the references.
- Check requirements, links, metadata, and positive and negative examples.
- Deliver and classify the evidence actually obtained.

Executor profile `lean` uses the same contract and checks with freedom to order the
steps. No profile grants extra authority.

## Verification and delivery

Validate the runtime entry with the target platform's rules. A validator from another
ecosystem that rejects a legitimate field does not authorize removing it. Check
relative paths from the file that references them, the absence of personal paths, and
that unrelated files are untouched.

Run the applicable existing checks. For objective tasks, prepare two or three
realistic cases with expectations about correct content; for subjective tasks, show
the artifacts to the user with clear criteria. To run or interpret comparisons, read
[the evaluation protocol](evaluation.md).

Preserve candidates and baselines after a failure. Do not run broad restores, and
never declare human approval from silence, from an existing file, or from a model's
note.

Write a short OKF v0.2 report outside the target's core, in the allowed artifact
location: `type`, `generated.by`, `generated.at` with timezone, `lifecycle.status`,
`sources` as a list of objects with `resource`, and `verified` events only for checks
actually performed. Include paths and hashes of regular evidence files confined to the
workspace. Use real data; never fabricate approval events or timestamps.

The report lists targets and baseline, profiles, changes, preserved requirements,
commands and results, models actually run, available measurements, and required next
steps. A revision can be edited and statically validated without a comparison on
every model — say which.

## Agent Skills and OKF

`SKILL.md` uses the runtime's native frontmatter, with provenance under `metadata`.
The narrative files in this folder use OKF v0.2 at the root. Validate each kind with
its own validator and report that boundary; in targets, preserve whatever contract is
already in use.
