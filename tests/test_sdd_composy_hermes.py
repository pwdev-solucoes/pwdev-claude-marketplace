import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins/sdd-composy"

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

def load_plugin():
    path = PLUGIN / ".hermes-plugin/__init__.py"
    spec = importlib.util.spec_from_file_location("sdd_composy_hermes", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class HermesPluginTest(unittest.TestCase):
    def test_manifest_declares_the_hook_exported_by_registration(self):
        manifest = {}
        for line in (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8").splitlines():
            if line.startswith(("name:", "version:")):
                key, value = line.split(":", 1)
                manifest[key] = value.strip()
        self.assertEqual(manifest, {"name": "sdd-composy", "version": "0.1.0"})
        ctx = FakeContext()
        load_plugin().register(ctx)
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})

    def test_registers_exactly_17_resolvable_skills_with_native_paths(self):
        ctx = FakeContext()
        load_plugin().register(ctx)
        expected = sorted(path.name for path in (PLUGIN / "skills").iterdir()
                          if (path / "SKILL.md").is_file())
        self.assertEqual(len(expected), 17)
        self.assertEqual([name for name, _path in ctx.skills], expected)
        for name, path in ctx.skills:
            self.assertEqual(path.resolve(), (PLUGIN / "skills" / name / "SKILL.md").resolve())
            self.assertTrue(path.is_file())

    def test_first_turn_bootstrap_routes_and_later_turn_is_empty(self):
        ctx = FakeContext()
        load_plugin().register(ctx)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertEqual(set(first), {"context"})
        self.assertGreater(len(first["context"]), 100)
        self.assertLess(len(first["context"]), 4000)
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_bootstrap_unavailability_is_diagnostic_and_registers_nothing(self):
        module = load_plugin()
        ctx = FakeContext()
        missing = ROOT / "definitely-missing-sdd-plugin"
        with patch.object(module, "_plugin_dir", side_effect=RuntimeError(
                f"sdd-composy: skills directory not found at {missing}")):
            with self.assertRaisesRegex(RuntimeError, "skills directory not found"):
                module.register(ctx)
        self.assertEqual(ctx.skills, [])
        self.assertEqual(ctx.hooks, {})

if __name__ == "__main__": unittest.main()
