# Changelog

## 3.2.0 — 2026-09-27

- **`feat-loop` (`/pwdev-feat:loop`, `$feat-loop`, `/feat-loop`).** Delivers one GitHub issue end
  to end by chaining the existing skills: intake with `gh issue view` (issue text is untrusted
  data), plan (`feat-feature`, `feat-backend`, `feat-frontend` or `feat-quick` by labels and size),
  `feat-exec`, `feat-review` on `base..HEAD`, at most 2 fix cycles, then `git push` and
  `gh pr create` with `Closes #N`. Never merges, never force-pushes; state in
  `.planning/feat/features/{slug}/loop.md`.
- **Orchestrated mode** (`references/orchestrated-mode.md`). Under an Orca worker preamble every
  gate becomes the preamble's `ask` to the coordinator (`[feat-loop #N][gate:<kind>]`), with
  checkpoints, `consumer_fenced` handling and exactly one `worker_done`. Used by
  `pwdev-hermes-orca`.
- `references/safety.md`: invoking `feat-loop` is the request for the push and the pull request
  only.

## 3.1.0 — 2026-09-27

Fixes from the end-to-end smoke run on Claude Code, Codex, Hermes and OpenCode.

- **No side effects in the project tree.** `audit.py init`/`export` write their ignore rules to
  `.planning/.gitignore` instead of the project's `.gitignore`. The executor runs `playwright-cli`
  from the feature's `evidence/` directory (its `.playwright-cli/` working files land there), stops
  servers it started, and checks `git status` before committing: tool side effects are deleted,
  stray modifications restored, unexplained changes reported.
- **Exported specs are part of the plan.** A plan with E2E scenarios must list each exported
  `*.spec.ts` in its Output Format and carry the `e2e_scenarios.py validate` and `export` commands in
  Verification; `plan_lint.py` enforces both for v3 plans.
- **Screenshot per UI criterion.** Each UI acceptance criterion verified with `playwright-cli`
  needs a screenshot in `evidence/`, cited in `plan.done.md`, which also gains an E2E table.
- **Findings files a subagent may write.** Claude Code refuses subagent writes to report-like
  names (`report.md`, `findings.md`, `analysis.md`), which forced the orchestrator to rewrite the
  review without the status marker. REPORT-mode findings are now `review.md` (review plans) and
  `test-audit.md` (test audits); if a runtime still refuses a required write, the executor returns
  the content between `--- BEGIN FILE <path> ---` / `--- END FILE ---` and `feat-exec` persists it
  verbatim, with `plan.done.md` rendered from the template (status marker included).
- **Audit on every runtime.** Planning skills, `feat-exec`, `feat-review` and `feat-quick` record
  their milestones; `audit-log.sh artifact` records planning artifacts on runtimes without hooks.

## 3.0.0 — 2026-09-27

### Portability
- The workflow moved to 12 portable skills (`skills/feat-*`); the 12 Claude commands are now
  thin wrappers with the same names.
- New adapters: Codex (`.codex-plugin/plugin.json`, `skills/*/agents/openai.yaml`), Hermes
  (`.hermes-plugin/`, first-turn bootstrap) and OpenCode (`.opencode-plugin/install.py`).
- Executor and advisor contracts are runtime-neutral (`references/executor-contract.md`,
  `references/advisor-contract.md`); dispatch per runtime in `references/runtime.md`, with an
  inline fallback when no subagent mechanism exists.
- Model profiles use tiers (`top`/`mid`); Codex, Hermes and OpenCode inherit the host model.

### Codebase analysis
- `scripts/feat_map.py`: deterministic, read-only evidence scan with secret-path exclusion,
  declared commands (never executed) and staleness against the last published map.
- `feat-map` writes `context/{architecture,conventions,testing,concerns}.md` with evidence and
  confidence per claim; `codebase.md` stays as the index.

### Plans and execution
- Plan template v3: frontmatter, `AC-nnn` criteria with verification, steps with `files:` and
  `covers:`, Risks and Verification sections. `scripts/plan_lint.py` validates it.
- `scripts/feat_state.py` replaces the bash in `exec`/`status`: stable status marker, mode rule,
  precheck (base commit, dirty planned files) and `--resume` from `progress.md`.
- `plan.done.md` records AC evidence (command, exit code), planned vs. changed files.

### Test and review
- `feat-review`: explicit `BASE..TARGET` scope with `scripts/review_package.sh`, `CR-nnn`
  findings with severity, rule citation and evidence, verdict and fix scope.
- `feat-test` / UI plans: coverage matrix, `playwright-cli` interactive checks, declarative E2E
  scenarios (`schemas/e2e-scenario.schema.json`) in the project's tests directory, exported to
  Playwright Test by `scripts/e2e_scenarios.py`.

### Other
- `feat-setup` writes `AGENTS.md` (template renamed to `templates/AGENTS.template.md`) and a
  `CLAUDE.md` importing it.
- `scripts/audit.py` replaces the SQL embedded in the audit command; the single-SELECT rule is
  enforced in code and the database is opened read-only. `audit.py init` creates the schema.

### Migration from 2.x
- Nothing to migrate in `.planning/feat/`: 2.x plans are linted with warnings only, their
  status strings are still recognized, and `codebase.md` is still read.
- Claude Code users: update the plugin and restart the session. Existing `CLAUDE.md` files are
  never overwritten by `feat-setup` without confirmation.
