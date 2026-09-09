---
type: CODE_REVIEW
okf_version: "0.2"
title: "{{PRODUCT_NAME}} code review"
sources:
  - resource: "{{BASE_REF}}"
  - resource: "{{TARGET_REF}}"
  - resource: "tasks/prd-{{SLUG}}/techspec.md"
  - resource: "tasks/prd-{{SLUG}}/tasks.md"
generated:
  by: "{{REVIEW_ACTOR}}"
  at: "{{GENERATED_AT}}"
verified: []
lifecycle:
  status: DRAFT
human_approval: PENDING
transition: verify_required
---

# {{PRODUCT_NAME}} — Code Review

## Scope

- Base ref: `{{BASE_REF}}`
- Target ref: `{{TARGET_REF}}`
- `base_ref: {{BASE_REF}}`
- `target_ref: {{TARGET_REF}}`
- Explicit diff scope: `{{DIFF_SCOPE}}`
- Changed paths: `{{CHANGED_PATHS}}`
- `changed_paths: {{CHANGED_PATHS}}`
- Scope status: `PENDING`

The review must compare only the declared base and target and must reject an
ambiguous, expanded, or unapproved diff scope.

## Approved contracts and rules

| Contract or rule | Source / rule citation | Review result | Evidence |
|---|---|---|---|
| Approved requirements | `{{REQUIREMENTS_SOURCE}}` | PENDING | `{{EVIDENCE}}` |
| Approved stories / acceptance criteria | `{{STORIES_SOURCE}}` | PENDING | `{{EVIDENCE}}` |
| Approved architecture / TechSpec | `{{TECHSPEC_SOURCE}}` | PENDING | `{{EVIDENCE}}` |
| Project rule | `{{RULE_CITATION}}` | PENDING | `{{EVIDENCE}}` |

`rule_citation: {{RULE_CITATION}}`

Every finding must cite the contract, project rule, or requirement it violates;
unsupported opinions are not blockers.

## Findings

| finding_id | severity | File / line | Rule citation | Description | Evidence | Blocker |
|---|---|---|---|---|---|---|
| CR-001 | PENDING | `{{PATH}}` | `{{RULE_CITATION}}` | `{{DESCRIPTION}}` | `{{EVIDENCE}}` | PENDING |

Severity is one of `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, or `INFO`. A blocker is
any issue that violates an approved contract, prevents required verification,
or leaves the declared scope unverifiable.

## Verification commands

| Command | Environment | Exit code | Result | Evidence |
|---|---|---:|---|---|
| `{{COMMAND}}` | `{{ENVIRONMENT}}` | {{EXIT_CODE}} | PENDING | `{{EVIDENCE}}` |

`exit_code: {{EXIT_CODE}}`

Record the exact command, environment, exit code, and confined evidence path.
Do not infer a pass from command availability or artifact existence.

## Skill conformity and no-silent-fix policy

- Skill used: `{{SKILL_NAME}}`
- Portable skill conformity: `PENDING`
- Runtime adapter conformity: `PENDING`
- No-silent-fix check: `PENDING`
- Unapproved modifications discovered: `{{UNAPPROVED_CHANGES}}`

Review does not edit source, contracts, evidence, or findings to make a check
pass. Any correction requires an explicit follow-up change and a new review.
Unresolved findings and unapproved changes remain visible; they may not be
silently fixed or omitted.

## Gate and next action

Set `lifecycle.status: APPROVED`, `human_approval: APPROVED`, and append a
matching verification event; human approval is explicit and required. Do so
only after the exact scope, approved contracts,
findings, commands, skill conformity, and no-silent-fix check are verified.
The permitted next transition is `verify_required`.

Any blocker, missing rule citation, missing command evidence, scope ambiguity,
skill non-conformity, or unapproved change sets `lifecycle.status: REJECTED`,
records a sanitized blocker and `next_action`, and prevents `verify_required`.
