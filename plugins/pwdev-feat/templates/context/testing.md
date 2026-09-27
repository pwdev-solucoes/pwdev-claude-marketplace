# Testing — {project name}

> Commit `{source_commit}`.

tests_dir: {tests}
e2e_scenarios_dir: {tests}/e2e/scenarios
e2e_generated_dir: {tests}/e2e/generated

## Frameworks
| Level | Framework | Config | Evidence |
|-------|-----------|--------|----------|
| unit | | | |
| integration | | | |
| e2e | | | |

## Commands
| Purpose | Command | Source |
|---------|---------|--------|
| lint | | |
| unit | | |
| integration | | |
| e2e | | |
| build | | |

## Layout
- Test files: {N} — locations: {paths}
- Naming: {pattern}
- Fixtures / factories: {paths}

## Coverage
{configured / not configured — tool and threshold}

## UI verification
- Playwright Test configured: {yes/no — config path}
- Base URL for local runs: {env var or value from config}
- playwright-cli: probe with `command -v playwright-cli` at execution time
