---
description: Create, list, or audit skills — domain knowledge packs that agents use for quality output
argument-hint: "[create <domain> | list | audit]"
---

# /pwdev-code:skill — Skill Management

## Role
Utility agent that creates, lists, and audits skills — the domain knowledge packs that agents consult during execution.

## Input
$ARGUMENTS: subcommand + optional arguments.
- `create backend` → guided wizard to create a backend skill
- `create frontend` → guided wizard to create a frontend skill
- `create <domain>` → guided wizard for any custom domain
- `list` → list installed skills with status
- `audit` → check if skills are being used and are up-to-date
- empty → show interactive menu

## Procedure

### STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

### STEP 1 — Route Subcommand

Parse $ARGUMENTS:

- **`create <domain>`** → go to STEP 2
- **`list`** → go to STEP 3
- **`audit`** → go to STEP 4
- **empty** → present menu:

  **PT-BR:**
  ```
  Gerenciamento de Skills

  1. create   — Criar uma nova skill (backend, frontend ou custom)
  2. list     — Listar skills instaladas
  3. audit    — Verificar uso e atualidade das skills

  Escolha (1-3):
  ```

  **EN:**
  ```
  Skill Management

  1. create   — Create a new skill (backend, frontend, or custom)
  2. list     — List installed skills
  3. audit    — Check skill usage and freshness

  Choose (1-3):
  ```

---

## STEP 2 — Create Skill

### STEP 2.1 — Determine Domain

If `$ARGUMENTS` specifies a domain (e.g., `create backend`), use it.
Otherwise, ask:

**PT-BR:**
```
Qual dominio para a nova skill?

1. backend     — API, servicos, ORM, banco de dados, autenticacao
2. frontend    — Componentes, estado, roteamento, design system
3. custom      — Qualquer dominio (descreva)

Escolha (1-3):
```

**EN:**
```
Which domain for the new skill?

1. backend     — API, services, ORM, database, authentication
2. frontend    — Components, state, routing, design system
3. custom      — Any domain (describe it)

Choose (1-3):
```

### STEP 2.2 — Detect Project Stack

```bash
# Detect stack for contextual defaults
cat package.json 2>/dev/null | head -40
cat composer.json 2>/dev/null | head -40
cat requirements.txt 2>/dev/null | head -20
cat go.mod 2>/dev/null | head -10
cat CLAUDE.md 2>/dev/null | head -40

# Existing skills
ls .claude/skills/*/SKILL.md 2>/dev/null
```

### STEP 2.3 — Guided Interview (3 rounds max)

Ask targeted questions based on the domain:

**For `backend`:**
1. Which framework and version? (e.g., Laravel 11, Express 5, Django 5, NestJS)
2. Architecture pattern? (MVC, Clean Architecture, DDD, Hexagonal)
3. Key concerns? (pick from: API design, database/ORM, authentication, validation, error handling, testing, caching, queues, observability)

**For `frontend`:**
1. Which framework and version? (e.g., Vue 3, React 19, Svelte 5, Angular)
2. Component library? (e.g., shadcn, PrimeVue, Radix, Headless UI, none)
3. Key concerns? (pick from: component architecture, state management, routing, forms/validation, accessibility, performance, testing, design tokens)

**For `custom`:**
1. What is the domain? (1 sentence)
2. Which technologies/tools?
3. What are the 3-5 most important rules?

Offer sensible defaults based on detected stack. Max 3 rounds of questions.

### STEP 2.4 — Analyze Codebase Patterns

```bash
# Read existing code to extract real patterns
find . -maxdepth 3 -type f \( -name "*.ts" -o -name "*.js" -o -name "*.vue" -o -name "*.php" -o -name "*.py" \) \
  -not -path "*/node_modules/*" -not -path "*/vendor/*" | head -20

# Sample a few files for pattern detection
# (read 3-5 representative files from the domain)
```

Identify: naming conventions, import patterns, error handling style, test patterns, architectural layers.

### STEP 2.5 — Generate Skill

Generate the skill following the standard anatomy:

```bash
SKILL_NAME="skill-${domain}-${framework}"
mkdir -p ".claude/skills/${SKILL_NAME}"
```

Write `SKILL.md` with this structure:

```markdown
---
name: {skill-name}
version: 1.0.0
description: >
  {One paragraph describing when to activate this skill.
   Include specific framework names and versions so agents know when to load it.}
compatible_with:
  - "{framework} {version}"
  - "{additional compatibility}"
author: {detected from git config or CLAUDE.md}
updated: {today's date}
---

# {Skill Title}

{One paragraph: what this skill covers and when to use it.}

**When to use this skill:** {specific scenarios}

---

## Integration with PWDEV-CODE

This skill integrates into the PWDEV-CODE workflow at multiple phases:

### In SPEC.md (DESIGN phase)
When this skill is active, add to SPEC.md Section 1 (Persona): include "{skill-name}" in Active Skills.
Quality criteria to add to Section 5: [list]

### In PLAN.md (PLAN phase)
Task-level instructions the planner should include: [list]

### In VERIFY.md (VERIFY phase)
Checklist items to validate: [list]

---

## Principles

1. **{Principle 1}** — {explanation}
2. **{Principle 2}** — {explanation}
3. **{Principle 3}** — {explanation}
4. **{Principle 4}** — {explanation} (if needed)
5. **{Principle 5}** — {explanation} (if needed)

---

## Guidelines

### {Category 1}

- {Rule with example}
- {Rule with example}

### {Category 2}

- {Rule with example}
- {Rule with example}

---

## Anti-Patterns

| Never do this | Why | Do this instead |
|--------------|-----|-----------------|
| {bad pattern} | {reason} | {good pattern} |
| {bad pattern} | {reason} | {good pattern} |

---

## Checklist

Before marking any task as done, verify:

- [ ] {checkpoint 1}
- [ ] {checkpoint 2}
- [ ] {checkpoint 3}
```

### STEP 2.6 — Present and Confirm

Show the generated skill to the human. Ask:

**PT-BR:**
```
Skill gerada: .claude/skills/{skill-name}/SKILL.md

Deseja:
1. Aprovar e salvar
2. Ajustar (descreva o que mudar)
3. Cancelar

Escolha (1-3):
```

**EN:**
```
Skill generated: .claude/skills/{skill-name}/SKILL.md

Would you like to:
1. Approve and save
2. Adjust (describe what to change)
3. Cancel

Choose (1-3):
```

If adjust → apply changes and re-present. Max 2 adjustment rounds.

### STEP 2.7 — Summary

```markdown
## Skill Created

**Name:** {skill-name}
**Path:** .claude/skills/{skill-name}/SKILL.md
**Domain:** {domain}
**Stack:** {framework} {version}

### Principles: {N}
### Guidelines: {N} rules across {N} categories
### Anti-patterns: {N}
### Checklist: {N} items

### How to use:
- The skill is auto-loaded when agents detect the matching stack
- Reference it in SPEC.md Section 1 (Active Skills)
- Verify compliance in VERIFY phase using the checklist

### Next steps:
  /pwdev-code:skill list    — See all installed skills
  /pwdev-code:skill audit   — Verify skill usage
  /pwdev-code:discover      — Start a feature (skill will be active)
```

---

## STEP 3 — List Skills

```bash
echo "=== INSTALLED SKILLS ==="
for skill_dir in .claude/skills/*/; do
  skill_name=$(basename "$skill_dir")
  if [ -f "$skill_dir/SKILL.md" ]; then
    version=$(grep "^version:" "$skill_dir/SKILL.md" | head -1 | awk '{print $2}')
    desc=$(grep "^description:" "$skill_dir/SKILL.md" | head -1 | sed 's/description: *//')
    updated=$(grep "^updated:" "$skill_dir/SKILL.md" | head -1 | awk '{print $2}')
    echo "$skill_name | v$version | $updated | $desc"
  else
    echo "$skill_name | INVALID (missing SKILL.md)"
  fi
done 2>/dev/null || echo "No skills found."
```

Present as table:
```markdown
## Installed Skills

| Skill | Version | Updated | Description |
|-------|---------|---------|-------------|
| {name} | {ver} | {date} | {desc} |

Total: {N} skills

### Commands:
  /pwdev-code:skill create <domain>  — Create new skill
  /pwdev-code:skill audit            — Check usage
```

---

## STEP 4 — Audit Skills

### STEP 4.1 — Collect Data

```bash
# List all skills
ls .claude/skills/*/SKILL.md 2>/dev/null

# Check if skills are referenced in SPEC.md or CLAUDE.md
grep -l "skill-" .planning/phases/*/spec.md CLAUDE.md 2>/dev/null

# Check agent frontmatter for skill references
grep -l "skills:" .claude/agents/*.md 2>/dev/null
```

### STEP 4.2 — Audit Report

```markdown
## Skill Audit Report

| Skill | Referenced in SPEC? | Referenced in agents? | Last updated | Status |
|-------|:------------------:|:--------------------:|:------------:|--------|
| {name} | Yes/No | Yes/No | {date} | Active / Unused / Stale |

### Findings:
- **Unused skills:** {list — consider removing or activating}
- **Stale skills:** {list — updated > 6 months ago, may need refresh}
- **Missing skills:** {suggested skills based on detected stack that don't exist yet}

### Recommendations:
1. {action}
2. {action}
```

---

## Backend Skill Templates

When creating a **backend** skill, include these guideline categories:

1. **API Design** — endpoint naming, HTTP methods, status codes, pagination, filtering
2. **Database & ORM** — query patterns, migrations, relationships, N+1 prevention
3. **Authentication & Authorization** — auth flow, middleware, RBAC/ABAC
4. **Validation** — input validation, sanitization, error messages
5. **Error Handling** — exception hierarchy, error responses, logging
6. **Testing** — unit/integration test patterns, factories, mocking strategy
7. **Architecture** — layer boundaries, dependency injection, service patterns

## Frontend Skill Templates

When creating a **frontend** skill, include these guideline categories:

1. **Component Architecture** — naming, composition, props/events, slots
2. **State Management** — store patterns, reactivity, derived state
3. **Routing** — route structure, guards, lazy loading
4. **Forms & Validation** — form handling, validation library, error display
5. **Accessibility** — WCAG compliance level, ARIA patterns, keyboard nav
6. **Performance** — lazy loading, memoization, bundle optimization
7. **Testing** — component tests, E2E with Playwright, test IDs

---

## Prohibitions
- NEVER generate a skill without detecting the project stack first
- NEVER include secrets, API keys, or credentials in skills
- NEVER overwrite an existing skill without confirmation
- NEVER create skills with generic/vague rules — every rule must be actionable
- NEVER skip the human confirmation step before saving
