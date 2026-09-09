"""Structural contract tests for the portable sdd-composy plugin."""

import json
import re
import tempfile
import unittest
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
CLAUDE_MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
REFERENCES = PLUGIN / "references"
READMES = (PLUGIN / "README.md", PLUGIN / "README.pt-BR.md")
SCHEMAS = PLUGIN / "schemas"

PLACEHOLDER_PATTERN = re.compile(r"(?im)(?:^|\W)(TODO|TBD|FIXME|XXX)(?:\W|$)|\{\{[^}\n]+\}\}")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")


def unresolved_placeholders(paths):
    return [path for path in paths if PLACEHOLDER_PATTERN.search(path.read_text(encoding="utf-8"))]


def broken_relative_links(paths):
    broken = []
    for path in paths:
        for raw_target in MARKDOWN_LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "/", "mailto:")) or "://" in target:
                continue
            relative = unquote(target.split("#", 1)[0])
            if relative and not (path.parent / relative).resolve().exists():
                broken.append((path, target))
    return broken


def unregistered_skills(plugin):
    skills_root = plugin / "skills"
    commands_root = plugin / "commands"
    skill_names = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    command_names = {path.stem for path in commands_root.glob("*.md")}
    # Portable skills use the sdd-* namespace while Claude adapters use the
    # shorter command name (for example sdd-init -> init).
    registered = command_names | {f"sdd-{name}" for name in command_names}
    return skill_names - registered


def assert_schema_valid(test, schema, value, root=None, path="$"):
    """Small dependency-free validator for the schema features used by fixtures."""
    root = root or schema
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return assert_schema_valid(test, target, value, root, path)
    if "const" in schema:
        test.assertEqual(value, schema["const"], path)
    if "enum" in schema:
        test.assertIn(value, schema["enum"], path)
    if "if" in schema:
        try:
            assert_schema_valid(test, schema["if"], value, root, path)
        except AssertionError:
            pass
        else:
            assert_schema_valid(test, schema["then"], value, root, path)
    expected = schema.get("type")
    if expected is None and ("properties" in schema or "required" in schema):
        expected = "object"
    if isinstance(expected, list):
        if value is None and "null" in expected:
            return
        expected = next(item for item in expected if item != "null")
    if expected == "object":
        test.assertIsInstance(value, dict, path)
        for key in schema.get("required", []):
            test.assertIn(key, value, f"{path}.{key}")
        for key, child in schema.get("properties", {}).items():
            if key in value:
                assert_schema_valid(test, child, value[key], root, f"{path}.{key}")
    elif expected == "array":
        test.assertIsInstance(value, list, path)
        test.assertGreaterEqual(len(value), schema.get("minItems", 0), path)
        if schema.get("uniqueItems"):
            test.assertEqual(len(value), len({json.dumps(v, sort_keys=True) for v in value}), path)
        for index, item in enumerate(value):
            assert_schema_valid(test, schema.get("items", {}), item, root, f"{path}[{index}]")
    elif expected == "string":
        test.assertIsInstance(value, str, path)
        test.assertGreaterEqual(len(value), schema.get("minLength", 0), path)
        if "pattern" in schema:
            test.assertRegex(value, schema["pattern"], path)
        if schema.get("format") == "date-time":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
    elif expected == "integer":
        test.assertIsInstance(value, int, path)
        test.assertGreaterEqual(value, schema.get("minimum", value), path)
        test.assertLessEqual(value, schema.get("maximum", value), path)
    elif expected == "boolean":
        test.assertIsInstance(value, bool, path)


class SddComposyManifestTest(unittest.TestCase):
    def test_dual_runtime_manifests_are_discoverable(self) -> None:
        self.assertTrue(CLAUDE_MANIFEST.is_file(), "Claude manifest must exist")
        self.assertTrue(CODEX_MANIFEST.is_file(), "Codex manifest must exist")

        claude = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))
        codex = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(claude["name"], "sdd-composy")
        self.assertEqual(codex["name"], "sdd-composy")
        self.assertEqual(codex["skills"], "./skills/")
        claude_version = claude["version"].split("+", 1)[0]
        codex_version = codex["version"].split("+", 1)[0]
        self.assertEqual(claude_version, "0.1.0")
        self.assertEqual(codex_version, "0.1.0")
        self.assertEqual(claude_version, codex_version, "runtime manifest versions diverged")
        self.assertEqual(codex["interface"]["displayName"], "SDD Composy")
        for manifest in (claude, codex):
            self.assertNotIn("hooks", manifest)
            self.assertNotIn("mcpServers", manifest)
            self.assertNotIn("apps", manifest)

    def test_claude_marketplace_registers_plugin(self) -> None:
        marketplace = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["sdd-composy"]

        self.assertEqual(entry["source"], "./plugins/sdd-composy")
        self.assertEqual(entry["category"], "workflow")
        self.assertTrue(entry["strict"])

    def test_codex_marketplace_registers_plugin(self) -> None:
        marketplace = json.loads(CODEX_MARKETPLACE.read_text(encoding="utf-8"))
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        entry = entries["sdd-composy"]

        self.assertEqual(
            entry["source"],
            {"source": "local", "path": "./plugins/sdd-composy"},
        )
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Developer Tools")


class SddComposySharedContractTest(unittest.TestCase):
    def reference(self, name: str) -> str:
        path = REFERENCES / f"{name}.md"
        self.assertTrue(path.is_file(), f"shared reference must exist: {path}")
        return path.read_text(encoding="utf-8")

    def test_workflow_defines_canonical_lifecycle_and_gates(self) -> None:
        workflow = self.reference("workflow")
        for phase in (
            "INIT", "MAP", "PRD", "STORIES", "TECHSPEC", "TASKS",
            "EXECUTE", "QA", "EVIDENCE", "REVIEW", "VERIFY", "COMPLETE",
        ):
            self.assertIn(phase, workflow)
        self.assertIn("NOT_APPLICABLE", workflow)
        self.assertIn("explicit human approval", workflow)
        self.assertIn("fresh", workflow)
        self.assertIn("QUICK", workflow)
        self.assertIn("5 implementation files", workflow)

    def test_artifacts_separate_human_and_operational_roots(self) -> None:
        artifacts = self.reference("artifacts")
        self.assertIn("tasks/prd-<slug>/", artifacts)
        self.assertIn(".planning/sdd-composy/", artifacts)
        self.assertIn("OKF v0.2", artifacts)
        self.assertIn("type", artifacts)
        self.assertIn("unknown", artifacts.lower())
        self.assertIn("events.jsonl", artifacts)
        self.assertIn("trace.json", artifacts)
        self.assertIn("never edited directly", artifacts.lower())

    def test_states_define_guarded_task_transitions(self) -> None:
        states = self.reference("states")
        for state in (
            "pending", "ready", "running", "qa_required", "evidence_required",
            "review_required", "verify_required", "complete", "blocked",
            "rejected", "skipped",
        ):
            self.assertIn(state, states)
        self.assertIn("rejected -> ready", states)
        self.assertIn("dependencies", states)
        self.assertIn("explicit justification", states)
        self.assertIn("fresh test evidence", states)

    def test_safety_prohibits_secrets_and_unsafe_automation(self) -> None:
        safety = self.reference("safety")
        for prohibited in (
            ".env", "credentials", "tokens", "private keys", "certificates",
            "fleet environment files",
        ):
            self.assertIn(prohibited, safety)
        self.assertIn("Never merge fleet branches automatically", safety)
        self.assertIn("Never infer human approval", safety)
        self.assertIn("Preserve unknown JSON fields", safety)
        self.assertIn("same-directory temporary files", safety)
        self.assertIn("atomically replace", safety)

    def test_foundation_markdown_has_no_placeholders_or_broken_relative_links(self) -> None:
        markdown = (*READMES, *sorted(REFERENCES.glob("*.md")))
        self.assertEqual(unresolved_placeholders(markdown), [])
        self.assertEqual(broken_relative_links(markdown), [])

    def test_structural_checks_reject_bad_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            placeholder = root / "placeholder.md"
            placeholder.write_text("## TODO: replace this\n", encoding="utf-8")
            broken = root / "broken.md"
            broken.write_text("[missing](./absent.md)\n", encoding="utf-8")
            self.assertEqual(unresolved_placeholders((placeholder,)), [placeholder])
            self.assertEqual(broken_relative_links((broken,)), [(broken, "./absent.md")])

    def test_every_portable_skill_has_a_claude_adapter(self) -> None:
        self.assertEqual(unregistered_skills(PLUGIN), set())

    def test_skill_registration_check_rejects_an_orphan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugin = Path(temporary)
            skill = plugin / "skills" / "orphan"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Orphan\n", encoding="utf-8")
            self.assertEqual(unregistered_skills(plugin), {"orphan"})

    def test_loop_skill_and_adapter_are_registered_and_disclose_bounds(self) -> None:
        skill = PLUGIN / "skills" / "sdd-loop" / "SKILL.md"
        adapter = PLUGIN / "skills" / "sdd-loop" / "agents" / "openai.yaml"
        command = PLUGIN / "commands" / "loop.md"
        self.assertTrue(skill.is_file())
        self.assertTrue(adapter.is_file())
        self.assertTrue(command.is_file())
        content = skill.read_text(encoding="utf-8")
        for required in (
            "sdd_loop.py", "start", "status", "continue", "cancel",
            "3 iterations", "human", "scope", "architecture", "destructive",
            "cancellation", "safe-stop", "sdd-verify",
        ):
            self.assertIn(required, content)
        self.assertIn("$sdd-loop", command.read_text(encoding="utf-8"))
        metadata = adapter.read_text(encoding="utf-8")
        self.assertIn("display_name", metadata)
        self.assertIn("bounded", metadata)


class SddComposyRuntimeContractTest(unittest.TestCase):
    def test_trace_skill_and_adapter_are_registered_and_safe(self) -> None:
        skill = PLUGIN / "skills" / "sdd-trace" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        command = PLUGIN / "commands" / "trace.md"
        self.assertTrue(skill.is_file())
        self.assertTrue(metadata.is_file())
        self.assertTrue(command.is_file())
        text = skill.read_text(encoding="utf-8")
        for required in (
            "name: sdd-trace", "scripts/sdd_trace.py", "record", "events",
            "summary", "verify", "build", "query", "verify-projection",
            "events.jsonl", "trace.json", "append-only", "Never record prompts",
            "Never edit trace.json", "semantic events are recorded only after",
        ):
            self.assertIn(required, text)
        self.assertIn("$sdd-trace", metadata.read_text(encoding="utf-8"))
        adapter = command.read_text(encoding="utf-8")
        for required in ("/sdd-composy:trace", "$ARGUMENTS", "$sdd-trace", "skills/sdd-trace/SKILL.md"):
            self.assertIn(required, adapter)
        self.assertLess(len(adapter), 1200)
        for forbidden in ("Never edit trace.json", "event validation", "append-only"):
            self.assertNotIn(forbidden.lower(), adapter.lower())

    def test_runtime_contract_defines_shared_core_discovery(self) -> None:
        runtime = (REFERENCES / "runtime.md").read_text(encoding="utf-8")
        for shared_root in ("skills/", "references/", "scripts/", "templates/", "schemas/"):
            self.assertIn(shared_root, runtime)
        self.assertIn(".claude-plugin/plugin.json", runtime)
        self.assertIn(".codex-plugin/plugin.json", runtime)
        self.assertIn('"skills": "./skills/"', runtime)
        self.assertIn("commands/<name>.md", runtime)
        self.assertIn("thin adapter", runtime.lower())
        self.assertIn("must not duplicate", runtime.lower())
        self.assertIn("must not depend", runtime.lower())
        self.assertIn("pwdev-flow", runtime)
        self.assertIn("pwdev-feat", runtime)

    def test_bilingual_readmes_describe_the_same_portable_contract(self) -> None:
        for path in READMES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Claude Code", text)
            self.assertIn("Codex", text)
            self.assertIn("tasks/prd-<slug>/", text)
            self.assertIn(".planning/sdd-composy/", text)
            self.assertIn("OKF v0.2", text)
            self.assertIn("$sdd-composy-<name>", text)
            self.assertIn("/sdd-composy:<name>", text)
            self.assertIn("references/runtime.md", text)


class SddComposyInitAdapterTest(unittest.TestCase):
    def test_init_skill_is_discoverable_with_codex_metadata(self) -> None:
        skill = PLUGIN / "skills" / "sdd-init" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file(), "portable sdd-init skill must exist")
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        skill_text = skill.read_text(encoding="utf-8")
        metadata_text = metadata.read_text(encoding="utf-8")
        self.assertRegex(skill_text, r"(?m)^name:\s*sdd-init\s*$")
        self.assertIn("description:", skill_text)
        self.assertIn("display_name:", metadata_text)
        self.assertIn("$sdd-init", metadata_text)

    def test_init_skill_routes_through_the_shared_helper_contract(self) -> None:
        skill = (PLUGIN / "skills" / "sdd-init" / "SKILL.md").read_text(encoding="utf-8")
        helper = "${CLAUDE_PLUGIN_ROOT}/scripts/sdd_init.py"
        self.assertIn(helper, skill)
        for operation in ("inspect", "plan", "apply", "verify"):
            self.assertRegex(skill, rf"\b{operation}\b")
        for shared_reference in ("references/runtime.md", "references/safety.md"):
            self.assertIn(shared_reference, skill)
        self.assertIn("--plan-token", skill)
        self.assertIn("tasks/index.md", skill)
        self.assertIn("never read", skill.lower())
        self.assertIn(".env", skill)

    def test_claude_init_command_is_a_thin_route_to_portable_skill(self) -> None:
        command_path = PLUGIN / "commands" / "init.md"
        self.assertTrue(command_path.is_file(), "Claude init command must exist")
        command = command_path.read_text(encoding="utf-8")
        self.assertIn("/sdd-composy:init", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$sdd-init", command)
        self.assertIn("skills/sdd-init/SKILL.md", command)
        self.assertLess(len(command), 1200, "Claude adapter should remain thin")
        for policy in ("Never overwrite", "lifecycle", "gate logic", "schema semantics"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyMapAdapterTest(unittest.TestCase):
    def test_map_skill_is_discoverable_and_declares_evidence_contract(self) -> None:
        skill = PLUGIN / "skills" / "sdd-map" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file(), "portable sdd-map skill must exist")
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        text = skill.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name:\s*sdd-map\s*$")
        for required in (
            "observation-only", "source_commit", "staleness", "--write",
            ".planning/sdd-composy/context/codebase.json", "project.md",
            "stack.md", "domain.md", "pitfalls.md", "references/mapping.md",
            "Never inspect or open", "manifest commands", "PRD", "STORIES",
            "TECHSPEC", "TASKS",
        ):
            self.assertIn(required, text)
        self.assertIn("$sdd-map", metadata.read_text(encoding="utf-8"))

    def test_map_skill_keeps_runtime_and_scanner_boundaries(self) -> None:
        text = (PLUGIN / "skills" / "sdd-map" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("scripts/sdd_map.py", text)
        self.assertIn("Do not execute commands discovered in manifests", text)
        self.assertIn("must not duplicate scanner logic", text)
        self.assertIn("runtime-specific tools", text)
        for forbidden in ("mcp__", "codex_app", "claude -p"):
            self.assertNotIn(forbidden, text)

    def test_claude_map_command_is_a_thin_route_to_portable_skill(self) -> None:
        command_path = PLUGIN / "commands" / "map.md"
        self.assertTrue(command_path.is_file(), "Claude map command must exist")
        command = command_path.read_text(encoding="utf-8")
        self.assertIn("/sdd-composy:map", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$sdd-map", command)
        self.assertIn("skills/sdd-map/SKILL.md", command)
        self.assertLess(len(command), 1000, "Claude adapter should remain thin")
        for policy in ("staleness", "secret exclusion", "architecture", "downstream"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyPrdAdapterTest(unittest.TestCase):
    def test_prd_skill_is_discoverable_and_routes_the_product_contract(self) -> None:
        skill = PLUGIN / "skills" / "sdd-prd" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file(), "portable sdd-prd skill must exist")
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        text = skill.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name:\s*sdd-prd\s*$")
        for required in (
            "references/product.md", "templates/prd.md", "user problem",
            "tasks/prd-<slug>/prd.md", "RF-", "CA-", "no architecture decisions",
        ):
            self.assertIn(required, text)
        self.assertIn("$sdd-prd", metadata.read_text(encoding="utf-8"))

    def test_prd_skill_enforces_an_explicit_human_gate(self) -> None:
        text = (PLUGIN / "skills" / "sdd-prd" / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "human_approval", "PENDING", "APPROVED", "verified", "human",
            "existence does not imply approval", "stops downstream generation",
        ):
            self.assertIn(required, text)
        self.assertNotIn("automatically approve", text.lower())

    def test_prd_skill_is_runtime_neutral(self) -> None:
        text = (PLUGIN / "skills" / "sdd-prd" / "SKILL.md").read_text(encoding="utf-8")
        for forbidden in ("mcp__", "codex_app", "claude -p"):
            self.assertNotIn(forbidden, text)
        self.assertIn("runtime-specific tools", text)

    def test_claude_prd_command_is_a_thin_route_to_portable_skill(self) -> None:
        command_path = PLUGIN / "commands" / "prd.md"
        self.assertTrue(command_path.is_file(), "Claude PRD command must exist")
        command = command_path.read_text(encoding="utf-8")
        self.assertIn("/sdd-composy:prd", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$sdd-prd", command)
        self.assertIn("skills/sdd-prd/SKILL.md", command)
        self.assertLess(len(command), 1000, "Claude adapter should remain thin")
        for policy in ("human_approval", "architecture", "RF-", "CA-"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyStoriesAdapterTest(unittest.TestCase):
    def test_claude_stories_command_is_a_thin_route_to_portable_skill(self) -> None:
        command_path = PLUGIN / "commands" / "stories.md"
        self.assertTrue(command_path.is_file(), "Claude stories command must exist")
        command = command_path.read_text(encoding="utf-8")
        self.assertIn("/sdd-composy:stories", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$sdd-stories", command)
        self.assertIn("skills/sdd-stories/SKILL.md", command)
        self.assertLess(len(command), 1000, "Claude adapter should remain thin")
        for policy in ("human_approval", "NOT_APPLICABLE", "architecture", "US-", "SC-"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyTasksAdapterTest(unittest.TestCase):
    def test_tasks_skill_routes_all_operations_and_boundaries(self) -> None:
        skill = PLUGIN / "skills" / "sdd-tasks" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file())
        self.assertTrue(metadata.is_file())
        text = skill.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name:\s*sdd-tasks\s*$")
        for operation in ("import", "list", "next", "show", "start", "block", "transition", "verify"):
            self.assertIn(operation, text)
        for required in ("scripts/sdd_tasks.py", "tasks/prd-<slug>/", "explicit human approval",
                         "stable", "unknown JSON fields", "atomic replacement", "runtime-neutral"):
            self.assertIn(required, text)
        for forbidden in ("mcp__", "codex_app", "claude -p"):
            self.assertNotIn(forbidden, text)
        self.assertIn("$sdd-tasks", metadata.read_text(encoding="utf-8"))

    def test_claude_tasks_command_is_a_thin_route(self) -> None:
        command = (PLUGIN / "commands" / "tasks.md").read_text(encoding="utf-8")
        for required in ("/sdd-composy:tasks", "$ARGUMENTS", "$sdd-tasks",
                         "skills/sdd-tasks/SKILL.md", "return the shared skill's result unchanged"):
            self.assertIn(required, command)
        self.assertLess(len(command), 1000)
        for policy in ("human approval", "dependencies", "atomic replacement", "evidence"):
            self.assertNotIn(policy, command.lower())


class SddComposySyncAdapterTest(unittest.TestCase):
    def test_sync_skill_is_discoverable_and_exposes_safe_operations(self) -> None:
        skill = PLUGIN / "skills" / "sdd-sync" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file(), "portable sdd-sync skill must exist")
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        text = skill.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name:\s*sdd-sync\s*$")
        for operation in ("inspect", "plan", "apply", "sdd_sync.py", "CONFIRM-SDD-SYNC"):
            self.assertIn(operation, text)
        for required in ("read-only", "explicit", "authority", "conflict", "runtime-neutral"):
            self.assertIn(required, text.lower())
        for forbidden in ("mcp__", "codex_app", "claude -p"):
            self.assertNotIn(forbidden, text)
        self.assertIn("$sdd-sync", metadata.read_text(encoding="utf-8"))

    def test_claude_sync_command_is_a_thin_route(self) -> None:
        command = (PLUGIN / "commands" / "sync.md").read_text(encoding="utf-8")
        for required in ("/sdd-composy:sync", "$ARGUMENTS", "$sdd-sync",
                         "skills/sdd-sync/SKILL.md", "return the shared skill's result unchanged"):
            self.assertIn(required, command)
        self.assertLess(len(command), 1000)
        for policy in ("CONFIRM-SDD-SYNC", "authority", "conflict", "atomic replacement"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyStatusAdapterTest(unittest.TestCase):
    def test_status_skill_is_discoverable_and_read_only(self) -> None:
        skill = PLUGIN / "skills" / "sdd-status" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        self.assertTrue(skill.is_file(), "portable sdd-status skill must exist")
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        text = skill.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name:\s*sdd-status\s*$")
        for required in ("sdd_status.py", "--feature", "--tasks", "--fleet", "--json", "read-only", "runtime-neutral"):
            self.assertIn(required, text)
        for forbidden in ("mcp__", "codex_app", "claude -p", "write", "repair"):
            self.assertNotIn(forbidden, text.lower())
        self.assertIn("$sdd-status", metadata.read_text(encoding="utf-8"))

    def test_claude_status_command_is_a_thin_route(self) -> None:
        command = (PLUGIN / "commands" / "status.md").read_text(encoding="utf-8")
        for required in ("/sdd-composy:status", "$ARGUMENTS", "$sdd-status",
                         "skills/sdd-status/SKILL.md", "return the shared skill's result unchanged"):
            self.assertIn(required, command)
        self.assertLess(len(command), 1000)
        for policy in ("repair", "write"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyQaAdapterTest(unittest.TestCase):
    def test_claude_qa_command_is_a_thin_route(self) -> None:
        command_path = PLUGIN / "commands" / "qa.md"
        self.assertTrue(command_path.is_file(), "Claude QA command must exist")
        command = command_path.read_text(encoding="utf-8")
        for required in (
            "/sdd-composy:qa", "$ARGUMENTS", "$sdd-qa",
            "skills/sdd-qa/SKILL.md", "return the shared skill's result unchanged",
        ):
            self.assertIn(required, command)
        self.assertLess(len(command), 1000, "Claude adapter should remain thin")
        for policy in ("qa_required", "evidence_required", "CA-", "SC-", "browser", "REJECTED"):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyTechSpecAdapterTest(unittest.TestCase):
    def skill_text(self) -> str:
        path = PLUGIN / "skills" / "sdd-techspec" / "SKILL.md"
        self.assertTrue(path.is_file(), "portable sdd-techspec skill must exist")
        return path.read_text(encoding="utf-8")

    def test_techspec_skill_is_discoverable_and_routes_contracts(self) -> None:
        skill = PLUGIN / "skills" / "sdd-techspec" / "SKILL.md"
        metadata = skill.parent / "agents" / "openai.yaml"
        text = self.skill_text()
        self.assertTrue(metadata.is_file(), "Codex metadata must exist")
        self.assertRegex(text, r"(?m)^name:\s*sdd-techspec\s*$")
        for required in (
            "references/specification.md", "templates/techspec.md",
            "references/workflow.md", "tasks/prd-<slug>/techspec.md",
        ):
            self.assertIn(required, text)
        self.assertIn("$sdd-techspec", metadata.read_text(encoding="utf-8"))

    def test_techspec_skill_enforces_upstream_prd_and_stories_gates(self) -> None:
        text = self.skill_text()
        for required in (
            "human_approval: APPROVED", "verified", "existence does not imply approval",
            "NOT_APPLICABLE", "applicability_justification", "user-facing behavior",
            "externally consumed APIs", "pending", "rejected", "stale", "contradictory",
        ):
            self.assertIn(required, text)
        self.assertRegex(text.lower(), r"(?:stop|block).*(?:missing|pending|rejected|stale|contradictory)")

    def test_techspec_skill_uses_progressive_disclosure(self) -> None:
        text = self.skill_text()
        self.assertIn("Read `references/specification.md`", text)
        self.assertIn("Render `templates/techspec.md`", text)
        self.assertRegex(text, r"(?i)only (?:when|if) persistence changes")
        self.assertRegex(text, r"(?i)only (?:when|if) (?:an |the )?API changes")
        self.assertIn("NOT_APPLICABLE", text)
        for detailed_policy in (
            "migration and backfill order", "authentication, authorization",
        ):
            self.assertNotIn(detailed_policy, text.lower())

    def test_techspec_skill_has_exact_output_and_runtime_neutrality(self) -> None:
        text = self.skill_text()
        self.assertIn("Write only `tasks/prd-<slug>/techspec.md`", text)
        self.assertIn("Return exactly", text)
        for output_field in (
            "path", "slug", "consumed sources", "generated actor and timestamp",
            "lifecycle status", "human approval", "exact draft artifact reference",
            "trace summary", "unresolved decisions", "risks",
            "next permitted lifecycle stage", "do not duplicate the techspec body",
        ):
            self.assertIn(output_field, text.lower())
        self.assertIn("runtime-specific tools", text)
        for forbidden in ("mcp__", "codex_app", "claude -p"):
            self.assertNotIn(forbidden, text)

    def test_claude_techspec_command_is_a_thin_route(self) -> None:
        command_path = PLUGIN / "commands" / "techspec.md"
        self.assertTrue(command_path.is_file(), "Claude TechSpec command must exist")
        command = command_path.read_text(encoding="utf-8")
        for required in (
            "/sdd-composy:techspec", "$ARGUMENTS", "$sdd-techspec",
            "skills/sdd-techspec/SKILL.md", "return the shared skill's result unchanged",
        ):
            self.assertIn(required, command)
        self.assertLess(len(command), 1000, "Claude adapter should remain thin")
        for policy in (
            "human_approval", "NOT_APPLICABLE", "applicability_justification",
            "TU-", "TI-", "E2E-", "architecture",
        ):
            self.assertNotIn(policy.lower(), command.lower())


class SddComposyCoreSchemaTest(unittest.TestCase):
    def schema(self, name: str) -> dict:
        path = SCHEMAS / f"{name}.schema.json"
        self.assertTrue(path.is_file(), f"core schema must exist: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_schema_shape_is_versioned_strict_and_extension_safe(self) -> None:
        for name in ("config", "state", "tasks", "trace"):
            schema = self.schema(name)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["type"], "object")
            self.assertIn("schema_version", schema["required"])
            self.assertEqual(schema["properties"]["schema_version"]["const"], "1")
            self.assertTrue(schema["additionalProperties"])
            self.assertIn("definitions", schema)

    def test_valid_core_documents_include_portable_extensions(self) -> None:
        fixtures = {
            "config": {"schema_version": "1", "actor_id": "agent:codex-1", "human_root": "tasks", "operational_root": ".planning/sdd-composy", "x-team": {"mode": "safe"}},
            "state": {"schema_version": "1", "revision": 3, "stage": "EXECUTE", "active_prd": "billing-api", "active_task": "TASK-004", "last_gate": {"name": "TASKS", "status": "approved", "at": "2026-09-08T12:00:00+00:00", "actor_id": "human:paulo"}, "blockers": [], "loops": [], "fleet": [], "trace": {"healthy": True, "source_event_count": 8}, "updated_at": "2026-09-08T12:01:00Z", "next_action": "Run focused tests", "x-runtime": "codex"},
            "tasks": {"schema_version": "1", "prd_slug": "billing-api", "updated_at": "2026-09-08T12:01:00Z", "tasks": [{"id": "TASK-004", "title": "Add schemas", "state": "ready", "dependencies": ["TASK-003"], "acceptance_criteria": ["CA-001"], "verification_commands": ["python3 -m unittest"], "allowed_paths": ["plugins/sdd-composy/schemas/"], "evidence_required": False, "x-owner": "platform"}]},
            "trace": {"schema_version": "1", "source_event_count": 1, "generated_at": "2026-09-08T12:02:00Z", "events": [{"sequence": 1, "id": "EVT-000001", "at": "2026-09-08T12:01:00Z", "actor_id": "agent:codex-1", "type": "task.transitioned", "stage": "EXECUTE", "task_id": "TASK-004", "data": {"from": "ready", "to": "running"}, "x-host": "codex"}]},
        }
        for name, fixture in fixtures.items():
            assert_schema_valid(self, self.schema(name), fixture)

    def test_invalid_identifiers_states_and_roots_are_rejected(self) -> None:
        config = {"schema_version": "1", "actor_id": "agent:codex-1", "human_root": "tasks", "operational_root": ".planning/sdd-composy"}
        state = {"schema_version": "1", "revision": 1, "stage": "EXECUTE", "active_prd": None, "active_task": None, "last_gate": None, "blockers": [], "loops": [], "fleet": [], "trace": {"healthy": True, "source_event_count": 0}, "updated_at": "2026-09-08T12:01:00Z", "next_action": "none"}
        task = {"id": "TASK-004", "title": "Valid", "state": "ready", "dependencies": [], "acceptance_criteria": ["CA-001"], "verification_commands": ["python3 -m unittest"], "allowed_paths": ["plugins/sdd-composy/schemas/"], "evidence_required": False}
        tasks = {"schema_version": "1", "prd_slug": "good-slug", "updated_at": "2026-09-08T12:01:00Z", "tasks": [task]}
        event = {"sequence": 1, "id": "EVT-000001", "at": "2026-09-08T12:01:00Z", "actor_id": "agent:codex-1", "type": "task.transitioned", "stage": "EXECUTE", "task_id": "TASK-004", "data": {}}
        trace = {"schema_version": "1", "source_event_count": 1, "generated_at": "2026-09-08T12:02:00Z", "events": [event]}
        cases = (
            ("config actor", "config", dict(config, actor_id="bad id")),
            ("config human root", "config", dict(config, human_root=".planning")),
            ("config operational root", "config", dict(config, operational_root="tasks")),
            ("state stage", "state", dict(state, stage="DONE")),
            ("task slug", "tasks", dict(tasks, prd_slug="Bad Slug")),
            ("task id", "tasks", dict(tasks, tasks=[dict(task, id="4")])),
            ("task state", "tasks", dict(tasks, tasks=[dict(task, state="done")])),
            ("task criteria", "tasks", dict(tasks, tasks=[dict(task, acceptance_criteria=[])])),
            ("task commands", "tasks", dict(tasks, tasks=[dict(task, verification_commands=[])])),
            ("task paths", "tasks", dict(tasks, tasks=[dict(task, allowed_paths=[])])),
            ("trace sequence", "trace", dict(trace, events=[dict(event, sequence=0)])),
            ("trace event id", "trace", dict(trace, events=[dict(event, id="event 1")])),
            ("trace actor", "trace", dict(trace, events=[dict(event, actor_id="bad id")])),
            ("trace type", "trace", dict(trace, events=[dict(event, type="bad type!")])),
            ("trace stage", "trace", dict(trace, events=[dict(event, stage="DONE")])),
            ("trace task id", "trace", dict(trace, events=[dict(event, task_id="4")])),
        )
        for label, name, fixture in cases:
            with self.subTest(label=label), self.assertRaises(AssertionError):
                assert_schema_valid(self, self.schema(name), fixture)

    def test_skipped_task_requires_explicit_non_empty_justification(self) -> None:
        schema = self.schema("tasks")
        task_schema = schema["definitions"]["task"]
        skipped = {
            "id": "TASK-004",
            "title": "Superseded task",
            "state": "skipped",
            "dependencies": [],
            "acceptance_criteria": ["CA-001"],
            "verification_commands": ["python3 -m unittest"],
            "allowed_paths": ["plugins/sdd-composy/schemas/"],
            "evidence_required": False,
            "justification": "Superseded by the approved TASK-005 contract",
            "x-authority": "human:paulo",
        }

        assert_schema_valid(self, task_schema, skipped, schema)
        for invalid_justification in (None, ""):
            invalid = dict(skipped)
            if invalid_justification is None:
                invalid.pop("justification")
            else:
                invalid["justification"] = invalid_justification
            with self.subTest(justification=invalid_justification):
                with self.assertRaises(AssertionError):
                    assert_schema_valid(self, task_schema, invalid, schema)


class SddComposyOperationalSchemaTest(unittest.TestCase):
    def schema(self, name: str) -> dict:
        path = SCHEMAS / f"{name}.schema.json"
        self.assertTrue(path.is_file(), f"operational schema must exist: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_operational_schemas_are_versioned_and_extension_safe(self) -> None:
        for name in ("loop", "fleet-member", "fleet-result", "evidence-manifest"):
            schema = self.schema(name)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["properties"]["schema_version"]["const"], "2" if name == "fleet-member" else "1")
            self.assertTrue(schema["additionalProperties"])
            for definition in schema["definitions"].values():
                if definition.get("type") == "object":
                    self.assertTrue(definition["additionalProperties"])

    def test_loop_defaults_to_three_iterations_and_accepts_terminal_state(self) -> None:
        schema = self.schema("loop")
        self.assertEqual(schema["properties"]["max_iterations"]["default"], 3)
        self.assertEqual(schema["properties"]["max_iterations"]["minimum"], 1)
        fixture = {"schema_version": "1", "id": "loop-001", "task_id": "TASK-005", "status": "iteration_cap", "iteration": 3, "max_iterations": 3, "stop_reason": "Iteration cap reached", "started_at": "2026-09-08T12:00:00Z", "updated_at": "2026-09-08T12:30:00Z", "finished_at": "2026-09-08T12:30:00Z", "x-runtime-note": "portable"}
        assert_schema_valid(self, schema, fixture)
        self.assertIn("completed", schema["definitions"]["loop_status"]["enum"])
        self.assertIn("cancelled", schema["definitions"]["loop_status"]["enum"])

    def test_fleet_runtime_ui_and_terminal_enums(self) -> None:
        member = self.schema("fleet-member")
        result = self.schema("fleet-result")
        self.assertEqual(member["definitions"]["runtime"]["enum"], ["claude-code", "codex", "hermes"])
        self.assertEqual(member["definitions"]["ui"]["enum"], ["cmux", "tmux", "headless"])
        assert_schema_valid(self, member, {"schema_version": "2", "id": "member-001", "task_id": "TASK-005", "status": "running", "runtime": "hermes", "ui": "headless", "branch": "codex/schemas", "worktree_path": "/tmp/worktree", "repository_root": "/tmp/repository", "started_at": "2026-09-08T12:00:00Z", "updated_at": "2026-09-08T12:01:00Z", "owner": {"kind":"sdd-composy-fleet","fleet_id":"demo","member_id":"member-001"}, "resources": {"branch":"codex/schemas","worktree_path":"/tmp/worktree","port":43000,"compose_project":"sdd_fleet_demo","compose_file":"docker-compose.yml"}, "x-host": "local"})
        assert_schema_valid(self, result, {"schema_version": "1", "member_id": "member-001", "task_id": "TASK-005", "status": "completed", "commit": "0123456789abcdef0123456789abcdef01234567", "verification": [{"command": "python3 -m unittest", "result": "passed", "output_sha256": "a" * 64}], "completed_at": "2026-09-08T12:30:00Z", "x-review": True})
        for terminal in ("completed", "failed", "blocked", "cancelled"):
            self.assertIn(terminal, result["definitions"]["result_status"]["enum"])

    def test_evidence_separates_result_and_type_and_confines_hashed_paths(self) -> None:
        schema = self.schema("evidence-manifest")
        entry = {"requirement_id": "RF-001", "story_id": "US-001", "scenario_id": "SC-001", "criterion_id": "CA-001", "test_id": "TEST-001", "result": "passed", "evidence_type": "test_output", "path": "runs/test-output.txt", "sha256": "b" * 64, "x-tool": "unittest"}
        fixture = {"schema_version": "1", "prd_slug": "billing-api", "task_id": "TASK-005", "generated_at": "2026-09-08T12:30:00Z", "entries": [entry], "x-owner": "qa"}
        assert_schema_valid(self, schema, fixture)
        required = schema["definitions"]["evidence"]["required"]
        self.assertIn("result", required)
        self.assertIn("evidence_type", required)
        self.assertNotEqual(schema["definitions"]["result"]["enum"], schema["definitions"]["evidence_type"]["enum"])
        for bad_path in (
            "/tmp/output.txt",
            "../output.txt",
            "runs/../report.txt",
            r"..\report.txt",
            r"runs\..\report.txt",
            r"runs\output.txt",
            "tasks/prd-billing-api/evidences/output.txt",
            "tasks/prd-payments/evidences/output.txt",
        ):
            invalid = dict(entry, path=bad_path)
            with self.subTest(path=bad_path), self.assertRaises(AssertionError):
                assert_schema_valid(self, schema["definitions"]["evidence"], invalid, schema)
        for bad_hash in ("b" * 63, "B" * 64, "not-a-digest"):
            invalid = dict(entry, sha256=bad_hash)
            with self.subTest(sha256=bad_hash), self.assertRaises(AssertionError):
                assert_schema_valid(self, schema["definitions"]["evidence"], invalid, schema)


class SddComposyOkfTest(unittest.TestCase):
    def _okf(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('sdd_okf_extra', PLUGIN / 'scripts' / 'sdd_okf.py')
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

    def test_frontmatter_quoted_colons_and_nested(self):
        okf = self._okf()
        meta, body = okf.parse_frontmatter('---\ntype: Concept\ntitle: "A: useful \\\"note\\\""\nitems:\n  - name: one\n    tags: [a, b]\n---\nbody')
        self.assertEqual(meta['title'], 'A: useful "note"')
        self.assertEqual(meta['items'][0]['tags'], ['a', 'b']); self.assertEqual(body, 'body')

    def test_inline_values_preserve_strings_commas_and_nested_literals(self):
        okf = self._okf()
        meta, _ = okf.parse_frontmatter('---\ntype: Concept\nvalues: [feature, "true", "a,b", {enabled: true, label: "false"}]\n---\n')
        self.assertEqual(meta['values'], ['feature', 'true', 'a,b', {'enabled': True, 'label': 'false'}])

    def test_block_scalars_and_malformed_inline_values_are_rejected(self):
        okf = self._okf()
        with self.assertRaises(ValueError):
            okf.parse_frontmatter('---\ntype: Concept\ntext: |\n  not supported\n---\n')
        with self.assertRaises(ValueError):
            okf.parse_frontmatter('---\ntype: Concept\nvalues: ["unterminated, true]\n---\n')

    def test_cli_executable_exit_and_json_contract(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'bad.md').write_text('---\ntitle: [broken\n---\n', encoding='utf-8')
            p=subprocess.run([str(PLUGIN/'scripts'/'sdd_okf.py'),'lint',str(root)], text=True, capture_output=True)
            self.assertEqual(p.returncode, 1); self.assertFalse(__import__('json').loads(p.stdout)['ok'])
            p=subprocess.run([str(PLUGIN/'scripts'/'sdd_okf.py'),'index',str(root)], text=True, capture_output=True)
            self.assertEqual(p.returncode, 2); self.assertIn('error', __import__('json').loads(p.stdout))

    def test_okf_lint_and_index_contract(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('sdd_okf', PLUGIN / 'scripts' / 'sdd_okf.py')
        okf = importlib.util.module_from_spec(spec); spec.loader.exec_module(okf)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/'doc.md').write_text('---\ntype: Concept\ncustom: keep\ngenerated:\n  by: human:me\n  at: 2026-01-01T00:00:00Z\nverified:\n  - by: human:me\n    at: 2026-01-01T00:00:00Z\nsources:\n  - resource: https://example.test\n---\n[missing](no.md)\n', encoding='utf-8')
            result = okf.lint(root, 'human:me'); self.assertTrue(result['ok']); self.assertEqual(len(result['warnings']), 1)
            index = okf.generate_index(root); self.assertIn('okf_version: "0.2"', index); self.assertIn('doc.md', index)
            (root/'index.md').write_text(index, encoding='utf-8'); self.assertTrue(okf.lint(root)['ok'])
            (root/'log.md').write_text('# Log\n', encoding='utf-8'); self.assertTrue(okf.lint(root)['ok'])
            (root/'bad.md').write_text('---\ntitle: [broken\n---\n', encoding='utf-8'); self.assertFalse(okf.lint(root)['ok'])
            (root/'bad.md').unlink()
            (root/'mismatch.md').write_text('---\ntype: Concept\ngenerated:\n  by: tool/1\n---\n', encoding='utf-8')
            self.assertFalse(okf.lint(root, 'human:me')['ok'])
            (root/'mismatch.md').unlink()
            (root/'log.md').write_text('---\ntype: Bad\n---\n[no](missing.md)\n', encoding='utf-8')
            self.assertTrue(okf.lint(root)['ok'])
            self.assertIn('custom: keep', (root/'doc.md').read_text(encoding='utf-8'))


class SddComposyQuickAdapterTest(unittest.TestCase):
    def test_quick_is_discoverable_with_thin_claude_and_codex_adapters(self):
        command = PLUGIN / "commands" / "quick.md"
        adapter = PLUGIN / "skills" / "sdd-quick" / "agents" / "openai.yaml"
        self.assertTrue(command.exists())
        self.assertTrue(adapter.exists())
        text = command.read_text(encoding="utf-8")
        self.assertIn("$sdd-quick", text)
        self.assertIn("ARGUMENTS", text)
        metadata = adapter.read_text(encoding="utf-8")
        self.assertIn("display_name", metadata)
        self.assertIn("default_prompt", metadata)

    def test_quick_adapter_preserves_escalation_boundary_and_task_guards(self):
        skill = (PLUGIN / "skills" / "sdd-quick" / "SKILL.md").read_text(encoding="utf-8")
        command = (PLUGIN / "commands" / "quick.md").read_text(encoding="utf-8")
        for token in ("five-file", "ESCALATE", "TASK-*", "sdd_tasks.py", "evidence", "sdd_trace.py"):
            self.assertIn(token, skill)
        self.assertIn("portable `$sdd-quick` skill", command)


class SddComposyFleetAdapterTest(unittest.TestCase):
    def test_fleet_is_discoverable_and_routes_all_operations(self):
        skill = PLUGIN / "skills" / "sdd-fleet" / "SKILL.md"
        adapter = skill.parent / "agents" / "openai.yaml"
        command = PLUGIN / "commands" / "fleet.md"
        self.assertTrue(skill.is_file())
        self.assertTrue(adapter.is_file())
        self.assertTrue(command.is_file())
        content = skill.read_text(encoding="utf-8")
        for required in ("launch", "status", "teardown", "sdd-fleet", "cmux", "never merge", "ready"):
            self.assertIn(required.lower(), content.lower())
        self.assertIn("$sdd-fleet", command.read_text(encoding="utf-8"))
        metadata = adapter.read_text(encoding="utf-8")
        self.assertIn("display_name", metadata)
        self.assertIn("default_prompt", metadata)

    def test_fleet_adapter_is_thin_and_provider_neutral(self):
        command = (PLUGIN / "commands" / "fleet.md").read_text(encoding="utf-8")
        self.assertIn("ARGUMENTS", command)
        self.assertLess(len(command), 1400)
        self.assertNotIn("claude -p", command)
        self.assertNotIn("codex exec", command)

    def test_full_plugin_catalogue_has_seventeen_skills_and_commands(self):
        self.assertEqual(len(list((PLUGIN / "skills").glob("*/SKILL.md"))), 17)
        self.assertEqual(len(list((PLUGIN / "commands").glob("*.md"))), 17)

if __name__ == "__main__":
    unittest.main()
