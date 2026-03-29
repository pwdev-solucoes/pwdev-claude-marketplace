---
name: skill
description: Manage project skills — list, install, create, audit, and link to SPEC.md
---

# /pwdev-code:skill — Skill Manager

## Role
Utility agent that manages project skills: list, install, create,
audit, and link to SPEC.md.

## Input
$ARGUMENTS: action + parameter. Available actions:

- `list` — list installed and available skills
- `install [name]` — install a skill in the project
- `create [name]` — create a new skill from scratch (guided)
- `audit [name]` — verify the quality of a skill
- `link [name]` — link a skill to the active SPEC.md

If $ARGUMENTS is empty → show action menu.

## Procedure

### Action: list

```bash
echo "=== INSTALLED SKILLS ==="
ls .claude/skills/*/SKILL.md 2>/dev/null | while read f; do
  DIR=$(dirname "$f")
  NAME=$(basename "$DIR")
  DESC=$(head -5 "$f" | grep "description:" | sed 's/description: *//')
  echo "  ✅ $NAME — $DESC"
done

echo ""
echo "=== AVAILABLE SKILLS (templates) ==="
echo "  📦 skill-uiux — UI/UX, accessibility, design tokens"
echo "  📦 skill-api-design — REST/GraphQL, API contracts"
echo "  📦 skill-security — OWASP, sanitization, headers"
echo "  📦 skill-testing — Test strategies, mocking"
echo "  📦 skill-performance — Lazy loading, caching, bundle"
echo "  📦 skill-accessibility — Full WCAG 2.1 AA"
echo "  📦 skill-devops — Docker, CI/CD, deploy"
echo ""
echo "Use: /pwdev-code:skill install [name] to install"
echo "Use: /pwdev-code:skill create [name] to create from scratch"
```

### Action: install [name]

```bash
# Check if it already exists
if [ -d ".claude/skills/$1" ]; then
  echo "⚠️ Skill '$1' is already installed."
  echo "Use /pwdev-code:skill audit $1 to verify."
  exit 0
fi

# Create structure
mkdir -p ".claude/skills/$1/references"
mkdir -p ".claude/skills/$1/assets"
mkdir -p ".claude/skills/$1/scripts"
```

If the skill is a known template (uiux, security, etc.):
→ Generate the complete SKILL.md with domain guidelines

If the skill is custom:
→ Create a SKILL.md scaffold and guide completion (see `create`)

After installation:

```markdown
## ✅ Skill installed

📁 `.claude/skills/[name]/`
├── SKILL.md (main guidelines)
├── references/ (on-demand reference)
└── assets/ (tokens, templates)

### Next steps:
- Review `.claude/skills/[name]/SKILL.md` and adjust to your project
- Use `/pwdev-code:skill link [name]` to link to the active SPEC.md
- Or manually reference in PLAN.md tasks
```

### Action: create [name]

Guided interview to create a custom skill:

**Round 1 — Scope:**
1. "What domain does this skill cover?"
2. "When should an agent activate it? (triggers)"
3. "What are the 3-5 most important principles of this domain?"

**Round 2 — Content:**
4. "Practical guidelines — what MUST the executor do?"
5. "Anti-patterns — what should NEVER be done?"
6. "Are there design tokens, configs, or templates to include?"

**Round 3 — Integration:**
7. "Verification items for VERIFY.md?"
8. "Additional references (docs, links)?"

Generate SKILL.md following this structure:

```markdown
---
name: skill-[name]
description: >
  [Trigger-rich description — include synonyms and activation contexts]
---

# [Title]

## Overview
[2-3 sentences]

## Core Principles
[3-5 principles with "why"]

## Practical Guidelines
### [Category 1]
[Concrete instructions + examples]

## Required Patterns
[Checklist of what to ALWAYS do]

## Anti-Patterns
[Table: anti-pattern | why | do this instead]

## Integration with PWDEV-CODE
### In SPEC.md
[What the architect adds]
### In PLAN.md
[How to reference in tasks]
### In VERIFY.md
[Extra verification items]

## References
- `references/[file].md` — [when to read]
```

### Action: audit [name]

Verify the quality of an installed skill:

```bash
SKILL_DIR=".claude/skills/$1"

# Checks
echo "=== Audit: $1 ==="

# 1. Does SKILL.md exist?
[ -f "$SKILL_DIR/SKILL.md" ] && echo "✅ SKILL.md exists" || echo "❌ SKILL.md not found"

# 2. Frontmatter?
head -3 "$SKILL_DIR/SKILL.md" | grep -q "^---" && echo "✅ Frontmatter present" || echo "❌ Missing YAML frontmatter"

# 3. Description?
grep -q "description:" "$SKILL_DIR/SKILL.md" && echo "✅ Description present" || echo "❌ Missing description (trigger)"

# 4. Size?
LINES=$(wc -l < "$SKILL_DIR/SKILL.md")
[ "$LINES" -lt 500 ] && echo "✅ $LINES lines (< 500 ideal)" || echo "⚠️ $LINES lines (>500, consider moving to references/)"

# 5. Essential sections?
grep -q "Anti-Padrão\|Anti-pattern\|NEVER" "$SKILL_DIR/SKILL.md" && echo "✅ Anti-patterns defined" || echo "⚠️ Missing anti-patterns section"
grep -q "Integration\|SPEC\|VERIFY\|PLAN" "$SKILL_DIR/SKILL.md" && echo "✅ Integration documented" || echo "⚠️ Missing integration section"
```

Present report:

```markdown
## 📋 Audit: skill-[name]

| Criterion | Status | Note |
|----------|:------:|------|
| SKILL.md exists | ✅/❌ | |
| YAML Frontmatter | ✅/❌ | name + description |
| Description with triggers | ✅/❌ | Sufficient synonyms? |
| Size < 500 lines | ✅/⚠️ | [N] lines |
| Principles defined | ✅/❌ | |
| Practical guidelines | ✅/❌ | With examples? |
| Anti-patterns | ✅/❌ | |
| Integration | ✅/❌ | SPEC + PLAN + VERIFY |
| References organized | ✅/⚠️ | |

**Score:** [N/9]
**Recommendations:** [list]
```

### Action: link [name]

Link a skill to the active SPEC.md:

```bash
# Check SPEC.md exists
if [ ! -f ".planning/SPEC.md" ]; then
  echo "❌ No active SPEC.md. Run /pwdev-code:design first."
  exit 1
fi

# Read skill
cat ".claude/skills/$1/SKILL.md" | head -5
```

Add to SPEC.md in the "Persona" section:

```markdown
### Active Skills
| Skill | Purpose | Reference |
|-------|---------|-----------|
| [name] | [from description] | .claude/skills/[name]/SKILL.md |
```

And in the "Quality Criteria" section:

```markdown
### [name] (skill)
- [ ] [skill verification item 1]
- [ ] [skill verification item 2]
```

## Stop Conditions
- Skill with the same name already exists → ask: update or rename?
- SKILL.md with >500 lines → suggest moving content to references/
- No SPEC.md when trying to link → suggest /pwdev-code:design first

## Prohibitions
- ❌ NEVER overwrite an existing skill without confirmation
- ❌ NEVER create a skill without a description (trigger is mandatory)
- ❌ NEVER generate a generic skill without an interview (create)
- ❌ NEVER link a non-existent skill to SPEC.md
