---
name: sdd-review
description: Perform an independent, traceable code review for an SDD Composy task.
metadata:
  version: 0.1.0
---

# SDD Review

This portable skill consumes an explicit base and target diff scope, approved
requirements/stories/architecture, task evidence, and project rules. Render
`templates/codereview.md` and record findings with stable IDs, severity,
 file/line, evidence, and direct rule citations or contract citations.

Read `references/quality.md` for the shared quality, evidence, and gate
semantics before reviewing.

## Procedure

1. Validate that the declared base, target, and changed paths are explicit and
   confined. Stop on an ambiguous or expanded diff scope.
2. Read only approved contracts, current task evidence, and applicable project
   rules. Do not change those artifacts or infer approval from their existence.
3. Run and record exact verification commands, environment, exit codes, and
   confined evidence paths.
4. Check skill conformity and runtime adapter conformity, including this
   portable skill's boundaries.
5. Record every finding and its severity (`BLOCKER`, `HIGH`, `MEDIUM`, `LOW`,
   or `INFO`) with a rule citation. Do not silently fix, hide, or rewrite a
   finding; an unapproved change requires a new review.
6. Produce an OKF v0.2 `CODE_REVIEW` report. A complete human-approved report
   transitions to `verify_required`; any blocker, missing evidence, scope
   ambiguity, contract violation, or non-conformity transitions to `rejected`.

## Output

Return the report path, exact base/target scope, approved contracts consumed,
findings and severities, cited rules, commands and exit codes, skill conformity,
blocker status, no-silent-fix result, lifecycle status, and permitted next
transition. Keep generation and verification actors separate.

## Boundaries

Do not edit source, requirements, stories, architecture, task evidence, or the
review to make checks pass. Do not commit. Do not read or expose secrets. Do
not stop user-owned services. Runtime adapters only route to this skill and
must pass through its result unchanged.
