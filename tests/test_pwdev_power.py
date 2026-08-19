"""Structure, runtime-parity and behaviour tests for the pwdev-power plugin.

Run from the repository root:

    python3 -m unittest tests.test_pwdev_power

`unittest discover` does not work in this tree — there is no tests/__init__.py, so
`discover -s tests -t .` raises ImportError and `discover -s . -p "test_*.py"` silently runs
zero tests, which looks like success. Name the module.
"""

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-power"
SCRIPTS = PLUGIN / "scripts"
SKILLS = PLUGIN / "skills"
COMMANDS = PLUGIN / "commands"

CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
HERMES_MANIFEST = PLUGIN / ".hermes-plugin" / "plugin.yaml"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

COMMAND_NAMES = {"init", "product", "plan", "exec", "fleet", "verify", "quick"}

# The command name and its skill differ where the verb reads better than the skill name.
COMMAND_TO_SKILL = {
    "init": "power-init",
    "product": "power-product",
    "plan": "power-plan",
    "exec": "power-execute",
    "fleet": "power-fleet",
    "verify": "power-verify",
    "quick": "power-quick",
}

SKILL_NAMES = {
    "power",
    "power-init",
    "power-product",
    "power-brainstorm",
    "power-plan",
    "power-execute",
    "power-fleet",
    "power-verify",
    "power-quick",
    "power-tdd",
    "power-debug",
    "power-review",
    "power-worktree",
    "power-finish",
}

AGENT_NAMES = {"implementer", "task-reviewer", "verifier", "roadmap", "mapper"}

RUNTIMES = ("claude", "codex", "hermes")

# Libraries, sourced by the scripts above rather than invoked.
SOURCED_SCRIPTS = {
    "cmux-common.sh",
    "fleet-common.sh",
    "fleet-engine-claude.sh",
    "fleet-engine-codex.sh",
    "fleet-engine-hermes.sh",
}

EXPECTED_SCRIPTS = {
    "audit-hook.sh",
    "audit-log.sh",
    "claude-fleet-panel.sh",
    "claude-fleet-run.sh",
    "claude-fleet-up.sh",
    "cmux-common.sh",
    "codex-fleet-run.sh",
    "codex-fleet-up.sh",
    "fleet-common.sh",
    "fleet-dashboard.sh",
    "fleet-engine-claude.sh",
    "fleet-engine-codex.sh",
    "fleet-engine-hermes.sh",
    "fleet-launch-core.sh",
    "fleet-panel-up.sh",
    "fleet-run.sh",
    "fleet-teardown.sh",
    "fleet-up.sh",
    "guard-secrets.sh",
    "hermes-fleet-run.sh",
    "hermes-fleet-up.sh",
    "kanban-bridge.sh",
    "power-workspace.sh",
    "review-package.sh",
    "task-brief.sh",
}


def frontmatter(path):
    """Parse the leading YAML block as flat key/value pairs.

    Deliberately hand-rolled: pyyaml is not installed in this environment, and a test that
    skips itself when a dependency is missing is a test that silently stops running.
    """
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not match:
        return {}
    fields = {}
    key = None
    for line in match.group(1).splitlines():
        if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:", line):
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def run_engine(runtime, worktree="/wt", schema="/schema.json", result="/result.json", prompt="PROMPT"):
    """Source an adapter and print the command it builds, so tests read real argv."""
    script = (
        f'source "{SCRIPTS}/fleet-common.sh"; '
        f'source "{SCRIPTS}/fleet-engine-{runtime}.sh"; '
        f'power_engine_{runtime}_stage_command "{worktree}" "{schema}" "{result}" "{prompt}"; '
        'printf "%s\\n" "${FLOW_ENGINE_COMMAND[*]}"; '
        'printf "cwd=%s\\n" "${FLOW_ENGINE_CWD}"; '
        'printf "stdout=%s\\n" "${FLOW_ENGINE_RESULT_FROM_STDOUT}"'
    )
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
    lines = out.stdout.strip().splitlines()
    return {
        "argv": lines[0],
        "cwd": lines[1].split("=", 1)[1],
        "stdout": lines[2].split("=", 1)[1],
    }


class TestStructure(unittest.TestCase):
    def test_every_command_exists_and_points_at_its_skill(self):
        found = {p.stem for p in COMMANDS.glob("*.md")}
        self.assertEqual(found, COMMAND_NAMES)
        for name, skill in COMMAND_TO_SKILL.items():
            text = (COMMANDS / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn(f"skills/{skill}/SKILL.md", text, f"{name}.md must load {skill}")
            self.assertIn("$ARGUMENTS", text, f"{name}.md must forward arguments")

    def test_every_command_declares_a_description(self):
        for name in COMMAND_NAMES:
            fields = frontmatter(COMMANDS / f"{name}.md")
            self.assertTrue(fields.get("description"), f"{name}.md needs a description")

    def test_privileged_commands_are_not_model_invocable(self):
        # fleet builds a privileged provider command, so it may only be entered by a human.
        fields = frontmatter(COMMANDS / "fleet.md")
        self.assertEqual(fields.get("disable-model-invocation"), "true")

    def test_every_skill_has_a_skill_file_and_codex_metadata(self):
        found = {p.name for p in SKILLS.iterdir() if p.is_dir()}
        self.assertEqual(found, SKILL_NAMES)
        for name in SKILL_NAMES:
            self.assertTrue((SKILLS / name / "SKILL.md").is_file(), f"{name} needs SKILL.md")
            self.assertTrue(
                (SKILLS / name / "agents" / "openai.yaml").is_file(),
                f"{name} needs agents/openai.yaml for the Codex adapter",
            )

    def test_skill_frontmatter_name_matches_its_directory(self):
        for name in SKILL_NAMES:
            fields = frontmatter(SKILLS / name / "SKILL.md")
            self.assertEqual(fields.get("name"), name)
            self.assertTrue(fields.get("description"), f"{name} needs a description")

    def test_skill_descriptions_are_triggers_not_summaries(self):
        # A description that summarises the workflow gets followed instead of the skill.
        for name in SKILL_NAMES:
            description = frontmatter(SKILLS / name / "SKILL.md")["description"]
            self.assertTrue(
                description.lower().startswith("use when") or description.lower().startswith("use before"),
                f"{name}: description must state when to trigger, not what the skill does",
            )
            self.assertLessEqual(len(description), 1024, f"{name}: description too long")

    def test_every_relative_reference_resolves(self):
        pattern = re.compile(r"\]\((\.\./[^)]+|[A-Za-z0-9_-]+\.md)\)")
        checked = 0
        for skill_file in SKILLS.glob("*/SKILL.md"):
            for target in pattern.findall(skill_file.read_text(encoding="utf-8")):
                resolved = (skill_file.parent / target).resolve()
                self.assertTrue(resolved.is_file(), f"{skill_file.name} -> {target} does not resolve")
                checked += 1
        self.assertGreater(checked, 0, "no references were checked; the pattern is wrong")

    def test_every_agent_declares_model_and_tools(self):
        found = {p.stem for p in (PLUGIN / "agents").glob("*.md")}
        self.assertEqual(found, AGENT_NAMES)
        for name in AGENT_NAMES:
            fields = frontmatter(PLUGIN / "agents" / f"{name}.md")
            self.assertEqual(fields.get("name"), name)
            self.assertTrue(fields.get("model"), f"{name}: model must be explicit, never inherited")
            self.assertTrue(fields.get("tools"), f"{name}: tools must be declared")

    def test_scripts_are_present_and_parse(self):
        found = {p.name for p in SCRIPTS.iterdir() if p.is_file()}
        self.assertEqual(found, EXPECTED_SCRIPTS)
        for name in EXPECTED_SCRIPTS:
            path = SCRIPTS / name
            shell = "sh" if path.read_text(encoding="utf-8").startswith("#!/bin/sh") else "bash"
            subprocess.run([shell, "-n", str(path)], check=True, capture_output=True)

    def test_invocable_scripts_are_executable(self):
        # SOURCED_SCRIPTS are libraries: they are sourced, never run, so they need no exec bit.
        for name in EXPECTED_SCRIPTS - SOURCED_SCRIPTS:
            self.assertTrue(os.access(SCRIPTS / name, os.X_OK), f"{name} is not executable")

    def test_repo_local_skill_symlinks_resolve(self):
        # hermes skills trust loads ./.agents/skills; a broken link there fails silently.
        link_root = ROOT / ".agents" / "skills"
        self.assertTrue(link_root.is_dir())
        linked = {p.name for p in link_root.iterdir()}
        self.assertEqual(linked, SKILL_NAMES)
        for name in SKILL_NAMES:
            self.assertTrue((link_root / name / "SKILL.md").is_file(), f"{name} symlink is broken")


class TestManifests(unittest.TestCase):
    def test_base_version_is_identical_across_runtimes(self):
        claude = json.loads(CLAUDE_MANIFEST.read_text())["version"]
        codex = json.loads(CODEX_MANIFEST.read_text())["version"]
        hermes = re.search(r"^version:\s*(\S+)$", HERMES_MANIFEST.read_text(), re.M).group(1)
        self.assertEqual(codex.split("+")[0], claude)
        self.assertEqual(hermes, claude)
        self.assertRegex(codex, r"^\d+\.\d+\.\d+(?:\+codex\.\d{14})?$")
        # Only the Codex manifest may carry build metadata.
        self.assertNotIn("+", claude)
        self.assertNotIn("+", hermes)

    def test_codex_manifest_points_at_the_shared_skills_tree(self):
        manifest = json.loads(CODEX_MANIFEST.read_text())
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)

    def test_hermes_manifest_declares_only_the_hook_it_provides(self):
        text = HERMES_MANIFEST.read_text()
        self.assertRegex(text, re.compile(r"^name:\s*pwdev-power$", re.M))
        self.assertIn("provides_hooks:", text)
        self.assertIn("- pre_llm_call", text)

    def test_plugin_is_registered_in_the_marketplace(self):
        entries = json.loads(MARKETPLACE.read_text())["plugins"]
        entry = next((e for e in entries if e["name"] == "pwdev-power"), None)
        self.assertIsNotNone(entry, "pwdev-power is not registered")
        self.assertEqual(entry["source"], "./plugins/pwdev-power")
        self.assertTrue(entry["strict"])

    def test_hooks_declare_the_secret_guard_and_the_bootstrap(self):
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
        # The bootstrap must be re-injected after a compact, not only at startup.
        self.assertEqual(hooks["SessionStart"][0]["matcher"], "startup|clear|compact")
        self.assertEqual(hooks["PreToolUse"][0]["matcher"], "Read|Bash")
        self.assertIn("guard-secrets.sh", hooks["PreToolUse"][0]["hooks"][0]["command"])


class TestRuntimeIsolation(unittest.TestCase):
    """The privileged vector of one runtime must never appear in another's command."""

    FORBIDDEN = {
        "claude": ["--ephemeral", "--dangerously-bypass-approvals-and-sandbox", "--yolo", "--output-schema"],
        "codex": ["--dangerously-skip-permissions", "--yolo", "--no-session-persistence"],
        "hermes": [
            "--dangerously-skip-permissions",
            "--dangerously-bypass-approvals-and-sandbox",
            "--ephemeral",
            "--ignore-rules",
            "--safe-mode",
        ],
    }

    REQUIRED = {
        "claude": ["claude", "-p", "--dangerously-skip-permissions"],
        "codex": ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox"],
        "hermes": ["hermes", "-z", "--yolo"],
    }

    def test_each_adapter_builds_only_its_own_vector(self):
        for runtime in RUNTIMES:
            argv = run_engine(runtime)["argv"]
            for flag in self.REQUIRED[runtime]:
                self.assertIn(flag, argv, f"{runtime} is missing {flag}")
            for flag in self.FORBIDDEN[runtime]:
                self.assertNotIn(flag, argv, f"{runtime} must not carry {flag}")

    def test_working_directory_handling_matches_each_provider(self):
        # claude has no --cd, so the runner chdirs for it; codex and hermes take a path flag.
        self.assertEqual(run_engine("claude")["cwd"], "/wt")
        self.assertEqual(run_engine("codex")["cwd"], "")
        self.assertEqual(run_engine("hermes")["cwd"], "")
        self.assertIn("--cd /wt", run_engine("codex")["argv"])
        self.assertIn("--in /wt", run_engine("hermes")["argv"])

    def test_only_codex_enforces_the_schema_natively(self):
        self.assertIn("--output-schema", run_engine("codex")["argv"])
        self.assertEqual(run_engine("codex")["stdout"], "false")
        for runtime in ("claude", "hermes"):
            self.assertEqual(run_engine(runtime)["stdout"], "true")

    def test_the_prose_contract_has_a_single_source(self):
        # Two hand-maintained copies of a schema drift, and the drift is silent.
        script = (
            f'source "{SCRIPTS}/fleet-common.sh"; '
            f'source "{SCRIPTS}/fleet-engine-claude.sh"; '
            f'source "{SCRIPTS}/fleet-engine-hermes.sh"; '
            'a=$(power_engine_claude_prompt_suffix verify); '
            'b=$(power_engine_hermes_prompt_suffix verify); '
            '[[ "$a" == "$b" ]] && printf same || printf different'
        )
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout.strip(), "same")

    def test_the_runtime_allowlist_rejects_anything_else(self):
        for runtime, expected in (("claude", 0), ("codex", 0), ("hermes", 0), ("bogus", 2), ("", 2)):
            result = subprocess.run(
                ["bash", "-c", f'source "{SCRIPTS}/fleet-common.sh"; power_require_runtime "{runtime}"'],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, expected, f"runtime {runtime!r}")

    def test_launch_core_refuses_an_unknown_runtime(self):
        result = subprocess.run(
            [str(SCRIPTS / "fleet-launch-core.sh"), "bogus", "/bin/echo", "hi"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported fleet runtime", result.stderr)


class TestResultPublication(unittest.TestCase):
    """A provider that answers with prose must never look like a successful stage."""

    def publish(self, runtime, raw):
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / "raw.json"
            out_path = Path(tmp) / "out.json"
            raw_path.write_text(raw, encoding="utf-8")
            out_path.touch()
            script = (
                f'source "{SCRIPTS}/fleet-common.sh"; '
                f'source "{SCRIPTS}/fleet-engine-{runtime}.sh"; '
                f'power_engine_{runtime}_publish_result "{raw_path}" "{out_path}"'
            )
            result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
            return result.returncode, out_path.read_text(encoding="utf-8")

    VALID = '{"stage":"plan","status":"OK","message":"m","verdict":"NONE"}'

    def test_hermes_accepts_bare_json_with_or_without_a_fence(self):
        # BSD sed has no \\? quantifier: an earlier regex let the opening fence survive, and
        # every fenced result failed to parse.
        for raw in (self.VALID, f"```json\n{self.VALID}\n```", f"```\n{self.VALID}\n```"):
            code, out = self.publish("hermes", raw)
            self.assertEqual(code, 0, f"should accept: {raw!r}")
            self.assertEqual(json.loads(out)["stage"], "plan")

    def test_hermes_rejects_prose_and_leaves_no_output(self):
        for raw in ("Sure! Here is the result.", "", "not json at all"):
            code, out = self.publish("hermes", raw)
            self.assertNotEqual(code, 0, f"should reject: {raw!r}")
            self.assertEqual(out, "", "a failed publish must leave the result empty")

    def test_claude_unwraps_its_envelope_and_fails_closed(self):
        code, out = self.publish("claude", json.dumps({"is_error": False, "result": self.VALID}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["status"], "OK")

        for raw in (
            json.dumps({"is_error": True, "result": self.VALID}),
            json.dumps({"no_result_field": 1}),
            '"a bare string"',
            json.dumps({"is_error": False, "result": "sorry, I could not"}),
        ):
            code, out = self.publish("claude", raw)
            self.assertNotEqual(code, 0, f"should reject: {raw!r}")
            self.assertEqual(out, "")


class TestSecretGuard(unittest.TestCase):
    def guard(self, target):
        payload = json.dumps({"tool_input": {"file_path": target}})
        return subprocess.run(
            [str(SCRIPTS / "guard-secrets.sh")], input=payload, capture_output=True, text=True
        ).returncode

    def test_secrets_are_blocked_and_templates_are_not(self):
        for target in (".env", ".env.local", ".env.fleet", "certs/a.pem", "a.key", "~/.ssh/id_rsa"):
            self.assertEqual(self.guard(target), 2, f"{target} must be blocked")
        for target in (".env.example", ".env.template", "src/app.ts", "README.md"):
            self.assertEqual(self.guard(target), 0, f"{target} must be allowed")

    def test_the_generated_fleet_environment_is_named_so_the_guard_sees_it(self):
        # The guard anchors on a delimiter before ".env", so ".fleet.env" would slip past it.
        # fleet-up.sh must keep using the name the guard recognises.
        text = (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"^ENV_FILE=\.env\.fleet$", re.M))
        self.assertEqual(self.guard(".fleet.env"), 0, "assumption check: this form is not guarded")


class TestExecutionHelpers(unittest.TestCase):
    """The three scripts that carry the per-task loop."""

    PLAN = """# Feature — Plan
Status: APPROVED

## Global Constraints

- Timeout: 2500ms exactly

## Task 01 — first
Complexity: low
Files: src/a.ts

## Task 02 — second
Complexity: medium
Files: src/b.ts
"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        for cmd in (
            ["git", "init", "-q", "-b", "main", "."],
            ["git", "config", "user.email", "t@t"],
            ["git", "config", "user.name", "t"],
        ):
            subprocess.run(cmd, cwd=self.repo, check=True, capture_output=True)
        (self.repo / "seed.txt").write_text("seed\n")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.repo, check=True, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, name, *args):
        return subprocess.run(
            [str(SCRIPTS / name), *args], cwd=self.repo, capture_output=True, text=True
        )

    def test_workspace_creates_a_ledger_bound_to_its_plan(self):
        result = self.run_script("power-workspace.sh", "my-feature")
        self.assertEqual(result.returncode, 0, result.stderr)
        workspace = Path(result.stdout.strip())
        ledger = workspace / "ledger.md"
        self.assertTrue(ledger.is_file())
        # The first line binds the ledger to its plan: a controller that reads a ledger
        # belonging to a different plan re-dispatches finished tasks.
        first_line = ledger.read_text(encoding="utf-8").splitlines()[0]
        self.assertIn("my-feature/plan.md", first_line)

    def test_workspace_rejects_an_invalid_slug(self):
        for slug in ("Bad Slug", "../escape", ""):
            self.assertNotEqual(self.run_script("power-workspace.sh", slug).returncode, 0, slug)

    def test_brief_carries_constraints_verbatim_and_only_its_own_task(self):
        workspace = Path(self.run_script("power-workspace.sh", "demo").stdout.strip())
        plan = workspace / "plan.md"
        plan.write_text(self.PLAN, encoding="utf-8")

        result = self.run_script("task-brief.sh", str(plan), "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        brief = Path(result.stdout.strip()).read_text(encoding="utf-8")

        self.assertIn("Timeout: 2500ms exactly", brief, "exact values must travel with the task")
        self.assertIn("Task 02 — second", brief)
        self.assertNotIn("Task 01", brief, "the implementer must not see its neighbours")
        # The brief is committed, so an absolute path would carry this machine's layout.
        self.assertIn("Plan: .planning/power/features/demo/plan.md", brief)

    def test_brief_fails_on_a_task_that_does_not_exist(self):
        workspace = Path(self.run_script("power-workspace.sh", "demo").stdout.strip())
        plan = workspace / "plan.md"
        plan.write_text(self.PLAN, encoding="utf-8")
        self.assertEqual(self.run_script("task-brief.sh", str(plan), "9").returncode, 3)

    def test_review_package_contains_commits_stat_and_diff(self):
        workspace = Path(self.run_script("power-workspace.sh", "demo").stdout.strip())
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        (self.repo / "src.ts").write_text("export const x = 1;\n")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "task 01"], cwd=self.repo, check=True, capture_output=True)

        result = self.run_script("review-package.sh", str(workspace), base, "HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        package = Path(result.stdout.strip()).read_text(encoding="utf-8")
        for section in ("## Commits", "## Files changed", "## Diff"):
            self.assertIn(section, package)
        self.assertIn("export const x = 1;", package)

    def test_review_package_refuses_an_empty_range(self):
        workspace = Path(self.run_script("power-workspace.sh", "demo").stdout.strip())
        result = self.run_script("review-package.sh", str(workspace), "HEAD", "HEAD")
        self.assertEqual(result.returncode, 3, "an empty range means nothing was committed")


class TestAuditTrail(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / ".planning" / "power" / "audit").mkdir(parents=True)
        for cmd in (
            ["git", "init", "-q", "."],
            ["git", "config", "user.email", "t@t"],
            ["git", "config", "user.name", "t"],
        ):
            subprocess.run(cmd, cwd=self.repo, check=True, capture_output=True)
        self.config = self.repo / ".planning" / "power" / "config.json"
        self.db = self.repo / ".planning" / "power" / "audit" / "pwdev-audit.db"

    def tearDown(self):
        self.tmp.cleanup()

    def log(self, *args):
        return subprocess.run(
            [str(SCRIPTS / "audit-log.sh"), *args], cwd=self.repo, capture_output=True, text=True
        )

    def rows(self):
        if not self.db.exists():
            return []
        out = subprocess.run(
            ["sqlite3", str(self.db), "SELECT action,phase,target,detail FROM events;"],
            capture_output=True,
            text=True,
        )
        return [line for line in out.stdout.splitlines() if line]

    def enable(self):
        self.config.write_text(json.dumps({"audit": True}))
        subprocess.run(["sqlite3", str(self.db), "SELECT 1;"], check=True, capture_output=True)

    def test_opt_in_requires_config_and_an_existing_database(self):
        self.config.write_text(json.dumps({"audit": False}))
        self.assertEqual(self.log("event", "plan", "DESIGN", "gate_approved", "spec.md").returncode, 0)
        self.assertFalse(self.db.exists())

        # Opted in, but creating the database is what actually turns auditing on.
        self.config.write_text(json.dumps({"audit": True}))
        self.assertEqual(self.log("event", "plan", "DESIGN", "gate_approved", "spec.md").returncode, 0)
        self.assertFalse(self.db.exists(), "audit-log.sh must never create the database itself")

    def test_records_are_written_once_enabled(self):
        self.enable()
        self.log("event", "plan", "DESIGN", "gate_approved", "spec.md", "sections=8")
        self.log("gate", "PLAN", "APPROVED", "plan.md")
        self.assertEqual(len(self.rows()), 2)

    def test_model_names_and_prompts_never_enter_the_trail(self):
        self.enable()
        for detail in ("model=opus", "prompt=do the thing", "api_key=abc", "password=hunter2"):
            result = self.log("event", "exec", "EXECUTE", "task_dispatched", "x", detail)
            self.assertEqual(result.returncode, 0, "audit is best-effort and always exits 0")
            self.assertIn("rejected", result.stderr)
        self.assertEqual(self.rows(), [], "nothing secret-like may be recorded")

    def test_unknown_actions_are_rejected_not_coerced(self):
        self.enable()
        result = self.log("event", "exec", "EXECUTE", "made_up_action", "x")
        self.assertEqual(result.returncode, 0)
        self.assertIn("unknown action", result.stderr)
        self.assertEqual(self.rows(), [])

    def test_spawn_records_a_tier_not_a_model(self):
        self.enable()
        self.log("spawn", "exec", "EXECUTE", "implementer", "mid", "task=03")
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertIn("tier=mid", rows[0])

    def test_absolute_paths_are_recorded_relative_to_the_repository(self):
        self.enable()
        absolute = str(self.repo / ".planning" / "power" / "features" / "x" / "spec.md")
        self.log("event", "plan", "DESIGN", "artifact_written", absolute)
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertNotIn(str(self.repo), rows[0], "absolute paths must not enter the trail")
        self.assertIn(".planning/power/features/x/spec.md", rows[0])


class TestSessionBootstrap(unittest.TestCase):
    def test_the_hook_emits_exactly_one_context_field(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(PLUGIN))
        env.pop("CURSOR_PLUGIN_ROOT", None)
        env.pop("COPILOT_CLI", None)
        result = subprocess.run(
            ["bash", str(PLUGIN / "hooks" / "session-start")],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        payload = json.loads(result.stdout)
        # Claude Code reads additional_context and hookSpecificOutput without de-duplicating,
        # so emitting both would inject the bootstrap twice.
        self.assertEqual(list(payload), ["hookSpecificOutput"])
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(context.startswith("<EXTREMELY_IMPORTANT>"))
        self.assertIn("power-tdd", context)
        self.assertNotIn("---\nname: power\n", context.split("<EXTREMELY_IMPORTANT>")[0])


class TestDocumentation(unittest.TestCase):
    """The README is long enough to rot quietly. Pin the claims that can be checked."""

    READMES = ("README.md", "README.pt-BR.md")

    # Error strings the troubleshooting table tells the reader to expect.
    DOCUMENTED_ERRORS = (
        "cmux: no socket at",
        "cmux: CLI not found",
        "spec must carry exactly one 'Status: APPROVED' field",
        "no .planning/power/config.json; run init first",
        "detached HEAD; check out a named branch first",
        "registered fleet member does not match canonical Git worktree registration",
        "approved fleet contracts do not match the bound member",
        "invalid structured result for",
        "fleet member is already running",
        "provider ownership is unresolved; retaining runner lock",
        "verification rejected after two correction cycles",
        "fleet allocation is already locked",
    )

    def script_text(self):
        return "\n".join(p.read_text(encoding="utf-8") for p in SCRIPTS.glob("*.sh"))

    def test_documented_errors_are_strings_the_scripts_actually_emit(self):
        scripts = self.script_text()
        for message in self.DOCUMENTED_ERRORS:
            self.assertIn(message, scripts, f"README documents an error nothing emits: {message}")

    def test_documented_environment_override_exists(self):
        self.assertIn("PWDEV_POWER_CMUX_BIN", (SCRIPTS / "cmux-common.sh").read_text(encoding="utf-8"))
        for name in self.READMES:
            self.assertIn("PWDEV_POWER_CMUX_BIN", (PLUGIN / name).read_text(encoding="utf-8"))

    def test_every_command_is_documented_in_both_readmes(self):
        for name in self.READMES:
            text = (PLUGIN / name).read_text(encoding="utf-8")
            for command in COMMAND_NAMES:
                self.assertIn(f"/pwdev-power:{command}", text, f"{name} does not mention {command}")

    def test_readmes_only_link_files_that_exist(self):
        pattern = re.compile(r"\]\((\./[^)#]+|references/[^)#]+|scripts/[^)#]+)\)")
        for name in self.READMES:
            for target in pattern.findall((PLUGIN / name).read_text(encoding="utf-8")):
                self.assertTrue((PLUGIN / target).exists(), f"{name} links a missing path: {target}")

    def test_both_readmes_document_the_same_scenarios(self):
        # A translation that drifts is worse than no translation.
        counts = []
        for name in self.READMES:
            text = (PLUGIN / name).read_text(encoding="utf-8")
            counts.append(len(re.findall(r"^## (?:Scenario|Cen\u00e1rio) [A-Z] ", text, re.M)))
        self.assertEqual(counts[0], counts[1], "the two READMEs describe a different number of scenarios")
        self.assertGreaterEqual(counts[0], 10, "the scenario walkthrough is incomplete")


class TestCodebaseContext(unittest.TestCase):
    """The codebase map: four documents, one producer, six consumers."""

    CONTEXT_FILES = ("project.md", "stack.md", "domain.md", "pitfalls.md")

    def test_the_contract_names_all_four_documents(self):
        contract = (PLUGIN / "references" / "context.md").read_text(encoding="utf-8")
        for name in self.CONTEXT_FILES:
            self.assertIn(name, contract, f"context.md does not define {name}")

    def test_the_artifact_tree_lists_the_context_directory(self):
        tree = (PLUGIN / "references" / "artifacts.md").read_text(encoding="utf-8")
        for name in self.CONTEXT_FILES:
            self.assertIn(f"context/{name}", tree, f"artifacts.md is missing context/{name}")

    def test_init_owns_mapping_rather_than_a_new_command(self):
        # The map is reachable from init; adding an eighth command was rejected deliberately.
        self.assertNotIn("map", {p.stem for p in COMMANDS.glob("*.md")})
        hint = frontmatter(COMMANDS / "init.md").get("argument-hint", "")
        self.assertIn("--map", hint)
        self.assertIn("--check", hint)

    def test_init_dispatches_the_mapper_and_skips_greenfield(self):
        skill = (SKILLS / "power-init" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("mapper", skill, "init must dispatch the mapper subagent")
        # A map of an empty directory is noise that later phases would read as fact.
        self.assertIn("Greenfield", skill)
        self.assertIn("context.md", skill, "init must link the context contract")

    def test_the_mapper_is_read_mostly_and_childless(self):
        text = (PLUGIN / "agents" / "mapper.md").read_text(encoding="utf-8")
        fields = frontmatter(PLUGIN / "agents" / "mapper.md")
        self.assertNotIn("Edit", fields["tools"], "the mapper observes; it does not edit code")
        self.assertIn("do not dispatch subagents", text.lower())
        self.assertIn("Observation, not decision", text)

    def test_every_consumer_reads_the_part_of_the_map_it_needs(self):
        expected = {
            "power-brainstorm": ("project.md", "domain.md"),
            "power-plan": ("project.md", "stack.md"),
            "power-execute": ("project.md",),
            "power-quick": ("project.md",),
            "power-debug": ("pitfalls.md",),
            "power-verify": ("project.md",),
        }
        for skill, wanted in expected.items():
            text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
            for document in wanted:
                self.assertIn(
                    f"context/{document}", text, f"{skill} should read context/{document}"
                )

    def test_execute_passes_paths_rather_than_contents(self):
        # Pasting the map into every brief costs the context the map was written to save.
        text = (SKILLS / "power-execute" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Paths, not contents", text)

    def test_the_map_is_never_authoritative_over_the_code(self):
        for source in (PLUGIN / "references" / "context.md", SKILLS / "power-init" / "SKILL.md"):
            text = source.read_text(encoding="utf-8")
            self.assertIn("the code is right", text, f"{source.name} must state staleness precedence")


class TestHermesSkillCatalogue(unittest.TestCase):
    """Hermes drops skills whose body names the instructions files, without saying so."""

    # Verified by bisecting a real Hermes install: a skill body containing either literal
    # filename vanishes from the catalogue — omitted by `skills list`, "no skill named …" from
    # `skills inspect` — while `skills trust` still counts it, so the numbers do not disagree.
    # SOUL.md, CLAUDE.template.md, "Claude Code" and "AGENTS file" all pass.
    FORBIDDEN_IN_SKILL_BODIES = ("CLAUDE" ".md", "AGENTS" ".md")

    def test_no_skill_body_names_an_instructions_file(self):
        for skill in sorted(SKILLS.glob("*/SKILL.md")):
            body = skill.read_text(encoding="utf-8")
            for token in self.FORBIDDEN_IN_SKILL_BODIES:
                # Skip this file's own explanation of the rule.
                occurrences = [
                    line for line in body.splitlines()
                    if token in line and "Hermes drops" not in line
                ]
                self.assertEqual(
                    occurrences,
                    [],
                    f"{skill.parent.name} names {token}; Hermes would drop the whole skill. "
                    "Refer to it indirectly, or say it in references/ instead.",
                )

    def test_references_may_name_them_because_they_are_not_catalogued(self):
        # The rule is about skill bodies only; reference files are read on demand, so the
        # per-runtime tool mappings can and should name the file each runtime reads.
        mapping = (PLUGIN / "references" / "claude-tools.md").read_text(encoding="utf-8")
        self.assertIn("CLAUDE" ".md", mapping, "the Claude tool mapping must name its instructions file")

    def test_the_constraint_is_documented_where_skill_authors_look(self):
        runtime = (PLUGIN / "references" / "runtime.md").read_text(encoding="utf-8")
        self.assertIn("silently drops any skill", runtime)


class TestCmuxWorkspaceIdentity(unittest.TestCase):
    """`power_cmux_new_workspace` must yield a UUID whatever shape cmux answers in.

    cmux 0.64.22 ignores --json and --id-format on new-workspace and answers "OK workspace:12".
    The original implementation piped that straight into `jq -er`, so every fleet launch died at
    its first workspace — and died *after* cmux had already created one, leaving an orphan in
    the sidebar with no recorded id to close it by.

    These tests stub the CLI instead of driving a real cmux: the contract under test is how the
    function reads an answer, not whether an app is installed.
    """

    UUID = "18CE17C3-6CC5-4651-B92D-9DB92D358A8D"

    def run_with_stub(self, new_workspace_stdout, *, list_json=None):
        """Source cmux-common.sh against a fake cmux and return the CompletedProcess."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            socket_path = tmp / "cmux.sock"
            # power_cmux_require insists on a real socket file, so bind a real one.
            import socket as socketlib

            sock = socketlib.socket(socketlib.AF_UNIX, socketlib.SOCK_STREAM)
            sock.bind(str(socket_path))
            try:
                if list_json is None:
                    list_json = json.dumps(
                        {"workspaces": [{"ref": "workspace:12", "id": self.UUID}]}
                    )
                stub = tmp / "cmux"
                stub.write_text(
                    "#!/usr/bin/env bash\n"
                    'for a in "$@"; do\n'
                    '  case $a in\n'
                    "    ping) echo PONG; exit 0 ;;\n"
                    f"    new-workspace) cat <<'EOF'\n{new_workspace_stdout}\nEOF\n"
                    "      exit 0 ;;\n"
                    f"    list-workspaces) cat <<'EOF'\n{list_json}\nEOF\n"
                    "      exit 0 ;;\n"
                    "  esac\n"
                    "done\n"
                    "exit 0\n",
                    encoding="utf-8",
                )
                stub.chmod(0o755)
                script = (
                    f'source "{SCRIPTS}/cmux-common.sh"; '
                    "power_cmux_require || exit 9; "
                    'power_cmux_new_workspace "power-fleet:slug" "/tmp" "true"'
                )
                return subprocess.run(
                    ["bash", "-c", script],
                    capture_output=True,
                    text=True,
                    env={
                        **os.environ,
                        "PWDEV_POWER_CMUX_BIN": str(stub),
                        "CMUX_SOCKET_PATH": str(socket_path),
                    },
                )
            finally:
                sock.close()

    def test_resolves_the_uuid_from_a_bare_ok_ref(self):
        # The shape cmux 0.64.22 actually emits.
        result = self.run_with_stub("OK workspace:12")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.UUID)

    def test_still_prefers_json_when_a_build_honours_the_flags(self):
        result = self.run_with_stub(json.dumps({"workspace_id": self.UUID}))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), self.UUID)

    def test_fails_loudly_when_no_id_can_be_established(self):
        # A ref that resolves to nothing must fail, never print a ref as if it were an id:
        # teardown closes by id, and "close only what I created" is only provable against one.
        result = self.run_with_stub("OK workspace:12", list_json=json.dumps({"workspaces": []}))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_never_reintroduces_the_unguarded_jq_pipe(self):
        text = (SCRIPTS / "cmux-common.sh").read_text(encoding="utf-8")
        self.assertIn("power_cmux_resolve_workspace_ref", text)
        self.assertIn("workspace:[0-9][0-9]*", text)


class TestVisualPanel(unittest.TestCase):
    """The panel is 1-4 members in one workspace, and the bounds are the contract.

    Four panes is where a grid stops being readable, and one panel at a time is what keeps the
    plugin from ever having to grow a live panel by typing a privileged command into a running
    shell. Both limits are refused at the door, before any worktree exists.
    """

    def panel(self, *slugs, cwd=None, runtime="claude"):
        return subprocess.run(
            ["bash", str(SCRIPTS / "fleet-panel-up.sh"), *slugs],
            capture_output=True,
            text=True,
            cwd=cwd or str(ROOT),
            env={**os.environ, "POWER_FLEET_RUNTIME": runtime},
        )

    def test_zero_slugs_is_refused(self):
        result = self.panel()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one slug is required", result.stderr)

    def test_five_slugs_is_refused(self):
        result = self.panel("a", "b", "c", "d", "e")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("a panel holds at most 4 members", result.stderr)

    def test_a_repeated_slug_is_refused_before_anything_is_provisioned(self):
        # Otherwise the first member builds a worktree and the second collides with it.
        result = self.panel("a", "a")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("more than once", result.stderr)

    def test_runtime_must_be_pinned_by_a_wrapper(self):
        result = subprocess.run(
            ["bash", str(SCRIPTS / "fleet-panel-up.sh"), "a"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env={k: v for k, v in os.environ.items() if k != "POWER_FLEET_RUNTIME"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no runtime pinned", result.stderr)

    def test_only_the_claude_engine_names_the_interactive_vector(self):
        # The same architectural lock the autonomous vector already has: one file may name the
        # provider and its permission flag, so there is one place to audit.
        engine = (SCRIPTS / "fleet-engine-claude.sh").read_text(encoding="utf-8")
        self.assertIn("--dangerously-skip-permissions", engine)
        for script in ("fleet-panel-up.sh", "claude-fleet-panel.sh", "fleet-up.sh"):
            text = (SCRIPTS / script).read_text(encoding="utf-8")
            self.assertNotIn(
                "--dangerously-skip-permissions",
                text,
                f"{script} names a permission flag; only fleet-engine-*.sh may",
            )

    def test_the_interactive_vector_is_not_the_print_vector(self):
        script = (
            f'source "{SCRIPTS}/fleet-engine-claude.sh"; '
            "power_engine_claude_interactive_command demo .planning/power/features/demo; "
            'printf "%s\n" "${FLOW_ENGINE_COMMAND[@]}"'
        )
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
        lines = out.stdout.splitlines()
        self.assertEqual(lines[0], "claude")
        self.assertIn("--dangerously-skip-permissions", lines)
        self.assertNotIn("-p", lines, "the visual vector must not be the non-interactive one")
        self.assertNotIn("--output-format", lines)
        # The brief points at the contract rather than embedding it: argv has a limit.
        self.assertIn("spec.md", lines[-1])
        self.assertIn("plan.md", lines[-1])

    def test_other_runtimes_refuse_visual_mode_in_a_sentence(self):
        for runtime in ("codex", "hermes"):
            script = (
                f'source "{SCRIPTS}/fleet-engine-{runtime}.sh"; '
                f"power_engine_{runtime}_interactive_command demo dir"
            )
            result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                f"visual mode is not implemented for the {runtime} runtime", result.stderr
            )

    def test_panes_self_register_rather_than_being_matched_by_index(self):
        # Layout order and pane order agreeing is an assumption; CMUX_SURFACE_ID is a fact.
        up = (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8")
        self.assertIn("CMUX_SURFACE_ID", up)
        panel = (SCRIPTS / "fleet-panel-up.sh").read_text(encoding="utf-8")
        self.assertIn(".surface", panel)

    def test_the_panel_is_built_in_one_call_not_grown_by_splitting(self):
        panel = (SCRIPTS / "fleet-panel-up.sh").read_text(encoding="utf-8")
        self.assertIn("power_cmux_new_workspace_layout", panel)
        # Comments stripped: the prohibition is on what the script *does*, and the script is
        # entitled to explain in prose why it does not do it.
        code = "\n".join(
            line for line in panel.splitlines() if not line.lstrip().startswith("#")
        )
        for forbidden in ("new-split", "power_cmux send", "send-key"):
            self.assertNotIn(
                forbidden,
                code,
                f"the panel must not reach for {forbidden}; a privileged command "
                "belongs in a shell-quoted file, not typed into a live shell",
            )


class TestPanelTeardown(unittest.TestCase):
    """A panel member closes its own pane. The workspace goes with the last member out."""

    def teardown_text(self):
        return (SCRIPTS / "fleet-teardown.sh").read_text(encoding="utf-8")

    def test_a_visual_member_closes_its_surface(self):
        text = self.teardown_text()
        self.assertIn("power_cmux_close_surface", text)
        self.assertIn("cmux_surface_id", text)

    def test_the_workspace_survives_while_siblings_remain(self):
        text = self.teardown_text()
        self.assertIn("panel_siblings_remaining", text)
        self.assertIn("CLOSE_WORKSPACE=false", text)

    def test_a_member_without_a_recorded_pane_is_left_alone(self):
        # Closing the workspace instead would take every sibling down as a side effect.
        self.assertIn("leaving the panel alone", self.teardown_text())

    def test_the_last_member_does_not_try_to_close_its_pane_first(self):
        """cmux refuses it: `invalid_state: Cannot close the last surface`.

        Found live, not by reading: the first version closed the surface and then the workspace,
        which worked for every member except the one that mattered. The pane close is now inside
        the sibling branch, so the last member goes straight to the workspace.
        """
        text = self.teardown_text()
        sibling_branch = text.split("panel_siblings_remaining) -gt 0 ]]; then", 1)[1]
        sibling_branch = sibling_branch.split("# The last member out", 1)[0]
        self.assertIn("power_cmux_close_surface", sibling_branch)
        self.assertIn("Cannot close the last surface", text)

    def test_closing_a_surface_passes_the_workspace(self):
        """cmux rejects an explicit --surface without --workspace or --window.

        Also found live. The call looked right and failed silently into a warning, which is the
        worst shape a bug can take: the pane stayed open and the teardown reported success.
        """
        common = (SCRIPTS / "cmux-common.sh").read_text(encoding="utf-8")
        body = common.split("power_cmux_close_surface() {", 1)[1].split("}", 1)[0]
        self.assertIn("--workspace", body)
        self.assertIn("--surface", body)


class TestMemberRecordSchema(unittest.TestCase):
    """Mode is recorded, never inferred from the absence of a runner status file."""

    def test_the_record_carries_mode_and_surface_at_schema_2(self):
        up = (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8")
        self.assertIn("schema_version: 2", up)
        self.assertIn("mode: $mode", up)
        self.assertIn("cmux_surface_id", up)

    def test_an_unsupported_mode_is_refused(self):
        self.assertIn("unsupported fleet mode", (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8"))

    def test_the_dashboard_tolerates_a_record_written_before_panels(self):
        # A schema-1 member has no mode field; it must still render, not vanish.
        dashboard = (SCRIPTS / "fleet-dashboard.sh").read_text(encoding="utf-8")
        self.assertIn('(.mode // "auto")', dashboard)

    def test_the_dashboard_explains_a_visual_member_rather_than_calling_it_unavailable(self):
        dashboard = (SCRIPTS / "fleet-dashboard.sh").read_text(encoding="utf-8")
        self.assertIn("driven by a human in a panel pane", dashboard)


class TestPortSlotAllocation(unittest.TestCase):
    """An occupied host port advances the slot; it does not refuse the launch.

    The old shape picked a slot from the member records alone, computed its ports, and only then
    probed them — so anyone running Postgres on 5432 could not start a fleet at all, on a machine
    with sixty-three free slots. The probe now lives inside the search.
    """

    # Extracted from fleet-up.sh so the allocator can be exercised without provisioning anything.
    def allocation_harness(self, members, occupied, base_app=13000, base_db=15432, step=10):
        up = (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8")
        logic = up.split("MALFORMED_MEMBER=\n", 1)[1]
        logic = "MALFORMED_MEMBER=\n" + logic.split("\nAPP_PORT=", 1)[0]

        with tempfile.TemporaryDirectory() as tmp:
            fleet_dir = Path(tmp) / "fleet"
            fleet_dir.mkdir()
            for name, record in members.items():
                (fleet_dir / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")

            sockets = []
            try:
                import socket as socketlib

                for port in occupied:
                    sock = socketlib.socket()
                    sock.setsockopt(socketlib.SOL_SOCKET, socketlib.SO_REUSEADDR, 1)
                    sock.bind(("127.0.0.1", port))
                    sock.listen(1)
                    sockets.append(sock)

                script = f"""
set -Eeuo pipefail
FLEET_DIR={fleet_dir}
PORT_BASE_APP={base_app}; PORT_BASE_DB={base_db}; PORT_STEP={step}; INDEX=0
port_in_use() {{ (: >/dev/tcp/127.0.0.1/"$1") >/dev/null 2>&1; }}
recover() {{ printf 'RECOVER %s\\n' "$2"; exit "$1"; }}
{logic}
printf '%s\\n' "$INDEX"
"""
                return subprocess.run(
                    ["bash", "-c", script], capture_output=True, text=True
                )
            finally:
                for sock in sockets:
                    sock.close()

    def test_an_occupied_port_advances_to_the_next_slot(self):
        result = self.allocation_harness(members={}, occupied=[15432])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "1", "slot 0's db port was taken; slot 1 is free")

    def test_a_registered_member_still_reserves_its_slot(self):
        members = {"taken": {"port_index": 0, "app_port": 13000, "db_port": 15432}}
        result = self.allocation_harness(members=members, occupied=[])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "1")

    def test_both_reasons_compose(self):
        # Slot 0 blocked by a live port, slot 1 by a member: the answer is 2, not a failure.
        members = {"taken": {"port_index": 1, "app_port": 13010, "db_port": 15442}}
        result = self.allocation_harness(members=members, occupied=[13000])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "2")

    def test_a_malformed_member_stops_the_launch_instead_of_being_skipped(self):
        members = {"broken": {"slug": "broken"}}
        result = self.allocation_harness(members=members, occupied=[])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed fleet member", result.stdout)


class TestCmuxStart(unittest.TestCase):
    """cmux can be started from the CLI, but only by a launch path, and only out loud."""

    def common_text(self):
        return (SCRIPTS / "cmux-common.sh").read_text(encoding="utf-8")

    def test_starting_is_opt_in_per_call(self):
        text = self.common_text()
        self.assertIn("power_cmux_start", text)
        self.assertIn("--start", text)
        self.assertIn("POWER_CMUX_NO_AUTOSTART", text)

    def test_only_launch_paths_ask_for_a_start(self):
        # Starting a GUI app in order to close a workspace would be absurd, and the dashboard is
        # a read-only status line.
        for script in ("fleet-up.sh", "fleet-panel-up.sh"):
            text = (SCRIPTS / script).read_text(encoding="utf-8")
            self.assertIn("power_cmux_require --start", text, f"{script} should start cmux")
        for script in ("fleet-teardown.sh", "fleet-run.sh", "kanban-bridge.sh"):
            text = (SCRIPTS / script).read_text(encoding="utf-8")
            self.assertNotIn(
                "power_cmux_require --start",
                text,
                f"{script} must not start cmux; it is not a launch path",
            )

    def test_the_socket_is_re_resolved_while_waiting(self):
        # A restart can move the socket, so caching the pre-start path would wait forever on a
        # file that is never going to appear.
        body = self.common_text().split("power_cmux_start() {", 1)[1].split("\n}", 1)[0]
        self.assertIn("power_cmux_alive", body)
        self.assertIn("POWER_CMUX_START_TIMEOUT", body)

    def test_a_start_that_never_answers_is_reported_not_assumed(self):
        self.assertIn("could not start cmux within", self.common_text())


class TestResultContractProse(unittest.TestCase):
    """Whatever the validator rejects, the prompt must have said out loud."""

    SCHEMA = PLUGIN / "templates" / "fleet-result.schema.json"

    def prose(self, stage="plan"):
        script = f'source "{SCRIPTS}/fleet-common.sh"; power_result_contract_prose {stage}'
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
        return out.stdout

    def test_the_prose_states_the_message_cap_the_validator_enforces(self):
        # A real plan stage returned a 507-character message and was rejected for a limit the
        # prompt never mentioned. Codex reads the cap from --output-schema; claude and hermes
        # only ever see this prose, so the number has to be in it.
        cap = json.loads(self.SCHEMA.read_text(encoding="utf-8"))["properties"]["message"]["maxLength"]
        self.assertIn(str(cap), self.prose(), "the prose must name the message length limit")

    def test_the_cap_in_the_prose_is_the_only_number_claimed(self):
        # Guards the drift the file's own comment warns about: a prose cap that no longer matches
        # the schema is worse than none, because it is confidently wrong.
        cap = json.loads(self.SCHEMA.read_text(encoding="utf-8"))["properties"]["message"]["maxLength"]
        numbers = {int(n) for n in re.findall(r"\b\d{2,}\b", self.prose())}
        self.assertEqual(numbers, {cap}, f"prose numbers {numbers} disagree with the schema cap")

    def test_the_runner_reads_the_cap_from_the_schema(self):
        # Three hand-maintained copies of one number is two too many. The schema is the source;
        # the prose quotes it and the runner reads it.
        body = (SCRIPTS / "fleet-run.sh").read_text(encoding="utf-8")
        self.assertIn(".properties.message.maxLength", body)
        self.assertIn("length <= $cap", body, "validate_result must use the schema-derived cap")

    def test_an_over_long_message_is_trimmed_not_failed(self):
        # Real runs came back at 507 and 520 characters with the cap stated in the prompt. The
        # summary is display text; the work is guarded by the contract hashes, not by its length.
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "r.json"
            result.write_text(
                json.dumps({"stage": "plan", "status": "OK", "message": "x" * 640, "verdict": "NONE"}),
                encoding="utf-8",
            )
            script = (
                f'MESSAGE_MAX=500; RESULT_DIR="{tmp}"; '
                + self.normalize_source()
                + f'; normalize_result plan "{result}"'
            )
            run = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            clamped = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(len(clamped["message"]), 500)
            self.assertTrue(clamped["message"].endswith("\u2026"))
            self.assertEqual(clamped["stage"], "plan", "clamping must not touch the other keys")

    def test_a_short_message_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "r.json"
            original = {"stage": "plan", "status": "OK", "message": "short", "verdict": "NONE"}
            result.write_text(json.dumps(original), encoding="utf-8")
            script = (
                f'MESSAGE_MAX=500; RESULT_DIR="{tmp}"; '
                + self.normalize_source()
                + f'; normalize_result plan "{result}"'
            )
            subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.read_text(encoding="utf-8")), original)

    def test_a_missing_verdict_outside_verify_is_defaulted(self):
        # A review stage came back with stage/status/message and no verdict. Outside verify the
        # only legal value is "NONE", so the omission carries nothing and costs a whole stage.
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "r.json"
            result.write_text(
                json.dumps({"stage": "review", "status": "OK", "message": "ok"}), encoding="utf-8"
            )
            script = (
                f'MESSAGE_MAX=500; RESULT_DIR="{tmp}"; '
                + self.normalize_source()
                + f'; normalize_result review "{result}"'
            )
            subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.read_text(encoding="utf-8"))["verdict"], "NONE")

    def test_verify_still_requires_its_own_verdict(self):
        # On verify the verdict is the result. Defaulting it would turn a silent provider into an
        # approval by omission.
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "r.json"
            result.write_text(
                json.dumps({"stage": "verify", "status": "OK", "message": "ok"}), encoding="utf-8"
            )
            script = (
                f'MESSAGE_MAX=500; RESULT_DIR="{tmp}"; '
                + self.normalize_source()
                + f'; normalize_result verify "{result}"'
            )
            subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
            self.assertNotIn("verdict", json.loads(result.read_text(encoding="utf-8")))

    def normalize_source(self):
        text = (SCRIPTS / "fleet-run.sh").read_text(encoding="utf-8")
        return "normalize_result() {" + text.split("normalize_result() {", 1)[1].split("\n}", 1)[0] + "\n}"


class TestPlanContractRebinding(unittest.TestCase):
    """The stage that writes a contract cannot be held to that contract's launch hash."""

    def runner(self):
        return (SCRIPTS / "fleet-run.sh").read_text(encoding="utf-8")

    def function_body(self, name):
        return self.runner().split(f"{name}() {{", 1)[1].split("\n}", 1)[0]

    def test_the_plan_stage_is_guarded_by_the_spec_alone(self):
        # plan.md is the plan stage's own artifact (references/artifacts.md), so a strict check
        # after the provider stops every member on its first stage.
        body = self.function_body("contract_guard_after_provider")
        self.assertIn("spec_matches_bound_member", body)
        self.assertIn("contracts_match_bound_member", body)
        self.assertIn("plan", body, "the exemption must be scoped to the plan stage")

    def test_every_later_stage_keeps_both_contracts_strict(self):
        # The exemption is one stage wide. Anything else may not touch either contract.
        body = self.function_body("contract_guard_after_provider")
        self.assertIn("else contracts_match_bound_member", body)

    def test_the_spec_stays_frozen_even_during_plan(self):
        body = self.function_body("spec_matches_bound_member")
        self.assertIn("spec_sha256", body)
        self.assertNotIn("plan_sha256", body, "the spec guard must not depend on the plan hash")

    def test_the_plan_is_rebound_atomically(self):
        # A member record published by a partial write is a member nothing can validate.
        body = self.function_body("rebind_plan_contract")
        self.assertIn("mktemp", body)
        self.assertIn("mv ", body)
        self.assertIn(".plan_sha256 = $plan", body)
        self.assertIn("[0-9a-f]{64}", body, "a malformed hash must not be published")

    def test_the_rebind_happens_after_the_stage_commit(self):
        # Re-binding to worktree bytes that were never committed would bind the member to a
        # document that does not exist on its branch.
        text = self.runner()
        commit = text.index('commit -m "chore(power-fleet): $SLUG $stage"')
        rebind = text.index("rebind_plan_contract ||")
        self.assertLess(commit, rebind, "the rebind must follow the commit")

    def test_a_failed_rebind_stops_the_member(self):
        self.assertIn("cannot re-bind the plan contract", self.runner())


class TestRawResultPreservation(unittest.TestCase):
    """The answer nobody could parse is the answer you most need to read."""

    def runner(self):
        return (SCRIPTS / "fleet-run.sh").read_text(encoding="utf-8")

    def test_the_raw_answer_survives_an_invalid_result(self):
        # An execute-fix stage exited 0 with empty stdout: the preserved file was zero bytes and
        # the provider's own output had already been deleted.
        text = self.runner()
        invalid = text.index('mv "$CURRENT_RESULT_TEMP" "$invalid_file"')
        raw = text.index('mv "$CURRENT_RAW_TEMP" "$raw_file"')
        needs_human = text.index('needs_human "$stage" "invalid structured result for $stage"')
        self.assertLess(invalid, raw, "both artifacts are preserved on the invalid path")
        self.assertLess(raw, needs_human, "the raw must be kept before the runner exits")

    def test_the_preserved_raw_cannot_ride_along_on_a_merge(self):
        # fleet-run.sh stages with `git add -A`, so a raw provider answer that is not ignored
        # would reach the human's branch on teardown --merge.
        up = (SCRIPTS / "fleet-up.sh").read_text(encoding="utf-8")
        self.assertIn(".planning/power/fleet-results/", up, "fleet-results must be gitignored")


class TestRunnerResume(unittest.TestCase):
    """A member stopped mid-flight restarts where it stopped, not from zero."""

    def runner(self):
        return (SCRIPTS / "fleet-run.sh").read_text(encoding="utf-8")

    def test_every_runtime_wrapper_accepts_the_flag(self):
        # A flag only one runtime understands is a flag that fails on the other two.
        for runtime in ("claude", "codex", "hermes"):
            text = (SCRIPTS / f"{runtime}-fleet-run.sh").read_text(encoding="utf-8")
            self.assertIn("--resume", text, f"{runtime} wrapper must accept --resume")

    def test_the_wrappers_still_reject_an_unknown_argument(self):
        for runtime in ("claude", "codex", "hermes"):
            result = subprocess.run(
                [str(SCRIPTS / f"{runtime}-fleet-run.sh"), "slug", "/tmp", "--wat"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected argument", result.stderr)

    def test_only_a_resume_may_pick_up_a_stopped_member(self):
        # NEEDS_HUMAN asks for a human. The flag is the human answering, so nothing else may
        # start that member.
        body = self.runner().split("member_binding_matches() {", 1)[1].split("\n}", 1)[0]
        self.assertIn('$resume and .status == "NEEDS_HUMAN"', body)

    def test_a_resume_inside_the_loop_skips_the_opening_sequence(self):
        # Re-running plan for a member whose plan finished long ago fails the fresh-artifact
        # check, which is how the single-shot lifecycle showed itself in the first place.
        text = self.runner()
        self.assertIn("if [[ $RESUME_IN_LOOP != true ]]; then", text)
        self.assertIn("if should_run plan;    then run_stage plan;    fi", text)

    def test_a_resumed_cycle_is_not_charged_twice(self):
        # The recorded count already includes the cycle being re-run, and the loop increments
        # before running it; without the decrement the cap arrives one correction early.
        text = self.runner()
        self.assertIn(
            "if [[ $RESUME_STAGE == execute-fix ]]; then CORRECTION_CYCLES=$((CORRECTION_CYCLES - 1)); fi",
            text,
        )

    def test_the_correction_count_is_read_back_within_range(self):
        text = self.runner()
        self.assertIn("select(type == \"number\" and . >= 0 and . <= 2)", text)

    def test_an_unknown_recorded_stage_refuses_to_resume(self):
        self.assertIn("cannot resume: unknown stage", self.runner())

    def test_a_status_from_another_member_refuses_to_resume(self):
        self.assertIn("cannot resume: the runner status does not belong to this member", self.runner())

    def test_the_resume_point_is_consumed_once(self):
        # Consuming it is what makes every stage after the resume point run normally.
        body = self.runner().split("should_run() {", 1)[1].split("\n}", 1)[0]
        self.assertIn("RESUME_STAGE=; return 0", body)


if __name__ == "__main__":
    unittest.main()
