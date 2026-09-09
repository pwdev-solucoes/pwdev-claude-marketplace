"""Contract tests for SDD Composy product artifacts."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
PRD_TEMPLATE = PLUGIN / "templates" / "prd.md"
PRODUCT_REFERENCE = PLUGIN / "references" / "product.md"
STORIES_TEMPLATE = PLUGIN / "templates" / "stories.md"
STORIES_REFERENCE = PLUGIN / "references" / "stories.md"
STORIES_SKILL = PLUGIN / "skills" / "sdd-stories" / "SKILL.md"
STORIES_METADATA = PLUGIN / "skills" / "sdd-stories" / "agents" / "openai.yaml"
TECHSPEC_TEMPLATE = PLUGIN / "templates" / "techspec.md"
SPECIFICATION_REFERENCE = PLUGIN / "references" / "specification.md"
WORKFLOW_REFERENCE = PLUGIN / "references" / "workflow.md"
PRD_SKILL = PLUGIN / "skills" / "sdd-prd" / "SKILL.md"
TECHSPEC_SKILL = PLUGIN / "skills" / "sdd-techspec" / "SKILL.md"


def render(template: str, **values: str) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def record_human_decision(document: str, status: str) -> str:
    document = document.replace("  status: DRAFT", f"  status: {status}", 1)
    document = document.replace("human_approval: PENDING", "human_approval: APPROVED", 1)
    return document.replace(
        "verified: []",
        "verified:\n  - by: human:reviewer\n    at: 2026-09-09T12:00:00Z",
        1,
    )


def assert_human_gate(test: unittest.TestCase, document: str, status: str) -> None:
    test.assertRegex(document, rf"(?m)^  status: {status}$")
    test.assertRegex(document, r"(?m)^human_approval: APPROVED$")
    test.assertRegex(document, r"(?m)^  - by: human:[^\n]+$")
    test.assertRegex(document, r"(?m)^    at: .+(?:Z|[+-][0-9]{2}:[0-9]{2})$")


def ids(document: str, prefix: str) -> set[str]:
    return set(re.findall(rf"(?m)^#+ ({prefix}-[0-9]{{3}})\b", document))


class SddComposyPrdContractTests(unittest.TestCase):
    def read_required(self, path: Path) -> str:
        if not path.is_file():
            self.fail(f"required PRD contract file is missing: {path}")
        return path.read_text(encoding="utf-8")

    def test_template_captures_complete_problem_first_product_contract(self):
        template = self.read_required(PRD_TEMPLATE)
        for heading in (
            "## Problem",
            "## Objectives",
            "## Success Metrics",
            "## Scope",
            "### In Scope",
            "### Out of Scope",
            "## Assumptions",
            "## Dependencies",
            "## Open Questions",
            "## Functional Requirements",
            "## Acceptance Criteria",
        ):
            self.assertIn(heading, template)

    def test_template_uses_stable_requirement_and_acceptance_identifiers(self):
        template = self.read_required(PRD_TEMPLATE)
        self.assertRegex(template, r"(?m)^### RF-[0-9]{3}\b")
        self.assertRegex(template, r"(?m)^### CA-[0-9]{3}\b")
        self.assertIn("RF-001", template)
        self.assertIn("CA-001", template)
        self.assertRegex(template, r"CA-001[^\n]*RF-001|RF-001[^\n]*CA-001")
        self.assertNotRegex(template, r"(?m)^### (?:REQ|FR|AC)-[0-9]+\b")

    def test_template_has_okf_v02_provenance_and_lifecycle_metadata(self):
        template = self.read_required(PRD_TEMPLATE)
        self.assertTrue(template.startswith("---\n"))
        for value in (
            'okf_version: "0.2"',
            "type: PRD",
            "sources:",
            "resource:",
            "generated:",
            "by:",
            "at:",
            "lifecycle:",
            "status:",
            "verified:",
        ):
            self.assertIn(value, template)

    def test_template_has_exactly_one_explicit_human_approval_field(self):
        template = self.read_required(PRD_TEMPLATE)
        approval_fields = re.findall(r"(?m)^human_approval:\s*", template)
        self.assertEqual(len(approval_fields), 1)
        self.assertIn("human_approval: PENDING", template)
        self.assertNotIn("human_approval: APPROVED", template)

    def test_contract_keeps_output_confined_and_architecture_out_of_prd(self):
        template = self.read_required(PRD_TEMPLATE)
        reference = self.read_required(PRODUCT_REFERENCE)
        self.assertIn("tasks/prd-<slug>/prd.md", reference)
        self.assertIn("user problem", reference.lower())
        self.assertIn("codebase", reference.lower())
        self.assertIn("domain", reference.lower())
        self.assertIn("exactly one", reference.lower())
        self.assertIn("human_approval", reference)
        self.assertIn("must not make architecture decisions", reference.lower())
        self.assertNotRegex(template, r"(?im)^#{1,6}\s+(?:Architecture|Technical Approach|Components|Implementation)")

    def test_prd_contract_uses_canonical_lifecycle_transitions(self):
        combined = "\n".join(
            self.read_required(path) for path in (WORKFLOW_REFERENCE, PRODUCT_REFERENCE, PRD_TEMPLATE, PRD_SKILL)
        )
        for state in ("DRAFT", "APPROVED", "REJECTED"):
            self.assertIn(state, combined)
        self.assertNotIn("corresponding approved state", combined)


class SddComposyStoriesContractTests(unittest.TestCase):
    def read_required(self, path: Path) -> str:
        if not path.is_file():
            self.fail(f"required stories contract file is missing: {path}")
        return path.read_text(encoding="utf-8")

    def test_template_captures_actors_journeys_dependencies_and_edge_cases(self):
        template = self.read_required(STORIES_TEMPLATE)
        for heading in (
            "## Actors",
            "## User Journeys",
            "## User Stories",
            "## Dependencies",
            "## Edge Cases",
            "## Gate",
        ):
            self.assertIn(heading, template)
        actor_blocks = re.findall(
            r"(?ms)^### Actor-[0-9]{3}\b.*?(?=^### Actor-|^## User Journeys)",
            template,
        )
        journey_blocks = re.findall(
            r"(?ms)^### Journey-[0-9]{3}\b.*?(?=^### Journey-|^## User Stories)",
            template,
        )
        self.assertGreaterEqual(len(actor_blocks), 2)
        self.assertGreaterEqual(len(journey_blocks), 2)
        for actor in actor_blocks:
            with self.subTest(actor=actor.splitlines()[0]):
                for required_field in ("goal", "context", "capabilities", "constraints"):
                    self.assertIn(required_field, actor.lower())
        for journey in journey_blocks:
            with self.subTest(journey=journey.splitlines()[0]):
                for required_field in (
                    "trigger",
                    "ordered interaction",
                    "outcome",
                    "actors",
                    "stories",
                ):
                    self.assertIn(required_field, journey.lower())
                self.assertRegex(journey.lower(), r"\b(?:alternate|recovery)\s+path\b")

    def test_template_uses_unique_stable_us_and_sc_identifiers_with_prd_links(self):
        template = self.read_required(STORIES_TEMPLATE)
        user_story_ids = re.findall(r"(?m)^### (US-[0-9]{3})\b", template)
        scenario_ids = re.findall(r"(?m)^#### (SC-[0-9]{3})\b", template)
        self.assertGreaterEqual(len(user_story_ids), 1)
        self.assertGreaterEqual(len(scenario_ids), 1)
        self.assertEqual(len(user_story_ids), len(set(user_story_ids)))
        self.assertEqual(len(scenario_ids), len(set(scenario_ids)))
        self.assertRegex(template, r"US-001[^\n]*RF-001")
        self.assertRegex(template, r"SC-001[^\n]*CA-001")
        self.assertNotRegex(template, r"US-002[^\n]*RF-002")
        self.assertNotRegex(template, r"SC-002[^\n]*CA-002")
        self.assertIn("only for identifiers present in the approved PRD", template)

    def test_template_has_okf_v02_provenance_and_lifecycle_metadata(self):
        template = self.read_required(STORIES_TEMPLATE)
        self.assertTrue(template.startswith("---\n"))
        for value in (
            'okf_version: "0.2"',
            "type: STORIES",
            "sources:",
            "resource:",
            "generated:",
            "by:",
            "at:",
            "lifecycle:",
            "status:",
            "verified:",
        ):
            self.assertIn(value, template)
        self.assertEqual(len(re.findall(r"(?m)^human_approval:\s*", template)), 1)
        self.assertIn("human_approval: PENDING", template)
        self.assertNotIn("human_approval: APPROVED", template)

    def test_applicability_gate_requires_stories_for_external_behavior(self):
        reference = self.read_required(STORIES_REFERENCE)
        self.assertIn("user-facing behavior", reference)
        self.assertIn("externally consumed APIs", reference)
        self.assertIn("NOT_APPLICABLE", reference)
        self.assertIn("internal work", reference)
        self.assertIn("justification", reference)
        self.assertIn("must not", reference.lower())

    def test_skill_consumes_approved_upstream_and_preserves_human_approval(self):
        skill = self.read_required(STORIES_SKILL)
        metadata = self.read_required(STORIES_METADATA)
        for upstream in ("approved `prd.md`", "`domain.md`", "`project.md`"):
            self.assertIn(upstream, skill)
        self.assertIn("tasks/prd-<slug>/stories.md", skill)
        self.assertIn("human", skill.lower())
        self.assertIn("verified", skill)
        self.assertIn("existence", skill.lower())
        self.assertIn("$sdd-stories", metadata)

    def test_stories_contract_uses_canonical_lifecycle_transitions(self):
        combined = "\n".join(
            self.read_required(path) for path in (WORKFLOW_REFERENCE, STORIES_REFERENCE, STORIES_TEMPLATE, STORIES_SKILL)
        )
        for state in ("DRAFT", "APPROVED", "REJECTED", "NOT_APPLICABLE"):
            self.assertIn(state, combined)
        self.assertNotIn("matching lifecycle state", combined)


class SddComposyTechSpecContractTests(unittest.TestCase):
    def read_required(self, path: Path) -> str:
        if not path.is_file():
            self.fail(f"required TechSpec contract file is missing: {path}")
        return path.read_text(encoding="utf-8")

    def test_reference_blocks_unapproved_or_unresolved_upstream_contracts(self):
        reference = self.read_required(SPECIFICATION_REFERENCE)
        for value in (
            "approved `prd.md`",
            "approved stories",
            "NOT_APPLICABLE",
            "applicability_justification",
            "human_approval",
            "verified",
            "existence",
            "codebase",
        ):
            self.assertIn(value, reference)
        self.assertRegex(reference.lower(), r"(?:stop|block).*(?:pending|rejected|stale)")

    def test_template_has_component_inventory_and_explicit_interfaces(self):
        template = self.read_required(TECHSPEC_TEMPLATE)
        for heading in (
            "## Component Inventory",
            "## Interfaces and Contracts",
            "## Decisions",
            "## Risks",
            "## Test Cases",
        ):
            self.assertIn(heading, template)
        for field in ("Responsibility", "Existing or new", "Inputs", "Outputs"):
            self.assertIn(field, template)

    def test_template_routes_conditional_data_and_api_detail_to_reference(self):
        template = self.read_required(TECHSPEC_TEMPLATE)
        reference = self.read_required(SPECIFICATION_REFERENCE)
        self.assertIn("## Data Model (Conditional)", template)
        self.assertIn("## API Contracts (Conditional)", template)
        self.assertIn("NOT_APPLICABLE", template)
        for topic in (
            "schema",
            "migration",
            "rollback",
            "endpoint",
            "authentication",
            "authorization",
            "error",
            "compatibility",
        ):
            self.assertIn(topic, reference.lower())

    def test_template_records_explicit_decisions_and_risks(self):
        template = self.read_required(TECHSPEC_TEMPLATE)
        for value in (
            "DEC-001",
            "Options",
            "Choice",
            "Rationale",
            "Trade-offs",
            "Reversible",
            "RISK-001",
            "Likelihood",
            "Impact",
            "Mitigation",
            "Owner",
        ):
            self.assertIn(value, template)

    def test_template_names_unique_ca_linked_test_cases_at_all_levels(self):
        template = self.read_required(TECHSPEC_TEMPLATE)
        cases = re.findall(r"(?m)^### ((?:TU|TI|E2E)-[0-9]{3})\b[^\n]*\b(CA-[0-9]{3})\b", template)
        identifiers = [identifier for identifier, _ in cases]
        self.assertGreaterEqual(len(cases), 3)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(any(identifier.startswith("TU-") for identifier in identifiers))
        self.assertTrue(any(identifier.startswith("TI-") for identifier in identifiers))
        self.assertTrue(any(identifier.startswith("E2E-") for identifier in identifiers))
        for identifier, criterion in cases:
            with self.subTest(identifier=identifier):
                block = re.search(
                    rf"(?ms)^### {identifier}\b.*?(?=^### (?:TU|TI|E2E)-|^## Gate)",
                    template,
                ).group(0)
                self.assertIn(criterion, block)
                for field in ("Name", "Level", "Setup", "Action", "Expected result"):
                    self.assertIn(field, block)

    def test_template_has_okf_v02_provenance_and_human_gate(self):
        template = self.read_required(TECHSPEC_TEMPLATE)
        self.assertTrue(template.startswith("---\n"))
        for value in (
            'okf_version: "0.2"',
            "type: TECHSPEC",
            "sources:",
            "resource:",
            "generated:",
            "by:",
            "at:",
            "lifecycle:",
            "status:",
            "verified:",
        ):
            self.assertIn(value, template)
        self.assertEqual(len(re.findall(r"(?m)^human_approval:\s*", template)), 1)
        self.assertIn("human_approval: PENDING", template)
        self.assertNotIn("human_approval: APPROVED", template)

    def test_reference_confines_output_and_forbids_product_scope_mutation(self):
        reference = self.read_required(SPECIFICATION_REFERENCE)
        self.assertIn("tasks/prd-<slug>/techspec.md", reference)
        self.assertIn("must not change", reference.lower())
        for scope_term in ("requirements", "stories", "acceptance criteria", "product scope"):
            self.assertIn(scope_term, reference.lower())

    def test_techspec_contract_uses_canonical_lifecycle_transitions(self):
        combined = "\n".join(
            self.read_required(path)
            for path in (WORKFLOW_REFERENCE, SPECIFICATION_REFERENCE, TECHSPEC_TEMPLATE, TECHSPEC_SKILL)
        )
        for state in ("DRAFT", "APPROVED", "REJECTED"):
            self.assertIn(state, combined)
        self.assertNotIn("approved lifecycle state", combined)


class SddComposyRenderedChainTests(unittest.TestCase):
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def rendered(self, path: Path, product: str) -> str:
        return render(
            self.read(path),
            SLUG="fixture",
            PRODUCT_NAME=product,
            ACTOR_ID="agent:fixture",
            GENERATED_AT="2026-09-09T11:00:00Z",
        )

    def assert_trace_integrity(self, prd: str, stories: str, techspec: str) -> None:
        requirement_ids = ids(prd, "RF")
        criterion_ids = ids(prd, "CA")
        story_ids = ids(stories, "US")
        scenario_ids = ids(stories, "SC")
        self.assertEqual(len(requirement_ids), len(re.findall(r"(?m)^### RF-[0-9]{3}\b", prd)))
        self.assertEqual(len(criterion_ids), len(re.findall(r"(?m)^### CA-[0-9]{3}\b", prd)))
        self.assertEqual(len(story_ids), len(re.findall(r"(?m)^### US-[0-9]{3}\b", stories)))
        self.assertEqual(len(scenario_ids), len(re.findall(r"(?m)^#### SC-[0-9]{3}\b", stories)))
        for target in re.findall(r"(?m)^### US-[0-9]{3}[^\n]*\b(RF-[0-9]{3})\b", stories):
            self.assertIn(target, requirement_ids)
        for target in re.findall(r"(?m)^#### SC-[0-9]{3}[^\n]*\b(CA-[0-9]{3})\b", stories):
            self.assertIn(target, criterion_ids)
        for target in re.findall(r"(?m)^### (?:TU|TI|E2E)-[0-9]{3}[^\n]*\b(CA-[0-9]{3})\b", techspec):
            self.assertIn(target, criterion_ids)

    def test_required_stories_path_passes_all_techspec_gates(self):
        prd = record_human_decision(self.rendered(PRD_TEMPLATE, "Required fixture"), "APPROVED")
        stories = record_human_decision(self.rendered(STORIES_TEMPLATE, "Required fixture"), "APPROVED")
        techspec = record_human_decision(self.rendered(TECHSPEC_TEMPLATE, "Required fixture"), "APPROVED")
        assert_human_gate(self, prd, "APPROVED")
        assert_human_gate(self, stories, "APPROVED")
        assert_human_gate(self, techspec, "APPROVED")
        self.assertRegex(stories, r"(?m)^applicability: REQUIRED$")
        self.assertIn('resource: "tasks/prd-fixture/prd.md"', stories)
        self.assertIn('resource: "tasks/prd-fixture/stories.md"', techspec)
        self.assert_trace_integrity(prd, stories, techspec)

    def test_internal_not_applicable_path_passes_all_techspec_gates(self):
        prd = record_human_decision(self.rendered(PRD_TEMPLATE, "Internal fixture"), "APPROVED")
        stories = self.rendered(STORIES_TEMPLATE, "Internal fixture")
        stories = re.sub(r"(?ms)^## User Stories\n.*?(?=^## Dependencies)", "## User Stories\n\nNOT_APPLICABLE — pure internal refactoring has no user-facing behavior or externally consumed API.\n\n", stories)
        stories = stories.replace("applicability: REQUIRED", "applicability: NOT_APPLICABLE", 1)
        stories = stories.replace('applicability_justification: ""', 'applicability_justification: "Pure internal refactoring with no externally consumed behavior"', 1)
        stories = record_human_decision(stories, "NOT_APPLICABLE")
        techspec = record_human_decision(self.rendered(TECHSPEC_TEMPLATE, "Internal fixture"), "APPROVED")
        assert_human_gate(self, prd, "APPROVED")
        assert_human_gate(self, stories, "NOT_APPLICABLE")
        assert_human_gate(self, techspec, "APPROVED")
        self.assertRegex(stories, r"(?m)^applicability: NOT_APPLICABLE$")
        self.assertRegex(stories, r'(?m)^applicability_justification: ".+"$')
        self.assertFalse(ids(stories, "US"))
        self.assertFalse(ids(stories, "SC"))
        self.assertNotRegex(techspec, r"\bUS-[0-9]{3}\b|\bSC-[0-9]{3}\b")
        self.assert_trace_integrity(prd, stories, techspec)


if __name__ == "__main__":
    unittest.main()
