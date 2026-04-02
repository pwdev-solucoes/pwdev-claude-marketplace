---
description: Run the design phase to produce spec.md with architecture decisions
---

# /pwdev-code:design — Design Phase

## Agent
Assume the persona of `.claude/agents/agent-architect.md`.

### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## References
Read: `CLAUDE.md` (sections 5, 10-15), Discovery artifacts.

## Skills
Read spec.md from each skill in `.claude/skills/` for informed decisions.

## Entry Gate
```bash
[ -f ".planning/context/project.md" ] || { echo "❌ No project.md. Run /pwdev-code:discover first."; exit 1; }
[ -f ".planning/context/requirements.md" ] || { echo "❌ No requirements.md. Run /pwdev-code:discover first."; exit 1; }
```

## Flow

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Absorb Inputs (silent)
Read: context/project.md, context/requirements.md, context/, active skills.
If --template provided → read template from `.planning/templates/`.

### STEP 2 — Determine Phase Slug
Ask for or derive the phase slug from the feature description (e.g., `user-auth`, `payment-integration`).
The slug must be lowercase, hyphen-separated, descriptive.

### STEP 3 — Create Phase Folder
```bash
PHASE_SLUG="{phase-slug}"
mkdir -p ".planning/phases/${PHASE_SLUG}/{plans,execution,review,verify}"
```

### STEP 4 — Design Decisions
Make and record decisions: Architecture, Data, API, Dependencies, Tests.
Format: Options → Choice → Justification → Trade-off → Reversible?
**Present to the human. Wait for approval.**

### STEP 5 — Generate spec.md (8 sections)
After decision approval:
1. Persona (stack + seniority + active skills)
2. Objective (1-3 measurable sentences)
3. Inputs (entities, endpoints, rules)
4. Output Format (structure, conventions)
5. Quality Criteria (tests + lint + skill items)
6. Stop Conditions (minimum 5)
7. Prohibitions (specific + global + skill anti-patterns)
8. Definition of Done (verifiable with commands)

Save: `.planning/phases/{phase-slug}/spec.md`

### STEP 6 — Generate decisions.md
Record decisions, discarded alternatives, trade-offs.
Save: `.planning/phases/{phase-slug}/decisions.md`

### STEP 7 — Update state.md
Phase: DESIGN ✅ | Next: /pwdev-code:plan

### Transition
```
✅ Design complete.
📄 spec.md + decisions.md generated in .planning/phases/{phase-slug}/
👉 Next: /pwdev-code:plan
```

## Prohibitions (command-level)
- ❌ NEVER generate production code
- ❌ NEVER generate spec.md without decision approval
- ❌ NEVER proceed without human-approved spec.md
