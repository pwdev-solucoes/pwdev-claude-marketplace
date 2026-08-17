# PWDEV Flow Marco 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add PWDEV Code-equivalent autonomous fleet orchestration and guarded external CLI delegation to PWDEV Flow for Codex.

**Architecture:** Preserve the proven Bash, Git worktree, Docker Compose, tmux, and provider-runner model while moving all state under `.planning/flow/`. Fleet stages invoke canonical Flow skills through structured `codex exec` results in explicitly authorized dangerous mode; standalone delegation remains allowlisted, confirmation-gated, locked, and independently reviewed.

**Tech Stack:** Bash 3.2-compatible shell, Git worktrees, Docker Compose, tmux, jq, Codex CLI 0.147-compatible arguments, JSON Schema, Markdown skills/references, YAML UI metadata, and Python 3 `unittest` subprocess tests.

**Spec:** `docs/superpowers/specs/2026-08-16-pwdev-flow-m5-design.md`

## Global Constraints

- Modify only `plugins/pwdev-flow/`, its tests, and the Marco 5 spec/plan files.
- Preserve unrelated modified and untracked files exactly as found.
- Do not hand-edit `.agents/plugins/marketplace.json` or Codex configuration.
- Add no hooks, MCP servers, apps, services, installers, or provider credentials.
- Store fleet and delegation state only under `.planning/flow/` in target repositories.
- Use `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral` only in `fleet-run.sh`.
- Do not execute a real dangerous Codex process, Docker project, tmux fleet, provider CLI, merge, or network call during validation.
- Use temporary Git repositories and fake executables for behavior tests.
- Do not read `.env`, credentials, tokens, private keys, certificates, or generated `.env.fleet` content.
- Keep stage commits inside fleet worktrees. Do not commit, push, branch, merge, or rewrite this plugin repository.
- Use test-first RED/GREEN cycles for every script behavior.
- Set the final base version to `0.5.0` and run the Codex cachebuster helper exactly once after all source changes pass.

## File map

| Path | Responsibility |
|---|---|
| `tests/flow_m5_fixtures.py` | Temporary Git repositories, fake executables, subprocess runner, and literal fixture builders |
| `tests/test_flow_delegation.py` | Provider vectors, locks, timeouts, output capture, and read-only mutation behavior |
| `tests/test_flow_fleet_lifecycle.py` | Launch, ports, worktrees, Docker/tmux bookkeeping, teardown, and merge gates |
| `tests/test_flow_fleet_runner.py` | Autonomous stage order, structured results, commits, correction bound, and dashboard |
| `plugins/pwdev-flow/scripts/run-agent.sh` | Standalone allowlisted external CLI execution |
| `plugins/pwdev-flow/scripts/fleet-up.sh` | Fleet member provisioning |
| `plugins/pwdev-flow/scripts/fleet-run.sh` | Autonomous Codex stage pipeline |
| `plugins/pwdev-flow/scripts/fleet-dashboard.sh` | One-shot and live status table |
| `plugins/pwdev-flow/scripts/fleet-teardown.sh` | Resource shutdown and status-gated merge |
| `plugins/pwdev-flow/templates/docker-compose.flow-fleet.yml` | Generic app/database Compose stack |
| `plugins/pwdev-flow/templates/fleet-env.example` | Non-secret generated environment field reference |
| `plugins/pwdev-flow/templates/fleet-result.schema.json` | Required structured result contract for Codex stages |
| `plugins/pwdev-flow/references/fleet.md` | Fleet configuration, lifecycle, dangerous-mode, and recovery contract |
| `plugins/pwdev-flow/references/delegation.md` | Providers, invocation vectors, safety prompt, and review contract |
| `plugins/pwdev-flow/skills/flow-fleet/` | User-facing fleet router and approval gates |
| `plugins/pwdev-flow/skills/flow-delegate/` | Provider selection and mandatory post-run review |

---

### Task 1: Lock the Marco 5 package contract

**Files:**
- Modify: `tests/test_pwdev_flow.py`

**Interfaces:**
- Consumes: the approved counts and paths from the Marco 5 specification.
- Produces: failing structural assertions for 17 skills, 16 references, 7 scripts, 3 templates, and version `0.5.0`.

- [x] **Step 1: Extend literal package expectations**

Add `flow-fleet` and `flow-delegate` to `SKILLS`, `fleet.md` and `delegation.md` to `REFERENCES`, and replace the script/template constants with:

```python
SCRIPTS = (
    "flow_audit.py",
    "migrate_legacy.py",
    "run-agent.sh",
    "fleet-up.sh",
    "fleet-run.sh",
    "fleet-dashboard.sh",
    "fleet-teardown.sh",
)
TEMPLATES = (
    "docker-compose.flow-fleet.yml",
    "fleet-env.example",
    "fleet-result.schema.json",
)
```

Change the manifest version assertion to:

```python
self.assertRegex(manifest["version"], r"^0\.5\.0(?:\+codex\.\d{14})?$")
```

Add this package behavior assertion:

```python
def test_fleet_templates_are_packaged(self) -> None:
    for template_name in TEMPLATES:
        with self.subTest(template=template_name):
            path = PLUGIN / "templates" / template_name
            self.assertTrue(path.is_file())
            self.assertGreater(len(path.read_text(encoding="utf-8")), 40)
```

- [x] **Step 2: Verify the structural suite is RED for the intended reason**

Run:

```bash
python3 -m unittest tests.test_pwdev_flow
```

Expected: failures name the two missing skills, two missing references, five missing scripts, three missing templates, and the old `0.4.0` version. Existing Marco 1–4 assertions must still pass.

- [x] **Step 3: Record the RED evidence in the task notes**

Record the command, failure count, and missing artifact names in the implementation commentary. Do not weaken assertions to reduce the count.

---

### Task 2: Build reusable test fixtures and delegation RED tests

**Files:**
- Create: `tests/flow_m5_fixtures.py`
- Create: `tests/test_flow_delegation.py`

**Interfaces:**
- Produces: `init_repository(root: Path) -> Path`, `write_executable(path: Path, body: str) -> None`, `run_shell(script: Path, repository: Path, *args: str, env: dict[str, str] | None = None) -> CompletedProcess[str]`, and fake command argument logs.
- Consumes later: Tasks 4 and 6 import the same fixtures rather than duplicating setup.

- [x] **Step 1: Create literal temporary-repository helpers**

Implement the fixture API with real Git and no mocks:

```python
def init_repository(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Flow Test"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "flow@example.invalid"], check=True)
    (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
    return root

def write_executable(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\nset -eu\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)
```

`run_shell` must prepend an optional fake-bin directory through the supplied environment, set `LC_ALL=C`, capture text output, and never use `shell=True`.

- [x] **Step 2: Write delegation behavior tests that name concrete breaks**

Add the following literal cases:

| Test | Fixture action | Required assertion |
|---|---|---|
| `test_unknown_provider_is_rejected_before_execution` | call provider `other` | exit `2`; fake-bin log absent |
| `test_codex_write_vector_never_contains_fleet_dangerous_flag` | fake Codex records argv | first arg `exec`; dangerous flag absent |
| `test_kiro_trusts_all_tools_only_in_write_mode` | run fake Kiro once per mode | flag present in write argv and absent in read argv |
| `test_read_mode_detects_a_real_worktree_mutation` | fake Gemini appends `changed` to tracked `README.md` | exit `3`; mutation remains for human review |
| `test_existing_write_lock_refuses_second_writer` | pre-create `.planning/flow/delegation/.lock` | exit `4`; provider not invoked |
| `test_missing_binary_returns_127` | PATH contains required system tools but no provider | exit `127` |
| `test_timeout_exit_is_preserved` | fake timeout exits `124` | runner exits `124` |
| `test_output_is_copied_under_flow_delegation` | fake provider prints `delegated-result` | one output file contains that literal result |
| `test_json_array_extra_args_are_passed_as_distinct_arguments` | configured OpenCode array | each element occupies one argv line; no injected file |

Use this complete pattern for the first two branches:

```python
def test_unknown_provider_is_rejected_before_execution(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
        repository = init_repository(Path(directory) / "repo")
        result = run_shell(RUNNER, repository, "other", "write", "task")
        self.assertEqual(result.returncode, 2)

def test_codex_write_vector_never_contains_fleet_dangerous_flag(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repository = init_repository(root / "repo")
        fake_bin = root / "bin"
        fake_bin.mkdir()
        argument_log = root / "arguments.txt"
        write_executable(
            fake_bin / "codex",
            'printf "%s\\n" "$@" > "$FLOW_FAKE_ARGS"\nprintf "delegated-result\\n"',
        )
        result = run_shell(
            RUNNER,
            repository,
            "codex",
            "write",
            "implement fixture",
            env={"PATH": f"{fake_bin}:{os.environ['PATH']}", "FLOW_FAKE_ARGS": str(argument_log)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        arguments = argument_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(arguments[0], "exec")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", arguments)
```

For the Codex vector, make a fake `codex` write each argument on its own line to `FLOW_FAKE_ARGS`, then assert:

```python
self.assertEqual(arguments[0], "exec")
self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", arguments)
self.assertIn("MANDATORY RULES", output_copy.read_text(encoding="utf-8"))
```

For the extra-argument test, configure:

```json
{"external_models":{"opencode":{"extra_args":["--model","vendor/model;touch-not-run"]}}}
```

Assert the semicolon-bearing value is one literal argument and no `touch-not-run` file exists.

- [x] **Step 3: Run delegation tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_flow_delegation
```

Expected: failures identify missing `plugins/pwdev-flow/scripts/run-agent.sh`; fixture-only tests pass.

---

### Task 3: Implement guarded standalone delegation

**Files:**
- Create: `plugins/pwdev-flow/scripts/run-agent.sh`
- Test: `tests/test_flow_delegation.py`

**Interfaces:**
- CLI: `run-agent.sh <codex|opencode|kimi|gemini|kiro> <write|read> <task words>`.
- Exit codes: `0` success, `2` usage/allowlist/config, `3` read-only violation, `4` write lock, `124` timeout, `127` binary missing.
- Configuration: `.planning/flow/config.json -> external_models.<agent>.{model,timeout_s,extra_args[]}`.

- [x] **Step 1: Implement validation, config, lock, and baseline**

Use Bash strict mode and these exact allowlists:

```bash
ALLOWLIST="codex opencode kimi gemini kiro"
case " $ALLOWLIST " in *" $AGENT "*) ;; *) exit 2 ;; esac
case "$MODE" in write|read) ;; *) exit 2 ;; esac
```

Resolve `kiro` to `kiro-cli`. Read only the Flow config with jq. Require `timeout_s` to be a positive integer and `extra_args` to be an array of strings. Append each jq-produced array element to a Bash array; never use `eval` or interpolate a command string.

Use `.planning/flow/delegation/.lock` for write mode and compare `git status --porcelain -- . ':(exclude).planning/flow/delegation'` before and after read mode.

- [x] **Step 2: Implement provider argument vectors**

Build arrays with these prefixes:

```bash
codex)    CMD=(codex exec --ephemeral --cd "$TOPLEVEL" "$PROMPT") ;;
opencode) CMD=(opencode run) ;;
kimi)     CMD=(kimi --quiet) ;;
gemini)   CMD=(gemini --prompt "$PROMPT") ;;
kiro)     CMD=(kiro-cli chat --no-interactive) ;;
```

Add configured `--model` only to OpenCode and Gemini. Detect Kimi `--prompt` support. Add `--trust-all-tools` to Kiro only in write mode. Place safe extra arguments before the prompt according to each provider vector.

The prompt must include repository root, explicit mode, the ten safety rules from the spec, and the literal task. Pass it as one argument.

- [x] **Step 3: Implement timeout, output, and audit behavior**

Use `timeout`, then `gtimeout`, otherwise run without a timeout and emit a warning. Mirror combined output to `.planning/flow/delegation/<UTC>-<agent>.md` with `tee` when Flow state exists. Preserve the provider exit code through `PIPESTATUS[0]`.

When audit is enabled, invoke `flow_audit.py` with `external_run`, provider, mode, exit, and timeout metadata only. Never include prompt, model, output, environment, or an absolute path.

- [x] **Step 4: Run focused GREEN tests**

Run:

```bash
python3 -m unittest tests.test_flow_delegation
```

Expected: all delegation tests pass with no real provider process.

- [x] **Step 5: Run the existing operational regression suite**

Run:

```bash
python3 -m unittest tests.test_flow_operations
```

Expected: all Marco 4 audit and migration tests remain green.

---

### Task 4: Define fleet launch and teardown behavior

**Files:**
- Create: `tests/test_flow_fleet_lifecycle.py`
- Modify: `tests/flow_m5_fixtures.py`

**Interfaces:**
- Produces: `create_approved_phase(repo: Path, slug: str, tracked: bool) -> None`, fake Docker/tmux command logs, and lifecycle expectations.
- Consumes later: `fleet-up.sh`, `fleet-teardown.sh`, Compose/environment templates.

- [x] **Step 1: Add approved-phase and fake-tool fixtures**

`create_approved_phase` must write literal approved contracts:

```markdown
# Demo specification

- Status: APPROVED
- Objective: exercise the fleet fixture
```

and:

```markdown
# Demo decisions

- Status: APPROVED
- Decision: keep fixture behavior isolated
```

When `tracked=True`, commit only those fixture files inside the temporary repository.

- [x] **Step 2: Write lifecycle RED tests**

Add these real subprocess cases:

| Test | Controlled setup | Literal expected behavior |
|---|---|---|
| `test_dry_run_prints_worktree_docker_tmux_and_flow_paths_without_mutation` | approved tracked phase; `DRY_RUN=1` | exit `0`; five command fragments below; branch/bookkeeping absent |
| `test_invalid_slug_and_non_dangerous_config_fail_before_mutation` | slugs `../escape` and `Demo`; permission `workspace-write` | exit `2`; no worktree path |
| `test_capacity_and_existing_member_collisions_are_rejected` | max `1` plus one literal member file | exit `2`; fake Docker/tmux logs absent |
| `test_occupied_port_is_rejected_before_worktree_creation` | Python socket listens on resolved app port | exit `2`; branch absent |
| `test_launch_allocates_first_free_slot_and_writes_bookkeeping` | member index `0` exists; fakes succeed | new member uses index `1`, ports `3010` and `5442` |
| `test_untracked_approved_contracts_are_adopted_only_in_worktree` | phase files absent from HEAD | initiating status unchanged; worktree contains committed contracts |
| `test_partial_docker_failure_persists_needs_human_resources` | fake Docker exits `9` | non-zero; member JSON says `NEEDS_HUMAN` and `worktree_created: true` |
| `test_teardown_without_merge_preserves_branch_and_worktree` | active member with fake resources | exit `0`; branch/worktree remain; Docker/tmux stop logged |
| `test_teardown_refuses_merge_when_status_is_not_done` | worktree status `NEEDS_HUMAN` | non-zero; current HEAD unchanged; worktree remains |
| `test_done_member_merges_and_removes_worktree` | `DONE` branch has committed `result.txt` | exit `0`; main contains file; worktree/bookkeeping absent |
| `test_merge_conflict_aborts_and_preserves_recoverable_state` | both branches change same README line | non-zero; merge state absent; branch/worktree/bookkeeping remain |

Use real Git worktrees only under the temporary directory. Fake `docker` and `tmux` append argument vectors to files. Never open the generated `.env.fleet`; assert only its existence and mode.

For dry run, assert output contains these literal fragments:

```text
git worktree add
flow-fleet/demo
docker compose
pwdev-flow-fleet:demo
.planning/flow/fleet/demo.json
```

- [x] **Step 3: Verify lifecycle tests are RED**

Run:

```bash
python3 -m unittest tests.test_flow_fleet_lifecycle
```

Expected: failures identify missing fleet scripts and templates; repository fixture setup passes.

---

### Task 5: Implement fleet provisioning and teardown

**Files:**
- Create: `plugins/pwdev-flow/scripts/fleet-up.sh`
- Create: `plugins/pwdev-flow/scripts/fleet-teardown.sh`
- Create: `plugins/pwdev-flow/templates/docker-compose.flow-fleet.yml`
- Create: `plugins/pwdev-flow/templates/fleet-env.example`
- Test: `tests/test_flow_fleet_lifecycle.py`

**Interfaces:**
- `fleet-up.sh <slug>` with `DRY_RUN=1` support.
- `fleet-teardown.sh <slug> [--merge]` with `DRY_RUN=1` support.
- Bookkeeping: `.planning/flow/fleet/<slug>.json` with slug, branch, worktree, ports, index, project, tmux window, compose filename, status, and timestamps.

- [x] **Step 1: Implement strict preflight and allocation**

Require lowercase slugs matching `^[a-z0-9][a-z0-9-]*$`, named branch, required binaries, Docker Compose, approved contracts, `permission_mode == danger-full-access`, `auto_simplify != true`, no collisions, and capacity below `max_concurrent`.

Use `.planning/flow/fleet/.lock` as a mkdir lock. Compute:

```bash
APP_PORT=$((PORT_BASE_APP + PORT_STEP * INDEX))
DB_PORT=$((PORT_BASE_DB + PORT_STEP * INDEX))
BRANCH="flow-fleet/${SLUG}"
PROJECT_NAME="flow-fleet-${SLUG}"
```

Check both ports before creating the worktree. `DRY_RUN=1` prints resolved commands and returns without files, branches, Docker, or tmux mutation.

- [x] **Step 2: Implement worktree and contract adoption**

Create a sibling worktree with `git worktree add "$WORKTREE_PATH" -b "$BRANCH"`. If `HEAD` lacks either approved contract, copy only `spec.md` and `decisions.md` from the initiating tree, stage them in the worktree, and commit `chore(flow-fleet): adopt approved ${SLUG} contracts`.

Add fleet-local ignore entries inside the worktree and commit them there. Generate `.env.fleet` with fixed development-only names and allocated ports, but never echo its content after creation. Set mode `0600`.

- [x] **Step 3: Implement Docker, tmux, and recoverable partial state**

Copy the Compose template. Start full services when `Dockerfile` exists, otherwise `db` only. Create `pwdev-flow-fleet` and its dashboard window if absent, then create the slug window through a generated pane wrapper.

On every post-worktree failure, write bookkeeping with `status: NEEDS_HUMAN` and booleans for created worktree, Docker attempt, and tmux attempt. Do not remove recoverable resources automatically.

- [x] **Step 4: Implement teardown and merge gate**

Read only the exact member bookkeeping path. Stop Compose and its tmux window. Without `--merge`, preserve worktree/branch and remove bookkeeping only after resource shutdown is verified. With `--merge`, require worktree status `DONE`, run `git merge --no-ff`, and remove the worktree only after success.

On conflict, run `git merge --abort`, preserve bookkeeping, branch, and worktree, and exit non-zero. Do not use recursive deletion or force-remove a worktree containing uncommitted files.

- [x] **Step 5: Run lifecycle GREEN tests**

Run:

```bash
python3 -m unittest tests.test_flow_fleet_lifecycle
```

Expected: all launch/teardown tests pass; fake command logs prove no real Docker or tmux invocation.

---

### Task 6: Define and implement the autonomous runner and dashboard

**Files:**
- Create: `tests/test_flow_fleet_runner.py`
- Modify: `tests/flow_m5_fixtures.py`
- Create: `plugins/pwdev-flow/scripts/fleet-run.sh`
- Create: `plugins/pwdev-flow/scripts/fleet-dashboard.sh`
- Create: `plugins/pwdev-flow/templates/fleet-result.schema.json`

**Interfaces:**
- `fleet-run.sh <slug> <worktree-path> [danger-full-access]`.
- `fleet-dashboard.sh [--once]`.
- Result schema fields: `stage`, `status`, `message`, `verdict`.
- Status file: `.planning/flow/fleet-status.json`.

- [x] **Step 1: Write runner RED tests with a fake Codex executable**

The fake Codex must log one argument per line, locate the `--output-last-message` destination, and write the next JSON object from a fixture-controlled sequence. It may create only the phase artifacts explicitly required by that stage.

Add these cases:

| Test | Fake result sequence | Literal expected behavior |
|---|---|---|
| `test_success_runs_four_stages_with_dangerous_ephemeral_structured_args` | four `OK` results, verify `APPROVED` | skill order plan/execute/review/verify; exact structured flags each time |
| `test_success_commits_stage_changes_and_marks_done` | same success sequence; fake writes one scoped artifact per stage | four stage commits; status `DONE` |
| `test_invalid_json_marks_needs_human` | plan output is `{broken` | exit non-zero; stage `plan`; status `NEEDS_HUMAN` |
| `test_failed_status_marks_needs_human` | plan result status `FAILED` | no execute call; status message copied from result |
| `test_three_rejections_stop_after_two_fix_cycles` | initial plus two post-fix verify results are `REJECTED` | three verify calls; two fix/review pairs; final `NEEDS_HUMAN` |
| `test_missing_expected_plan_artifact_halts_pipeline` | plan says `OK` but creates no plan Markdown | no execute call; missing-artifact message |
| `test_dashboard_once_renders_literal_member_fields` | one central member and one worktree status file | exit `0`; row contains slug, ports, stage, status, branch, timestamp, message |

For every fake Codex invocation, assert the argument log includes exactly one each of:

```text
--dangerously-bypass-approvals-and-sandbox
--ephemeral
--cd
--output-schema
--output-last-message
```

Assert the successful skill order is `$flow-plan`, `$flow-execute`, `$flow-review`, `$flow-verify`. For rejection escalation, assert exactly three verify calls and two each of execute-fix/review-fix.

- [x] **Step 2: Run runner tests and observe RED**

Run:

```bash
python3 -m unittest tests.test_flow_fleet_runner
```

Expected: missing runner/dashboard/schema failures.

- [x] **Step 3: Create the strict result schema**

Use this contract:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["stage", "status", "message", "verdict"],
  "properties": {
    "stage": {"enum": ["plan", "execute", "review", "verify", "execute-fix", "review-fix"]},
    "status": {"enum": ["OK", "FAILED", "NEEDS_HUMAN"]},
    "message": {"type": "string", "minLength": 1},
    "verdict": {"enum": ["NONE", "APPROVED", "CAVEATS", "REJECTED"]}
  }
}
```

- [x] **Step 4: Implement stage execution and validation**

Build each Codex command as an array and pass the autonomous prompt as one argument. Use the exact dangerous and structured flags from the spec. Redirect Codex event output to `.planning/flow/fleet-logs/` and final output to `.planning/flow/fleet-results/`.

Validate final JSON with jq against all schema enums and the expected stage. Reject a non-zero Codex exit, invalid JSON, wrong stage, non-`OK` status, or missing required artifact. Commit stage changes with `git add -A` and `git commit -m "chore(flow-fleet): ${SLUG} ${STAGE}"`; commit failure is `NEEDS_HUMAN`.

- [x] **Step 5: Implement the two-cycle correction state machine**

Run plan, execute, review, verify. On `REJECTED`, run execute-fix and review-fix, then verify again. Allow two correction iterations; a third rejection writes `NEEDS_HUMAN` and exits non-zero. `APPROVED` and `CAVEATS` write `DONE`.

- [x] **Step 6: Implement dashboard rendering**

Read central member files and per-worktree status. Print literal columns `SLUG`, `APP:DB`, `STAGE`, `STATUS`, `BRANCH`, `UPDATED`, and `MESSAGE`; truncate messages to 60 characters. `--once` exits after one render. Live mode refreshes every five seconds and handles `INT`/`TERM` without touching the fleet.

- [x] **Step 7: Run runner/dashboard GREEN tests**

Run:

```bash
python3 -m unittest tests.test_flow_fleet_runner
```

Expected: all tests pass without a real Codex, Docker, tmux, or dangerous process.

---

### Task 7: Add Marco 5 references, skills, compatibility, and audit vocabulary

**Files:**
- Create: `plugins/pwdev-flow/references/fleet.md`
- Create: `plugins/pwdev-flow/references/delegation.md`
- Create: `plugins/pwdev-flow/skills/flow-fleet/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-fleet/agents/openai.yaml`
- Create: `plugins/pwdev-flow/skills/flow-delegate/SKILL.md`
- Create: `plugins/pwdev-flow/skills/flow-delegate/agents/openai.yaml`
- Modify: `plugins/pwdev-flow/skills/flow-compat/SKILL.md`
- Modify: `plugins/pwdev-flow/references/artifacts.md`
- Modify: `plugins/pwdev-flow/references/collaboration.md`
- Modify: `plugins/pwdev-flow/references/safety.md`
- Modify: `plugins/pwdev-flow/references/audit.md`
- Modify: `plugins/pwdev-flow/scripts/flow_audit.py`
- Modify: `tests/test_flow_operations.py`

**Interfaces:**
- Consumes: all five tested scripts and the approved design.
- Produces: user-facing routes, full legacy compatibility, four new semantic audit actions, and UI metadata.

- [x] **Step 1: Add a failing audit behavior test**

Add a literal subprocess test that records `fleet_launched`, `fleet_stage`, `fleet_teardown`, and `external_run`, then asserts summary counts exactly equal one for each. Add a secret-boundary case proving model/prompt keys remain rejected.

Run:

```bash
python3 -m unittest tests.test_flow_operations
```

Expected: RED with `Unknown audit action` for the first new action.

- [x] **Step 2: Extend the audit action allowlist minimally**

Add exactly:

```python
"fleet_launched",
"fleet_stage",
"fleet_teardown",
"external_run",
```

Keep existing secret-key and target rejection unchanged. Re-run `tests.test_flow_operations`; expected GREEN.

- [x] **Step 3: Initialize both skills with the official utility**

Run:

```bash
python3 /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  flow-fleet --path plugins/pwdev-flow/skills \
  --interface display_name="PWDEV Flow Fleet" \
  --interface short_description="Run isolated autonomous Codex phase fleets" \
  --interface default_prompt="Use $flow-fleet to launch approved phases in isolated worktrees."

python3 /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  flow-delegate --path plugins/pwdev-flow/skills \
  --interface display_name="PWDEV Flow Delegate" \
  --interface short_description="Delegate safely to external coding CLIs" \
  --interface default_prompt="Use $flow-delegate to select and run an external coding CLI."
```

Delete the generated placeholder `SKILL.md` files through `apply_patch`, then add the final contents. Keep generated `agents/openai.yaml` unchanged unless validation reports mismatch.

- [x] **Step 4: Write `fleet.md` and `flow-fleet`**

The reference must contain configuration defaults, entry gate, dangerous flag, worktree/port/Docker/tmux lifecycle, state schemas, stage sequence, correction bound, dashboard, teardown, recovery, audit, and prohibitions.

The skill must route `<slugs>`, `--status`, `--teardown <slug>`, and `--teardown --all`, show the exact dangerous command before first launch, require acknowledgement, merge the default fleet block while preserving unknown config fields, and call only packaged scripts. Before launching multiple slugs, compare their spec/decision text for repeated repository paths and emit an advisory overlap warning without blocking automatically. Report worktrees/ports/status without loading full logs.

- [x] **Step 5: Write `delegation.md` and `flow-delegate`**

The reference must contain provider matrix, binary names, config schema, safe prompt, exit codes, command vectors, read/write behavior, and mandatory independent review.

The skill must support auto-selection and explicit `codex|opencode|kimi|gemini|kiro`, show the exact runner command, confirm the first external run, execute it with a host timeout at least 60 seconds above the script timeout, and always perform status/full-diff/test review afterward.

- [x] **Step 6: Update shared contracts and compatibility**

Add fleet/delegation paths and `.env.fleet` prohibition to artifacts/safety. State in collaboration that invoking `flow-fleet` or `flow-delegate` is explicit delegation authorization only for the exact confirmed command; it does not authorize unrelated subagents.

Replace `UNSUPPORTED_IN_M4` routes in `flow-compat` with:

```text
fleet -> flow-fleet
delegate -> flow-delegate auto
codex|opencode|kimi|gemini|kiro -> flow-delegate with explicit provider
```

Never translate Flow output back into `.planning/fleet` or `.planning/delegation`.

- [x] **Step 7: Validate the two new skills and all shared links**

Run:

```bash
PYTHONPATH=/tmp/pwdev-flow-validation-deps /usr/bin/python3 \
  /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/pwdev-flow/skills/flow-fleet

PYTHONPATH=/tmp/pwdev-flow-validation-deps /usr/bin/python3 \
  /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/pwdev-flow/skills/flow-delegate

python3 -m unittest tests.test_pwdev_flow tests.test_flow_operations
```

Expected: skill validation passes; structural tests now fail only for manifest version until Task 8.

---

### Task 8: Version, validate, reinstall, and prove source/cache parity

**Files:**
- Modify: `plugins/pwdev-flow/.codex-plugin/plugin.json`
- Modify: `docs/superpowers/plans/2026-08-16-pwdev-flow-m5.md` checkboxes only

**Interfaces:**
- Consumes: complete source and green Marco 1–5 tests.
- Produces: installed `0.5.0+codex.<UTC timestamp>` with byte-for-byte source/cache equality.

- [x] **Step 1: Set the base manifest version and metadata**

Use `apply_patch` to set `"version": "0.5.0"`, add fleet/delegation keywords, extend the description/long description, and add a starter prompt for isolated fleet or external delegation. Keep `hooks`, `mcpServers`, and `apps` absent.

- [x] **Step 2: Run the full source suite before cachebusting**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
```

Expected: all Marco 1–5 tests pass with no warning, real provider, Docker, tmux, dangerous Codex, or network activity.

- [x] **Step 3: Validate every skill and the plugin**

Run:

```bash
for skill_dir in plugins/pwdev-flow/skills/*; do
  PYTHONPATH=/tmp/pwdev-flow-validation-deps /usr/bin/python3 \
    /Users/paulosoares/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
    "$skill_dir" || exit 1
done

PYTHONPATH=/tmp/pwdev-flow-validation-deps /usr/bin/python3 \
  /Users/paulosoares/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/pwdev-flow
```

Expected: 17 `Skill is valid!` results and one plugin validation success.

- [x] **Step 4: Remove only discovered Finder metadata from the plugin package**

List exact paths first:

```bash
find plugins/pwdev-flow -name '.DS_Store' -print
```

Move each reported file to a uniquely named path under `/tmp`; do not use recursive deletion or a broad glob. Re-run the find command and require empty output.

- [x] **Step 5: Run content and integrity scans**

Run:

```bash
rg -n '[T]ODO|[T]BD|\[[T]ODO|[P]LACEHOLDER' plugins/pwdev-flow \
  docs/superpowers/specs/2026-08-16-pwdev-flow-m5-design.md \
  docs/superpowers/plans/2026-08-16-pwdev-flow-m5.md || true

rg -n '[[:blank:]]+$' plugins/pwdev-flow tests/test_flow_*.py \
  docs/superpowers/specs/2026-08-16-pwdev-flow-m5-design.md \
  docs/superpowers/plans/2026-08-16-pwdev-flow-m5.md || true

git diff --check
```

Expected: no Marco 5 placeholder, trailing-whitespace, or diff-integrity finding. Inspect any unrelated preexisting result without modifying it.

- [x] **Step 6: Apply exactly one cachebuster and reinstall**

Run once:

```bash
python3 /Users/paulosoares/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  plugins/pwdev-flow
```

Then reinstall through the already configured local marketplace:

```bash
codex plugin add pwdev-flow@pwdev-flow
```

Do not edit marketplace files before or after this command.

- [x] **Step 7: Verify the installed cache directly**

Resolve the installed path printed by `codex plugin add`, then derive it independently from the installed manifest version and run the plugin validator plus all 17 skill validators against that path:

```bash
PWDEV_FLOW_VERSION=$(python3 -c 'import json; print(json.load(open("plugins/pwdev-flow/.codex-plugin/plugin.json"))["version"])')
PWDEV_FLOW_INSTALLED="/Users/paulosoares/.codex/plugins/cache/pwdev-flow/pwdev-flow/${PWDEV_FLOW_VERSION}"
test -d "$PWDEV_FLOW_INSTALLED"
diff -qr plugins/pwdev-flow "$PWDEV_FLOW_INSTALLED"
```

Expected: no diff output. Also require exactly 17 skill directories, 16 reference Markdown files, 7 scripts, and 3 templates in both source and cache.

- [x] **Step 8: Run one final fresh test suite and status review**

Run:

```bash
python3 -m unittest discover -s tests -p 'test*.py'
git status --short
```

Expected: all tests pass; unrelated preexisting changes remain present and untouched; no real fleet/provider artifacts exist in this repository.

- [x] **Step 9: Mark plan checkboxes complete without committing**

Update only this plan's checkbox markers after the corresponding evidence exists. Do not create a branch, commit, push, merge, or PR. Tell the user to start a new Codex task so the newly installed skills are loaded.
