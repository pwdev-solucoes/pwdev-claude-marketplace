"""pwdev-skills packaging for Claude Code, Codex and Hermes Agent (OpenCode loads the skill folder directly).

The plugin ships one skill. These tests pin what each runtime needs to find it: consistent
manifests, the Codex skills path and interface, and a Hermes adapter that registers exactly that
skill as a pathlib.Path in both install layouts, with no hook and a closed inventory.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-skills"
SKILL = PLUGIN / "skills" / "skill-refactor"
ADAPTER = PLUGIN / ".hermes-plugin" / "__init__.py"


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location(f"pwdev_skills_hermes_{abs(hash(str(path)))}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RecordingContext:
    """Hermes context double: rejects string paths and any hook, as the adapter must use neither."""

    def __init__(self):
        self.skills = []

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError("register_skill requires a pathlib.Path; a str disables the plugin in Hermes")
        self.skills.append((name, path))

    def register_hook(self, *_args, **_kwargs):
        raise AssertionError("pwdev-skills must not register hooks")


class ManifestTest(unittest.TestCase):
    def test_three_manifests_agree_on_identity(self):
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        hermes = (PLUGIN / ".hermes-plugin" / "plugin.yaml").read_text(encoding="utf-8")
        hermes_fields = dict(re.findall(r"^(\w+):\s*(.+)$", hermes, re.M))
        self.assertEqual(claude["name"], "pwdev-skills")
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(hermes_fields["name"], claude["name"])
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(hermes_fields["version"], claude["version"])
        for manifest in (claude, codex):
            self.assertEqual(manifest["license"], "Apache-2.0")
            self.assertNotIn("hooks", manifest)
            self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", hermes_fields)
        self.assertNotIn("provides_hooks", hermes_fields)

    def test_codex_discovers_the_skill_and_its_interface(self):
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue((PLUGIN / codex["skills"] / "skill-refactor" / "SKILL.md").is_file())
        for field in ("displayName", "shortDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("display_name:", openai)
        self.assertIn("$skill-refactor", openai)

    def test_the_plugin_ships_exactly_one_skill_and_no_claude_extras(self):
        self.assertEqual([p.parent.name for p in PLUGIN.rglob("SKILL.md")], ["skill-refactor"])
        for absent in ("commands", "agents", "hooks", ".mcp.json"):
            self.assertFalse((PLUGIN / absent).exists(), absent)

    def test_skill_body_never_names_the_instruction_files_hermes_filters(self):
        # Hermes silently drops a registered skill whose body contains these literals.
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("CLAUDE.md", body)
        self.assertNotIn("AGENTS.md", body)

    def test_marketplace_catalogs_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        claude_entries = [p for p in claude["plugins"] if p["name"] == "pwdev-skills"]
        codex_entries = [p for p in codex["plugins"] if p["name"] == "pwdev-skills"]
        self.assertEqual(len(claude_entries), 1)
        self.assertEqual(len(codex_entries), 1)
        self.assertEqual(claude_entries[0]["source"], "./plugins/pwdev-skills")
        self.assertTrue(claude_entries[0]["strict"])
        self.assertEqual(codex_entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-skills"})

    def test_the_skill_left_pwdev_code(self):
        self.assertFalse((ROOT / "plugins" / "pwdev-code" / "skills" / "skill-refactor").exists())
        for readme in ("README.md", "README.pt-BR.md"):
            self.assertNotIn("skill-refactor", (ROOT / "plugins" / "pwdev-code" / readme).read_text(encoding="utf-8"))


class HermesAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def clone_layout(self) -> Path:
        plugin = self.root / "clone" / "pwdev-skills"
        (plugin / ".hermes-plugin").mkdir(parents=True)
        shutil.copy(ADAPTER, plugin / ".hermes-plugin" / "__init__.py")
        shutil.copytree(PLUGIN / "skills", plugin / "skills")
        return plugin / ".hermes-plugin" / "__init__.py"

    def flat_layout(self) -> Path:
        plugin = self.root / "flat" / "pwdev-skills"
        plugin.mkdir(parents=True)
        shutil.copy(ADAPTER, plugin / "__init__.py")
        shutil.copytree(PLUGIN / "skills", plugin / "skills")
        return plugin / "__init__.py"

    def test_registers_exactly_the_skill_as_a_path_in_both_layouts(self):
        for adapter in (self.clone_layout(), self.flat_layout()):
            with self.subTest(layout=adapter.parent.name):
                ctx = RecordingContext()
                load_adapter(adapter).register(ctx)
                self.assertEqual([name for name, _ in ctx.skills], ["skill-refactor"])
                path = ctx.skills[0][1]
                self.assertIsInstance(path, Path)
                self.assertEqual(path.name, "SKILL.md")
                self.assertTrue(path.is_file())

    def test_the_repository_adapter_registers_the_real_skill(self):
        ctx = RecordingContext()
        load_adapter(ADAPTER).register(ctx)
        self.assertEqual(ctx.skills, [("skill-refactor", (SKILL / "SKILL.md").resolve())])

    def test_rejects_an_extra_or_missing_skill(self):
        adapter = self.clone_layout()
        skills = adapter.parent.parent / "skills"
        (skills / "stray").mkdir()
        (skills / "stray" / "SKILL.md").write_text("---\nname: stray\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "invalid skills inventory"):
            load_adapter(adapter).register(RecordingContext())
        shutil.rmtree(skills / "stray")
        shutil.rmtree(skills / "skill-refactor")
        with self.assertRaisesRegex(RuntimeError, "invalid skills inventory"):
            load_adapter(adapter).register(RecordingContext())

    def test_rejects_symlinked_skill_trees(self):
        adapter = self.clone_layout()
        skill = adapter.parent.parent / "skills" / "skill-refactor"
        outside = self.root / "outside"
        shutil.move(str(skill), str(outside))
        skill.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "unsafe skills tree"):
            load_adapter(adapter).register(RecordingContext())

    def test_missing_skills_directory_fails_before_any_registration(self):
        adapter = self.clone_layout()
        shutil.rmtree(adapter.parent.parent / "skills")
        ctx = RecordingContext()
        with self.assertRaisesRegex(RuntimeError, "skills directory not found"):
            load_adapter(adapter).register(ctx)
        self.assertEqual(ctx.skills, [])


INSTALLER = PLUGIN / ".opencode-plugin" / "install.py"


class OpenCodeInstallerTest(unittest.TestCase):
    """OpenCode reads skill folders, not plugins: the installer links or copies ours there, and only ours."""

    def setUp(self):
        self.installer = load_adapter(INSTALLER)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "plugin"
        (self.plugin / "skills" / "skill-refactor").mkdir(parents=True)
        (self.plugin / "skills" / "skill-refactor" / "SKILL.md").write_text("---\nname: skill-refactor\n---\n# x\n")
        (self.plugin / "skills" / "skill-refactor" / "__pycache__").mkdir()
        (self.plugin / "skills" / "skill-refactor" / "__pycache__" / "m.pyc").write_bytes(b"x")
        (self.plugin / "skills" / "not-a-skill").mkdir()  # no SKILL.md: ignored
        self.config = self.root / "xdg"
        self._env = dict(os.environ)
        os.environ["XDG_CONFIG_HOME"] = str(self.config)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def run_installer(self, *args: str) -> int:
        return self.installer.main(["--root", str(self.plugin), *args])

    def test_links_every_skill_into_the_global_dir_and_is_idempotent(self):
        self.assertEqual(self.run_installer(), 0)
        target = self.config / "opencode" / "skills" / "skill-refactor"
        self.assertTrue(target.is_symlink())
        self.assertEqual(target.resolve(), (self.plugin / "skills" / "skill-refactor").resolve())
        self.assertFalse((self.config / "opencode" / "skills" / "not-a-skill").exists())
        self.assertEqual(self.run_installer(), 0)  # second run: nothing to redo, no error
        self.assertTrue(target.is_symlink())

    def test_project_scope_uses_the_opencode_folder_of_that_project(self):
        project = self.root / "proj"
        project.mkdir()
        self.assertEqual(self.run_installer("--project", str(project)), 0)
        self.assertTrue((project / ".opencode" / "skills" / "skill-refactor" / "SKILL.md").is_file())
        self.assertFalse((self.config / "opencode").exists())

    def test_copy_mode_copies_without_caches_and_marks_the_copy(self):
        self.assertEqual(self.run_installer("--copy"), 0)
        target = self.config / "opencode" / "skills" / "skill-refactor"
        self.assertFalse(target.is_symlink())
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertTrue((target / self.installer.MARKER).is_file())
        self.assertFalse((target / "__pycache__").exists())

    def test_refuses_to_replace_a_skill_it_did_not_install_unless_forced(self):
        foreign = self.config / "opencode" / "skills" / "skill-refactor"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("the user's own\n")
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual((foreign / "SKILL.md").read_text(), "the user's own\n")
        self.assertEqual(self.run_installer("--uninstall"), 0)
        self.assertTrue(foreign.is_dir())  # never removes what it did not install
        self.assertEqual(self.run_installer("--force"), 0)
        self.assertTrue(foreign.is_symlink())

    def test_uninstall_removes_links_and_marked_copies_only(self):
        self.run_installer()
        self.assertEqual(self.run_installer("--uninstall"), 0)
        self.assertFalse((self.config / "opencode" / "skills" / "skill-refactor").exists())
        self.run_installer("--copy")
        self.assertEqual(self.run_installer("--uninstall"), 0)
        self.assertFalse((self.config / "opencode" / "skills" / "skill-refactor").exists())

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.run_installer("--dry-run"), 0)
        self.assertFalse((self.config / "opencode").exists())

    def test_real_plugin_has_exactly_one_installable_skill(self):
        self.assertEqual([p.name for p in self.installer.skills_of(PLUGIN)], ["skill-refactor"])


if __name__ == "__main__":
    unittest.main()
