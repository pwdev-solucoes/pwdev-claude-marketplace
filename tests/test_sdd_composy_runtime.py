"""Focused contract tests for the sdd-composy governance templates."""

from pathlib import Path
import json
import re
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "plugins" / "sdd-composy" / "templates"
SCRIPTS = ROOT / "plugins" / "sdd-composy" / "scripts"


class SddMapFixtureTests(unittest.TestCase):
    def test_external_symlink_files_and_directories_are_ignored(self):
        import sys
        sys.path.insert(0, str(SCRIPTS))
        import sdd_map

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "repo"
            outside = base / "outside"
            repo.mkdir()
            outside.mkdir()
            (outside / "leak.py").write_text("not repository evidence\n", encoding="utf-8")
            (outside / "package.json").write_text('{"scripts":{"leak":"echo leak"}}', encoding="utf-8")
            (repo / "external-file.py").symlink_to(outside / "leak.py")
            (repo / "external-dir").symlink_to(outside, target_is_directory=True)

            data = sdd_map.build_map(repo)
            observed = {item["path"] for item in data["manifests"]}
            self.assertNotIn("external-dir/package.json", observed)
            self.assertNotIn("external-file.py", observed)
            self.assertEqual(data["files_observed"], 0)

    def test_companion_publication_uses_temporary_files_and_cleans_up_on_failure(self):
        import sys
        sys.path.insert(0, str(SCRIPTS))
        import sdd_map

        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            data = sdd_map.build_map(repo)
            context = repo / ".planning" / "sdd-composy" / "context"
            original = sdd_map._atomic_write_text

            def fail_once(path, content):
                if path.name == "stack.md":
                    raise RuntimeError("injected publication failure")
                return original(path, content)

            with mock.patch.object(sdd_map, "_atomic_write_text", side_effect=fail_once):
                with self.assertRaisesRegex(RuntimeError, "injected publication failure"):
                    sdd_map.write_map(repo, data)

            self.assertFalse(list(context.glob(".*.tmp")))
            self.assertFalse((context / "stack.md").exists())
            self.assertTrue((context / "project.md").exists())

    def test_adaptive_inventory_commands_domain_staleness_and_secret_exclusion(self):
        import sys
        sys.path.insert(0, str(SCRIPTS))
        import sdd_map

        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "package.json").write_text(json.dumps({"scripts": {"test": "pytest", "lint": "ruff"}}), encoding="utf-8")
            (repo / "pyproject.toml").write_text("[tool.pytest.ini_options]\ntestpaths=['tests']\n", encoding="utf-8")
            (repo / "src" / "billing").mkdir(parents=True)
            (repo / "src" / "billing" / "invoice.py").write_text("# evidence\n", encoding="utf-8")
            (repo / ".env").write_text("SHOULD_NOT_BE_READ=secret\n", encoding="utf-8")
            (repo / "fleet").mkdir()
            (repo / "fleet" / ".env.production").write_text("TOKEN=secret\n", encoding="utf-8")
            output = repo / ".planning" / "sdd-composy" / "context"
            data = sdd_map.build_map(repo, output)

            self.assertEqual(data["schema_version"], "0.2")
            self.assertEqual([x["name"] for x in data["languages"]], ["Python"])
            self.assertEqual([x["command"] for x in data["commands"]], ["npm run lint", "npm run test", "pytest"])
            self.assertTrue(any(x["term"] == "billing" for x in data["domain_evidence"]))
            self.assertFalse(any(".env" in item["path"] for item in data["manifests"]))

            output.mkdir(parents=True)
            (output / "codebase.json").write_text(json.dumps({"source_commit": "old"}), encoding="utf-8")
            refreshed = sdd_map.build_map(repo, output)
            self.assertTrue(refreshed["staleness"]["stale"] is False)  # no git commit is available in fixture

    def test_json_serialization_is_deterministic_and_write_is_repository_bound(self):
        import sys
        sys.path.insert(0, str(SCRIPTS))
        import sdd_map

        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "app.py").write_text("print('ok')\n", encoding="utf-8")
            first = sdd_map.build_map(repo)
            second = sdd_map.build_map(repo)
            self.assertEqual(json.dumps(first, indent=2, sort_keys=True), json.dumps(second, indent=2, sort_keys=True))
            path = sdd_map.write_map(repo, first)
            self.assertTrue(path.is_file())
            self.assertIn('okf_version: "0.2"', (path.parent / "stack.md").read_text(encoding="utf-8"))
            with self.assertRaises(ValueError):
                sdd_map.write_map(repo, first, Path(temporary).parent / "outside")


class SddComposyGovernanceTemplateTests(unittest.TestCase):
    def test_governance_templates_exist_and_have_required_sections(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        claude = (TEMPLATES / "CLAUDE.md").read_text(encoding="utf-8")

        for heading in (
            "## Codebase",
            "## Commands",
            "## Workflow",
            "## Gates",
            "## Artifacts",
            "## Safety",
        ):
            self.assertIn(heading, agents)

        self.assertIn("AGENTS.md", claude)
        self.assertIn("canonical", claude.lower())
        self.assertNotIn("## Codebase", claude)

    def test_agents_template_consumes_f01_workflow_and_artifact_contracts(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")

        for value in (
            "INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS",
            "EXECUTE",
            "QA",
            "EVIDENCE",
            "REVIEW",
            "VERIFY",
            "COMPLETE",
            "tasks/prd-<slug>/",
            ".planning/sdd-composy/",
            "tasks/index.md",
            "okf_version: \"0.2\"",
        ):
            self.assertIn(value, agents)

    def test_agents_template_declares_render_variables(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        variables = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", agents))

        self.assertGreaterEqual(
            variables,
            {
                "PROJECT_NAME",
                "SOURCE_COMMIT",
                "GENERATED_AT",
                "ACTOR_ID",
                "STACK_SUMMARY",
                "COMMANDS",
            },
        )
        self.assertNotRegex(agents, r"\{\{\s*TODO|\$\{|<TODO>|TBD")

    def test_rendering_replaces_every_scaffold_variable(self):
        values = {
            "PROJECT_NAME": "Example project",
            "SOURCE_COMMIT": "0123456789abcdef",
            "GENERATED_AT": "2026-09-08T18:29:34+00:00",
            "ACTOR_ID": "human:example",
            "STACK_SUMMARY": "Python 3; unittest",
            "COMMANDS": "python3 -m unittest",
        }
        for path in (TEMPLATES / "AGENTS.md", TEMPLATES / "CLAUDE.md"):
            rendered = path.read_text(encoding="utf-8")
            for name, value in values.items():
                rendered = rendered.replace("{{" + name + "}}", value)
            self.assertNotRegex(rendered, r"\{\{[A-Z][A-Z0-9_]*\}\}")
            self.assertNotRegex(rendered, r"\{\{\s*TODO|\$\{|<TODO>|TBD")

    def test_safety_contract_is_explicit(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")

        for value in (
            "Never overwrite existing governance files",
            "Never read .env",
            "credentials",
            "tokens",
            "private keys",
            "certificates",
            "Never merge fleet branches automatically",
            "Never infer human approval from artifact existence",
            "atomic",
            "preserve unknown JSON fields",
        ):
            self.assertIn(value, agents)


if __name__ == "__main__":
    unittest.main()
