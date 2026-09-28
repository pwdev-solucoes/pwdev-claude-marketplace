"""pwdev-fumadocs: portable layout on four runtimes and the fdscan.py project scanner.

Run from the repository root:

    python3 -m unittest tests.test_pwdev_fumadocs
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-fumadocs"
SKILLS = {"fumadocs-setup", "fumadocs-content", "fumadocs-feature", "fumadocs-doctor"}
COMMANDS = {"setup": "fumadocs-setup", "content": "fumadocs-content",
            "feature": "fumadocs-feature", "doctor": "fumadocs-doctor"}
# Hermes silently drops a skill whose body names the project instructions files.
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fdscan = load_module(PLUGIN / "scripts" / "fdscan.py", "pwdev_fumadocs_fdscan")


class FakeHermes:
    def __init__(self):
        self.skills, self.hooks = [], {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError(f"Hermes skill path must be a Path, got {type(path)!r}")
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


class PortableLayoutTest(unittest.TestCase):
    def test_skills_are_the_single_source_and_commands_wrap_them(self):
        self.assertEqual({p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}, SKILLS)
        self.assertEqual({p.stem for p in (PLUGIN / "commands").glob("*.md")}, set(COMMANDS))
        for command, skill in COMMANDS.items():
            text = (PLUGIN / "commands" / f"{command}.md").read_text(encoding="utf-8")
            with self.subTest(command=command):
                self.assertIn(f"skills/{skill}/SKILL.md", text)
                self.assertIn("Do not add workflow steps here.", text)
                self.assertLess(len(text.splitlines()), 20, f"{command}.md must stay a thin wrapper")

    def test_skill_frontmatter_and_runtime_neutral_bodies(self):
        for skill in SKILLS:
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(front)
                self.assertIn(f"name: {skill}\n", front.group(1))
                self.assertIn("description:", front.group(1))
                self.assertIn("version: 0.1.0", front.group(1))
                for token in FORBIDDEN_IN_SKILLS:
                    self.assertNotIn(token, text)
                self.assertIn("references/runtime.md", text)
                self.assertIn("scripts/fdscan.py", text, "every skill starts from the scanner")
                self.assertTrue((PLUGIN / "skills" / skill / "agents" / "openai.yaml").is_file())

    def test_referenced_plugin_files_exist(self):
        for skill_md in (PLUGIN / "skills").glob("*/SKILL.md"):
            text = skill_md.read_text(encoding="utf-8")
            for rel in set(re.findall(r"<plugin-root>/((?:references|scripts)/[\w./-]+?)[`\"\s)]", text)):
                with self.subTest(skill=skill_md.parent.name, path=rel):
                    self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_references_cover_every_scanner_finding(self):
        source = (PLUGIN / "scripts" / "fdscan.py").read_text(encoding="utf-8")
        pitfalls = (PLUGIN / "references" / "pitfalls.md").read_text(encoding="utf-8")
        for code in sorted(set(re.findall(r'add\("(FD\d{3})"', source))):
            with self.subTest(code=code):
                self.assertIn(f"| {code} |", pitfalls)

    def test_manifests_agree_and_declare_the_mcp_server(self):
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        hermes = dict(re.findall(r"^(\w+):\s*(.+)$",
                                 (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"), re.M))
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-fumadocs",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        self.assertEqual(codex["skills"], "./skills/")
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        self.assertEqual(claude["mcpServers"], "./.mcp.json")
        mcp = json.loads((PLUGIN / ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(mcp, {"fumadocs": {"type": "http", "url": "https://www.fumadocs.dev/api/mcp"}})
        changelog = (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {claude['version']} ", changelog)

    def test_marketplaces_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in claude["plugins"]].count("pwdev-fumadocs"), 1)
        entries = [p for p in codex["plugins"] if p["name"] == "pwdev-fumadocs"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-fumadocs"})


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_with_a_bounded_first_turn_bootstrap(self):
        manifest = (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("provides_hooks:\n  - pre_llm_call", manifest)
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_fumadocs_hermes").register(ctx)
        self.assertEqual({name for name, _ in ctx.skills}, SKILLS)
        for name, path in ctx.skills:
            self.assertEqual(path.resolve(), (PLUGIN / "skills" / name / "SKILL.md").resolve())
        first = ctx.hooks["pre_llm_call"](is_first_turn=True, session_id="s")
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-fumadocs:fumadocs-<name>")', first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_missing_skills_fail_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "__init__.py").write_text(
                (PLUGIN / ".hermes-plugin/__init__.py").read_text(encoding="utf-8"), encoding="utf-8")
            ctx = FakeHermes()
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load_module(Path(tmp) / "__init__.py", "pwdev_fumadocs_hermes_broken").register(ctx)
            self.assertEqual((ctx.skills, ctx.hooks), ([], {}))


class OpenCodeInstallerTest(unittest.TestCase):
    def test_links_skills_writes_commands_and_uninstalls_only_its_own(self):
        installer = load_module(PLUGIN / ".opencode-plugin/install.py", "pwdev_fumadocs_opencode")
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / ".opencode"
            out = io.StringIO()
            self.assertEqual(installer.install(PLUGIN, dest, force=False, dry_run=False, out=out), 0)
            self.assertEqual({p.name for p in (dest / "skills").iterdir()}, SKILLS)
            self.assertTrue(all(p.is_symlink() for p in (dest / "skills").iterdir()))
            self.assertEqual({p.stem for p in (dest / "command").iterdir()}, set(COMMANDS.values()))
            text = (dest / "command" / "fumadocs-doctor.md").read_text(encoding="utf-8")
            self.assertIn("`fumadocs-doctor`", text)
            self.assertIn(installer.COMMAND_MARKER, text)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
            scanner = dest / "skills" / "fumadocs-setup" / ".." / ".." / "scripts" / "fdscan.py"
            self.assertTrue((dest / "skills" / "fumadocs-setup").resolve().parent.parent.joinpath(
                "scripts", "fdscan.py").is_file(), scanner)
            self.assertEqual(installer.uninstall(PLUGIN, dest, dry_run=False, out=out), 0)
            self.assertEqual(list((dest / "skills").iterdir()), [])


def write(root: Path, files: dict) -> Path:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip("\n") if isinstance(content, str)
                        else json.dumps(content), encoding="utf-8")
    return root


def package(**deps):
    return {"name": "app", "dependencies": deps}


HEALTHY_NEXT = {
    "package.json": package(**{"next": "16.3.5", "react": "^19.3.0", "fumadocs-core": "16.15.15",
                               "fumadocs-ui": "npm:@fumadocs/base-ui@16.15.15", "fumadocs-mdx": "15.4.5",
                               "tailwindcss": "^4.3.3"}),
    "pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
    "next.config.mjs": """
        import { createMDX } from 'fumadocs-mdx/next';
        const withMDX = createMDX();
        export default withMDX({});
    """,
    "lib/shared.ts": "export const docsRoute = '/docs';\n",
    "lib/source.ts": """
        import { loader } from 'fumadocs-core/source';
        import { defineDocs } from 'fumadocs-mdx/macro';
        import { docsRoute } from './shared';
        const docs = defineDocs({ dir: 'content/docs' });
        export const source = loader({ baseUrl: docsRoute, source: docs.toFumadocsSource() });
    """,
    "app/global.css": "@import 'tailwindcss';\n@import 'fumadocs-ui/css/neutral.css';\n@import 'fumadocs-ui/css/preset.css';\n",
    "app/layout.tsx": """
        import { RootProvider } from 'fumadocs-ui/provider/next';
        export default function Layout({ children }) {
          return <html lang="en" suppressHydrationWarning><body><RootProvider>{children}</RootProvider></body></html>;
        }
    """,
    "app/api/search/route.ts": "import { createFromSource } from 'fumadocs-core/search/server';\n",
    "app/llms.txt/route.ts": "export async function GET() {}\n",
    "app/api/mcp/route.ts": "import { registerSearchTool } from 'fumadocs-core/mcp';\n",
    "content/docs/index.mdx": "---\ntitle: Hello\n---\n\n# Hi\n",
    "content/docs/meta.json": {"pages": ["index", "..."]},
    "node_modules/fumadocs-core/package.json": {"name": "fumadocs-core", "version": "16.15.15"},
    ".next/server/app.js": "import 'fumadocs-core/mcp';\n",
}


class FdscanTest(unittest.TestCase):
    def scan(self, files: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            return fdscan.scan(write(Path(tmp), files), check_node=False)

    def codes(self, report: dict) -> set:
        return {f["id"] for f in report["findings"]}

    def test_empty_directory_is_a_new_project(self):
        report = self.scan({})
        self.assertEqual(report["schema"], "pwdev-fdscan/1")
        self.assertFalse(report["package_json"])
        self.assertFalse(report["installed"])
        self.assertIsNone(report["framework"])
        self.assertEqual(report["findings"], [])

    def test_healthy_next_app(self):
        report = self.scan(HEALTHY_NEXT)
        self.assertEqual(report["framework"], "next")
        self.assertEqual(report["bundler"], "next")
        self.assertEqual(report["package_manager"], "pnpm")
        self.assertEqual(report["content_source"], {"kind": "fumadocs-mdx", "mode": "macro"})
        self.assertEqual(report["base_urls"], ["/docs"], "baseUrl bound to an exported constant")
        self.assertEqual(report["content_dirs"], ["content/docs"])
        self.assertEqual(report["content"], {"pages": 1, "meta_files": 1, "untitled": []})
        self.assertEqual(report["fumadocs"]["fumadocs-core"]["installed"], "16.15.15")
        self.assertEqual(set(report["features"]), {"search", "llms", "mcp"})
        self.assertNotIn(".next/server/app.js", report["features"]["mcp"], "build output is skipped")
        self.assertEqual(report["findings"], [])

    def test_broken_next_app_reports_each_pitfall(self):
        files = dict(HEALTHY_NEXT)
        files.pop("next.config.mjs")
        files.pop("node_modules/fumadocs-core/package.json")  # installed version wins over declared
        files.update({
            "package.json": package(**{"next": "15.0.0", "fumadocs-core": "15.8.0", "fumadocs-ui": "16.0.0",
                                       "fumadocs-mdx": "11.0.0", "tailwindcss": "^3.4.0"}),
            "next.config.js": "module.exports = {};\n",
            "app/global.css": "@tailwind base;\n",
            "app/layout.tsx": "import { RootProvider } from 'fumadocs-ui/provider';\n"
                              "export default () => <html><body><RootProvider /></body></html>;\n",
            "content/docs/untitled.mdx": "# No frontmatter\n",
        })
        report = self.scan(files)
        self.assertTrue({"FD002", "FD003", "FD004", "FD006", "FD007", "FD008", "FD013"} <= self.codes(report),
                        self.codes(report))
        fd013 = next(f for f in report["findings"] if f["id"] == "FD013")
        self.assertEqual(fd013["files"], ["content/docs/untitled.mdx"])
        self.assertTrue(all(f["doc"].startswith("https://www.fumadocs.dev/docs") for f in report["findings"]))

    def test_vite_app_without_plugin_and_config_api_codegen(self):
        report = self.scan({
            "package.json": package(**{"@react-router/dev": "7.0.0", "react-router": "7.0.0",
                                       "fumadocs-core": "16.0.0", "fumadocs-mdx": "15.0.0"}),
            "vite.config.ts": "import { reactRouter } from '@react-router/dev/vite';\nexport default {};\n",
            "source.config.ts": "import { defineDocs } from 'fumadocs-mdx/config';\n"
                                "export const docs = defineDocs({ dir: 'content/guides' });\n",
            ".gitignore": "node_modules\n",
        })
        self.assertEqual(report["framework"], "react-router")
        self.assertEqual(report["bundler"], "vite")
        self.assertEqual(report["content_source"], {"kind": "fumadocs-mdx", "mode": "config"})
        self.assertEqual(report["content_dirs"], ["content/guides"])
        self.assertTrue({"FD009", "FD011", "FD012"} <= self.codes(report), self.codes(report))

    def test_macro_api_with_global_source_config_needs_no_gitignore(self):
        files = dict(HEALTHY_NEXT)
        files["source.config.ts"] = "import { defineConfig } from 'fumadocs-mdx/config';\nexport default defineConfig();\n"
        report = self.scan(files)
        self.assertEqual(report["content_source"]["mode"], "macro")
        self.assertNotIn("FD011", self.codes(report))

    def test_meta_framework_wins_over_its_router(self):
        report = self.scan({"package.json": package(**{"@tanstack/react-start": "1.0.0",
                                                        "@tanstack/react-router": "1.0.0"})})
        self.assertEqual(report["framework"], "tanstack-start")

    def test_i18n_static_export_and_old_node(self):
        files = dict(HEALTHY_NEXT)
        files["next.config.mjs"] = files["next.config.mjs"].replace("withMDX({})", "withMDX({ output: 'export' })")
        files["lib/i18n.ts"] = "import { defineI18n } from 'fumadocs-core/i18n';\nexport const i18n = defineI18n({ parser: 'dir' });\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = write(Path(tmp), files)
            original = fdscan.node_version
            fdscan.node_version = lambda: "20.11.0"
            try:
                report = fdscan.scan(root)
            finally:
                fdscan.node_version = original
        self.assertIn("static-export", report["features"])
        self.assertEqual(report["i18n_parser"], "dir")
        self.assertIn("FD001", self.codes(report))

    def test_cli_formats_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write(Path(tmp), HEALTHY_NEXT)
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(fdscan.main([str(root), "--no-node"]), 0)
            self.assertEqual(json.loads(out.getvalue())["framework"], "next")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(fdscan.main([str(root), "--no-node", "--format", "text"]), 0)
            self.assertIn("FRAMEWORK: next", out.getvalue())
            self.assertIn("ACHADOS: nenhum", out.getvalue())
            missing = subprocess.run([sys.executable, str(PLUGIN / "scripts" / "fdscan.py"),
                                      str(root / "nope")], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)

    def test_scanner_never_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write(Path(tmp), HEALTHY_NEXT)
            before = sorted((p.relative_to(root), p.stat().st_mtime_ns) for p in root.rglob("*"))
            fdscan.scan(root, check_node=False)
            after = sorted((p.relative_to(root), p.stat().st_mtime_ns) for p in root.rglob("*"))
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
