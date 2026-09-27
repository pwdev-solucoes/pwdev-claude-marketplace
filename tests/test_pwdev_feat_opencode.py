"""pwdev-feat on OpenCode: the installer links the twelve feat-* skills and writes one command each."""
from __future__ import annotations

import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-feat"
INSTALLER = PLUGIN / ".opencode-plugin" / "install.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("pwdev_feat_opencode", INSTALLER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OpenCodeInstallerTest(unittest.TestCase):
    def setUp(self):
        self.installer = load_installer()
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)
        self._env = dict(os.environ)
        os.environ["XDG_CONFIG_HOME"] = str(self.project / "xdg")
        self.out = io.StringIO()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def install(self, *args: str) -> int:
        return self.installer.install(PLUGIN, self.project / ".opencode", out=self.out,
                                      force="--force" in args, dry_run="--dry-run" in args)

    def test_links_all_skills_and_writes_commands_idempotently(self):
        self.assertEqual(self.install(), 0)
        dest = self.project / ".opencode"
        skills = sorted(p.name for p in (dest / "skills").iterdir())
        self.assertEqual(len(skills), 12)
        for name in skills:
            self.assertTrue((dest / "skills" / name).is_symlink())
            self.assertEqual((dest / "skills" / name).resolve(), (PLUGIN / "skills" / name).resolve())
        commands = sorted(p.stem for p in (dest / "command").iterdir())
        self.assertEqual(commands, skills)
        text = (dest / "command" / "feat-feature.md").read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", text)
        self.assertIn("`feat-feature`", text)
        self.assertIn(self.installer.COMMAND_MARKER, text)
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
        self.assertNotIn("argument-hint", text)
        self.assertEqual(self.install(), 0)
        self.assertIn("already linked", self.out.getvalue())

    def test_refuses_foreign_targets_unless_forced(self):
        target = self.project / ".opencode" / "command" / "feat-exec.md"
        target.parent.mkdir(parents=True)
        target.write_text("user file\n", encoding="utf-8")
        self.assertEqual(self.install(), 1)
        self.assertEqual(target.read_text(encoding="utf-8"), "user file\n")
        self.assertEqual(self.install("--force"), 0)
        self.assertIn(self.installer.COMMAND_MARKER, target.read_text(encoding="utf-8"))

    def test_dry_run_changes_nothing_and_uninstall_removes_only_own_files(self):
        self.assertEqual(self.install("--dry-run"), 0)
        self.assertFalse((self.project / ".opencode").exists())
        self.assertEqual(self.install(), 0)
        keep = self.project / ".opencode" / "command" / "mine.md"
        keep.write_text("mine\n", encoding="utf-8")
        self.assertEqual(self.installer.uninstall(PLUGIN, self.project / ".opencode", dry_run=False, out=self.out), 0)
        self.assertEqual(sorted(p.name for p in (self.project / ".opencode" / "command").iterdir()), ["mine.md"])
        self.assertEqual(list((self.project / ".opencode" / "skills").iterdir()), [])

    def test_main_project_scope(self):
        self.assertEqual(self.installer.main(["--project", str(self.project)]), 0)
        self.assertTrue((self.project / ".opencode" / "skills" / "feat-exec").is_symlink())


if __name__ == "__main__":
    unittest.main()
