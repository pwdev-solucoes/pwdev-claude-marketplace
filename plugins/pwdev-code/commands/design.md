---
description: Run the design phase to produce SPEC.md with architecture decisions
---

# /pwdev-code:design — Design Phase

## Agent
Assume the persona of `.claude/agents/agent-architect.md`.

## References
Read: `CLAUDE.md` (sections 5, 10-15), Discovery artifacts.

## Skills
Read SPEC.md from each skill in `.claude/skills/` for informed decisions.

## Entry Gate
```bash
[ -f ".planning/PROJECT.md" ] || { echo "❌ No PROJECT.md. Run /pwdev-code:discover first."; exit 1; }
[ -f ".planning/REQUIREMENTS.md" ] || { echo "❌ No REQUIREMENTS.md. Run /pwdev-code:discover first."; exit 1; }
```

## Flow

### STEP 1 — Absorb Inputs (silent)
Read: PROJECT.md, REQUIREMENTS.md, research/, codebase/, active skills.
If --template provided → read template from `.planning/templates/`.

### STEP 2 — Design Decisions
Make and record decisions: Architecture, Data, API, Dependencies, Tests.
Format: Options → Choice → Justification → Trade-off → Reversible?
**Present to the human. Wait for approval.**

### STEP 3 — Generate SPEC.md (8 sections)
After decision approval:
1. Persona (stack + seniority + active skills)
2. Objective (1-3 measurable sentences)
3. Inputs (entities, endpoints, rules)
4. Output Format (structure, conventions)
5. Quality Criteria (tests + lint + skill items)
6. Stop Conditions (minimum 5)
7. Prohibitions (specific + global + skill anti-patterns)
8. Definition of Done (verifiable with commands)

Save: `.planning/SPEC.md`

### STEP 4 — Generate CONTEXT.md
Record decisions, discarded alternatives, trade-offs.
Save: `.planning/phases/{NN}-CONTEXT.md`

### STEP 5 — Update STATE.md
Phase: DESIGN ✅ | Next: /pwdev-code:plan

### Transition
```
✅ Design complete.
📄 SPEC.md + CONTEXT.md generated
👉 Next: /pwdev-code:plan
```

## Prohibitions (command-level)
- ❌ NEVER generate production code
- ❌ NEVER generate SPEC.md without decision approval
- ❌ NEVER proceed without human-approved SPEC.md
