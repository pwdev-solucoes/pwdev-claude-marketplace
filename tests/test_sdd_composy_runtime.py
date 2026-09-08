"""Focused contract tests for the sdd-composy governance templates."""

from pathlib import Path
import re
import json
import importlib.util
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "plugins" / "sdd-composy" / "templates"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class SddComposyGovernanceTemplateTests(unittest.TestCase):
    def test_governance_templates_exist_and_have_required_sections(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        claude = (TEMPLATES / "CLAUDE.md").read_text(encoding="utf-8")
        for heading in ("## Codebase", "## Commands", "## Workflow", "## Gates", "## Artifacts", "## Safety"):
            self.assertIn(heading, agents)
        self.assertIn("AGENTS.md", claude)
        self.assertIn("canonical", claude.lower())
        self.assertNotIn("## Codebase", claude)

    def test_agents_template_consumes_f01_workflow_and_artifact_contracts(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        for value in ("INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS", "EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY", "COMPLETE", "tasks/prd-<slug>/", ".planning/sdd-composy/", "tasks/index.md", "okf_version: \"0.2\""):
            self.assertIn(value, agents)

    def test_agents_template_declares_render_variables(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        variables = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", agents))
        self.assertGreaterEqual(variables, {"PROJECT_NAME", "SOURCE_COMMIT", "GENERATED_AT", "ACTOR_ID", "STACK_SUMMARY", "COMMANDS"})
        self.assertNotRegex(agents, r"\{\{\s*TODO|\$\{|<TODO>|TBD")

    def test_rendering_replaces_every_scaffold_variable(self):
        values = {"PROJECT_NAME": "Example project", "SOURCE_COMMIT": "0123456789abcdef", "GENERATED_AT": "2026-09-08T18:29:34+00:00", "ACTOR_ID": "human:example", "STACK_SUMMARY": "Python 3; unittest", "COMMANDS": "python3 -m unittest"}
        for path in (TEMPLATES / "AGENTS.md", TEMPLATES / "CLAUDE.md"):
            rendered = path.read_text(encoding="utf-8")
            for name, value in values.items():
                rendered = rendered.replace("{{" + name + "}}", value)
            self.assertNotRegex(rendered, r"\{\{[A-Z][A-Z0-9_]*\}\}")
            self.assertNotRegex(rendered, r"\{\{[^{}]+\}\}")
            self.assertNotRegex(rendered, r"\{\{\s*TODO|\$\{|<TODO>|TBD")

    def test_safety_contract_is_explicit(self):
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        for value in ("Never overwrite existing governance files", "Never read .env", "credentials", "tokens", "private keys", "certificates", "Never merge fleet branches automatically", "Never infer human approval from artifact existence", "atomic", "preserve unknown JSON fields"):
            self.assertIn(value, agents)

    def test_rule_templates_are_discoverable_from_canonical_governance(self):
        rules_dir = TEMPLATES / "rules"
        expected = {
            "00-sdd-composy.md",
            "architecture.md",
            "testing.md",
            "workflow.md",
        }
        self.assertTrue(rules_dir.is_dir())
        self.assertEqual({path.name for path in rules_dir.glob("*.md")}, expected)
        agents = (TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")
        expected_links = {f".agents/rules/{name}" for name in expected}
        actual_links = set(MARKDOWN_LINK.findall(agents))
        self.assertEqual(actual_links, expected_links)
        with tempfile.TemporaryDirectory() as directory:
            installed_root = Path(directory)
            installed_rules = installed_root / ".agents" / "rules"
            installed_rules.mkdir(parents=True)
            for name in expected:
                (installed_rules / name).write_text("# installed rule\n", encoding="utf-8")
            for destination in actual_links:
                resolved = (installed_root / destination).resolve()
                self.assertTrue(resolved.is_file())
                self.assertEqual(resolved, (installed_rules / destination.removeprefix(".agents/rules/")).resolve())

    def test_rule_templates_have_distinct_responsibilities_and_canonical_links(self):
        rules_dir = TEMPLATES / "rules"
        rules = {
            path.stem: path.read_text(encoding="utf-8")
            for path in sorted(rules_dir.glob("*.md"))
        }
        self.assertEqual(set(rules), {"00-sdd-composy", "architecture", "testing", "workflow"})
        self.assertIn("AGENTS.md", rules["00-sdd-composy"])
        responsibility_markers = {
            "00-sdd-composy": "rule discovery and precedence",
            "architecture": "architecture decisions and boundaries",
            "testing": "verification and evidence",
            "workflow": "lifecycle sequencing and approvals",
        }
        for name, marker in responsibility_markers.items():
            self.assertIn("## Responsibility", rules[name], name)
            self.assertIn(marker, rules[name], name)
        for name, content in rules.items():
            self.assertTrue(content.startswith("# "), name)
            self.assertNotIn("{{", content, name)
            self.assertNotIn("TBD", content, name)
        # The segmented files point back to the canonical contract instead of
        # creating a second governance root or repeating its full policy.
        with tempfile.TemporaryDirectory() as directory:
            installed_root = Path(directory)
            installed_rules = installed_root / ".agents" / "rules"
            installed_rules.mkdir(parents=True)
            canonical = (installed_root / ".agents" / "AGENTS.md").resolve()
            canonical.write_text("# canonical governance\n", encoding="utf-8")
            for name, content in rules.items():
                installed_path = installed_rules / f"{name}.md"
                installed_path.write_text(content, encoding="utf-8")
                destinations = MARKDOWN_LINK.findall(content)
                self.assertIn("../AGENTS.md", destinations, name)
                resolved = (installed_path.parent / "../AGENTS.md").resolve()
                self.assertTrue(resolved.is_file(), name)
                self.assertEqual(resolved, canonical, name)
        owned_policy = {
            "architecture": ("record architecture, interfaces, migrations", "reuse established modules and conventions"),
            "testing": ("smallest relevant command", "fresh output as evidence"),
            "workflow": ("canonical lifecycle", "explicit human approval", "keep `quick` within its five-file limit"),
        }
        for owner, phrases in owned_policy.items():
            for phrase in phrases:
                self.assertIn(phrase, rules[owner].lower(), f"{phrase} missing from {owner}")
                for other, content in rules.items():
                    if other != owner:
                        self.assertNotIn(phrase, content.lower(), f"{phrase} duplicated in {other}")
        self.assertLess(len(rules["architecture"]), len((TEMPLATES / "AGENTS.md").read_text(encoding="utf-8")))


class SddComposyInitRuntimeTests(unittest.TestCase):
    SCRIPT = ROOT / "plugins" / "sdd-composy" / "scripts" / "sdd_init.py"

    def run_init(self, root, command, *extra):
        result = subprocess.run(
            ["python3", str(self.SCRIPT), command, str(root), "--actor", "human:test", *extra],
            text=True, capture_output=True, check=False,
        )
        payload = json.loads(result.stdout)
        return result, payload

    def test_clean_init_creates_okf_bundle_and_compatibility_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            applied, payload = self.run_init(root, "apply")
            self.assertEqual(applied.returncode, 0, payload)
            self.assertTrue((root / ".claude").is_symlink())
            self.assertEqual((root / ".claude").readlink(), Path(".agents"))
            index = (root / "tasks/index.md").read_text(encoding="utf-8")
            self.assertIn('okf_version: "0.2"', index)
            self.assertIn("by: human:test", index)
            self.assertEqual(self.run_init(root, "verify")[1]["ok"], True)

    def test_reinit_is_idempotent_and_does_not_change_generated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_init(root, "apply")
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            self.assertFalse(plan["actions"])
            self.assertFalse(plan["conflicts"])
            self.run_init(root, "apply")
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)

    def test_file_directory_and_symlink_conflicts_are_reported_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("user file\n", encoding="utf-8")
            (root / ".agents").mkdir()
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            self.assertIn({"path": "AGENTS.md", "reason": "file"}, plan["conflicts"])
            self.assertIn({"path": ".agents", "reason": "existing directory"}, plan["conflicts"])
            before = (root / "AGENTS.md").read_text(encoding="utf-8")
            bad = self.run_init(root, "apply", "--plan-token", "wrong")[0]
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8"), before)

    def test_unsafe_symlink_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / "AGENTS.md").symlink_to(Path(outside) / "AGENTS.md")
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            self.assertIn({"path": "AGENTS.md", "reason": "symlink"}, plan["conflicts"])
            self.assertFalse((Path(outside) / "AGENTS.md").exists())

    def test_verify_rejects_malformed_actor_missing_rules_and_wrong_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_init(root, "apply")
            index = root / "tasks/index.md"
            index.write_text(index.read_text(encoding="utf-8").replace("by: human:test", "notby: human:test"), encoding="utf-8")
            self.assertFalse(self.run_init(root, "verify")[1]["ok"])
            index.write_text(index.read_text(encoding="utf-8").replace("notby: human:test", "by: human:test"), encoding="utf-8")
            (root / ".agents/rules/testing.md").unlink()
            self.assertFalse(self.run_init(root, "verify")[1]["ok"])
            (root / ".agents/rules/testing.md").write_text("# testing\n", encoding="utf-8")
            (root / ".claude").unlink()
            (root / ".claude").symlink_to("wrong-target")
            self.assertFalse(self.run_init(root, "verify")[1]["ok"])

    def test_verify_rejects_missing_or_mismatched_top_level_actor_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_init(root, "apply")
            index = root / "tasks/index.md"
            original = index.read_text(encoding="utf-8")
            self.assertIn("actor_id: human:test", original)
            index.write_text(original.replace("actor_id: human:test", "actor_id: another:actor"), encoding="utf-8")
            self.assertFalse(self.run_init(root, "verify")[1]["ok"])
            index.write_text(original.replace("actor_id: human:test\n", ""), encoding="utf-8")
            self.assertFalse(self.run_init(root, "verify")[1]["ok"])

    def test_real_destination_directory_conflict_and_saved_token_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").mkdir()
            _, plan = self.run_init(root, "plan")
            self.assertIn({"path": "AGENTS.md", "reason": "directory"}, plan["conflicts"])
            applied, payload = self.run_init(root, "apply", "--plan-token", plan["plan_token"])
            self.assertEqual(applied.returncode, 0, payload)
            self.assertTrue((root / "CLAUDE.md").is_file())
            self.assertTrue((root / "AGENTS.md").is_dir())

    def test_parent_symlink_is_rejected_during_apply(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / "tasks").symlink_to(outside, target_is_directory=True)
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            applied, payload = self.run_init(root, "apply", "--plan-token", plan["plan_token"])
            self.assertNotEqual(applied.returncode, 0)
            self.assertFalse((Path(outside) / "index.md").exists())

    def test_atomic_failure_cleans_temporary_publication_file(self):
        spec = importlib.util.spec_from_file_location("sdd_init_under_test", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = module._plan(root, "human:test", module._template_root(None))
            original = module._atomic_create
            calls = []
            def fail_after_first(path, text):
                calls.append(path)
                if len(calls) == 2:
                    raise OSError("injected publication failure")
                return original(path, text)
            module._atomic_create = fail_after_first
            with self.assertRaises(OSError):
                module.apply(root, plan, module._template_root(None))
            self.assertFalse(list(root.rglob(".*.*")))


if __name__ == "__main__":
    unittest.main()
