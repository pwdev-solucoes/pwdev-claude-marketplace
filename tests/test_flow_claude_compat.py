import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.flow_m5_fixtures import write_executable


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-flow"
SCRIPTS = PLUGIN / "scripts"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

CLAUDE_COMMANDS = {
    "audit", "compat", "delegate", "design", "discover", "execute",
    "fleet", "health", "init", "maintenance", "memory", "plan",
    "product", "quick", "review", "simplify", "verify",
}

COMMAND_TO_SKILL = {name: f"flow-{name}" for name in CLAUDE_COMMANDS}

EXPECTED_SCRIPTS = {
    "claude-fleet-run.sh",
    "claude-fleet-up.sh",
    "fleet-common.sh",
    "fleet-dashboard.sh",
    "fleet-engine-claude.sh",
    "fleet-engine-codex.sh",
    "fleet-launch-core.sh",
    "fleet-run.sh",
    "fleet-teardown.sh",
    "fleet-up.sh",
    "flow_audit.py",
    "migrate_legacy.py",
    "run-agent.sh",
}


class ClaudeCompatibilityTests(unittest.TestCase):
    def test_claude_manifest_is_native_and_hook_free(self):
        manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "pwdev-flow")
        self.assertEqual(manifest["version"], "0.6.0")
        self.assertFalse({"hooks", "mcpServers", "apps"} & manifest.keys())

    def test_every_claude_command_maps_to_one_portable_skill(self):
        command_files = {p.stem: p for p in (PLUGIN / "commands").glob("*.md")}
        self.assertEqual(set(command_files), CLAUDE_COMMANDS)
        for name, path in command_files.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn("$ARGUMENTS", text)
            self.assertEqual(text.count("$ARGUMENTS"), 1)
            self.assertIn(
                f"${{CLAUDE_PLUGIN_ROOT}}/skills/{COMMAND_TO_SKILL[name]}/SKILL.md",
                text,
            )
            self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", text)

    def test_command_adapters_have_frontmatter_and_safe_resource_paths(self):
        for path in (PLUGIN / "commands").glob("*.md"):
            with self.subTest(command=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(
                    text,
                    r"^---\ndescription: .+\n(?:argument-hint: .+\n)?"
                    r"(?:disable-model-invocation: true\n)?---\n",
                )
                for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}([^\s)`]+)", text):
                    self.assertFalse(".." in Path(target).parts)
                    self.assertTrue((PLUGIN / target.lstrip("/")).is_file())

    def test_privileged_commands_are_user_invoked_only(self):
        """Fleet and delegation spawn privileged processes; the model must not
        reach for them on its own. The user can still type the slash command."""
        for name in ("fleet", "delegate"):
            with self.subTest(command=name):
                text = (PLUGIN / "commands" / f"{name}.md").read_text(encoding="utf-8")
                self.assertIn("disable-model-invocation: true", text)

    def test_claude_marketplace_registers_strict_local_plugin(self):
        marketplace = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["pwdev-flow"]
        self.assertEqual(entry["source"], "./plugins/pwdev-flow")
        self.assertEqual(entry["category"], "workflow")
        self.assertTrue(entry["strict"])

    def test_public_docs_describe_dual_runtime_commands(self):
        for readme in (ROOT / "README.md", ROOT / "README.pt-BR.md"):
            text = readme.read_text(encoding="utf-8")
            with self.subTest(readme=readme.name):
                self.assertIn("pwdev-flow", text)
                self.assertIn("claude -p", text)
                self.assertIn("codex exec", text)
                for command in CLAUDE_COMMANDS:
                    self.assertIn(f"/pwdev-flow:{command}", text)

    def test_codex_version_is_new_compatible_base(self):
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertRegex(manifest["version"], r"^0\.6\.0(?:\+codex\.\d{14})?$")

    def test_dual_runtime_script_inventory_is_exact(self):
        actual = {p.name for p in (PLUGIN / "scripts").iterdir() if p.is_file()}
        self.assertEqual(actual, EXPECTED_SCRIPTS)

    def test_no_claude_hooks_agents_mcp_or_apps_are_packaged(self):
        manifest = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse({"hooks", "agents", "mcpServers", "apps"} & manifest.keys())
        self.assertFalse((PLUGIN / "hooks").exists())
        self.assertFalse((PLUGIN / "agents").exists())

    def test_native_engines_keep_privileged_vectors_separate(self):
        codex = (PLUGIN / "scripts/fleet-engine-codex.sh").read_text(encoding="utf-8")
        claude = (PLUGIN / "scripts/fleet-engine-claude.sh").read_text(encoding="utf-8")
        self.assertIn("codex exec", codex)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", codex)
        self.assertIn("claude -p", claude)
        self.assertNotIn("codex exec", claude)
        self.assertNotIn("--sandbox", claude)
        self.assertNotIn("--dangerously-skip-permissions", codex)

    def test_only_the_adapters_construct_a_provider_command(self):
        """The shared runner must never name a provider or a permission flag."""
        runner = (PLUGIN / "scripts/fleet-run.sh").read_text(encoding="utf-8")
        for forbidden in (
            "codex exec",
            "claude -p",
            "--dangerously-bypass-approvals-and-sandbox",
            "--dangerously-skip-permissions",
            "--output-last-message",
            "--output-format",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, runner)

    def test_claude_launcher_and_runner_reach_the_shared_lifecycle(self):
        launcher = (PLUGIN / "scripts/claude-fleet-up.sh").read_text(encoding="utf-8")
        runner = (PLUGIN / "scripts/claude-fleet-run.sh").read_text(encoding="utf-8")
        self.assertIn('fleet-launch-core.sh" claude', launcher)
        self.assertIn("fleet-up.sh", launcher)
        # The Claude pane runs the same autonomous runner as Codex.
        self.assertIn('fleet-run.sh" "$@"', runner)

    def test_claude_runner_exports_runtime_identity(self):
        runner = (PLUGIN / "scripts/claude-fleet-run.sh").read_text(encoding="utf-8")
        self.assertRegex(runner, r"FLOW_FLEET_RUNTIME=claude")


class NativeRuntimeAdapterBehaviourTest(unittest.TestCase):
    """Execute the runtime adapters instead of grepping them.

    The string assertions above pass even when a dispatcher defines a function it
    never calls, which is exactly how a silently no-op Claude fleet path shipped.
    These tests run the scripts with stubbed provider binaries and assert on the
    observable effect: the process that gets executed and the arguments it receives.
    """

    def run_script(self, script, *args, path_prefix=None, cwd=None):
        environment = os.environ.copy()
        if path_prefix is not None:
            environment["PATH"] = f"{path_prefix}{os.pathsep}{environment['PATH']}"
        environment["LC_ALL"] = "C"
        return subprocess.run(
            ["/bin/bash", str(SCRIPTS / script), *args],
            cwd=str(cwd) if cwd is not None else None,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

    def stub_provider(self, directory, name):
        """Install a stub that records its argument vector, one argument per line."""
        fake_bin = Path(directory) / "bin"
        fake_bin.mkdir(exist_ok=True)
        record = Path(directory) / f"{name}-args.txt"
        write_executable(
            fake_bin / name,
            f'for argument in "$@"; do printf "%s\\n" "$argument"; done > {record}',
        )
        return fake_bin, record

    def test_launch_core_executes_its_command_and_exports_the_runtime(self):
        for runtime in ("codex", "claude"):
            with self.subTest(runtime=runtime):
                result = self.run_script(
                    "fleet-launch-core.sh",
                    runtime,
                    "/bin/sh",
                    "-c",
                    'printf "%s" "$FLOW_FLEET_RUNTIME"',
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, runtime)

    def adapter_stage_command(self, runtime, worktree="/wt", schema="/schema.json",
                              result="/result.json", prompt="stage prompt"):
        """Source an adapter and print the vector it builds, one argument per line."""
        script = (
            f'source "{SCRIPTS}/fleet-engine-{runtime}.sh"\n'
            f'flow_engine_{runtime}_stage_command "{worktree}" "{schema}" "{result}" "{prompt}"\n'
            'printf "cwd=%s\\n" "$FLOW_ENGINE_CWD"\n'
            'printf "stdout_result=%s\\n" "$FLOW_ENGINE_RESULT_FROM_STDOUT"\n'
            'for argument in "${FLOW_ENGINE_COMMAND[@]}"; do printf "%s\\n" "$argument"; done\n'
        )
        completed = subprocess.run(
            ["/bin/bash", "-c", script], check=True, capture_output=True, text=True
        )
        lines = completed.stdout.splitlines()
        return lines[0].split("=", 1)[1], lines[1].split("=", 1)[1], lines[2:]

    def test_codex_adapter_builds_the_exact_approved_vector(self):
        cwd, from_stdout, command = self.adapter_stage_command("codex")
        self.assertEqual(
            command,
            ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", "--ephemeral",
             "--cd", "/wt", "--output-schema", "/schema.json",
             "--output-last-message", "/result.json", "stage prompt"],
        )
        # Codex takes --cd and writes the result itself.
        self.assertEqual(cwd, "")
        self.assertEqual(from_stdout, "false")

    def test_claude_adapter_builds_the_exact_native_vector(self):
        cwd, from_stdout, command = self.adapter_stage_command("claude")
        self.assertEqual(
            command,
            ["claude", "-p", "--dangerously-skip-permissions", "--no-session-persistence",
             "--output-format", "json", "stage prompt"],
        )
        # Claude has no --cd and reports its final message on stdout.
        self.assertEqual(cwd, "/wt")
        self.assertEqual(from_stdout, "true")

    def test_adapters_never_cross_contaminate_privileged_flags(self):
        for runtime, forbidden in (
            ("claude", "--dangerously-bypass-approvals-and-sandbox"),
            ("claude", "--ephemeral"),
            ("claude", "--output-schema"),
            ("codex", "--dangerously-skip-permissions"),
            ("codex", "--output-format"),
        ):
            with self.subTest(runtime=runtime, forbidden=forbidden):
                _, _, command = self.adapter_stage_command(runtime)
                self.assertNotIn(forbidden, command)

    def test_claude_adapter_publishes_only_a_well_formed_result(self):
        good = json.dumps({"stage": "plan", "status": "OK", "message": "done", "verdict": "NONE"})
        cases = (
            ("plain envelope", {"is_error": False, "result": good}, True),
            ("fenced result", {"is_error": False, "result": f"```json\n{good}\n```"}, True),
            ("provider error", {"is_error": True, "result": good}, False),
            ("prose instead of json", {"is_error": False, "result": "I finished the plan."}, False),
            ("envelope without result", {"is_error": False, "type": "result"}, False),
        )
        for label, envelope, expected in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as directory:
                raw = Path(directory) / "raw.json"
                out = Path(directory) / "out.json"
                raw.write_text(json.dumps(envelope), encoding="utf-8")
                completed = subprocess.run(
                    ["/bin/bash", "-c",
                     f'source "{SCRIPTS}/fleet-engine-claude.sh"\n'
                     f'flow_engine_claude_publish_result "{raw}" "{out}"'],
                    check=False, capture_output=True, text=True,
                )
                if expected:
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(json.loads(out.read_text(encoding="utf-8")), json.loads(good))
                else:
                    self.assertNotEqual(completed.returncode, 0)
                    # Fails closed: the runner rejects an empty result file.
                    self.assertEqual(out.read_text(encoding="utf-8"), "")

    def test_unsupported_runtime_fails_closed_before_any_effect(self):
        result = self.run_script("fleet-launch-core.sh", "gemini", "/bin/echo", "must-not-run")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported fleet runtime", result.stderr)
        self.assertNotIn("must-not-run", result.stdout)

    def test_launch_core_rejects_a_missing_payload(self):
        result = self.run_script("fleet-launch-core.sh", "claude")
        self.assertEqual(result.returncode, 2)
        self.assertNotEqual(result.stderr.strip(), "")

    def test_claude_runner_validates_slug_and_permission_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            worktree = Path(directory)
            for arguments, expected in (
                (("Bad-Slug", str(worktree)), "invalid slug"),
                (("demo", str(worktree), "full-access"), "permission mode"),
            ):
                with self.subTest(arguments=arguments):
                    result = self.run_script("claude-fleet-run.sh", *arguments)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
