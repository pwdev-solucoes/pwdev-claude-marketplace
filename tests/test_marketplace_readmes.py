"""The root READMEs must describe every plugin the marketplace ships.

Run from the repository root:

    python3 -m unittest tests.test_marketplace_readmes

This exists because pwdev-obsidian shipped in the marketplace and was never added to either
README — no table row, no section, no install command — and nothing noticed. Documentation
drifts silently; a manifest does not.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
READMES = ("README.md", "README.pt-BR.md")


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
        re.findall(r"\[\*\*(pwdev-[a-z-]+)\*\*\][^|]*\|[^|]*\|\s*([0-9][^ |]*)\s*\|", text)
    )


def sections(text):
    return set(re.findall(r"^### (pwdev-[a-z-]+)$", text, re.M))


def install_commands(text):
    return set(re.findall(r"claude plugin install (pwdev-[a-z-]+)@", text))


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


if __name__ == "__main__":
    unittest.main()
