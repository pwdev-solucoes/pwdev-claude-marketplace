import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]

class FakeContext:
    def __init__(self): self.skills = []; self.hooks = {}
    def register_skill(self, name, path): self.skills.append((name, Path(path)))
    def register_hook(self, name, callback): self.hooks[name] = callback

def load_plugin():
    path = ROOT / "plugins/sdd-composy/.hermes-plugin/__init__.py"
    spec = importlib.util.spec_from_file_location("sdd_composy_hermes", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

class HermesPluginTest(unittest.TestCase):
    def test_manifest_and_mapping_exist(self):
        self.assertTrue((ROOT / "plugins/sdd-composy/.hermes-plugin/plugin.yaml").is_file())
        self.assertIn("read_file", (ROOT / "plugins/sdd-composy/references/hermes-tools.md").read_text())

    def test_registers_all_skills_and_first_turn_bootstrap(self):
        ctx = FakeContext(); load_plugin().register(ctx)
        expected = {p.name for p in (ROOT / "plugins/sdd-composy/skills").iterdir() if (p / "SKILL.md").is_file()}
        self.assertEqual({name for name, _ in ctx.skills}, expected)
        self.assertIn("context", ctx.hooks["pre_llm_call"](is_first_turn=True))
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_hermes_runner_is_explicit_and_no_fallback_is_defined(self):
        runner = (ROOT / "plugins/sdd-composy/scripts/fleet/run.sh").read_text()
        launch = (ROOT / "plugins/sdd-composy/scripts/fleet/launch.sh").read_text()
        self.assertIn("codex|claude|hermes", runner)
        self.assertIn("runtime == hermes", launch)
        adapter = (ROOT / "plugins/sdd-composy/scripts/fleet/engine-hermes.sh").read_text()
        self.assertIn("hermes run", adapter)

if __name__ == "__main__": unittest.main()
