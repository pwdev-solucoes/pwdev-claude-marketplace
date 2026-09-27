---
description: Create a test plan or test audit — unit, integration, E2E scenarios exportable to Playwright, playwright-cli checks.
argument-hint: "[what to test, e.g. 'UserService' or 'authentication flow']"
---

# /pwdev-feat:test

Route this request exclusively to the portable `feat-test` skill. Read
`${CLAUDE_PLUGIN_ROOT}/skills/feat-test/SKILL.md` and follow it exactly, passing through
`$ARGUMENTS`. Paths `references/`, `scripts/`, `templates/` and `schemas/` in the skill are
relative to `${CLAUDE_PLUGIN_ROOT}`. Do not add workflow steps here.
