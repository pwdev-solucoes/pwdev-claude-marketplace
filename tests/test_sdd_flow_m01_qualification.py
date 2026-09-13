"""Structural contract tests for M01's PRD gate, not runtime qualification."""

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "tasks/prd-specflow/prd.md"
SOURCE = ROOT / ".planning/power/product/prd.md"
STORIES = ROOT / "tasks/prd-specflow/stories.md"
QUALIFICATION = ROOT / ".planning/power/features/specflow-m01/runtime-qualification.md"
RECIPE = ROOT / ".planning/power/features/specflow-m01/probe-recipe.md"
HEADINGS = (
    "Problem", "Objectives", "Success Metrics", "Scope", "Assumptions",
    "Dependencies", "Open Questions", "Functional Requirements",
    "Acceptance Criteria", "Gate",
)


def contract_errors(document):
    """Check recorded gate structure, not authenticity or runtime authorization."""
    errors = []
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", document, re.S)
    if not frontmatter:
        return ["frontmatter"]
    metadata = frontmatter.group(1)
    for clause in ('type: PRD', 'okf_version: "0.2"', 'generated:',
                   'lifecycle:\n  status: APPROVED', 'human_approval: APPROVED',
                   'sources:', 'verified:'):
        if clause not in metadata:
            errors.append(clause)
    if len(re.findall(r"(?m)^human_approval:", metadata)) != 1:
        errors.append("single approval")
    event = ('verified:\n  - event: human_approval\n    by: human:user\n'
             '    at: "2026-09-12T11:28:23Z"\n'
             '    scope: tasks/prd-specflow/prd.md\n    source: "user: aprovado"')
    if event not in metadata:
        errors.append("matching human event")
    for heading in HEADINGS:
        if f"## {heading}\n" not in document:
            errors.append(heading)
    for prefix, count in (("RF", 17), ("CA", 16)):
        declared = re.findall(rf"(?m)^### ({prefix}-\d{{3}})\b", document)
        expected = {f"{prefix}-{number:03}" for number in range(1, count + 1)}
        if len(declared) != count or set(declared) != expected:
            errors.append(prefix + " ids")
    for prefix, count in (("FR", 17), ("AC", 16), ("NFR", 9), ("G", 6)):
        for number in range(1, count + 1):
            if not re.search(rf"\b{prefix}-{number:03}\b", document):
                errors.append(f"source {prefix}-{number:03}")
    criteria = document.split("## Acceptance Criteria\n", 1)[-1]
    requirements = set(re.findall(r"(?m)^### (RF-\d{3})\b", document))
    for block in re.split(r"(?m)^### CA-\d{3}", criteria)[1:]:
        refs = set(re.findall(r"\bRF-\d{3}\b", block))
        if not refs or not refs <= requirements:
            errors.append("criterion reference")
    if re.search(r"(?im)^#{1,6}\s+(Architecture|Technical Approach|Components|Implementation)\b", document):
        errors.append("architecture heading")
    return errors


class SpecFlowM01PrdTests(unittest.TestCase):
    def read_prd(self):
        self.assertTrue(PRD.is_file(), "missing required PRD: tasks/prd-specflow/prd.md")
        return PRD.read_text(encoding="utf-8")

    def test_required_prd_is_a_complete_approved_contract(self):
        self.assertEqual(contract_errors(self.read_prd()), [])

    def test_source_ids_are_present_in_the_observed_power_prd(self):
        source = SOURCE.read_text(encoding="utf-8")
        for prefix, count in (("FR", 17), ("AC", 16), ("NFR", 9), ("G", 6)):
            for number in range(1, count + 1):
                self.assertRegex(source, rf"\b{prefix}-{number:03}\b")

    def test_local_source_links_resolve(self):
        document = self.read_prd()
        links = re.findall(r"\]\(([^)]+)\)", document)
        self.assertGreater(len(links), 0)
        for link in links:
            target = (PRD.parent / link).resolve()
            self.assertTrue(target.is_relative_to(ROOT))
            self.assertTrue(target.is_file(), link)

    def test_critical_limits_and_optional_behavior_are_explicit(self):
        document = self.read_prd()
        for text in (
            "9 agentes, 20 skills, 4 Loops e 11 templates SDD",
            "3 tentativas totais", "incluindo a primeira", "janela de ausência de progresso 2",
            "fan-out 1", "5 arquivos de implementação", "NOT_RUN",
            "checkout atual", "Network Local", "aplicação e dependências de teste",
            "agentes e daemon permanecem no host", "sem instalar", "SHA-256",
            "pt-BR e en-US", "roadmap.md", "environment.md", "approval-receipt.md",
            "export-receipt.md", "evidence-report.html", "BLOCKED",
        ):
            self.assertIn(text, document)

    def test_mutations_cannot_hide_missing_ids_or_inherit_approval(self):
        document = self.read_prd()
        mutations = (
            document.replace("human_approval: APPROVED", "human_approval: PENDING"),
            document.replace("  status: APPROVED", "  status: DRAFT"),
            document.replace("event: human_approval", "event: source_review"),
            document.replace("by: human:user", "by: agent:reviewer"),
            document.replace("scope: tasks/prd-specflow/prd.md", "scope: another.md"),
            document.replace("### RF-001", "### RF-002", 1),
            document.replace("### CA-001", "### CA-002", 1),
            document.replace("## Problem", "## Architecture", 1),
            document.replace("RF-017", "RF-999"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation[:100]):
                self.assertTrue(contract_errors(mutation))


def stories_gate_errors(document, prd_bytes):
    """Validate the recorded Stories event and upstream freshness, not authenticity."""
    match = re.match(r"\A---\n(.*?)\n---\n", document, re.S)
    if not match:
        return ["frontmatter"]
    metadata = match.group(1)
    expected = (
        "lifecycle:\n  status: APPROVED", "human_approval: APPROVED",
        "applicability: REQUIRED",
        'verified:\n  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-12T18:43:31Z"\n'
        '    scope: tasks/prd-specflow/stories.md\n    source: "user: aprovado"',
        "  - resource: tasks/prd-specflow/prd.md\n    sha256: "
        + hashlib.sha256(prd_bytes).hexdigest(),
    )
    errors = [clause for clause in expected if clause not in metadata]
    if len(re.findall(r"(?m)^human_approval:", metadata)) != 1:
        errors.append("single approval")
    return errors


class SpecFlowM01PreparationTests(unittest.TestCase):
    def read_required(self, path):
        self.assertTrue(path.is_file(), f"missing preparation artifact: {path.name}")
        return path.read_text(encoding="utf-8")

    def test_documents_preserve_their_individual_gates_and_resolving_links(self):
        for path, kind in ((STORIES, "STORIES"), (QUALIFICATION, "RUNTIME_QUALIFICATION"),
                           (RECIPE, "PROBE_RECIPE")):
            with self.subTest(path=path.name):
                doc = self.read_required(path)
                metadata = doc.split("---\n", 2)[1]
                for clause in (f"type: {kind}", 'okf_version: "0.2"'):
                    self.assertIn(clause, metadata)
                if path == STORIES:
                    self.assertEqual(stories_gate_errors(doc, PRD.read_bytes()), [])
                elif path == QUALIFICATION:
                    for clause in ("status: FAILED", "human_approval: APPROVED", "result: failed"):
                        self.assertIn(clause, metadata)
                else:
                    for clause in ("status: DRAFT", "human_approval: PENDING", "verified: []"):
                        self.assertIn(clause, metadata)
                for link in re.findall(r"\]\(([^)]+)\)", doc):
                    target = (path.parent / link).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file(), link)

    def test_stories_gate_rejects_missing_event_mismatch_and_stale_upstream(self):
        doc = self.read_required(STORIES)
        mutations = (
            doc.replace("human_approval: APPROVED", "human_approval: PENDING"),
            doc.replace("status: APPROVED", "status: DRAFT"),
            doc.replace("event: human_approval", "event: source_review"),
            doc.replace("by: human:user", "by: agent:reviewer"),
            doc.replace("2026-09-12T18:43:31Z", "2026-09-12T11:28:23Z"),
            doc.replace("scope: tasks/prd-specflow/stories.md", "scope: tasks/prd-specflow/prd.md"),
            doc.replace(hashlib.sha256(PRD.read_bytes()).hexdigest(), "0" * 64),
        )
        for number, mutation in enumerate(mutations):
            with self.subTest(number=number):
                self.assertTrue(stories_gate_errors(mutation, PRD.read_bytes()))
        self.assertTrue(stories_gate_errors(doc, PRD.read_bytes() + b"\nchanged"))

    def test_stories_cover_every_prd_criterion_without_new_ids(self):
        doc = self.read_required(STORIES)
        self.assertIn("applicability: REQUIRED", doc)
        self.assertIn(hashlib.sha256(PRD.read_bytes()).hexdigest(), doc)
        stories = re.findall(r"(?m)^### (US-\d{3})\b", doc)
        self.assertEqual(len(stories), 10)
        self.assertEqual(len(set(stories)), 10)
        scenarios = re.findall(r"(?m)^#### (SC-\d{3}) — (CA-\d{3})\b", doc)
        self.assertEqual(len(scenarios), 16)
        self.assertEqual({ca for _, ca in scenarios}, {f"CA-{i:03}" for i in range(1, 17)})
        self.assertEqual(len({sc for sc, _ in scenarios}), 16)
        self.assertLessEqual(set(re.findall(r"\bRF-\d{3}\b", doc)),
                             set(re.findall(r"(?m)^### (RF-\d{3})\b", PRD.read_text())))
        for heading in ("Actors", "User Journeys", "User Stories", "Dependencies", "Edge Cases", "Gate"):
            self.assertIn(f"## {heading}", doc)

    def test_qualification_lists_core_and_optional_as_unproved(self):
        doc = self.read_required(QUALIFICATION)
        data = json.loads(re.search(r"```json\n(.*?)\n```", doc, re.S).group(1))
        self.assertEqual({item["id"] for item in data["core_checks"]},
                         {f"CORE-{number:03}" for number in range(1, 10)})
        self.assertEqual({item["id"] for item in data["optional_checks"]},
                         {f"OPT-{number:03}" for number in range(1, 6)})
        self.assertEqual(data["core_checks"][0]["result"], "FAIL")
        self.assertEqual(data["core_checks"][1]["result"], "FAIL")
        self.assertTrue(all(item["result"] == "NOT_RUN" for item in data["core_checks"][2:]))
        self.assertTrue(all(item["result"] == "NOT_RUN" for item in data["optional_checks"]))
        self.assertEqual(data["verdict"], "FAIL")
        self.assertIn("BLOCKED", doc)

    def test_recipe_binds_pre_run_approval_without_execution(self):
        doc = self.read_required(RECIPE)
        data = json.loads(re.search(r"```json\n(.*?)\n```", doc, re.S).group(1))
        recipes = data["runtime_recipes"]
        self.assertEqual(len(recipes), 7)
        self.assertEqual(len({recipe["id"] for recipe in recipes}), 7)
        self.assertEqual(data["status"], "BLOCKED")
        self.assertIsNone(data["approved_scope"])
        self.assertEqual(data["result"], "NOT_RUN")
        for recipe in recipes:
            self.assertTrue(recipe["executable"])
            self.assertTrue(recipe["argv"])
            self.assertTrue(recipe["cwd"])
            self.assertTrue(recipe["mutable_scope"])
            approval = recipe["approved_scope"]
            self.assertEqual(approval["gate_id"], "gate:specflow-m01:runtime-recipe")
            self.assertTrue(approval["run_id"].startswith("power-approval-run:"))
            self.assertEqual(approval["actor_ref"], "human:user")
            self.assertEqual(approval["decision"], "approved")
            self.assertEqual(len(approval["artifacts"]), 1)
            self.assertEqual(approval["artifacts"][0]["sha256"], "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4")
            self.assertEqual(recipe["observed"], "NOT_RUN")
            self.assertEqual(recipe["result"], "NOT_RUN")
            self.assertEqual(recipe["evidence_refs"], [])
        for clause in ("Task 03", "sem probes", "3 tentativas totais",
                       "janela de ausência de progresso 2", "fan-out 1", "Cleanup", "RuntimeRecipe"):
            self.assertIn(clause, doc)


class SpecFlowM01RuntimeReconciliationTests(unittest.TestCase):
    def test_runtime_qualification_binds_the_renewed_gate_and_fails_closed(self):
        document = QUALIFICATION.read_text(encoding="utf-8")
        payload = json.loads(re.search(r"```json\n(.*?)\n```", document, re.S).group(1))

        self.assertIn("version", payload, "RuntimeQualification still has the pre-probe shape")
        self.assertEqual(payload["version"], "compozy 0.3.0-beta.25")
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertEqual(len(payload["command_recipes"]), 7)
        self.assertEqual(len(payload["core_checks"]), 9)
        self.assertEqual(len(payload["optional_checks"]), 5)
        self.assertTrue(payload["evidence_refs"])

        for recipe in payload["command_recipes"]:
            approval = recipe["approved_scope"]
            self.assertEqual(
                approval["run_id"],
                "power-approval-run:b2098dfc41fbdf167c9b202263882a1dd45c9348dc88202dfd560f8dcf05555a",
            )
            self.assertEqual(approval["gate_id"], "gate:specflow-m01:runtime-probe-beta25")
            self.assertEqual(
                approval["decision_id"],
                "decision:5bfdf63eb59c86278e4013fb7d3a9643cadd4b3ec9e5803683d32f005a6cd7a2",
            )
        self.assertEqual(payload["command_recipes"][0]["result"], "FAIL")
        self.assertEqual(payload["command_recipes"][0]["exit_code"], 1)
        self.assertEqual(payload["command_recipes"][1]["result"], "FAIL")
        self.assertEqual(payload["command_recipes"][1]["exit_code"], 1)
        for recipe in payload["command_recipes"][2:]:
            self.assertEqual(recipe["result"], "NOT_RUN")
            self.assertEqual(recipe["observed"], "NOT_RUN")

        for check in payload["core_checks"]:
            self.assertIn(check["result"], {"FAIL", "NOT_RUN"})
            self.assertTrue(check["revision_ref"])

        for check in payload["optional_checks"]:
            self.assertEqual(check["result"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
