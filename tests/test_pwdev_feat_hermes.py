"""pwdev-feat on Hermes: twelve skills registered as Path objects and a short first-turn bootstrap."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-feat"


class FakeContext:
    def __init__(self):
        self.skills = []
        self.hooks = {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError(f"Hermes skill path must remain Path, got {type(path)!r}")
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


def load_plugin(path: Path = PLUGIN / ".hermes-plugin/__init__.py"):
    spec = importlib.util.spec_from_file_location(f"pwdev_feat_hermes_{abs(hash(str(path)))}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HermesPluginTest(unittest.TestCase):
    def test_manifest_declares_exactly_the_registered_hook(self):
        manifest = (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("name: pwdev-feat", manifest)
        self.assertIn("provides_hooks:\n  - pre_llm_call", manifest)
        ctx = FakeContext()
        load_plugin().register(ctx)
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})

    def test_registers_twelve_skills_with_native_paths(self):
        ctx = FakeContext()
        load_plugin().register(ctx)
        expected = sorted(p.name for p in (PLUGIN / "skills").iterdir() if (p / "SKILL.md").is_file())
        self.assertEqual(len(expected), 12)
        self.assertEqual([name for name, _ in ctx.skills], expected)
        for name, path in ctx.skills:
            self.assertEqual(path.resolve(), (PLUGIN / "skills" / name / "SKILL.md").resolve())

    def test_bootstrap_is_first_turn_only_and_bounded(self):
        ctx = FakeContext()
        load_plugin().register(ctx)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True, session_id="x")
        self.assertEqual(set(first), {"context"})
        self.assertGreater(len(first["context"]), 100)
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-feat:feat-<name>")', first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_flat_install_layout_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            flat = Path(tmp) / "pwdev-feat"
            shutil.copytree(PLUGIN / "skills", flat / "skills")
            shutil.copy(PLUGIN / ".hermes-plugin/__init__.py", flat / "__init__.py")
            ctx = FakeContext()
            load_plugin(flat / "__init__.py").register(ctx)
            self.assertEqual(len(ctx.skills), 12)

    def test_missing_skills_raise_before_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken"
            broken.mkdir()
            shutil.copy(PLUGIN / ".hermes-plugin/__init__.py", broken / "__init__.py")
            ctx = FakeContext()
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load_plugin(broken / "__init__.py").register(ctx)
            self.assertEqual(ctx.skills, [])
            self.assertEqual(ctx.hooks, {})


if __name__ == "__main__":
    unittest.main()
