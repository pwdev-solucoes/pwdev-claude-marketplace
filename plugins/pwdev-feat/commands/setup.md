---
description: Generate a CLAUDE.md governance file for the project based on detected stack and conventions.
---

# /pwdev-feat:setup — Generate CLAUDE.md

## Purpose

Create a `CLAUDE.md` file in the project root with conventions, stack info, and rules that all agents will follow.

## STEP 0 — Language Selection
Read `.planning/config.json` for the `lang` field (`pt-BR` or `en`).
If set → use it silently. If not set → detect from $ARGUMENTS or ask:
"Em qual idioma deseja seguir? / Which language would you like to use? 1. Portugues (PT-BR) 2. English (EN)"
Save choice to `.planning/config.json` (merge, do not overwrite other fields).
All subsequent output follows the resolved language. Technical terms stay in English.

## STEP 1 — Check existing

```bash
if [ -f "CLAUDE.md" ]; then
  echo "EXISTS"
  cat CLAUDE.md | head -20
else
  echo "NEW"
fi
```

If CLAUDE.md exists → ask: "Update existing or replace?"

## STEP 2 — Gather context

```bash
# Read codebase analysis if available
cat .planning/feat/codebase.md 2>/dev/null

# Or detect fresh
cat package.json composer.json 2>/dev/null | head -30
cat .editorconfig tsconfig.json 2>/dev/null | head -20
git log --oneline -5 2>/dev/null
```

## STEP 3 — Ask the human (1 round max)

If critical info is missing, ask:
- What is this project? (1 sentence)
- Any specific coding rules? (or "use defaults")

## STEP 4 — Generate CLAUDE.md

Write from template in `templates/CLAUDE.template.md`, filling in project-specific values.

## STEP 5 — Present

```
✅ CLAUDE.md generated

Sections: Identity, Stack, Conventions, Commands, Quality, Security, Golden Rules
Stack: {detected stack}

👉 Review CLAUDE.md and adjust as needed.
👉 Then: /pwdev-feat:feat "description" to start building.
```

## Prohibitions
- NEVER overwrite CLAUDE.md without asking
- NEVER invent conventions — detect from code or ask
