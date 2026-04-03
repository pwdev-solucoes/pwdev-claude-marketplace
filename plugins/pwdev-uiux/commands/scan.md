---
description: >
  Scans the existing UI of the project and generates a contextual skill in
  .planning/ui/project-ui-skill.md. Use before starting development
  on an existing project to ensure new components are consistent.
argument-hint: "[optional URL or route, e.g.: http://localhost:3000/dashboard]"
---

# /pwdev-uiux:scan — Scan Project UI

**Optional argument**: $ARGUMENTS

## What this command does

Activates the `ui-scanner` agent to analyze the current project and generate
`.planning/ui/project-ui-skill.md` — a contextual skill that serves
as a reference for the `ui-builder` to build components consistent
with what already exists in the project.

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## Pre-check

```bash
# Read stack config to determine expected framework
cat .planning/ui/stack.json 2>/dev/null || echo "NO_STACK"

# Confirm this is a frontend project with a package.json
ls package.json && cat package.json | python3 -c "
import json, sys
p = json.load(sys.stdin)
deps = {**p.get('dependencies',{}), **p.get('devDependencies',{})}
frameworks = ['vue', 'nuxt', 'react', 'next', 'svelte', '@angular/core']
found = [f for f in frameworks if f in deps]
print('Frontend project:', bool(found), '— frameworks:', ', '.join(found) if found else 'none detected')
"
```

If no frontend framework detected and no stack.json: inform and suggest running `/pwdev-uiux:stack` first.

## Determine analysis mode

**If argument contains URL** (http://localhost or https://):
→ Visual + code analysis

**If argument is `--visual-only`**:
→ Visual analysis only via browser

**If argument is `--code-only`** or no argument:
→ Code analysis only

**If no argument** (default mode):
→ Code analysis + browser attempt on localhost:3000 and localhost:5173

## Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolution order: (1) `model_overrides[agent-name]` → (2) profile lookup → (3) agent frontmatter `model:` default.
Profiles — **performance**: opus for all except reviewer/scanner (sonnet). **balanced**: opus for orchestrator, sonnet for planner/executor/builder/interviewer/reviewer/researcher, haiku for scanner. **economy**: sonnet for most, haiku for reviewer/scanner.
When spawning the agent, pass the resolved model via the `model` parameter.

## Activate ui-scanner

Spawn `ui-scanner` agent with:
```
Task: Analyze the current project's UI and generate .planning/ui/project-ui-skill.md

Mode: [determined above]
Analysis URL: [ARGUMENTS or default localhost]

Execute all protocol analysis steps:
1. Structure and stack inventory
2. Component analysis (shadcn-vue + product)
3. CSS token and tailwind.config extraction
4. Visual analysis (if URL available)
5. Best practices compliance check (using ui-best-practices skill)
6. Generate project-ui-skill.md (including compliance report section)

The ui-scanner agent has ui-best-practices and ui-theme-reference declared as skills
in its frontmatter — they are loaded automatically.

Prioritize: most recurring patterns, most used tokens, most complex components.
Document inconsistencies as observations — not judgments.
The compliance report should flag P0 violations as issues and P1 as recommendations.
```

## Final report

After `ui-scanner` completion, present summary:

```
✅ /pwdev-uiux:scan completed

📦 Stack
  [Framework] x.x | [Component Library] | Tailwind x.x
  Forms: [library] | TypeScript: [yes/no]

📁 Components
  Library components installed: N
  Product components: N files
  Composables/hooks: N files

🎨 Tokens
  Custom CSS tokens: N found
  Additional colors: [short list]

⚙️ Identified patterns
  Component style: [SFC script setup / TSX / Options API / etc.]
  Forms: [vee-validate / react-hook-form / manual / etc.]
  Organization: [by feature / by type]

📋 Best Practices Compliance
  P0 rules: N/N passed [✅ / ⚠️ N violations]
  P1 rules: N/N passed
  Top issues: [brief list of most impactful violations]

⚠️ Inconsistencies
  [list of divergences found]

📄 Skill saved at: .planning/ui/project-ui-skill.md
   Valid for this project. Update with /pwdev-uiux:scan after significant changes.

→ Next step: /pwdev-uiux:start "task description"
  [If P0 violations found] → Fix P0 issues first, then /pwdev-uiux:scan again
```

## Notes

- Run `/pwdev-uiux:scan` whenever the project has significant structural changes
- The generated skill is stored in `.planning/ui/` and is automatically read by the `ui-builder`
- For new projects (without components), the skill will be a minimal template
- Add `.planning/ui/project-ui-skill.md` to `.gitignore` or commit as living documentation
