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


if __name__ == "__main__":
    unittest.main()
