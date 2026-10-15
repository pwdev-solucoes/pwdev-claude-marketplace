"""pwdev-social-media v3: portable layout on three runtimes, generation only through the pwdev-media
CLI (estimate before confirm), removed v2 scripts, subagents wired to existing skills.

Run from the repository root:

    python3 -m unittest tests.test_pwdev_social_media
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-social-media"
CATALOG = ROOT / "plugins" / "pwdev-media" / "engine" / "src" / "pwdev_media" / "data" / "catalogo.json"

SKILLS = {
    "social-imagem", "social-video", "social-prompt", "social-custo", "social-conceito", "social-revisao",
    "social-carrossel", "social-reels", "social-post", "social-marca", "social-consistencia",
    "social-curadoria", "social-upscale", "social-alt-text", "social-formatos", "social-entrega",
    "social-figma", "social-contexto", "social-vault", "social-lote", "social-video-curto", "social-criar",
}
COMMANDS = {
    "init": "social-contexto", "status": "social-contexto", "criar": "social-criar", "gerar": "social-imagem",
    "carrossel": "social-carrossel", "video": "social-video", "revisar": "social-revisao",
    "exportar": "social-entrega", "custo": "social-custo", "formatos": "social-formatos", "lote": "social-lote",
}
AGENTS = {"art-director", "asset-generator", "creative-reviewer", "figma-builder"}
# Items the pwdev-media 0.4.0 catalog adds for this plugin; anything else must exist in the catalog.
NEW_ITEMS = {"ideogram:ideogram-3", "bfl:flux-pro-1.1", "bfl:flux-2-pro", "leonardo:conta",
             "runway:gen4_turbo", "magnific:upscale"}
V2_SKILLS = {"image-gen", "video-gen", "prompt-craft", "cost-control", "creative-concept", "creative-review",
             "carousel-builder", "story-reels", "post-visual", "brand-kit", "visual-consistency",
             "asset-curation", "asset-upscale", "format-specs", "export-handoff", "figma-pipeline",
             "social-context", "vault-sync"}
V2_SCRIPTS = ("gen-ideogram.sh", "gen-leonardo.sh", "gen-flux.sh", "gen-runway.sh", "upscale-freepik.sh",
              "check-keys.sh", "lib.sh", "scripts/gen-")
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeHermes:
    def __init__(self):
        self.skills, self.hooks = [], {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError(f"Hermes skill path must be a Path, got {type(path)!r}")
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


def skill_text(name: str) -> str:
    return (PLUGIN / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def all_docs():
    return [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "agents").glob("*.md"),
            *(PLUGIN / "references").glob("*.md"), *(PLUGIN / "commands").glob("*.md"),
            *(PLUGIN / "templates").glob("*.md"), PLUGIN / "README.md", PLUGIN / "README.pt-BR.md"]


class PortableLayoutTest(unittest.TestCase):
    def manifest(self) -> dict:
        return json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))

    def test_skills_are_the_single_source_and_commands_wrap_them(self):
        self.assertEqual({p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}, SKILLS)
        self.assertEqual({p.stem for p in (PLUGIN / "commands").glob("*.md")}, set(COMMANDS))
        for command, skill in COMMANDS.items():
            text = (PLUGIN / "commands" / f"{command}.md").read_text(encoding="utf-8")
            with self.subTest(command=command):
                self.assertIn(f"skills/{skill}/SKILL.md", text)
                self.assertIn("Do not add workflow steps here.", text)
                self.assertLess(len(text.splitlines()), 20)

    def test_skill_frontmatter_and_runtime_neutral_bodies(self):
        version = self.manifest()["version"]
        for skill in SKILLS:
            text = skill_text(skill)
            with self.subTest(skill=skill):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(front)
                self.assertIn(f"name: {skill}\n", front.group(1))
                self.assertRegex(front.group(1), r"description: >\n  Use quando")
                self.assertIn("Não use", front.group(1))
                self.assertIn(f"version: {version}", front.group(1))
                for token in FORBIDDEN_IN_SKILLS:
                    self.assertNotIn(token, text)
                self.assertIn("<plugin-root>/references/runtime.md", text)
                yaml = (PLUGIN / "skills" / skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn(f"${skill}", yaml)

    def test_no_reference_to_v2_skill_names_or_scripts(self):
        self.assertFalse((PLUGIN / "scripts").exists(), "v2 scripts were removed")
        for md in all_docs():
            if md.name == "CHANGELOG.md":
                continue
            text = md.read_text(encoding="utf-8")
            with self.subTest(file=str(md.relative_to(PLUGIN))):
                for script in V2_SCRIPTS:
                    self.assertNotIn(script, text)
                for old in V2_SKILLS:
                    self.assertNotRegex(text, rf"`{re.escape(old)}`", f"old skill name {old}")
                self.assertNotIn("manifest.jsonl", text.replace("`.pwdev-social/gerados/manifest.jsonl` continua", ""))

    def test_referenced_plugin_files_exist(self):
        for md in [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "references").glob("*.md")]:
            text = md.read_text(encoding="utf-8")
            for rel in set(re.findall(r"<plugin-root>/(\w[\w./-]*?)[`'\"\s)]", text)):
                with self.subTest(file=md.name, path=rel):
                    self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_manifests_agree_and_declare_the_mcp_servers(self):
        claude = self.manifest()
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        hermes = dict(re.findall(r"^(\w+):\s*(.+)$",
                                 (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"), re.M))
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-social-media",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        self.assertEqual(claude["version"].split(".")[0], "3")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertEqual((claude["mcpServers"], codex["mcpServers"]), ("./.mcp.json", "./.mcp.json"))
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        mcp = json.loads((PLUGIN / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(mcp, {"figma": {"type": "http", "url": "https://mcp.figma.com/mcp"},
                               "notion": {"type": "http", "url": "https://mcp.notion.com/mcp"}})
        changelog = (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {claude['version']} ", changelog)
        for old in V2_SKILLS:
            self.assertIn(f"`{old}`", changelog, f"migration table lists {old}")
        self.assertIn("pwdev-media` ≥ 0.4.0", changelog)
        self.assertTrue((PLUGIN / "LICENSE").is_file())

    def test_marketplaces_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in claude["plugins"]].count("pwdev-social-media"), 1)
        entries = [p for p in codex["plugins"] if p["name"] == "pwdev-social-media"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-social-media"})


class GenerationThroughCoreTest(unittest.TestCase):
    def catalog_ids(self) -> set:
        return {item["id"] for item in json.loads(CATALOG.read_text(encoding="utf-8"))["itens"]}

    def gerar_calls(self):
        for md in [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "agents").glob("*.md"),
                   *(PLUGIN / "references").glob("*.md")]:
            text = md.read_text(encoding="utf-8")
            # join shell line continuations so one command is one string
            text = text.replace("\\\n", " ")
            for line in text.splitlines():
                for m in re.finditer(r"pwdev-media gerar ([\w.:/-]+)", line):
                    yield md, line, m.group(1)

    def test_every_generation_item_exists(self):
        known = self.catalog_ids() | NEW_ITEMS
        seen = set()
        for md, _, item in self.gerar_calls():
            if not re.match(r"^[\w-]+:[\w./-]+$", item):
                continue  # placeholders such as <item> or {{item}}
            seen.add(item)
            with self.subTest(file=md.name, item=item):
                self.assertIn(item, known)
        self.assertTrue({"ideogram:ideogram-3", "runway:gen4_turbo", "magnific:upscale"} <= seen)

    def test_the_new_items_are_in_the_core_catalog(self):
        missing = NEW_ITEMS - self.catalog_ids()
        self.assertEqual(missing, set(), "pwdev-media 0.4.0 must ship these catalog items")

    def test_paid_examples_estimate_before_confirming(self):
        for md in [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "agents").glob("*.md"),
                   *(PLUGIN / "references").glob("*.md")]:
            text = md.read_text(encoding="utf-8").replace("\\\n", " ")
            calls = [line for line in text.splitlines() if re.search(r"pwdev-media gerar [\w{<]", line)]
            if not calls:
                continue
            with self.subTest(file=md.name):
                self.assertTrue(any("--estimar" in line for line in calls) or "--estimar" in text,
                                "every file that generates shows the estimate first")
                first_estimate = text.find("--estimar")
                first_confirm = text.find("--confirmar")
                if first_confirm != -1:
                    self.assertNotEqual(first_estimate, -1)
                    self.assertLess(first_estimate, first_confirm, "--estimar comes before --confirmar")
                for line in calls:
                    self.assertFalse("--confirmar" in line and "--estimar" in line)
                    self.assertNotIn("--confirm ", line + " ", "v2 flag")

    def test_keys_are_never_requested_in_the_conversation(self):
        for name in ("social-contexto", "social-imagem"):
            text = skill_text(name)
            with self.subTest(skill=name):
                self.assertIn("pwdev-media chaves guardar", text)
        self.assertIn("NÃO GERADO", skill_text("social-imagem"))

    def test_formats_come_from_the_core(self):
        text = skill_text("social-formatos")
        for cmd in ("pwdev-media formatos listar", "pwdev-media formatos mostrar", "pwdev-media formatos conferir"):
            self.assertIn(cmd, text)
        for fmt in ("reels-9x16", "feed-4x5", "feed-1x1", "youtube-16x9", "link-1.91x1", "display-300x250"):
            self.assertIn(fmt, text)
        self.assertNotIn("900 × 1350", skill_text("social-reels"), "safe-zone pixels live in the core")


class AgentsTest(unittest.TestCase):
    def test_agents_reference_existing_skills_and_the_core(self):
        self.assertEqual({p.stem for p in (PLUGIN / "agents").glob("*.md")}, AGENTS)
        for md in (PLUGIN / "agents").glob("*.md"):
            text = md.read_text(encoding="utf-8")
            with self.subTest(agent=md.stem):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIn(f"name: {md.stem}\n", front.group(1))
                for ref in set(re.findall(r"`(social-[a-z-]+)`", text)):
                    self.assertIn(ref, SKILLS, ref)
        generator = (PLUGIN / "agents" / "asset-generator.md").read_text(encoding="utf-8")
        self.assertIn("pwdev-media gerar", generator)
        self.assertIn("--estimar", generator)

    def test_skills_point_to_existing_skills(self):
        for skill in SKILLS:
            for ref in set(re.findall(r"`(social-[a-z-]+)`", skill_text(skill))):
                with self.subTest(skill=skill, ref=ref):
                    self.assertIn(ref, SKILLS)

    def test_runtime_reference_explains_inline_subagents(self):
        text = (PLUGIN / "references" / "runtime.md").read_text(encoding="utf-8")
        self.assertIn("inline", text)
        for agent in AGENTS:
            self.assertIn(agent, text)
        for skill in set(COMMANDS.values()):
            self.assertIn(skill, text)


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_with_a_bounded_first_turn_bootstrap(self):
        self.assertIn("provides_hooks:\n  - pre_llm_call",
                      (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"))
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_social_hermes").register(ctx)
        self.assertEqual({name for name, _ in ctx.skills}, SKILLS)
        for name, path in ctx.skills:
            self.assertEqual(path.resolve(), (PLUGIN / "skills" / name / "SKILL.md").resolve())
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-social-media:social-<name>")', first["context"])
        for skill in SKILLS:
            self.assertIn(skill, first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_missing_skills_fail_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "__init__.py").write_text(
                (PLUGIN / ".hermes-plugin/__init__.py").read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load_module(Path(tmp) / "__init__.py", "pwdev_social_hermes_broken").register(FakeHermes())


if __name__ == "__main__":
    unittest.main()
