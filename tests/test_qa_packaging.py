"""Packaging contract tests for the PWDEV QA plugin."""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
HERMES_MANIFEST = PLUGIN / ".hermes-plugin" / "plugin.yaml"
HERMES_INIT = PLUGIN / ".hermes-plugin" / "__init__.py"

EXPECTED_SKILLS = tuple(sorted({
    "qa",
    "qa-tooling",
    "qa-init",
    "qa-strategy",
    "qa-test",
    "qa-explore",
    "qa-bug",
    "qa-regression",
    "qa-review",
    "qa-release",
    "qa-report",
    "qa-status",
    "qa-specialist-accessibility",
    "qa-specialist-api",
    "qa-specialist-automation",
    "qa-specialist-cicd",
    "qa-specialist-data",
    "qa-specialist-defects",
    "qa-specialist-functional",
    "qa-specialist-metrics",
    "qa-specialist-mobile",
    "qa-specialist-performance",
    "qa-specialist-production",
    "qa-specialist-readiness",
    "qa-specialist-regression",
    "qa-specialist-requirements",
    "qa-specialist-security",
    "qa-specialist-strategy",
    "qa-specialist-web",
}))


def load_adapter(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_flat_yaml(path):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith((" ", "-")) and ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip().strip('"').strip("'")
    return values


class RecordingContext:
    def __init__(self):
        self.calls = []

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise AttributeError("register_skill requires pathlib.Path")
        self.calls.append((name, path))

    def register_hook(self, *args, **kwargs):
        raise AssertionError("PWDEV QA must not register intrusive hooks")


class TestManifests(unittest.TestCase):
    def test_runtime_manifests_are_equivalent_and_non_intrusive(self):
        for path in (CLAUDE_MANIFEST, CODEX_MANIFEST, HERMES_MANIFEST):
            self.assertTrue(path.is_file(), f"missing manifest: {path}")

        claude = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        codex = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))
        hermes = parse_flat_yaml(HERMES_MANIFEST)

        for manifest in (claude, codex, hermes):
            self.assertEqual(manifest["name"], "pwdev-qa")
            self.assertEqual(manifest["version"], "0.1.0")
            self.assertEqual(manifest["repository"], "https://github.com/pwdev-solucoes/pwdev-claude-marketplace")
            self.assertEqual(manifest["license"], "Apache-2.0")

        self.assertEqual(claude["author"], codex["author"])
        self.assertEqual(claude["author"]["name"], hermes["author"])
        self.assertEqual(claude["description"], codex["description"])
        self.assertEqual(claude["description"], hermes["description"])
        self.assertEqual(codex["skills"], "./skills/")
        self.assertLessEqual(len(codex["interface"]["defaultPrompt"]), 3)

        for data in (claude, codex):
            self.assertNotIn("hooks", data)
            self.assertNotIn("mcpServers", data)
        hermes_text = HERMES_MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn("provides_hooks", hermes_text)
        self.assertNotIn("mcp", hermes_text.lower())


class TestHermesRegistration(unittest.TestCase):
    def stage_adapter(self, root, layout="clone"):
        plugin_root = root / "pwdev-qa"
        adapter_root = plugin_root / ".hermes-plugin" if layout == "clone" else plugin_root
        adapter_root.mkdir(parents=True)
        shutil.copytree(PLUGIN / "skills", plugin_root / "skills")
        shutil.copy(HERMES_INIT, adapter_root / "__init__.py")
        return plugin_root, adapter_root / "__init__.py"

    def test_repository_layout_registers_exactly_the_29_installed_skills(self):
        self.assertTrue(HERMES_INIT.is_file(), f"missing adapter: {HERMES_INIT}")
        module = load_adapter(HERMES_INIT, "qa_hermes_repository")
        context = RecordingContext()

        result = module.register(context)

        self.assertIsNone(result)
        expected_calls = [(name, PLUGIN / "skills" / name / "SKILL.md") for name in EXPECTED_SKILLS]
        self.assertEqual(context.calls, expected_calls)
        self.assertEqual(len(context.calls), 29)
        for name, path in context.calls:
            self.assertIsInstance(path, Path)
            self.assertEqual(path, PLUGIN / "skills" / name / "SKILL.md")
            self.assertTrue(path.is_file())

    def test_clone_and_flattened_layouts_are_supported(self):
        self.assertTrue(HERMES_INIT.is_file(), f"missing adapter: {HERMES_INIT}")
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            for layout in ("clone", "flattened"):
                with self.subTest(layout=layout):
                    plugin_root, adapter = self.stage_adapter(temporary_root / layout, layout)
                    module = load_adapter(adapter, f"qa_hermes_{layout}")
                    context = RecordingContext()
                    self.assertIsNone(module.register(context))
                    expected = [
                        (name, plugin_root.resolve() / "skills" / name / "SKILL.md")
                        for name in EXPECTED_SKILLS
                    ]
                    self.assertEqual(context.calls, expected)
                    self.assertTrue(all(isinstance(path, Path) for _, path in context.calls))

    def test_missing_skills_tree_fails_safely_without_partial_registration(self):
        self.assertTrue(HERMES_INIT.is_file(), f"missing adapter: {HERMES_INIT}")
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter_root = Path(temporary_directory) / "pwdev-qa" / ".hermes-plugin"
            adapter_root.mkdir(parents=True)
            shutil.copy(HERMES_INIT, adapter_root / "__init__.py")
            module = load_adapter(adapter_root / "__init__.py", "qa_hermes_missing")
            context = RecordingContext()

            with self.assertRaisesRegex(RuntimeError, "skills directory not found"):
                module.register(context)

            self.assertEqual(context.calls, [])

    def test_incomplete_or_extra_inventory_fails_before_registration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            for variant in ("missing", "extra"):
                with self.subTest(variant=variant):
                    plugin_root, adapter = self.stage_adapter(temporary_root / variant)
                    if variant == "missing":
                        shutil.rmtree(plugin_root / "skills" / EXPECTED_SKILLS[0])
                    else:
                        unexpected = plugin_root / "skills" / "qa-unexpected"
                        unexpected.mkdir()
                        (unexpected / "SKILL.md").write_text("---\nname: qa-unexpected\n---\n", encoding="utf-8")
                    module = load_adapter(adapter, f"qa_hermes_inventory_{variant}")
                    context = RecordingContext()

                    with self.assertRaisesRegex(RuntimeError, "invalid skills inventory"):
                        module.register(context)

                    self.assertEqual(context.calls, [])

    def test_symlinked_root_directory_or_file_is_rejected_before_registration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            for variant in ("root", "directory", "file"):
                with self.subTest(variant=variant):
                    external = temporary_root / f"external-{variant}"
                    shutil.copytree(PLUGIN / "skills", external)
                    plugin_root, adapter = self.stage_adapter(temporary_root / variant)
                    skills_root = plugin_root / "skills"
                    target_name = EXPECTED_SKILLS[0]
                    if variant == "root":
                        shutil.rmtree(skills_root)
                        skills_root.symlink_to(external, target_is_directory=True)
                    elif variant == "directory":
                        shutil.rmtree(skills_root / target_name)
                        (skills_root / target_name).symlink_to(
                            external / target_name,
                            target_is_directory=True,
                        )
                    else:
                        skill_file = skills_root / target_name / "SKILL.md"
                        skill_file.unlink()
                        skill_file.symlink_to(external / target_name / "SKILL.md")
                    module = load_adapter(adapter, f"qa_hermes_symlink_{variant}")
                    context = RecordingContext()

                    with self.assertRaisesRegex(RuntimeError, "unsafe skills tree"):
                        module.register(context)

                    self.assertEqual(context.calls, [])

    def test_callback_failure_stops_without_claiming_impossible_rollback(self):
        class FailingContext(RecordingContext):
            def register_skill(self, name, path):
                super().register_skill(name, path)
                if len(self.calls) == 2:
                    raise RuntimeError("callback failed")

        module = load_adapter(HERMES_INIT, "qa_hermes_callback_failure")
        context = FailingContext()

        with self.assertRaisesRegex(RuntimeError, "callback failed"):
            module.register(context)

        expected = [
            (name, PLUGIN / "skills" / name / "SKILL.md")
            for name in EXPECTED_SKILLS[:2]
        ]
        self.assertEqual(context.calls, expected)


if __name__ == "__main__":
    unittest.main()
