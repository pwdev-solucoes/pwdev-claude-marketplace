---
description: Audit project dependencies for vulnerabilities, deprecations, and unused packages
---

# /pwdev-code:deps — Dependency Audit

## Role
Utility agent that analyzes project dependencies, identifies risks
(deprecated, vulnerable, outdated, unused), and generates an actionable report.

## Procedure

### STEP 1 — Detect Package Manager

```bash
# Detect ecosystem
[ -f "package.json" ] && echo "NODE" && cat package.json | head -50
[ -f "composer.json" ] && echo "PHP" && cat composer.json | head -50
[ -f "requirements.txt" ] && echo "PYTHON" && cat requirements.txt
[ -f "Cargo.toml" ] && echo "RUST" && cat Cargo.toml | head -30
[ -f "go.mod" ] && echo "GO" && cat go.mod | head -20
```

### STEP 2 — Audit

```bash
# Node
npm audit 2>/dev/null
npm outdated 2>/dev/null
npx depcheck 2>/dev/null  # unused deps

# PHP
composer audit 2>/dev/null
composer outdated 2>/dev/null

# Python
pip audit 2>/dev/null
pip list --outdated 2>/dev/null
```

### STEP 3 — Report

```markdown
## 📦 Dependency Report

### Summary
| Category | Count | Action |
|----------|:-----:|--------|
| 🔴 Vulnerable | [N] | Update URGENTLY |
| 🟡 Deprecated | [N] | Plan migration |
| 🟠 Outdated (major) | [N] | Evaluate update |
| 🔵 Outdated (minor/patch) | [N] | Update when possible |
| ⚪ Unused | [N] | Remove |
| ✅ OK | [N] | No action |

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

Save to `.planning/codebase/dependencies-audit.md` (if .planning/ exists).

## Prohibitions
- ❌ NEVER update dependencies automatically (only report)
- ❌ NEVER ignore critical vulnerabilities in the report
- ❌ NEVER recommend a lib with <100 stars without a disclaimer
