"""Structural tests for the proposed M01 TechSpec contracts, not runtime proof."""

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / ".planning/power/features/specflow-m01"
PRD = ROOT / "tasks/prd-specflow/prd.md"
STORIES = ROOT / "tasks/prd-specflow/stories.md"
RECIPE = FEATURE / "probe-recipe.md"
COMPATIBILITY = FEATURE / "compatibility.md"
DECISIONS = FEATURE / "interface-decisions.md"
TECHSPEC = ROOT / "tasks/prd-specflow/techspec.md"
TASKS = ROOT / "tasks/prd-specflow/tasks.md"
REPORT = FEATURE / "task-02-report.md"
ALLOWED_PATHS = {
    "tests/test_sdd_flow_m01_qualification.py",
    "tests/test_sdd_flow_m01_contracts.py",
    ".planning/power/features/specflow-m01/compatibility.md",
    "tasks/prd-specflow/techspec.md",
    "tasks/prd-specflow/tasks.md",
}

RUNTIME_RECIPE = (
    "RuntimeRecipe = {id: string, executable: string, argv: string[], cwd: string, "
    "mutable_scope: string[], approved_scope: ApprovalRef|null, expected: string, "
    "observed: string, result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, "
    "evidence_refs: ArtifactRef[]}"
)
QUALIFICATION_CHECK = (
    "QualificationCheck = {id: string, guarantee: string, positive_recipe: string, "
    "negative_recipe: string, revision_ref: string, "
    "result: PASS|FAIL|ENVIRONMENT_FAILURE|NOT_RUN, evidence_refs: ArtifactRef[]}"
)
RESOURCE_SET = (
    "ResourceSet = {paths: string[], source_digests: object<string,string>, interfaces: "
    "string[], validation_refs: ArtifactRef[]}; representa recursos estáticos, sem "
    "estado operacional alternativo."
)
CHECKOUT_REF = (
    "CheckoutRef | workspace_id: string; worktree_id: string ou null; checkout_root: "
    "caminho absoluto resolvido pelo runtime; revision_ref: string com identidade de "
    "HEAD e alterações locais relevantes"
)
ARTIFACT_REF = (
    "ArtifactRef | checkout_ref: CheckoutRef; path: relativo ao checkout; sha256: 64 "
    "caracteres hex minúsculos; role: contract, evidence, verdict, report ou manifest"
)
APPROVAL_REF = (
    "ApprovalRef | run_id, gate_id, decision_id, actor_ref: strings opacas/ator real; "
    "decision: approved, changes_requested ou rejected; decided_at: RFC3339 UTC; "
    "artifacts: ArtifactRef[] não vazio; prerequisites: decision_id[]"
)


def proposal_errors(document, kind):
    """Validate proposal state without treating it as approval or runtime evidence."""
    errors = []
    match = re.match(r"\A---\n(.*?)\n---\n", document, re.S)
    if not match:
        return ["frontmatter"]
    metadata = match.group(1)
    for clause in (
        f"type: {kind}",
        'okf_version: "0.2"',
        "lifecycle:\n  status: DRAFT",
        "human_approval: PENDING",
        "verified: []",
    ):
        if clause not in metadata:
            errors.append(clause)
    if re.search(r"(?m)^\s*status:\s*(APPROVED|READY|COMPLETE)\s*$", metadata):
        errors.append("premature lifecycle")
    if re.search(r"(?m)^human_approval:\s*(APPROVED|REJECTED)\s*$", metadata):
        errors.append("invented decision")
    return errors


def interface_errors(document):
    errors = []
    normalized = " ".join(document.split())
    for clause in (
        RUNTIME_RECIPE,
        QUALIFICATION_CHECK,
        RESOURCE_SET,
        CHECKOUT_REF,
        ARTIFACT_REF,
        APPROVAL_REF,
        "null significa não conhecido/não aplicável justificado",
        "Lista vazia significa consulta concluída sem itens.",
        "Approvals precisam de identidade humana comprovada pelo runtime.",
    ):
        if " ".join(clause.split()) not in normalized:
            errors.append(clause)
    return errors


def techspec_gate_errors(document, prd_bytes, stories_bytes, recipe_bytes):
    """Validate the renewed approved gate, historical chain, and source freshness."""
    match = re.match(r"\A---\n(.*?)\n---\n", document, re.S)
    if not match:
        return ["frontmatter"]
    metadata = match.group(1)
    expected = (
        "lifecycle:\n  status: APPROVED",
        "human_approval: APPROVED",
        'verified:\n  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-12T19:00:09Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n    source: "user: sim"',
        '  - event: approval_invalidated\n    by: agent:pwdev-power\n'
        '    at: "2026-09-12T19:11:57Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n'
        '    source: ".planning/power/features/specflow-m01/task-02-review-1.md"\n'
        '    reason: "semantic revision required; previous approval is stale"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-12T23:57:17Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n    source: "user: sim"',
        '  - event: approval_invalidated\n    by: agent:pwdev-power\n'
        '    at: "2026-09-13T00:49:13Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n'
        '    source: ".planning/power/features/specflow-m01/task-04-brief.md"\n'
        '    reason: "concrete RuntimeRecipe input and source digest require renewed TechSpec gate"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-13T08:19:39Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n'
        '    source: "user: aprovado"\n'
        '    snapshot_sha256: adcafa36482c90a988a6af8a723a77dabdf051891ffe2e8e39a4df806c734364',
        '  - event: approval_invalidated\n    by: agent:pwdev-power\n'
        '    at: "2026-09-13T08:28:28Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n'
        '    source: ".planning/power/features/specflow-m01/task-04-review.md"\n'
        '    reason: "interface-decisions stale consumer required explicit historical classification"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-13T08:30:59Z"\n'
        '    scope: tasks/prd-specflow/techspec.md\n'
        '    source: "user: sim"\n'
        '    snapshot_sha256: e3564a37d48b4df77e92e4d9ffaa2a6e2467dcfb9cafa6a67c0feed51098394b',
        hashlib.sha256(prd_bytes).hexdigest(),
        hashlib.sha256(stories_bytes).hexdigest(),
        "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4",
    )
    errors = [clause for clause in expected if clause not in metadata]
    if len(re.findall(r"(?m)^human_approval:", metadata)) != 1:
        errors.append("single approval")
    return errors


def tasks_gate_errors(document, prd_bytes, stories_bytes, techspec_bytes, recipe_bytes):
    """Validate approved TASKS, its history, snapshot, and upstream digests."""
    match = re.match(r"\A---\n(.*?)\n---\n", document, re.S)
    if not match:
        return ["frontmatter"]
    metadata = match.group(1)
    expected = (
        "lifecycle:\n  status: APPROVED",
        "human_approval: APPROVED",
        'verified:\n  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-12T19:05:36Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n    source: "user: sim"',
        '  - event: approval_invalidated\n    by: agent:pwdev-power\n'
        '    at: "2026-09-12T19:11:57Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n'
        '    source: ".planning/power/features/specflow-m01/task-02-review-1.md"\n'
        '    reason: "upstream TechSpec semantic revision; previous approval is stale"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-13T00:02:44Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n    source: "user: sim"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-13T08:22:00Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n'
        '    source: "user: sim"\n'
        '    snapshot_sha256: 863e7391fe4b8704c812f4dddea836663237346da07f78a45b1af7d9d65d1b76',
        '  - event: approval_invalidated\n    by: agent:pwdev-power\n'
        '    at: "2026-09-13T08:28:28Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n'
        '    source: ".planning/power/features/specflow-m01/task-04-review.md"\n'
        '    reason: "upstream TechSpec changed for stale consumer classification"',
        '  - event: human_approval\n    by: human:user\n'
        '    at: "2026-09-13T08:34:15Z"\n'
        '    scope: tasks/prd-specflow/tasks.md\n'
        '    source: "user: sim"\n'
        '    snapshot_sha256: 8ce06b559e9593fef24c0b3c9c7cbbc438756f01b53701b2ab00d4ad1af699a8',
        hashlib.sha256(prd_bytes).hexdigest(),
        hashlib.sha256(stories_bytes).hexdigest(),
        hashlib.sha256(techspec_bytes).hexdigest(),
        "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4",
    )
    errors = [clause for clause in expected if clause not in metadata]
    if len(re.findall(r"(?m)^human_approval:", metadata)) != 1:
        errors.append("single approval")
    return errors


class SpecFlowM01ContractTests(unittest.TestCase):
    def read_required(self, path):
        self.assertTrue(path.is_file(), f"missing required contract: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_upstream_gates_are_fresh_and_recipe_remains_blocked(self):
        prd = PRD.read_text(encoding="utf-8")
        stories = STORIES.read_text(encoding="utf-8")
        recipe = RECIPE.read_text(encoding="utf-8")
        self.assertIn("lifecycle:\n  status: APPROVED", prd)
        self.assertIn("human_approval: APPROVED", prd)
        self.assertIn("lifecycle:\n  status: APPROVED", stories)
        self.assertIn("human_approval: APPROVED", stories)
        self.assertIn(hashlib.sha256(PRD.read_bytes()).hexdigest(), stories)
        self.assertEqual(len(re.findall(r'(?m)^      "id": "RCP-', recipe)), 7)
        self.assertIn('"status": "BLOCKED"', recipe)
        self.assertIn('"result": "NOT_RUN"', recipe)

    def test_all_proposals_have_independent_pending_gates(self):
        for path, kind in (
            (COMPATIBILITY, "COMPATIBILITY_PROPOSAL"),
            (DECISIONS, "INTERFACE_DECISIONS"),
        ):
            with self.subTest(path=path):
                self.assertEqual(proposal_errors(self.read_required(path), kind), [])

    def test_techspec_has_the_exact_human_gate_and_fresh_sources(self):
        document = self.read_required(TECHSPEC)
        self.assertEqual(
            techspec_gate_errors(
                document, PRD.read_bytes(), STORIES.read_bytes(), RECIPE.read_bytes()
            ),
            [],
        )

    def test_tasks_has_the_exact_human_gate_and_fresh_sources(self):
        document = self.read_required(TASKS)
        self.assertEqual(
            tasks_gate_errors(
                document,
                PRD.read_bytes(),
                STORIES.read_bytes(),
                TECHSPEC.read_bytes(),
                RECIPE.read_bytes(),
            ),
            [],
        )

    def test_interface_signatures_and_transitive_invariants_are_preserved(self):
        for path in (DECISIONS, TECHSPEC):
            with self.subTest(path=path):
                self.assertEqual(interface_errors(self.read_required(path)), [])

    def test_compatibility_defines_every_unexecuted_check(self):
        document = self.read_required(COMPATIBILITY)
        core = set(re.findall(r"(?m)^\| (CORE-\d{3}) \|", document))
        optional = set(re.findall(r"(?m)^\| (OPT-\d{3}) \|", document))
        self.assertEqual(core, {f"CORE-{number:03}" for number in range(1, 10)})
        self.assertEqual(optional, {f"OPT-{number:03}" for number in range(1, 6)})
        rows = re.findall(r"(?m)^\| (?:CORE|OPT)-\d{3} \|.*$", document)
        self.assertEqual(len(rows), 14)
        for row in rows:
            self.assertIn("NOT_RUN", row)
        for clause in ("RuntimeRecipe[] concreta", "BLOCKED", "Task 03", "sem probes"):
            self.assertIn(clause, document)

    def test_techspec_has_contractual_sections_and_traceability(self):
        document = self.read_required(TECHSPEC)
        for heading in (
            "Technical Context", "Component Inventory", "Interfaces and Contracts",
            "Data Model (Conditional)", "API Contracts (Conditional)", "Decisions",
            "Risks", "Test Cases", "Gate",
        ):
            self.assertIn(f"## {heading}", document)
        for number in range(1, 18):
            self.assertRegex(document, rf"\bRF-{number:03}\b")
        for number in range(1, 17):
            self.assertRegex(document, rf"\b(?:CA|SC)-{number:03}\b")
        for clause in (
            "contract_root = execution_root = checkout_root",
            "preservar campos desconhecidos",
            "same-directory",
            "evento de sucesso",
            "STALE",
            "NEEDS_CONTEXT",
        ):
            self.assertIn(clause, document)

    def test_techspec_rejects_stale_empty_recipe_and_old_task_ownership(self):
        document = self.read_required(TECHSPEC)
        normalized = " ".join(document.split())
        for stale in (
            "o input permanece `RuntimeRecipe[]` vazio",
            "a receita está vazia/BLOCKED",
            "executor futuro da Task 03",
        ):
            self.assertNotIn(stale, normalized)
        for current in (
            "RuntimeRecipe[] concreta",
            "Task 05 vinculará o gate operacional separado",
            "somente Task 06 poderá executar probes aprovados",
        ):
            self.assertIn(current, normalized)

    def test_native_traceability_preserves_required_stories_and_gates_nullable_ids(self):
        document = self.read_required(TECHSPEC)
        for clause in (
            "schema nativo separado",
            "Stories são REQUIRED",
            "conserva a entrada original",
            "story_id",
            "scenario_id",
            "dispensa de Stories aprovada",
            "contrato QUICK aprovado",
            "vinculados no envelope",
            "requirement_id",
            "criterion_id",
            "test_id",
            "RF/CA locais",
            "objetivo reduzido",
            "gate técnico",
            "sem gate e testes, não avança",
            "TU-005 — Positivo",
            "TU-006 — Negativo",
        ):
            self.assertIn(clause, document)

        mutations = (
            document.replace("conserva a entrada original", "normaliza a entrada"),
            document.replace("dispensa de Stories aprovada", "Stories ausentes"),
            document.replace("contrato QUICK aprovado", "modo QUICK"),
            document.replace("requirement_id", "requirement_ref"),
            document.replace("criterion_id", "criterion_ref"),
            document.replace("test_id", "test_ref"),
            document.replace("sem gate e testes, não avança", "pode avançar por confiança"),
        )
        for mutation in mutations:
            self.assertNotEqual(mutation, document)
            required = (
                "conserva a entrada original", "dispensa de Stories aprovada",
                "contrato QUICK aprovado", "requirement_id", "criterion_id",
                "test_id", "sem gate e testes, não avança",
            )
            self.assertTrue(any(clause not in mutation for clause in required))

    def test_local_links_and_recorded_source_digests_resolve(self):
        expected = {
            "tasks/prd-specflow/prd.md": hashlib.sha256(PRD.read_bytes()).hexdigest(),
            "tasks/prd-specflow/stories.md": hashlib.sha256(STORIES.read_bytes()).hexdigest(),
            ".planning/power/features/specflow-m01/probe-recipe.md": hashlib.sha256(
                RECIPE.read_bytes()
            ).hexdigest(),
        }
        for path in (COMPATIBILITY, DECISIONS, TECHSPEC, TASKS):
            document = self.read_required(path)
            for source, digest in expected.items():
                if path == DECISIONS:
                    continue
                if source != ".planning/power/features/specflow-m01/probe-recipe.md":
                    self.assertIn(source, document)
                    self.assertIn(digest, document)
            if path == DECISIONS:
                techspec = self.read_required(TECHSPEC)
                self.assertIn("interface-decisions.md é um snapshot histórico arquivado", techspec)
                self.assertIn(
                    "a21d7f6bdad4abbeee411c7c6629d3ac27bebe11fecf53fe5a7f8c26e50d5c75",
                    techspec,
                )
                self.assertIn("c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4", techspec)
            if path == TASKS:
                self.assertIn("tasks/prd-specflow/techspec.md", document)
                self.assertIn(hashlib.sha256(TECHSPEC.read_bytes()).hexdigest(), document)
            for link in re.findall(r"\]\(([^)]+)\)", document):
                target = (path.parent / link).resolve()
                self.assertTrue(target.is_relative_to(ROOT), link)
                self.assertTrue(target.is_file(), link)

    def test_tasks_scope_has_exact_allowlist_commands_dependencies_and_gates(self):
        document = self.read_required(TASKS)
        task_004 = document.split("## TASK-004", 1)[1]
        allowed = set(re.findall(r"(?m)^    - path: `([^`]+)`$", task_004))
        self.assertEqual(allowed, ALLOWED_PATHS)
        for command in (
            "python3 -m unittest tests.test_sdd_flow_m01_contracts",
            "python3 -m unittest tests.test_sdd_flow_m01_contracts tests.test_sdd_flow_m01_qualification tests.test_sdd_composy_product",
        ):
            self.assertIn(f"`{command}`", document)
        for clause in (
            "M01.01", "PRD APPROVED", "Stories APPROVED",
            "RuntimeRecipe[] concreta", "BLOCKED", "NOT_RUN", "Task 03",
            "gate humano de TASKS", "gate separado da receita", "não ready",
            "não complete", "CA-002", "SC-002", "CA-014", "SC-014",
            "TechSpec APPROVED", "gate renovado de TASKS",
        ):
            self.assertIn(clause, document)
        task_ids = re.findall(r"(?m)^\| TASK-(\d{3}) \|", document)
        self.assertEqual(task_ids, [f"{number:03}" for number in range(1, 8)])
        self.assertNotRegex(document, r"(?m)^\| TASK-\d{3} \|.*\| (?:ready|complete) \|")
        self.assertNotRegex(document, r"(?m)^\s*(?:executable|argv):\s*[^n]")

    def test_report_records_the_tasks_gate_reconciliation(self):
        document = self.read_required(REPORT)
        for clause in (
            "Terceira parcela — gate de TASKS aprovado",
            "2026-09-12T19:05:36Z",
            "tasks/prd-specflow/tasks.md",
            "4c7398bd77bf5d96ef49ea08573faf760dbc70d983b9a58ed788a0b22932b9f3",
            "STATUS: DONE",
            "RuntimeRecipe[] continua vazio",
            "Task 03 ainda não está liberada",
        ):
            self.assertIn(clause, document)

    def test_report_records_the_corrected_techspec_renewed_gate(self):
        document = self.read_required(REPORT)
        for clause in (
            "Correction round 1 — TechSpec corrigido reaprovado",
            "2026-09-12T23:57:17Z",
            "f047d562a41062daf1003d363d49cd130ade8d9430fb9b7a9ad943085afbb633",
            "a952198143a3f8b9a97e88331a2fd7bc048c7117a00babcf67025c42cccfd88c",
            "STATUS: NEEDS_CONTEXT",
            "gate renovado de TASKS",
        ):
            self.assertIn(clause, document)

    def test_report_records_the_renewed_tasks_gate_and_handoff_block(self):
        document = self.read_required(REPORT)
        for clause in (
            "Correction round 1 — TASKS reaprovado",
            "2026-09-13T00:02:44Z",
            "62e84e21284a77aa80fff6d827fc9e39e38b7f690861b342e07f38d820fc2332",
            "9b8ce2dfe58d60ec16f1a8a9b2e98c896dfa5f86253af7ed4e658e9611c3de7d",
            "STATUS: DONE",
            "RuntimeRecipe concreta",
            "comando qualificado",
            "aprovação de escopo mutável",
            "handoff da Task 03 segue bloqueado",
        ):
            self.assertIn(clause, document)

    def test_negative_mutations_are_rejected_without_touching_contracts(self):
        decisions = self.read_required(DECISIONS)
        techspec = self.read_required(TECHSPEC)
        for document, kind in (
            (decisions.replace("human_approval: PENDING", "human_approval: APPROVED", 1),
             "INTERFACE_DECISIONS"),
            (decisions.replace("RuntimeRecipe =", "RuntimeRecipeV2 =", 1),
             "INTERFACE_DECISIONS"),
            (decisions.replace("ArtifactRef |", "EvidenceRef |", 1),
             "INTERFACE_DECISIONS"),
        ):
            with self.subTest(mutation=document[:100]):
                self.assertTrue(proposal_errors(document, kind) or interface_errors(document))

        gate_mutations = (
            techspec.replace("human_approval: APPROVED", "human_approval: PENDING", 1),
            techspec.replace("event: human_approval", "event: source_review", 1),
            techspec.replace("event: approval_invalidated", "event: source_review", 1),
            techspec.replace("by: human:user", "by: agent:reviewer", 1),
            techspec.replace("2026-09-12T23:57:17Z", "2026-09-12T19:00:09Z", 1),
            techspec.replace("scope: tasks/prd-specflow/techspec.md", "scope: tasks/prd-specflow/stories.md", 1),
            techspec.replace('source: "user: sim"', 'source: "user: aprovado"', 1),
            techspec.replace("previous approval is stale", "approval remains valid", 1),
            techspec.replace(hashlib.sha256(PRD.read_bytes()).hexdigest(), "0" * 64, 1),
        )
        for mutation in gate_mutations:
            self.assertTrue(
                techspec_gate_errors(
                    mutation, PRD.read_bytes(), STORIES.read_bytes(), RECIPE.read_bytes()
                )
            )
        self.assertTrue(
            techspec_gate_errors(
                techspec, PRD.read_bytes() + b"\nchanged", STORIES.read_bytes(), RECIPE.read_bytes()
            )
        )

        tasks = self.read_required(TASKS)
        tasks_mutations = (
            tasks.replace("human_approval: APPROVED", "human_approval: PENDING", 1),
            tasks.replace("event: human_approval", "event: source_review", 1),
            tasks.replace("event: approval_invalidated", "event: source_review", 1),
            tasks.replace("by: human:user", "by: agent:reviewer", 1),
            tasks.replace("2026-09-13T00:02:44Z", "2026-09-12T19:05:36Z", 1),
            tasks.replace("scope: tasks/prd-specflow/tasks.md", "scope: tasks/prd-specflow/techspec.md", 1),
            tasks.replace('source: "user: sim"', 'source: "user: aprovado"', 1),
            tasks.replace("previous approval is stale", "approval remains valid", 1),
            tasks.replace(hashlib.sha256(TECHSPEC.read_bytes()).hexdigest(), "0" * 64, 1),
        )
        for mutation in tasks_mutations:
            self.assertTrue(
                tasks_gate_errors(
                    mutation,
                    PRD.read_bytes(),
                    STORIES.read_bytes(),
                    TECHSPEC.read_bytes(),
                    RECIPE.read_bytes(),
                )
            )
        self.assertTrue(
            tasks_gate_errors(
                tasks,
                PRD.read_bytes(),
                STORIES.read_bytes(),
                TECHSPEC.read_bytes() + b"\nchanged",
                RECIPE.read_bytes(),
            )
        )


if __name__ == "__main__":
    unittest.main()
