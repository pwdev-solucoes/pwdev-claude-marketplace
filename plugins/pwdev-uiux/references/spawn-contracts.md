# Spawn Contracts — canonical subagent prompts

Harness rules for EVERY spawn:

1. **Self-contained prompt** — task scope, phase context summary, stack from
   `.planning/ui/stack.json`, and the SKILL.md paths to read (skills are NOT
   auto-loaded). Paths to `.planning/ui/*` artifacts the subagent must read.
2. **Artifacts are the contract** — full output goes to `.planning/ui/...`;
   the reply is ≤10 status lines; the orchestrating command never pastes
   reports back into its context.
3. **Model** — resolve per `references/model-profiles.md` (override keys
   `uiux-<agent>`), pass via the Task tool `model` parameter.
4. **Language** — always include `LANGUAGE: {lang}`.
5. **Parallelism** — independent spawns (a11y-reviewer + ux-critic; design-
   bridge + ux-analyst with Figma) are issued in the SAME message.

Common prompt skeleton (adapt the CAPS blocks per agent):

```
TASK: {exact scope — components/files/domain}
PHASE CONTEXT: {1-5 line summary of prior phases/gates}
STACK: {content or path of .planning/ui/stack.json}
SKILLS — read these files BEFORE working:
{one ${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md path per line}
ARTIFACTS TO READ: {paths in .planning/ui/}
LANGUAGE: {lang}

OUTPUT CONTRACT:
1. {agent-specific outputs — see below}
2. Reply with AT MOST 10 lines: STATUS (COMPLETE|CAVEATS|FAILED|STOPPED:<condition>),
   OUTPUT: <main artifact path>, NOTE: <1 line>.
```

Per-agent outputs:

- **ux-analyst** (`pwdev-uiux:ux-analyst`) — write `.planning/ui/ux-spec.md`
  (Phase 1) or the component mapping section of `figma-spec.md` (Phase 2,
  no-Figma path). Skills: ux-tokens, component-audit.
- **ui-builder** (`pwdev-uiux:ui-builder`) — implement the listed components
  per spec + stack; register each in `.planning/ui/component-log.md`.
  Skills: ux-tokens, component-audit, ui-best-practices, ui-theme-reference
  + every skill in stack.json `skills[]`.
- **design-bridge** (`pwdev-uiux:design-bridge`) — `MODE: READ` (Figma →
  `.planning/ui/figma-spec.md`) or `MODE: WRITE` (code → Figma). Skills:
  figma, ux-tokens. Requires the session-level Figma MCP server
  (/pwdev-uiux:setup-figma); external `/figma:*` skills must be loaded in the
  session per the figma skill's instructions.
- **a11y-reviewer** (`pwdev-uiux:a11y-reviewer`) — append the a11y audit to
  `.planning/ui/review-findings.md`. Skills: accessibility,
  ui-best-practices, ui-theme-reference.
- **ux-critic** (`pwdev-uiux:ux-critic`) — append the UX review to
  `.planning/ui/review-findings.md`. Skills: component-audit, ux-tokens,
  ui-best-practices, ui-theme-reference.
- **ui-scanner** (`pwdev-uiux:ui-scanner`) — write
  `.planning/ui/project-ui-skill.md` + compliance check. Skills: ux-tokens,
  component-audit, ui-best-practices, ui-theme-reference.

On retry after FAILED, append:

```
PREVIOUS ATTEMPT FAILED WITH:
{status note}
Do not repeat the same approach blindly — diagnose first.
```
