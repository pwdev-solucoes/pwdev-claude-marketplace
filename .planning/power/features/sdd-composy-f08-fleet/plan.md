# SDD Composy F08 Fleet and Integration — Plan
Status: APPROVED
Spec: .planning/power/features/sdd-composy/spec.md
Updated: 2026-09-08

For agentic workers: execute this with pwdev-power:power-execute.

## Goal
Execute independent ready tasks in isolated worktrees with provider-neutral lifecycle ownership, cmux-first presentation, safe teardown, authorized merge, and final plugin validation.

## Architecture
Fleet core owns worktrees, locks, ports, task binding, process groups, and results. UI adapters own presentation only. Provider adapters are runtime-isolated. cmux is preferred, tmux is fallback, and headless is always available.

## Tech Stack
POSIX shell, Python 3, Git worktrees, Docker Compose v2, cmux CLI, tmux, Python `unittest`.

## Global Constraints
- Fleet accepts only ready tasks with complete dependencies, explicit acceptance criteria, known verification commands, and no confirmed path overlap.
- Never merge fleet branches automatically.
- Preserve recoverable branches and worktrees after failure.
- Runtime-specific provider command vectors are built only in their dedicated adapters.
- cmux is a presentation adapter and must not own process lifecycle truth.
- cmux operations are restricted to the workspace created by this fleet.
- Never read or adopt an existing `.env.fleet`.

## File Structure
- `plugins/sdd-composy/scripts/fleet/{common,launch,run,dashboard,teardown}.sh`
- `plugins/sdd-composy/scripts/fleet/ui-{headless,tmux,cmux}.sh`
- `plugins/sdd-composy/scripts/fleet/engine-{codex,claude}.sh`
- `plugins/sdd-composy/references/{fleet,cmux}.md`
- `plugins/sdd-composy/templates/docker-compose.sdd-fleet.yml`
- `plugins/sdd-composy/skills/sdd-fleet/`
- `plugins/sdd-composy/commands/fleet.md`
- `tests/{test_sdd_composy_fleet,test_sdd_composy_fleet_runner}.py`

## Task 01 — Fleet core and worktree binding
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/common.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `plugins/sdd-composy/references/fleet.md`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: approved ready task, named base branch, clean contract identity
  Produces: locked member record, isolated `sdd-fleet/<id>` branch, sibling worktree, and bound hashes
Steps:
- [ ] Add failing tests for eligibility, symlinks, collisions, dirty contracts, hash binding, partial launch, and central-worktree preservation.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_fleet` and observe failure.
- [ ] Implement safe path validation, lock ownership, branch/worktree setup, and member publication.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 02 — Ports and isolated services
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/common.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `plugins/sdd-composy/templates/docker-compose.sdd-fleet.yml`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: locked fleet capacity and validated configuration
  Produces: deterministic free port slot and isolated Compose project
Steps:
- [ ] Add failing tests for allocation races, invalid ranges, occupied ports, existing runtime files, Compose absence, and rollback bookkeeping.
- [ ] Run the focused test and observe failures.
- [ ] Implement locked allocation, generated mode-restricted environment, and isolated Compose startup.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 03 — Runtime engines and runner
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/engine-codex.sh`, `plugins/sdd-composy/scripts/fleet/engine-claude.sh`, `plugins/sdd-composy/scripts/fleet/run.sh`, `tests/test_sdd_composy_fleet_runner.py`
Interfaces:
  Consumes: registered member, task contract, loop/result schemas
  Produces: runtime-fixed stage results, process-group cleanup, commits inside fleet branch, and terminal member status
Steps:
- [ ] Add failing command-vector, dangerous-mode acknowledgement, runtime mismatch, process-group, malformed-result, contract-change, and loop-cap tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy_fleet_runner` and observe failure.
- [ ] Implement dedicated engines and shared runner with fail-closed validation.
- [ ] Re-run the focused test.
- [ ] Commit only when explicitly authorized.

## Task 04 — Headless and tmux UI adapters
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/ui-headless.sh`, `plugins/sdd-composy/scripts/fleet/ui-tmux.sh`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: bound runner vector and selected UI driver
  Produces: detached headless process or isolated tmux session/window without changing core lifecycle truth
Steps:
- [ ] Add failing selection, command quoting, missing-tool fallback, collision, and teardown-handle tests.
- [ ] Run the fleet test and observe failures.
- [ ] Implement headless and tmux adapters plus explicit fallback selection.
- [ ] Re-run the fleet test.
- [ ] Commit only when explicitly authorized.

## Task 05 — cmux UI adapter
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/ui-cmux.sh`, `plugins/sdd-composy/references/cmux.md`, `plugins/sdd-composy/scripts/fleet/launch.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: cmux identify/list/new-workspace/new-split/surface operations and bound member
  Produces: plugin-owned workspace/pane/surface handles, status decoration, and attention flash
Steps:
- [ ] Add failing mocked-CLI tests for unavailable cmux, workspace ownership, handle parsing, no foreign mutation, flash, stale handles, and fallback.
- [ ] Run the fleet test and observe failures.
- [ ] Implement deterministic cmux operations restricted to the recorded workspace.
- [ ] Re-run the fleet test.
- [ ] Commit only when explicitly authorized.

## Task 06 — Dashboard and status integration
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/dashboard.sh`, `plugins/sdd-composy/scripts/sdd_status.py`, `plugins/sdd-composy/scripts/fleet/ui-cmux.sh`, `tests/test_sdd_composy_fleet.py`
Interfaces:
  Consumes: validated central members and per-worktree status
  Produces: concise one-shot dashboard plus cmux descriptions/colors/flashes and global status snapshot
Steps:
- [ ] Add failing tests for malformed members, truncated messages, safe relative output, status aggregation, and attention transitions.
- [ ] Run fleet and observability tests.
- [ ] Implement dashboard and guarded presentation updates.
- [ ] Re-run fleet and observability tests.
- [ ] Commit only when explicitly authorized.

## Task 07 — Teardown and authorized merge
Complexity: high
Files: `plugins/sdd-composy/scripts/fleet/teardown.sh`, `plugins/sdd-composy/scripts/fleet/common.sh`, `tests/test_sdd_composy_fleet.py`, `tests/test_sdd_composy_fleet_runner.py`
Interfaces:
  Consumes: exact member identity and optional explicit merge authorization
  Produces: verified service/UI shutdown; preserved worktree without merge or no-ff merged branch with post-merge verification
Steps:
- [ ] Add failing tests for non-terminal merge refusal, no authorization, conflict abort, cleanup failure, foreign resource protection, and recoverable preservation.
- [ ] Run both fleet test modules.
- [ ] Implement bounded teardown and merge guards without deleting unknown data or volumes.
- [ ] Re-run both fleet modules.
- [ ] Commit only when explicitly authorized.

## Task 08 — Fleet skill and final integration
Complexity: high
Files: `plugins/sdd-composy/skills/sdd-fleet/SKILL.md`, `plugins/sdd-composy/skills/sdd-fleet/agents/openai.yaml`, `plugins/sdd-composy/commands/fleet.md`, `tests/test_sdd_composy.py`, `tests/test_marketplace_readmes.py`
Interfaces:
  Consumes: launch/status/teardown routes and all completed SDD contracts
  Produces: portable `$sdd-fleet`, `/sdd-composy:fleet`, registered 17-skill plugin, and final validation evidence
Steps:
- [ ] Add failing route, authorization, adapter-order, full-catalogue, README, and marketplace coverage tests.
- [ ] Run `python3 -m unittest tests.test_sdd_composy tests.test_marketplace_readmes`.
- [ ] Implement skill, metadata, adapter, and final documentation references.
- [ ] Run all `tests.test_sdd_composy*` modules explicitly, the OKF v0.2 linter fixtures, marketplace tests, and plugin validators.
- [ ] Inspect the full plugin diff for secrets, placeholders, runtime coupling, and scope drift.
- [ ] Commit only when explicitly authorized.
