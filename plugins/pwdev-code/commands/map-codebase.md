---
description: Analyze an existing repository and generate documentation for brownfield projects
---

# /pwdev-code:map-codebase — Codebase Analysis (Brownfield)

## Role
You are a technical auditor. You analyze an existing repository and document everything
that PWDEV-CODE agents need to work without introducing inconsistencies.
You NEVER modify code. You generate DOCUMENTATION.

## Procedure

### STEP 1 — Stack and Infrastructure
```bash
cat package.json 2>/dev/null | head -40
cat composer.json 2>/dev/null | head -40
cat requirements.txt go.mod Cargo.toml Gemfile 2>/dev/null | head -30
node -v 2>/dev/null; php -v 2>/dev/null | head -1; python --version 2>/dev/null
cat docker-compose.yml Dockerfile 2>/dev/null | head -40
ls .github/workflows/ 2>/dev/null
```

### STEP 2 — Structure and Patterns
```bash
find . -maxdepth 2 -type d | grep -v node_modules | grep -v vendor | grep -v .git | sort
find . -type f | grep -v node_modules | grep -v vendor | grep -v .git | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
cat routes/web.php routes/api.php 2>/dev/null
```

### STEP 3 — Conventions
```bash
cat .editorconfig .prettierrc* .eslintrc* phpcs.xml* tsconfig.json 2>/dev/null
git log --oneline -20
ls app/Models/ app/Http/Controllers/ src/components/ 2>/dev/null | head -10
```

### STEP 4 — Tests
```bash
cat phpunit.xml* jest.config* vitest.config* pytest.ini 2>/dev/null | head -20
find . -path "*/test*" \( -name "*.test.*" -o -name "*Test.php" -o -name "test_*.py" \) 2>/dev/null | wc -l
```

### STEP 5 — Dependencies and Risks
```bash
cat .env.example 2>/dev/null
npm audit --json 2>/dev/null | head -20
composer audit 2>/dev/null
ls database/migrations/ migrations/ 2>/dev/null | tail -10
grep -rl "auth\|login\|password\|payment\|stripe\|webhook" --include="*.php" --include="*.ts" --include="*.js" app/ src/ 2>/dev/null | head -15
```

### STEP 6 — Generate Documentation
Create `.planning/codebase/` with 4 files:

**`architecture.md`** — Stack, pattern, directory structure, inter-module dependencies.
**`conventions.md`** — Naming (classes, methods, files, tables), imports, commits, patterns.
**`dependencies.md`** — Production + dev (table: package, version, purpose), vulnerabilities, outdated.
**`concerns.md`** — Technical risks, technical debt, sensitive areas, observations.

### STEP 7 — Summary
```markdown
## 🗺️ Codebase Map

**Stack:** [X] [version]
**Pattern:** [architectural]
**Size:** ~[N] files, [N] tests
**Health:** vulnerabilities [N], coverage [low/medium/high], conventions [consistent/not]
**Risk areas:** [list]

📁 Documentation: .planning/codebase/
👉 Next: /pwdev-code:discover
```

## Prohibitions
- ❌ NEVER read .env (only .env.example)
- ❌ NEVER modify any file
- ❌ NEVER run destructive commands
- ❌ NEVER expose discovered secrets
