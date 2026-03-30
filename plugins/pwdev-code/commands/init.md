---
description: Initialize the PWDEV-CODE v3 framework in a repository
---

# /pwdev-code:init — Framework Initialization

## Role
Utility agent that sets up the PWDEV-CODE v3 framework (3 layers) in a repository.

## Input
$ARGUMENTS: "greenfield" or "brownfield" (if empty, auto-detect).

## Procedure

### STEP 1 — Detection
```bash
if [ -f ".planning/STATE.md" ]; then
  echo "⚠️ Already initialized. Use /pwdev-code:status to see current state."
  exit 0
fi

FILE_COUNT=$(find . -maxdepth 2 -type f \( -name "*.ts" -o -name "*.js" -o -name "*.php" -o -name "*.py" -o -name "*.vue" -o -name "*.jsx" \) -not -path "*/node_modules/*" -not -path "*/vendor/*" 2>/dev/null | wc -l)
[ "$FILE_COUNT" -gt 5 ] && TYPE="brownfield" || TYPE="greenfield"
```

### STEP 2 — Create 3-Layer Structure
```bash
# Layer 1 — Commands
mkdir -p .claude/commands

# Layer 2 — Agents
mkdir -p .claude/agents

# Layer 3 — Skills
mkdir -p .claude/skills

# Workspace
mkdir -p .planning/{research,codebase,phases,quick,templates,checklists,archive}

# Roadmap (inside .planning)
mkdir -p .planning/roadmap
```

### STEP 3 — Initial Files

**`.planning/config.json`:**
```json
{
  "framework": "PWDEV-CODE",
  "version": "3.0",
  "architecture": "3-layer (commands, agents, skills)",
  "type": "[greenfield|brownfield]",
  "created": "[date]",
  "default_intensity": "standard",
  "branch_strategy": "feature-branch",
  "commit_convention": "conventional-commits"
}
```

**`.planning/STATE.md`:**
```markdown
# STATE.md
## Current Position
- Phase: NONE (freshly initialized)
- Status: Awaiting /pwdev-code:discover, /pwdev-code:prd or /pwdev-code:quick
## Decisions
- [date]: PWDEV-CODE v3 framework initialized — type [greenfield|brownfield]
## Blockers
- None
```

**`.claude/settings.json`:**
```json
{
  "permissions": {
    "allow": [
      "git add", "git commit", "git status", "git log", "git diff",
      "git tag", "git branch", "git checkout", "git stash",
      "mkdir -p", "cat", "ls", "find", "grep", "wc",
      "npm run", "npm test", "npm audit",
      "composer run", "composer test", "composer audit",
      "npx vitest", "npx playwright", "npx eslint", "npx tsc"
    ],
    "deny": [
      "rm -rf /", "git push --force", "git reset --hard",
      "cat .env", "cat .env.local", "cat .env.production",
      "cat *.pem", "cat *.key", "cat id_rsa*"
    ]
  }
}
```

### STEP 4 — If Brownfield
Suggest: "/pwdev-code:map-codebase to analyze existing repo."

### STEP 5 — Summary
```markdown
## ✅ PWDEV-CODE v3 Initialized

**Type:** [greenfield|brownfield]
**Architecture:** 3 layers (commands, agents, skills)

**Structure created:**
.claude/
├── commands/     # Orchestration (21 commands)
├── agents/       # Personas (11 agents)
├── skills/       # Knowledge (N skills)
└── settings.json

.planning/
├── STATE.md, config.json
├── research/, codebase/, phases/, quick/
├── templates/, checklists/, archive/

### Next steps:
1. [If brownfield] /pwdev-code:map-codebase
2. /pwdev-code:prd — create product PRD
3. /pwdev-code:roadmap — generate executable roadmap
4. /pwdev-code:discover — start first feature
```

## Prohibitions
- ❌ NEVER overwrite existing .planning/
- ❌ NEVER overwrite existing .claude/ without confirmation
- ❌ NEVER modify .gitignore without confirmation
- ❌ NEVER read .env
