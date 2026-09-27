# PWDEV-FEAT v3.0.0

*Read this in [Português Brasileiro](./README.pt-BR.md)*

> **Fast AI-assisted feature development for Claude Code, Codex, Hermes Agent and OpenCode**

```
Map (evidence) → Plan (PWDEVIA, linted) → Execute (IMPLEMENT/REPORT, resume) → Review
```

PWDEV-FEAT uses the **PWDEVIA 7-question methodology** to write executable action plans —
created inline while interviewing you (max 2 rounds) — that an **executor** implements with a
fresh context, verifying every acceptance criterion with real evidence. No heavy ceremony:
describe, plan, execute.

---

## What's new in 3.0

- **Four runtimes, one set of skills.** The workflow lives in 12 portable skills
  (`skills/feat-*`). Claude Code keeps every `/pwdev-feat:*` command as a thin wrapper; Codex,
  Hermes and OpenCode load the same skills natively. Subagents run on each runtime's own
  mechanism, and **inline** when a runtime has none.
- **Evidence-based codebase map.** `feat-map` runs a deterministic, read-only scan
  (`scripts/feat_map.py`: stack, frameworks, declared commands — never executed — tests, CI,
  migrations, modules, sensitive areas, secret paths skipped) and writes four context documents
  (`architecture`, `conventions`, `testing`, `concerns`) where every claim cites its evidence
  and confidence. Planners warn when the map is stale.
- **Traceable plans.** Plans carry `AC-nnn` acceptance criteria with their verification; steps
  name the files and ACs they cover; `scripts/plan_lint.py` checks structure and traceability
  before a plan is shown or executed.
- **Better execution.** Base commit recorded, dirty planned files flagged, per-step checkpoints
  in `progress.md` and `feat-exec <slug> --resume`; `plan.done.md` records every AC with its
  command, exit code and evidence, and planned vs. changed files.
- **Reviews with stable findings.** `feat-review` fixes an explicit `BASE..TARGET` scope
  (`scripts/review_package.sh`), reports `CR-nnn` findings with severity
  (`BLOCKER`…`INFO`), `path:line`, rule citation and evidence, and never fixes code silently.
- **UI testing in two tracks.** Interactive checks with **`playwright-cli`** in a task-owned
  session, and **declarative E2E scenarios** (JSON validated by
  `schemas/e2e-scenario.schema.json`) stored in the project's tests directory and exported to
  Playwright Test specs (`scripts/e2e_scenarios.py`) for any QA to run later.
- **Project instructions for every runtime.** `feat-setup` writes `AGENTS.md` and a
  `CLAUDE.md` that imports it.

Existing `.planning/feat/` workspaces keep working: 2.x plans are read, linted with warnings
only, executed and reported by status. See the [CHANGELOG](./CHANGELOG.md).

---

## Installation

| Runtime | Install | Invoke |
|---|---|---|
| Claude Code | `claude plugin install pwdev-feat@pwdev-claude-marketplace` | `/pwdev-feat:feat "…"` |
| Codex | add this repository as a marketplace and enable **pwdev-feat** (`.agents/plugins/marketplace.json`) | `$feat-feature …` |
| Hermes Agent | install the plugin from this repository (`.hermes-plugin/`) | `skill_view("pwdev-feat:feat-feature")` or just ask |
| OpenCode | `python3 plugins/pwdev-feat/.opencode-plugin/install.py [--project <dir>]` | `/feat-feature …` or the `skill` tool |

Codex subagents need `[features] multi_agent = true` in `~/.codex/config.toml`; without it the
executor runs inline. Details per runtime: [`references/runtime.md`](./references/runtime.md).

---

## Quick start

```bash
/pwdev-feat:init                      # language, model profile, optional audit, workspace
/pwdev-feat:map-codebase              # evidence scan + context documents (existing projects)
/pwdev-feat:setup                     # AGENTS.md (+ CLAUDE.md import)
/pwdev-feat:feat "User CRUD with validation and E2E"
/pwdev-feat:exec user-crud            # or: latest, --resume
/pwdev-feat:review user-crud          # base_commit..HEAD of that feature
/pwdev-feat:quick "fix the date format in the invoice list"
```

On Codex use `$feat-init`, `$feat-map`, `$feat-setup`, `$feat-feature`, `$feat-exec`… — same
names as the skills.

---

## Commands and skills

| Claude command | Skill | What it does |
|---|---|---|
| `/pwdev-feat:init` | `feat-init` | Language, model profile, audit trail, `.planning/feat/` |
| `/pwdev-feat:map-codebase` | `feat-map` | Evidence scan + `codebase.md` + 4 context documents |
| `/pwdev-feat:setup` | `feat-setup` | Project instructions file for all runtimes |
| `/pwdev-feat:feat` | `feat-feature` | Full feature plan (backend + UI + tests) |
| `/pwdev-feat:backend` | `feat-backend` | Backend plan: API, services, models, migrations |
| `/pwdev-feat:frontend` | `feat-frontend` | UI plan with E2E scenarios and `playwright-cli` checks |
| `/pwdev-feat:test` | `feat-test` | Test plan (IMPLEMENT) or test audit (REPORT) |
| `/pwdev-feat:review` | `feat-review` | Review plan for an explicit range (REPORT) |
| `/pwdev-feat:exec` | `feat-exec` | Execute a plan: executor, advisor, retry, resume |
| `/pwdev-feat:quick` | `feat-quick` | ≤5 files, mini-plan, no plan file |
| `/pwdev-feat:status` | `feat-status` | Pending / done / caveats / failed / resumable, map freshness |
| `/pwdev-feat:audit` | `feat-audit` | Audit summary, events, stats, export, read-only query |

---

## The method

**PWDEVIA 7 questions:** Persona & Scope · Direct Objective · Minimum Inputs · Output Format ·
Quality Criteria (`AC-nnn` + verification) · Ambiguity Handling · Prohibitions. The planner
runs in the main session because it interviews you; subagents cannot talk to the user.
Reference: [`references/pwdevia-method.md`](./references/pwdevia-method.md), template
[`templates/plan.md`](./templates/plan.md).

**Execution modes.** Review plans and report-only plans run in **REPORT** mode (findings in
`report.md`, no code change, no commit); everything else runs in **IMPLEMENT** mode. The
executor contract is [`references/executor-contract.md`](./references/executor-contract.md);
when it hits a genuine decision it returns `NEEDS_ADVICE` and the **advisor** (strongest tier,
read-only) picks one direction — [`references/advisor-contract.md`](./references/advisor-contract.md).

**Workspace:**

```
.planning/feat/
├── codebase.md                 # index (feat-map)
├── context/                    # codebase.json + architecture, conventions, testing, concerns
└── features/{slug}/
    ├── plan.md                 # the action plan
    ├── progress.md             # per-step checkpoints (resume)
    ├── plan.done.md            # execution report with AC evidence
    ├── report.md               # REPORT-mode findings (review / test audit)
    ├── review/                 # review package (range, diff, changed files)
    ├── evidence/               # playwright-cli screenshots
    └── advice-request.md / advice.md
```

E2E scenarios live in the project's tests directory: `<tests-dir>/e2e/scenarios/*.scenario.json`
and generated specs in `<tests-dir>/e2e/generated/` — see
[`references/testing.md`](./references/testing.md).

---

## E2E scenarios for Playwright

```bash
python3 <plugin>/scripts/e2e_scenarios.py validate tests/e2e/scenarios --plan .planning/feat/features/<slug>/plan.md
python3 <plugin>/scripts/e2e_scenarios.py export --to playwright tests/e2e/scenarios --out tests/e2e/generated
python3 <plugin>/scripts/e2e_scenarios.py coverage .planning/feat/features/<slug>/plan.md tests/e2e/scenarios
APP_BASE_URL=http://localhost:8000 npx playwright test tests/e2e/generated   # or open in UI mode
```

Each scenario is traceable to plan ACs, has variants (happy path, validation error, forbidden,
empty state), prefers role/label locators, and never holds a literal secret — credentials are
`${env:NAME}` placeholders resolved at run time.

---

## Configuration

`.planning/config.json` is shared with pwdev-code (merge, never overwrite):

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus", "feat-advisor": "opus" },
  "audit": false
}
```

| Role | performance | balanced | economy |
|---|---|---|---|
| executor | top | mid | mid |
| advisor | top | top | mid |

On Claude Code `top` = Opus and `mid` = Sonnet; Codex, Hermes and OpenCode inherit the host
model unless an explicit override names a model the host exposes —
[`references/model-profiles.md`](./references/model-profiles.md).

---

## Audit trail and safety

The optional SQLite audit (`.planning/pwdev-audit.db`, shared with other PWDEV plugins, never
versioned) is created by `feat-init` (`scripts/audit.py init`) and read by `feat-audit`
(read-only; single `SELECT` only). On Claude Code, hooks record sessions, subagent durations
and `.planning/` writes; on every runtime the skills log milestones, dispatches and config
changes — [`references/audit-schema.md`](./references/audit-schema.md).

Secrets (`.env*`, keys, certificates) are never read: enforced by the `guard-secrets.sh` hook on
Claude Code and by the skills' own rule everywhere else —
[`references/safety.md`](./references/safety.md).

---

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_pwdev_feat tests.test_pwdev_feat_hermes \
  tests.test_pwdev_feat_opencode tests.test_pwdev_feat_map tests.test_pwdev_feat_e2e tests.test_pwdev_feat_scripts
```

## License

Apache-2.0 — see [LICENSE](./LICENSE).
