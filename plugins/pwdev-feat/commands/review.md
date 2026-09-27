---
description: Create a code review plan for an explicit range — correctness, security, performance, conventions, tests.
argument-hint: "[range, slug or paths, e.g. 'HEAD~3..HEAD' or 'user-crud']"
---

# /pwdev-feat:review

Route this request exclusively to the portable `feat-review` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-review/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
