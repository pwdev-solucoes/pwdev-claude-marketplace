---
description: Run a comprehensive project health diagnostic across code, tests, dependencies, security, and process. Use --deps for a focused dependency audit.
argument-hint: "[--deps]"
disable-model-invocation: true
allowed-tools: Read, Bash, Glob, Grep, Write
---

# /pwdev-code:health — Project Health Diagnostics

## Role
Utility agent that runs a comprehensive assessment of project health:
code, tests, dependencies, security, documentation, and **framework workspace** (.planning/).

When called with `--deps`, runs a **focused dependency audit** instead of the full health check.

## Input
$ARGUMENTS: Optional flags.
- `--deps` → run only the dependency audit (STEP 2.5 + STEP 2.6)
- empty → run full health check

## Procedure

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 0.1 — Framework Workspace Validation

Validates the PROJECT's pwdev-code workspace (the plugin itself is validated
with `claude plugin validate`, not here).

```bash
echo "=== WORKSPACE VALIDATION ==="
ERRORS=0

# .planning/ workspace
[ -d ".planning" ] || { echo "❌ Missing: .planning/ (run /pwdev-code:init)"; ERRORS=$((ERRORS+1)); }
[ -f ".planning/state.md" ] && echo "✅ Found: .planning/state.md" || echo "⚠️ Missing: .planning/state.md"

# config.json required fields
if [ -f ".planning/config.json" ]; then
  echo "✅ Found: .planning/config.json"
  for field in lang model_profile audit version; do
    grep -q "\"$field\"" .planning/config.json || echo "⚠️ Missing field in config.json: $field"
  done
else
  echo "❌ Missing: .planning/config.json (run /pwdev-code:init)"
  ERRORS=$((ERRORS+1))
fi

# Project skills (optional)
if [ -d ".claude/skills" ]; then
  for skill_dir in .claude/skills/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
      echo "✅ Skill: $skill_name"
    else
      echo "❌ Skill: $skill_name (missing SKILL.md)"
      ERRORS=$((ERRORS+1))
    fi
  done
fi

# CLAUDE.md must exist
[ -f "CLAUDE.md" ] && echo "✅ Found: CLAUDE.md" || echo "⚠️ Missing: CLAUDE.md"

# .mcp.json at root (optional)
[ -f ".mcp.json" ] && echo "✅ Found: .mcp.json" || echo "ℹ️ Optional: .mcp.json not found"

# Memory index consistency (if memory exists)
if [ -f ".planning/memory/MEMORY.md" ]; then
  grep -o '(memory/[^)]*)' .planning/memory/MEMORY.md | tr -d '()' | while read -r m; do
    [ -f ".planning/$m" ] || echo "⚠️ Memory index points to missing file: $m"
  done
  for f in .planning/memory/*.md; do
    [ "$(basename "$f")" = "MEMORY.md" ] && continue
    if grep -q "status: active" "$f" 2>/dev/null; then
      grep -q "$(basename "$f")" .planning/memory/MEMORY.md || echo "⚠️ Active memory not indexed: $(basename "$f")"
    fi
  done
fi

# Audit DB integrity (when enabled)
if grep -q '"audit"[[:space:]]*:[[:space:]]*true' .planning/config.json 2>/dev/null; then
  if [ -f ".planning/pwdev-audit.db" ] && command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 .planning/pwdev-audit.db "PRAGMA integrity_check;" 2>/dev/null | head -1
  else
    echo "⚠️ Audit enabled but DB or sqlite3 missing"
  fi
fi

echo "=== STRUCTURE ERRORS: $ERRORS ==="
```

### STEP 1 — Data Collection

```bash
# Code
echo "=== LOC ==="
find . -type f \( -name "*.ts" -o -name "*.vue" -o -name "*.php" -o -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.tsx" \) \
  -not -path "*/node_modules/*" -not -path "*/vendor/*" -not -path "*/dist/*" | xargs wc -l 2>/dev/null | tail -1

echo "=== TESTS ==="
find . -type f \( -name "*.test.*" -o -name "*.spec.*" -o -name "*Test.php" \) \
  -not -path "*/node_modules/*" | wc -l

echo "=== LINT ==="
npm run lint 2>/dev/null; echo "EXIT: $?"
composer run lint 2>/dev/null; echo "EXIT: $?"

echo "=== TYPE CHECK ==="
npx tsc --noEmit 2>/dev/null; echo "EXIT: $?"
npx vue-tsc --noEmit 2>/dev/null; echo "EXIT: $?"

echo "=== TESTS RUN ==="
npm test -- --passWithNoTests 2>/dev/null; echo "EXIT: $?"
php artisan test 2>/dev/null; echo "EXIT: $?"

echo "=== SECURITY ==="
npm audit --json 2>/dev/null | head -5
grep -rn "password\s*=\s*['\"]" --include="*.ts" --include="*.js" --include="*.php" --include="*.vue" src/ app/ 2>/dev/null | wc -l

echo "=== GIT ==="
git log --oneline -5 2>/dev/null
git diff --stat 2>/dev/null
git stash list 2>/dev/null

echo "=== FRAMEWORK ==="
ls .planning/state.md .planning/phases/*/spec.md .planning/product/roadmap/ROADMAP.md 2>/dev/null
```

### STEP 1.5 — Dependency Audit

> This step runs as part of the full health check, or standalone with `--deps`.
> If `$ARGUMENTS` contains `--deps`, skip STEP 0.1, STEP 1, STEP 2 and run only this step + STEP 1.6.

```bash
# Detect ecosystem
[ -f "package.json" ] && echo "NODE" && cat package.json | head -50
[ -f "composer.json" ] && echo "PHP" && cat composer.json | head -50
[ -f "requirements.txt" ] && echo "PYTHON" && cat requirements.txt
[ -f "Cargo.toml" ] && echo "RUST" && cat Cargo.toml | head -30
[ -f "go.mod" ] && echo "GO" && cat go.mod | head -20

# Node
npm audit 2>/dev/null
npm outdated 2>/dev/null
npx depcheck 2>/dev/null

# PHP
composer audit 2>/dev/null
composer outdated 2>/dev/null

# Python
pip audit 2>/dev/null
pip list --outdated 2>/dev/null
```

### STEP 1.6 — Dependency Report

```markdown
## Dependency Report

### Summary
| Category | Count | Action |
|----------|:-----:|--------|
| Vulnerable | [N] | Update URGENTLY |
| Deprecated | [N] | Plan migration |
| Outdated (major) | [N] | Evaluate update |
| Outdated (minor/patch) | [N] | Update when possible |
| Unused | [N] | Remove |
| OK | [N] | No action |

### Vulnerabilities (URGENT)
| Package | Version | Severity | Fix available? | CVE |
|---------|---------|:--------:|:--------------:|-----|
| [name] | [ver]  | Critical/High | Yes → [ver] | [id] |

### Deprecated
| Package | Version | Recommended replacement |
|---------|---------|------------------------|
| [name] | [ver]  | [alternative]          |

### Unused
| Package | Detection confidence |
|---------|:-------------------:|
| [name] | High/Medium         |

### Recommendations
1. [priority action 1]
2. [priority action 2]
```

Save to `.planning/reports/deps/{date}.md` (if .planning/ exists).

If `--deps` was used, stop here. Do not continue to STEP 2.

### STEP 2 — Scorecard

```markdown
## 🏥 Health Check — [Project Name]

**Date:** [date]
**Overall Score:** [A/B/C/D/F]

### Scorecard

| Area | Score | Details |
|------|:-----:|---------|
| 🏗️ Workspace | [A-F] | .planning/ [✅/❌], config.json [✅/❌], state.md [✅/❌] |
| 🧪 Tests | [A-F] | [X] test files, coverage ~[X%] |
| 🔍 Lint/Types | [A-F] | [X] lint errors, [X] type errors |
| 🔒 Security | [A-F] | [X] vulnerabilities, [X] exposed secrets |
| 📦 Dependencies | [A-F] | [X] outdated, [X] deprecated |
| 📝 Documentation | [A-F] | README [✅/❌], CLAUDE.md [✅/❌], API docs [✅/❌] |
| 🔄 Git | [A-F] | Conventional commits [✅/❌], branch strategy [✅/❌] |
| 📋 Process | [A-F] | .planning/ [✅/❌], spec.md [✅/❌], roadmap [✅/❌] |

### Score Criteria
- **A:** Excellent, no action needed
- **B:** Good, minor improvements
- **C:** Acceptable, improvements recommended
- **D:** Concerning, action needed
- **F:** Critical, urgent action needed

### 🔴 Urgent Actions
1. [critical action — if any]

### 🟡 Recommended Actions
1. [recommended improvement]
2. [recommended improvement]

### 🟢 Strengths
1. [what is going well]
```

Save to `.planning/reports/health/{date}.md` (if .planning/ exists).

## Prohibitions
- ❌ NEVER fix problems automatically (only diagnose)
- ❌ NEVER give score A if there is a critical vulnerability
- ❌ NEVER read .env (only .env.example)
