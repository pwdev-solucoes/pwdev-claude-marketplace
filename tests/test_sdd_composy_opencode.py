"""sdd-composy on OpenCode: the installer links the 17 skills and generates 17 commands, and only those.

OpenCode has no plugin mechanism for Agent Skills. It discovers ``<name>/SKILL.md`` folders under
``.opencode/skills/`` (project) or ``~/.config/opencode/skills/`` (global) and custom commands under
the sibling ``command/`` folder. The installer links each skill folder (never copies: every SKILL.md
reaches ``scripts/``, ``references/`` and ``templates/`` by plugin-relative path, which resolves through
a symlink but not through a copy) and writes one ``sdd-<name>.md`` command per Claude command.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
INSTALLER = PLUGIN / ".opencode-plugin" / "install.py"
NAMES = ("evidence", "execute", "fleet", "init", "loop", "map", "prd", "qa", "quick", "review",
         "status", "stories", "sync", "tasks", "techspec", "trace", "verify")


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location(f"sdd_composy_opencode_{abs(hash(str(path)))}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OpenCodeInstallerTest(unittest.TestCase):
    def setUp(self):
        self.installer = load_adapter(INSTALLER)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "plugin"
        for name in NAMES:
            skill = self.plugin / "skills" / f"sdd-{name}"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(f"---\nname: sdd-{name}\n---\n# x\n")
            (self.plugin / "commands").mkdir(exist_ok=True)
            (self.plugin / "commands" / f"{name}.md").write_text(
                f"---\ndescription: Do {name} for SDD Composy\nargument-hint: \"<x>\"\n---\n\n"
                f"Route to `$sdd-{name}`. Read `${{CLAUDE_PLUGIN_ROOT}}/skills/sdd-{name}/SKILL.md`.\n")
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

    def dest(self) -> Path:
        return self.config / "opencode"

    def test_links_every_skill_and_generates_every_command_idempotently(self):
        self.assertEqual(self.run_installer(), 0)
        for name in NAMES:
            target = self.dest() / "skills" / f"sdd-{name}"
            self.assertTrue(target.is_symlink(), name)
            self.assertEqual(target.resolve(), (self.plugin / "skills" / f"sdd-{name}").resolve())
            command = self.dest() / "command" / f"sdd-{name}.md"
            text = command.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\ndescription: Do {name} for SDD Composy\n---\n"), text)
            self.assertIn("$ARGUMENTS", text)
            self.assertIn(f"`sdd-{name}`", text)
            self.assertIn(self.installer.COMMAND_MARKER, text)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
            self.assertNotIn("argument-hint", text)
        self.assertEqual(len(list((self.dest() / "skills").iterdir())), 17)
        self.assertEqual(len(list((self.dest() / "command").iterdir())), 17)
        self.assertFalse((self.dest() / "skills" / "not-a-skill").exists())
        self.assertFalse((self.dest() / "opencode.json").exists())
        self.assertEqual(self.run_installer(), 0)  # second run: nothing to redo, no error
        self.assertTrue((self.dest() / "skills" / "sdd-init").is_symlink())

    def test_project_scope_uses_the_opencode_folder_of_that_project(self):
        project = self.root / "proj"
        project.mkdir()
        self.assertEqual(self.run_installer("--project", str(project)), 0)
        self.assertTrue((project / ".opencode" / "skills" / "sdd-init" / "SKILL.md").is_file())
        self.assertTrue((project / ".opencode" / "command" / "sdd-init.md").is_file())
        self.assertFalse(self.dest().exists())

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.run_installer("--dry-run"), 0)
        self.assertFalse(self.dest().exists())

    def test_copy_is_not_an_option(self):
        with self.assertRaises(SystemExit):
            self.run_installer("--copy")
        self.assertFalse(self.dest().exists())

    def test_refuses_to_replace_what_it_did_not_install_unless_forced(self):
        foreign = self.dest() / "skills" / "sdd-init"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("the user's own\n")
        own_command = self.dest() / "command" / "sdd-prd.md"
        own_command.parent.mkdir(parents=True)
        own_command.write_text("---\ndescription: mine\n---\nmy prompt\n")
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual((foreign / "SKILL.md").read_text(), "the user's own\n")
        self.assertEqual(own_command.read_text(), "---\ndescription: mine\n---\nmy prompt\n")
        self.assertEqual(self.run_installer("--uninstall"), 0)
        self.assertTrue(foreign.is_dir())  # never removes what it did not install
        self.assertTrue(own_command.is_file())
        self.assertEqual(self.run_installer("--force"), 0)
        self.assertTrue(foreign.is_symlink())
        self.assertIn(self.installer.COMMAND_MARKER, own_command.read_text())

    def test_uninstall_removes_only_its_links_and_generated_commands(self):
        self.run_installer()
        stranger = self.dest() / "skills" / "other-skill"
        stranger.mkdir()
        (stranger / "SKILL.md").write_text("keep\n")
        (self.dest() / "command" / "deploy.md").write_text("---\ndescription: keep\n---\nkeep\n")
        self.assertEqual(self.run_installer("--uninstall"), 0)
        for name in NAMES:
            self.assertFalse((self.dest() / "skills" / f"sdd-{name}").exists(), name)
            self.assertFalse((self.dest() / "command" / f"sdd-{name}.md").exists(), name)
        self.assertTrue((stranger / "SKILL.md").is_file())
        self.assertTrue((self.dest() / "command" / "deploy.md").is_file())

    def test_rejects_a_symlinked_skills_tree(self):
        real = self.root / "elsewhere"
        (self.plugin / "skills").rename(real)
        (self.plugin / "skills").symlink_to(real, target_is_directory=True)
        self.assertNotEqual(self.run_installer(), 0)
        self.assertFalse(self.dest().exists())

    def test_rejects_a_skill_whose_skill_md_is_not_a_regular_file(self):
        (self.plugin / "skills" / "sdd-init" / "SKILL.md").unlink()
        (self.plugin / "skills" / "sdd-init" / "SKILL.md").symlink_to(self.plugin / "skills" / "sdd-map" / "SKILL.md")
        self.assertNotEqual(self.run_installer(), 0)
        self.assertFalse(self.dest().exists())

    def test_the_real_plugin_ships_exactly_the_seventeen_skills_and_commands(self):
        self.assertEqual(sorted(p.name for p in self.installer.skills_of(PLUGIN)),
                         sorted(f"sdd-{name}" for name in NAMES))
        self.assertEqual(sorted(p.stem for p in self.installer.commands_of(PLUGIN)), sorted(NAMES))


if __name__ == "__main__":
    unittest.main()
