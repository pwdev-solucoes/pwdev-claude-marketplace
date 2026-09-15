"""The root READMEs must describe every plugin the marketplace ships.

Run from the repository root:

    python3 -m unittest tests.test_marketplace_readmes

This exists because pwdev-obsidian shipped in the marketplace and was never added to either
README — no table row, no section, no install command — and nothing noticed. Documentation
drifts silently; a manifest does not.
"""

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
READMES = ("README.md", "README.pt-BR.md")
PLUGIN_NAME = r"(?:pwdev|sdd)-[a-z-]+"


def marketplace_plugins():
    return [p["name"] for p in json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]]


def declared_version(name):
    manifest = ROOT / "plugins" / name / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return None
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def readme(name):
    return (ROOT / name).read_text(encoding="utf-8")


def table_rows(text):
    """{plugin: version} from the plugin table."""
    return dict(
        re.findall(rf"\[\*\*({PLUGIN_NAME})\*\*\][^|]*\|[^|]*\|\s*([0-9][^ |]*)\s*\|", text)
    )


def sections(text):
    return set(re.findall(rf"^### ({PLUGIN_NAME})$", text, re.M))


def install_commands(text):
    return set(re.findall(rf"claude plugin install ({PLUGIN_NAME})@", text))


def inventory_claims(text):
    """{plugin: declared inventory} from README inventory lines."""
    claims = {}
    pattern = re.compile(
        r"^\*\*(?:Ships|Inclui):\*\* (?P<inventory>[^\n]+)\n\n"
        rf"[^\n]*\./plugins/(?P<plugin>{PLUGIN_NAME})/",
        re.M,
    )
    for match in pattern.finditer(text):
        inventory = match["inventory"]

        def count(*names):
            labels = "|".join(names)
            if re.search(rf"\b(?:no|sem)\s+(?:\d+\s+)?(?:{labels})\b", inventory, re.I):
                return 0
            found = re.search(rf"\b(\d+)\s+(?:{labels})\b", inventory, re.I)
            return int(found[1]) if found else 0

        def present(name):
            return bool(re.search(rf"\b{name}\b", inventory, re.I)) and not bool(
                re.search(rf"\b(?:no|sem)\s+(?:\w+\s+)*{name}\b", inventory, re.I)
            )

        claims[match["plugin"]] = {
            "commands": count("commands", "comandos"),
            "subagents": count("subagents", "subagentes"),
            "skills": count("skill", "skills"),
            "MCP": present("MCP"),
            "hooks": present("hooks"),
        }
    return claims


def distributed_skills(plugin):
    """SKILL.md files git would ship: tracked or untracked, never ignored (benchmark copies are)."""
    listed = subprocess.run(
        ["git", "-C", str(plugin), "ls-files", "--cached", "--others", "--exclude-standard", "--", "skills"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return sum(1 for line in set(listed) if Path(line).name == "SKILL.md" and (plugin / line).is_file())


def plugin_inventory(name, root=ROOT):
    """Actual inventory from a plugin directory."""
    plugin = root / "plugins" / name
    return {
        "commands": sum(path.is_file() for path in (plugin / "commands").glob("*.md")),
        "subagents": sum(path.is_file() for path in (plugin / "agents").glob("*.md")),
        "skills": distributed_skills(plugin),
        "MCP": (plugin / ".mcp.json").is_file(),
        "hooks": (plugin / "hooks").is_dir(),
    }


class TestMarketplaceCoverage(unittest.TestCase):
    def test_every_shipped_plugin_has_a_table_row(self):
        for name in READMES:
            missing = set(marketplace_plugins()) - set(table_rows(readme(name)))
            self.assertEqual(missing, set(), f"{name} has no table row for: {sorted(missing)}")

    def test_every_shipped_plugin_has_a_section(self):
        for name in READMES:
            missing = set(marketplace_plugins()) - sections(readme(name))
            self.assertEqual(missing, set(), f"{name} has no section for: {sorted(missing)}")

    def test_every_shipped_plugin_has_an_install_command(self):
        for name in READMES:
            missing = set(marketplace_plugins()) - install_commands(readme(name))
            self.assertEqual(missing, set(), f"{name} has no install command for: {sorted(missing)}")

    def test_no_readme_documents_a_plugin_that_is_not_shipped(self):
        shipped = set(marketplace_plugins())
        for name in READMES:
            extra = sections(readme(name)) - shipped
            self.assertEqual(extra, set(), f"{name} documents plugins that do not ship: {sorted(extra)}")

    def test_table_versions_match_the_plugin_manifests(self):
        for name in READMES:
            for plugin, shown in sorted(table_rows(readme(name)).items()):
                real = declared_version(plugin)
                if real is None:
                    continue
                self.assertEqual(
                    shown, real, f"{name}: {plugin} shows {shown}, its manifest says {real}"
                )

    def test_both_readmes_cover_the_same_plugins(self):
        # A translation that drifts is worse than no translation.
        en, pt = (sections(readme(n)) for n in READMES)
        self.assertEqual(en, pt, "the two READMEs document different plugin sets")

    def test_every_plugin_section_links_its_own_documentation(self):
        for name in READMES:
            text = readme(name)
            for plugin in marketplace_plugins():
                # The section body should point at the plugin's own README rather than
                # re-explaining it here, where it would go stale.
                self.assertRegex(
                    text,
                    rf"\./plugins/{re.escape(plugin)}/",
                    f"{name}: the {plugin} section does not link its plugin directory",
                )

    def test_inventory_lines_match_plugin_contents(self):
        for name in READMES:
            claims = inventory_claims(readme(name))
            for plugin in marketplace_plugins():
                stated = claims.get(plugin)
                actual = plugin_inventory(plugin)
                self.assertIsNotNone(
                    stated,
                    f"{name}: {plugin} states <missing>, real value is {actual}",
                )
                for dimension in ("commands", "subagents", "skills", "MCP", "hooks"):
                    with self.subTest(readme=name, plugin=plugin, dimension=dimension):
                        self.assertEqual(
                            stated[dimension],
                            actual[dimension],
                            f"{name}: {plugin} states {stated[dimension]}, "
                            f"real value is {actual[dimension]}",
                        )


class TestPluginInventory(unittest.TestCase):
    def test_skills_ignored_by_git_are_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            plugin = root / "plugins" / "demo"
            (plugin / "skills" / "real").mkdir(parents=True)
            (plugin / "skills" / "real" / "SKILL.md").write_text("---\nname: real\n---\n")
            copy = plugin / "skills" / "real" / "evals" / "baseline" / "skills" / "copied"
            copy.mkdir(parents=True)
            (copy / "SKILL.md").write_text("---\nname: copied\n---\n")
            (root / ".gitignore").write_text("**/evals/baseline/\n")
            self.assertEqual(plugin_inventory("demo", root)["skills"], 1)


if __name__ == "__main__":
    unittest.main()
