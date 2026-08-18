"""Tests for the pwdev-power Hermes Agent plugin.

Run from the repository root:

    python3 -m unittest tests.test_power_hermes
"""

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-power"
HERMES_INIT = PLUGIN / ".hermes-plugin" / "__init__.py"


def load(path, name="power_hermes_under_test"):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Ctx:
    """Stand-in for the Hermes plugin context.

    register_skill mirrors the real one, which calls path.exists() and therefore breaks on a
    str — the bug that silently disabled a whole plugin. Keeping that fidelity here turns a
    regression to str paths into a test failure instead of a silent one inside Hermes.
    """

    def __init__(self):
        self.hooks = {}
        self.skills = {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise AttributeError(f"register_skill requires a pathlib.Path, got {type(path).__name__}")
        self.skills[name] = path

    def register_hook(self, event, handler):
        self.hooks[event] = handler


def fire(ctx, **overrides):
    payload = dict(
        session_id="s1",
        user_message="hi",
        conversation_history=[],
        is_first_turn=False,
        model="test-model",
        platform="cli",
    )
    payload.update(overrides)
    return ctx.hooks["pre_llm_call"](**payload)


class TestRegistration(unittest.TestCase):
    def setUp(self):
        self.module = load(HERMES_INIT)
        self.ctx = Ctx()
        self.module.register(self.ctx)

    def test_only_the_hook_it_declares_is_registered(self):
        # The manifest promises pre_llm_call and nothing else.
        self.assertEqual(list(self.ctx.hooks), ["pre_llm_call"])

    def test_every_skill_is_registered_as_a_path(self):
        skill_dirs = {p.name for p in (PLUGIN / "skills").iterdir() if (p / "SKILL.md").is_file()}
        self.assertEqual(set(self.ctx.skills), skill_dirs)
        for name, path in self.ctx.skills.items():
            self.assertIsInstance(path, Path)
            self.assertEqual(path.name, "SKILL.md")
            self.assertEqual(path.parent.name, name)
            self.assertTrue(path.is_file())


class TestBootstrapInjection(unittest.TestCase):
    def setUp(self):
        self.module = load(HERMES_INIT)
        self.ctx = Ctx()
        self.module.register(self.ctx)

    def test_the_first_turn_receives_the_bootstrap(self):
        result = fire(self.ctx, is_first_turn=True)
        self.assertIsInstance(result, dict)
        context = result["context"]
        self.assertIn(self.module.BOOTSTRAP_MARKER, context)
        self.assertTrue(context.startswith("<EXTREMELY_IMPORTANT>"))
        self.assertTrue(context.endswith("</EXTREMELY_IMPORTANT>"))

    def test_later_turns_receive_nothing(self):
        self.assertIsNone(fire(self.ctx, is_first_turn=False))
        self.assertIsNone(fire(self.ctx, is_first_turn=None))

    def test_unknown_keyword_arguments_do_not_break_the_hook(self):
        result = self.ctx.hooks["pre_llm_call"](is_first_turn=True, telemetry_schema_version=3, brand_new=1)
        self.assertIsInstance(result, dict)

    def test_the_bootstrap_stays_under_the_context_spill_limit(self):
        # Above this, Hermes spills injected context to a file and inline injection breaks.
        context = fire(self.ctx, is_first_turn=True)["context"]
        self.assertLess(len(context), self.module.CONTEXT_SPILL_LIMIT)

    def test_the_skill_body_is_embedded_without_its_frontmatter(self):
        context = fire(self.ctx, is_first_turn=True)["context"]
        self.assertIn("## The rule", context)
        self.assertIn("power-tdd", context)
        self.assertNotIn("---\nname: power\n", context)

    def test_the_tool_mapping_has_a_single_source(self):
        # Read at runtime rather than duplicated inline, so the two cannot drift.
        context = fire(self.ctx, is_first_turn=True)["context"]
        mapping = (PLUGIN / "references" / "hermes-tools.md").read_text(encoding="utf-8").strip()
        self.assertIn(mapping, context)

    def test_the_fallback_path_it_prints_actually_exists(self):
        context = fire(self.ctx, is_first_turn=True)["context"]
        skills_dir = str(PLUGIN / "skills")
        self.assertIn(skills_dir, context)
        self.assertTrue(Path(skills_dir).is_dir())


class TestLayoutResolution(unittest.TestCase):
    """Hermes installs plugins in more than one shape; both must resolve."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def stage(self, layout):
        root = Path(self.tmp.name) / layout
        base = root / "pwdev-power"
        plugin_dir = base / ".hermes-plugin" if layout == "clone" else base
        plugin_dir.mkdir(parents=True, exist_ok=True)
        for skill in ("power", "power-tdd"):
            (base / "skills" / skill).mkdir(parents=True, exist_ok=True)
            shutil.copy(PLUGIN / "skills" / skill / "SKILL.md", base / "skills" / skill / "SKILL.md")
        (base / "references").mkdir(parents=True, exist_ok=True)
        shutil.copy(PLUGIN / "references" / "hermes-tools.md", base / "references" / "hermes-tools.md")
        shutil.copy(HERMES_INIT, plugin_dir / "__init__.py")
        return plugin_dir / "__init__.py"

    def test_the_git_clone_layout_resolves(self):
        module = load(self.stage("clone"), "h_clone")
        ctx = Ctx()
        module.register(ctx)
        self.assertIn("power", ctx.skills)

    def test_the_flattened_layout_resolves(self):
        module = load(self.stage("flat"), "h_flat")
        ctx = Ctx()
        module.register(ctx)
        self.assertIn("power", ctx.skills)

    def test_a_broken_install_raises_instead_of_skipping(self):
        # A bootstrap that silently skips is how a broken install masquerades as a working one.
        root = Path(self.tmp.name) / "broken" / ".hermes-plugin"
        root.mkdir(parents=True)
        shutil.copy(HERMES_INIT, root / "__init__.py")
        module = load(root / "__init__.py", "h_broken")
        with self.assertRaises(RuntimeError) as caught:
            module.register(Ctx())
        self.assertIn("cannot find the skills", str(caught.exception))

    def test_a_symlinked_install_resolves(self):
        # realpath before walking up, so an install by symlink still finds its siblings.
        real = self.stage("clone")
        link_root = Path(self.tmp.name) / "linked"
        link_root.symlink_to(real.parent.parent.parent, target_is_directory=True)
        module = load(link_root / "pwdev-power" / ".hermes-plugin" / "__init__.py", "h_link")
        ctx = Ctx()
        module.register(ctx)
        self.assertIn("power", ctx.skills)


class TestManifest(unittest.TestCase):
    def test_the_manifest_declares_the_hook_the_code_registers(self):
        text = (PLUGIN / ".hermes-plugin" / "plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("- pre_llm_call", text)

        module = load(HERMES_INIT, "h_manifest")
        ctx = Ctx()
        module.register(ctx)
        declared = [
            line.strip()[2:]
            for line in text.splitlines()
            if line.strip().startswith("- ")
        ]
        self.assertEqual(sorted(declared), sorted(ctx.hooks))


if __name__ == "__main__":
    unittest.main()
