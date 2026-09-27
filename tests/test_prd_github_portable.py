"""pwdev-prd and pwdev-github on Claude Code, Codex, Hermes Agent and OpenCode.

Skills are the single source of truth; Claude commands are wrappers; Codex, Hermes and OpenCode
adapters expose the same skills.
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLUGINS = {
    "pwdev-prd": {
        "prefix": "prd-",
        "skills": {"prd-init", "prd-create", "prd-refine", "prd-list", "prd-export",
                   "prd-roadmap", "prd-stories", "prd-publish", "prd-audit"},
        "commands": {"init": "prd-init", "create": "prd-create", "refine": "prd-refine",
                     "list": "prd-list", "export": "prd-export", "roadmap": "prd-roadmap", "stories": "prd-stories",
                     "publish": "prd-publish", "audit": "prd-audit"},
    },
    "pwdev-github": {
        "prefix": "github-",
        "skills": {"github-init", "github-project", "github-publish", "github-status", "github-issues"},
        "commands": {"init": "github-init", "project": "github-project",
                     "publish": "github-publish", "status": "github-status"},
    },
}
# Hermes silently drops a skill whose body names the project instructions files.
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeHermes:
    def __init__(self):
        self.skills = []
        self.hooks = {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError(f"Hermes skill path must be a Path, got {type(path)!r}")
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


class PortableLayoutTest(unittest.TestCase):
    def test_skills_are_the_single_source_and_commands_wrap_them(self):
        for plugin, spec in PLUGINS.items():
            root = ROOT / "plugins" / plugin
            with self.subTest(plugin=plugin):
                skills = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
                self.assertEqual(skills, spec["skills"])
                commands = {p.stem for p in (root / "commands").glob("*.md")}
                self.assertEqual(commands, set(spec["commands"]))
                for command, skill in spec["commands"].items():
                    text = (root / "commands" / f"{command}.md").read_text(encoding="utf-8")
                    self.assertIn(f"skills/{skill}/SKILL.md", text)
                    self.assertIn("Do not add workflow steps here.", text)
                    self.assertLess(len(text.splitlines()), 20, f"{command}.md must stay a thin wrapper")

    def test_skill_frontmatter_and_runtime_neutral_bodies(self):
        for plugin, spec in PLUGINS.items():
            root = ROOT / "plugins" / plugin
            for skill in spec["skills"]:
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                with self.subTest(plugin=plugin, skill=skill):
                    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                    self.assertIsNotNone(front)
                    self.assertIn(f"name: {skill}\n", front.group(1))
                    self.assertIn("description:", front.group(1))
                    for token in FORBIDDEN_IN_SKILLS:
                        self.assertNotIn(token, text)
                    self.assertIn("references/runtime.md", text)
                    self.assertTrue((root / "skills" / skill / "agents" / "openai.yaml").is_file())

    def test_referenced_plugin_files_exist(self):
        for plugin in PLUGINS:
            root = ROOT / "plugins" / plugin
            for skill_md in (root / "skills").glob("*/SKILL.md"):
                text = skill_md.read_text(encoding="utf-8")
                for rel in set(re.findall(r"<plugin-root>/((?:references|scripts|templates)/[\w./-]+?)[`\"\s)]", text)):
                    with self.subTest(skill=skill_md.parent.name, path=rel):
                        self.assertTrue((root / rel).exists(), rel)

    def test_three_manifests_agree(self):
        for plugin in PLUGINS:
            root = ROOT / "plugins" / plugin
            with self.subTest(plugin=plugin):
                claude = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
                codex = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
                hermes = dict(re.findall(r"^(\w+):\s*(.+)$",
                                         (root / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"), re.M))
                self.assertEqual(codex["name"], plugin)
                self.assertEqual(hermes["name"], plugin)
                self.assertEqual(codex["version"], claude["version"])
                self.assertEqual(hermes["version"], claude["version"])
                self.assertEqual(codex["skills"], "./skills/")
                for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
                    self.assertTrue(codex["interface"].get(field), field)

    def test_marketplaces_list_both_plugins_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                self.assertEqual([p["name"] for p in claude["plugins"]].count(plugin), 1)
                entries = [p for p in codex["plugins"] if p["name"] == plugin]
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["source"], {"source": "local", "path": f"./plugins/{plugin}"})


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_as_path_with_a_bounded_first_turn_bootstrap(self):
        for plugin, spec in PLUGINS.items():
            root = ROOT / "plugins" / plugin
            with self.subTest(plugin=plugin):
                manifest = (root / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8")
                self.assertIn("provides_hooks:\n  - pre_llm_call", manifest)
                ctx = FakeHermes()
                load_module(root / ".hermes-plugin/__init__.py", f"{plugin}_hermes").register(ctx)
                self.assertEqual({name for name, _ in ctx.skills}, spec["skills"])
                for name, path in ctx.skills:
                    self.assertEqual(path.resolve(), (root / "skills" / name / "SKILL.md").resolve())
                self.assertEqual(set(ctx.hooks), {"pre_llm_call"})
                first = ctx.hooks["pre_llm_call"](is_first_turn=True, session_id="s")
                self.assertLess(len(first["context"]), 4000)
                self.assertIn(f'skill_view("{plugin}:{spec["prefix"]}<name>")', first["context"])
                self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_flat_layout_and_missing_skills(self):
        for plugin, spec in PLUGINS.items():
            root = ROOT / "plugins" / plugin
            with self.subTest(plugin=plugin), tempfile.TemporaryDirectory() as tmp:
                flat = Path(tmp) / "flat"
                shutil.copytree(root / "skills", flat / "skills")
                shutil.copy(root / ".hermes-plugin/__init__.py", flat / "__init__.py")
                ctx = FakeHermes()
                load_module(flat / "__init__.py", f"{plugin}_hermes_flat").register(ctx)
                self.assertEqual(len(ctx.skills), len(spec["skills"]))
                broken = Path(tmp) / "broken"
                broken.mkdir()
                shutil.copy(root / ".hermes-plugin/__init__.py", broken / "__init__.py")
                ctx = FakeHermes()
                with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                    load_module(broken / "__init__.py", f"{plugin}_hermes_broken").register(ctx)
                self.assertEqual((ctx.skills, ctx.hooks), ([], {}))


class OpenCodeInstallerTest(unittest.TestCase):
    def test_links_skills_writes_commands_and_uninstalls_only_its_own(self):
        for plugin, spec in PLUGINS.items():
            root = ROOT / "plugins" / plugin
            installer = load_module(root / ".opencode-plugin/install.py", f"{plugin}_opencode")
            with self.subTest(plugin=plugin), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / ".opencode"
                out = io.StringIO()
                self.assertEqual(installer.install(root, dest, force=False, dry_run=False, out=out), 0)
                linked = {p.name for p in (dest / "skills").iterdir()}
                self.assertEqual(linked, spec["skills"])
                for name in linked:
                    self.assertTrue((dest / "skills" / name).is_symlink())
                commands = {p.stem for p in (dest / "command").iterdir()}
                self.assertEqual(commands, set(spec["commands"].values()))
                sample = next(iter(spec["commands"].values()))
                text = (dest / "command" / f"{sample}.md").read_text(encoding="utf-8")
                self.assertIn(f"`{sample}`", text)
                self.assertIn("$ARGUMENTS", text)
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
                self.assertIn(installer.COMMAND_MARKER, text)
                # idempotent
                self.assertEqual(installer.install(root, dest, force=False, dry_run=False, out=out), 0)
                self.assertIn("already linked", out.getvalue())
                # a foreign file is refused, kept on uninstall
                foreign = dest / "skills" / f"{spec['prefix']}mine"
                foreign.mkdir()
                own_cmd = dest / "command" / f"{sample}.md"
                own_cmd.write_text("user file\n", encoding="utf-8")
                self.assertEqual(installer.install(root, dest, force=False, dry_run=False, out=out), 1)
                self.assertEqual(own_cmd.read_text(encoding="utf-8"), "user file\n")
                self.assertEqual(installer.uninstall(root, dest, dry_run=False, out=out), 0)
                self.assertEqual({p.name for p in (dest / "skills").iterdir()}, {foreign.name})
                self.assertTrue(own_cmd.exists(), "a file the installer did not write must survive uninstall")

    def test_plugin_scripts_resolve_through_the_symlink(self):
        root = ROOT / "plugins" / "pwdev-prd"
        installer = load_module(root / ".opencode-plugin/install.py", "prd_opencode_paths")
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / ".opencode"
            installer.install(root, dest, force=False, dry_run=False, out=io.StringIO())
            skill = (dest / "skills" / "prd-roadmap" / "SKILL.md").resolve()
            plugin_root = skill.parent.parent.parent
            self.assertTrue((plugin_root / "scripts" / "roadmap-check.py").is_file())
            self.assertTrue((plugin_root / "references" / "roadmap-agent.md").is_file())


class RoadmapDispatchTest(unittest.TestCase):
    def test_roadmap_contract_is_shared_by_every_runtime(self):
        root = ROOT / "plugins" / "pwdev-prd"
        skill = (root / "skills/prd-roadmap/SKILL.md").read_text(encoding="utf-8")
        for token in ('subagent_type: "pwdev-prd:roadmap"', "spawn_agent", "delegate_task", "`task`", "inline"):
            self.assertIn(token, skill)
        self.assertIn("Contract: <plugin-root>/references/roadmap-agent.md", skill)
        agent = (root / "agents/roadmap.md").read_text(encoding="utf-8")
        self.assertIn("references/roadmap-agent.md", agent)
        self.assertLess(len(agent.splitlines()), 30, "the Claude agent must only point at the contract")
        runtime = (root / "references/runtime.md").read_text(encoding="utf-8")
        for token in ("Codex", "Hermes", "OpenCode", "github-publish"):
            self.assertIn(token, runtime)


if __name__ == "__main__":
    unittest.main()
