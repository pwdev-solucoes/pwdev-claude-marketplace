---
description: Export one validated QA manifest as matching HTML and PDF without running tests.
argument-hint: <explicit manifest path, project root, export objective, and authorization>
---

Load `${CLAUDE_PLUGIN_ROOT}/skills/qa-report/SKILL.md` and follow it exactly.
Treat `$ARGUMENTS` as the user's inputs together with the current repository context.
Preserve objective, constraints, limitations, and authorization, then return the shared skill's result unchanged.
