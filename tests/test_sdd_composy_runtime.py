"""Focused contract tests for the sdd-composy governance templates."""

from pathlib import Path
import re
import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "plugins" / "sdd-composy" / "templates"
sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class SddMapFixtureTests(unittest.TestCase):
    @staticmethod
    def initialize(repo, language="en-US"):
        spec = importlib.util.spec_from_file_location("sdd_init_map_fixture", ROOT / "plugins/sdd-composy/scripts/sdd_init.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plan = module.run_plan(repo, "human:test", TEMPLATES, language)
        result = module.apply(repo, plan, TEMPLATES)
        if result.get("ok") is not True:
            raise AssertionError(result)

    def test_external_symlink_files_and_directories_are_ignored(self):
        import sys
        sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
        import sdd_map
        import sdd_language
        import sdd_language
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); repo = base / "repo"; outside = base / "outside"
            repo.mkdir(); outside.mkdir()
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
        sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
        import sdd_map
        import sdd_language
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.initialize(repo)
            data = sdd_map.build_map(repo)
            context = repo / ".planning/sdd-composy/context"
            context.mkdir(parents=True)
            previous = {name: f"previous {name}\n" for name in ("codebase.json", "project.md", "stack.md", "domain.md", "pitfalls.md")}
            for name, content in previous.items():
                (context / name).write_text(content, encoding="utf-8")
            original = sdd_map.os.replace
            calls = []

            def fail_on_third(source, destination):
                calls.append(Path(destination).name)
                if len(calls) == 3:
                    raise OSError("injected publication failure")
                return original(source, destination)

            with mock.patch.object(sdd_map.os, "replace", side_effect=fail_on_third):
                with self.assertRaisesRegex(OSError, "injected publication failure"):
                    sdd_map.write_map(repo, data)
            self.assertEqual(
                {name: (context / name).read_text(encoding="utf-8") for name in previous},
                previous,
            )
            self.assertEqual(list(context.glob(".*.tmp")), [])

    def test_map_excludes_nested_worktrees_and_its_output_without_hiding_legitimate_directories(self):
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.initialize(repo)
            (repo / ".worktrees/nested/src").mkdir(parents=True)
            (repo / ".worktrees/nested/src/duplicate.py").write_text("# duplicate\n", encoding="utf-8")
            (repo / "src/worktrees").mkdir(parents=True)
            (repo / "src/worktrees/legitimate.py").write_text("# legitimate\n", encoding="utf-8")
            first = sdd_map.build_map(repo)
            sdd_map.write_map(repo, first)
            second = sdd_map.build_map(repo)
            self.assertEqual(first["files_observed"], second["files_observed"])
            evidence = {path for item in second["domain_evidence"] for path in item["evidence"]}
            self.assertIn("src/worktrees/legitimate.py", evidence)
            self.assertFalse(any(path.startswith(".worktrees/") for path in evidence))
            self.assertFalse(any(path.startswith(".planning/sdd-composy/context/") for path in evidence))

    def test_remap_preserves_unknown_json_fields_and_refreshes_known_fields(self):
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.initialize(repo)
            (repo / "current.py").write_text("# current\n", encoding="utf-8")
            context = repo / ".planning/sdd-composy/context"
            context.mkdir(parents=True)
            (context / "codebase.json").write_text(json.dumps({
                "schema": "obsolete",
                "files_observed": -1,
                "future_field": {"keep": True},
                "future_scalar": "unchanged",
            }), encoding="utf-8")
            remapped = sdd_map.build_map(repo)
            self.assertEqual(remapped["schema"], "sdd-composy.codebase")
            self.assertGreater(remapped["files_observed"], 0)
            self.assertEqual(remapped.get("future_field"), {"keep": True})
            self.assertEqual(remapped.get("future_scalar"), "unchanged")
            sdd_map.write_map(repo, remapped)
            published = json.loads((context / "codebase.json").read_text(encoding="utf-8"))
            self.assertEqual(published["future_field"], {"keep": True})
            self.assertEqual(published["future_scalar"], "unchanged")

    def test_map_refuses_symlink_output_and_ancestor_before_reading_or_writing(self):
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            repo = Path(temporary)
            self.initialize(repo)
            context = repo / "generated/context"
            context.parent.mkdir()
            context.symlink_to(outside, target_is_directory=True)
            (Path(outside) / "codebase.json").write_text("not json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "symlink"):
                sdd_map.build_map(repo, context)
            with self.assertRaisesRegex(ValueError, "symlink"):
                sdd_map.write_map(repo, {}, context)
            self.assertEqual((Path(outside) / "codebase.json").read_text(encoding="utf-8"), "not json\n")

    def test_map_refuses_symlink_publication_destination_before_reading_or_writing(self):
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            repo = Path(temporary)
            self.initialize(repo)
            context = repo / ".planning/sdd-composy/context"
            context.mkdir(parents=True)
            external = Path(outside) / "codebase.json"
            external.write_text("not json\n", encoding="utf-8")
            (context / "codebase.json").symlink_to(external)
            with self.assertRaisesRegex(ValueError, "symlink"):
                sdd_map.build_map(repo)
            with self.assertRaisesRegex(ValueError, "symlink"):
                sdd_map.write_map(repo, {})
            self.assertEqual(external.read_text(encoding="utf-8"), "not json\n")

    def test_adaptive_inventory_commands_domain_staleness_and_secret_exclusion(self):
        import sys
        sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
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
            self.assertFalse(refreshed["staleness"]["stale"])

    def test_json_serialization_is_deterministic_and_write_is_repository_bound(self):
        import sys
        sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.initialize(repo)
            (repo / "app.py").write_text("print('ok')\n", encoding="utf-8")
            first = sdd_map.build_map(repo)
            second = sdd_map.build_map(repo)
            self.assertEqual(json.dumps(first, indent=2, sort_keys=True), json.dumps(second, indent=2, sort_keys=True))
            path = sdd_map.write_map(repo, first)
            self.assertTrue(path.is_file())
            self.assertIn('okf_version: "0.2"', (path.parent / "stack.md").read_text(encoding="utf-8"))
            with self.assertRaises(ValueError):
                sdd_map.write_map(repo, first, Path(temporary).parent / "outside")

    def test_external_output_is_rejected_before_read_or_write_in_both_modes(self):
        import sys
        sys.path.insert(0, str(ROOT / "plugins" / "sdd-composy" / "scripts"))
        import sdd_map
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); repo = base / "repo"; outside = base / "outside"
            repo.mkdir(); outside.mkdir()
            # Invalid JSON proves the read-only path rejects the location before
            # attempting to inspect a prior map outside the repository.
            (outside / "codebase.json").write_text("not json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside repository root"):
                sdd_map.build_map(repo, outside)
            with self.assertRaisesRegex(ValueError, "inside repository root"):
                sdd_map.write_map(repo, {}, outside)
            self.assertEqual(list(outside.iterdir()), [outside / "codebase.json"])


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
        # Existing fixture callers model an explicit first-run language choice;
        # the dedicated language tests cover the omitted-language prompt.
        options = list(extra)
        if command in {"plan", "apply"} and "--lang" not in options and "--language" not in options:
            options.extend(["--lang", "en-US"])
        result = subprocess.run(
            ["python3", str(self.SCRIPT), command, str(root), "--actor", "human:test", *options],
            text=True, capture_output=True, check=False,
        )
        payload = json.loads(result.stdout)
        return result, payload

    def test_omitted_language_prompts_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                ["python3", str(self.SCRIPT), "plan", str(root), "--actor", "human:test"],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), {"choices": ["pt-BR", "en-US"]})
            self.assertFalse((root / ".planning").exists())

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

    def test_apply_reports_only_real_creations_and_publishes_valid_init_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, first = self.run_init(root, "apply")
            self.assertEqual(set(first["created"]), {
                "AGENTS.md", "CLAUDE.md", ".agents/rules/00-sdd-composy.md",
                ".agents/rules/architecture.md", ".agents/rules/testing.md",
                ".agents/rules/workflow.md", "tasks/index.md", ".claude",
                ".planning/sdd-composy/config.json", ".planning/sdd-composy/state.json",
            })
            state = json.loads((root / ".planning/sdd-composy/state.json").read_text())
            self.assertEqual(state["schema_version"], "1")
            self.assertEqual(state["revision"], 0)
            self.assertEqual(state["stage"], "INIT")
            self.assertIsNone(state["active_prd"])
            self.assertIsNone(state["active_task"])
            self.assertIsNone(state["last_gate"])
            self.assertEqual(state["blockers"], [])
            self.assertEqual(state["loops"], [])
            self.assertEqual(state["fleet"], [])
            self.assertEqual(state["trace"], {"healthy": True, "source_event_count": 0})
            self.assertEqual(state["next_action"], "run_map")
            _, second = self.run_init(root, "apply")
            self.assertEqual(second["created"], [])

    def test_apply_preserves_unknown_existing_state_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_init(root, "apply")
            state_path = root / ".planning/sdd-composy/state.json"
            state = json.loads(state_path.read_text())
            state["extension"] = {"owned_by": "user", "id": "TASK-999"}
            state_path.write_text(json.dumps(state), encoding="utf-8")
            _, payload = self.run_init(root, "apply")
            self.assertEqual(payload["created"], [])
            self.assertEqual(json.loads(state_path.read_text())["extension"], state["extension"])

    def test_conflicted_apply_does_not_publish_init_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("user-owned\n", encoding="utf-8")
            _, plan = self.run_init(root, "plan")
            result, payload = self.run_init(root, "apply", "--plan-token", plan["plan_token"])
            self.assertNotEqual(result.returncode, 0, payload)
            self.assertFalse(payload["ok"])
            self.assertNotIn(".planning/sdd-composy/state.json", payload["created"])
            self.assertFalse((root / ".planning/sdd-composy/state.json").exists())

    def test_invalid_existing_state_is_rejected_before_any_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / ".planning/sdd-composy/state.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text('{"schema_version":"1","extension":{"id":"TASK-999"}}\n', encoding="utf-8")
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            result, payload = self.run_init(root, "apply")
            self.assertNotEqual(result.returncode, 0, payload)
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after, before)

    def test_existing_claude_directory_requires_coherent_bridge_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".claude").mkdir()
            _, plan = self.run_init(root, "plan")
            self.assertEqual(plan["claude_compatibility"], "existing_directory")
            self.assertIn({"path": ".claude/AGENTS.md", "operation": "create"}, plan["actions"])
            _, applied = self.run_init(root, "apply")
            self.assertIn(".claude/AGENTS.md", applied["created"])
            self.assertEqual((root / ".claude/AGENTS.md").read_text(), "../AGENTS.md\n")
            verified = self.run_init(root, "verify")[1]
            self.assertTrue(verified["ok"], verified)
            self.assertFalse(verified["claude_link_ok"])
            self.assertEqual(verified["claude_compatibility"], "existing_directory")

    def test_verify_requires_valid_language_and_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_init(root, "apply")
            (root / ".planning/sdd-composy/config.json").write_text('{"language":"fr-FR"}')
            result = self.run_init(root, "verify")[1]
            self.assertFalse(result["ok"])
            self.assertFalse(result["language_ok"])
            (root / ".planning/sdd-composy/config.json").write_text('{"language":"en-US"}')
            (root / ".planning/sdd-composy/state.json").unlink()
            result = self.run_init(root, "verify")[1]
            self.assertFalse(result["ok"])
            self.assertFalse(result["state_ok"])
            self.assertEqual(result["next_action"], "reconcile_init_state")

    def test_file_directory_and_symlink_conflicts_are_reported_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("user file\n", encoding="utf-8")
            (root / ".agents").mkdir()
            result, plan = self.run_init(root, "plan")
            self.assertEqual(result.returncode, 0)
            self.assertIn({"path": "AGENTS.md", "reason": "file"}, plan["conflicts"])
            self.assertIn(".agents", plan["unchanged"])
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
            self.assertNotEqual(applied.returncode, 0, payload)
            self.assertFalse(payload["ok"])
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

    def test_plan_rejects_symlink_ancestor_without_reading_external_content(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external = Path(outside)
            (root / ".agents").mkdir()
            (root / ".agents/rules").symlink_to(external, target_is_directory=True)
            (external / "testing.md").write_text("external sentinel", encoding="utf-8")
            _, plan = self.run_init(root, "plan")
            self.assertIn({"path": ".agents/rules/00-sdd-composy.md", "reason": "ancestor symlink"}, plan["conflicts"])
            self.assertNotIn({"path": ".agents/rules/testing.md", "reason": "file"}, plan["conflicts"])

    def test_state_validation_enforces_schema_patterns_types_and_ranges(self):
        spec = importlib.util.spec_from_file_location("sdd_init_state_validation", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        valid = module._state("2026-09-09T00:00:00+00:00")
        invalid_values = [
            {**valid, "active_prd": 123},
            {**valid, "active_prd": "Bad Slug"},
            {**valid, "active_task": "task-2"},
            {**valid, "updated_at": "not-a-date"},
            {**valid, "blockers": [{"id": "bad id", "status": "open"}]},
            {**valid, "loops": [{"id": "LOOP-1", "status": ""}]},
            {**valid, "fleet": ["not-an-object"]},
            {**valid, "trace": {"healthy": True, "source_event_count": -1}},
            {**valid, "revision": True},
        ]
        for value in invalid_values:
            with self.subTest(value=value):
                self.assertFalse(module._valid_state(value))

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
            result = module.apply(root, plan, module._template_root(None))
            self.assertFalse(result["ok"])
            self.assertEqual(result["created"], ["AGENTS.md"])
            self.assertEqual(result["pending"][0], "CLAUDE.md")
            self.assertIn("tasks/index.md", result["pending"])
            self.assertIn("injected publication failure", result["error"])
            self.assertFalse([path for path in root.rglob("*") if path.name.startswith(".") and path.is_file()])

    def test_third_publication_failure_reports_exact_created_and_pending(self):
        spec = importlib.util.spec_from_file_location("sdd_init_partial_report", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = module._plan(root, "human:test", module._template_root(None))
            original = module._atomic_create
            calls = []
            def fail_on_third(path, text):
                calls.append(path)
                if len(calls) == 3:
                    raise OSError("injected-third-publication")
                return original(path, text)
            module._atomic_create = fail_on_third
            result = module.apply(root, plan, module._template_root(None))
            self.assertFalse(result["ok"])
            self.assertEqual(result["created"], ["AGENTS.md", "CLAUDE.md"])
            self.assertEqual(result["pending"][0], ".agents/rules/00-sdd-composy.md")
            self.assertNotIn("AGENTS.md", result["pending"])
            self.assertNotIn("CLAUDE.md", result["pending"])
            self.assertIn("tasks/index.md", result["pending"])
            self.assertIn("injected-third-publication", result["error"])

    def test_symlink_publication_failure_reports_all_documents_and_remaining_steps(self):
        spec = importlib.util.spec_from_file_location("sdd_init_symlink_failure", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = module._plan(root, "human:test", module._template_root(None))
            original = module.os.symlink
            module.os.symlink = lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected-symlink"))
            try:
                result = module.apply(root, plan, module._template_root(None))
            finally:
                module.os.symlink = original
            self.assertFalse(result["ok"])
            self.assertEqual(result["created"], list(module._template_contents(
                module._template_root(None), {
                    "PROJECT_NAME": root.name, "SOURCE_COMMIT": "uncommitted",
                    "GENERATED_AT": "ignored", "ACTOR_ID": "human:test",
                    "STACK_SUMMARY": "Not mapped yet", "COMMANDS": "ignored",
                }
            )) + ["tasks/index.md"])
            self.assertEqual(result["pending"], [".claude", ".planning/sdd-composy/state.json"])
            self.assertIn("injected-symlink", result["error"])

    def test_late_state_publication_failure_reports_config_created_and_only_state_pending(self):
        spec = importlib.util.spec_from_file_location("sdd_init_state_failure", self.SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = module._plan(root, "human:test", module._template_root(None))
            plan["language"] = "en-US"
            original = module._atomic_json
            def fail_state(path, value):
                if path.name == "state.json":
                    raise OSError("injected-state-publication")
                return original(path, value)
            module._atomic_json = fail_state
            result = module.apply(root, plan, module._template_root(None))
            self.assertFalse(result["ok"])
            self.assertIn(".planning/sdd-composy/config.json", result["created"])
            self.assertEqual(result["pending"], [".planning/sdd-composy/state.json"])
            self.assertIn("injected-state-publication", result["error"])


if __name__ == "__main__":
    unittest.main()
