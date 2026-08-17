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
    "fleet-run-core.sh",
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
                self.assertRegex(text, r"^---\ndescription: .+\n(?:argument-hint: .+\n)?---\n")
                for target in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}([^\s)`]+)", text):
                    self.assertFalse(".." in Path(target).parts)
                    self.assertTrue((PLUGIN / target.lstrip("/")).is_file())

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
        self.assertIn("--sandbox danger-full-access", codex)
        self.assertIn("claude -p", claude)
        self.assertNotIn("codex exec", claude)
        self.assertNotIn("--sandbox", claude)

    def test_claude_launcher_selects_claude_runner(self):
        launcher = (PLUGIN / "scripts/claude-fleet-up.sh").read_text(encoding="utf-8")
        runner = (PLUGIN / "scripts/claude-fleet-run.sh").read_text(encoding="utf-8")
        self.assertIn('fleet-launch-core.sh" claude', launcher)
        self.assertIn('fleet-run-core.sh" claude', runner)

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

    def test_run_core_invokes_the_matching_engine_with_the_native_vector(self):
        expected = {
            "claude": [
                "-p",
                "--dangerously-skip-permissions",
                "--no-session-persistence",
                "--output-format",
                "json",
                "stage prompt",
            ],
            "codex": [
                "exec",
                "--sandbox",
                "danger-full-access",
                "-c",
                "approval_policy=never",
                "--add-dir",
            ],
        }
        for runtime, binary in (("claude", "claude"), ("codex", "codex")):
            with self.subTest(runtime=runtime), tempfile.TemporaryDirectory() as directory:
                fake_bin, record = self.stub_provider(directory, binary)

                result = self.run_script(
                    "fleet-run-core.sh", runtime, "stage prompt", path_prefix=fake_bin
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(record.exists(), f"{binary} stub was never executed")
                arguments = record.read_text(encoding="utf-8").splitlines()
                if runtime == "claude":
                    self.assertEqual(arguments, expected["claude"])
                else:
                    self.assertEqual(arguments[: len(expected["codex"])], expected["codex"])
                    self.assertEqual(arguments[-1], "stage prompt")

    def test_engines_never_cross_contaminate_privileged_flags(self):
        for runtime, binary, forbidden in (
            ("claude", "claude", "--dangerously-bypass-approvals-and-sandbox"),
            ("claude", "claude", "danger-full-access"),
            ("codex", "codex", "--dangerously-skip-permissions"),
        ):
            with self.subTest(runtime=runtime, forbidden=forbidden), tempfile.TemporaryDirectory() as directory:
                fake_bin, record = self.stub_provider(directory, binary)

                self.run_script("fleet-run-core.sh", runtime, "stage prompt", path_prefix=fake_bin)

                self.assertNotIn(forbidden, record.read_text(encoding="utf-8").splitlines())

    def test_unsupported_runtime_fails_closed_before_any_effect(self):
        for script, extra in (
            ("fleet-launch-core.sh", ("/bin/echo", "must-not-run")),
            ("fleet-run-core.sh", ("stage prompt",)),
        ):
            with self.subTest(script=script):
                result = self.run_script(script, "gemini", *extra)
                self.assertEqual(result.returncode, 2)
                self.assertIn("unsupported fleet runtime", result.stderr)
                self.assertNotIn("must-not-run", result.stdout)

    def test_core_dispatchers_reject_a_missing_payload(self):
        for script in ("fleet-launch-core.sh", "fleet-run-core.sh"):
            with self.subTest(script=script):
                result = self.run_script(script, "claude")
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

    def test_claude_runner_accepts_the_pane_permission_mode_argument(self):
        """fleet-up.sh writes a three-argument pane vector; the runner must accept it."""
        with tempfile.TemporaryDirectory() as directory:
            fake_bin, record = self.stub_provider(directory, "claude")
            worktree = Path(directory) / "worktree"
            worktree.mkdir()

            result = self.run_script(
                "claude-fleet-run.sh",
                "demo",
                str(worktree),
                "danger-full-access",
                path_prefix=fake_bin,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            arguments = record.read_text(encoding="utf-8").splitlines()
            self.assertIn("demo", arguments[-1])
            self.assertNotIn("danger-full-access", arguments)


if __name__ == "__main__":
    unittest.main()
