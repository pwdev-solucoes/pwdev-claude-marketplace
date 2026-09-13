"""Structural tests for M01 Task 03's proposed, still-unapproved recipes."""

import json
import hashlib
import re
import unittest
from copy import deepcopy
from pathlib import Path
from pathlib import PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / ".planning/power/features/specflow-m01"
QUALIFICATION = FEATURE / "runtime-command-qualification.md"
RECIPE = FEATURE / "probe-recipe.md"
RUNTIME = FEATURE / "runtime-qualification.md"
TASKS = ROOT / "tasks/prd-specflow/tasks.md"
EXECUTABLE = "/Users/paulosoares/.local/bin/compozy"
ALLOWED_PATHS = {
    "tests/test_sdd_flow_m01_recipe.py",
    ".planning/power/features/specflow-m01/runtime-command-qualification.md",
    ".planning/power/features/specflow-m01/probe-recipe.md",
    ".planning/power/features/specflow-m01/runtime-qualification.md",
    "tasks/prd-specflow/tasks.md",
}


def recipe_envelope(document):
    blocks = re.findall(r"```json\n(.*?)\n```", document, re.S)
    for block in blocks:
        value = json.loads(block)
        if isinstance(value, dict) and "runtime_recipes" in value:
            return value
    raise AssertionError("missing RuntimeRecipe[] envelope")


def recipe_contract_errors(envelope):
    """Validate documentary proposal shape; this is not runtime enforcement."""
    errors = []
    if envelope.get("status") != "BLOCKED":
        errors.append("status")
    if envelope.get("approved_scope") is not None:
        errors.append("envelope approval")
    if envelope.get("result") != "NOT_RUN":
        errors.append("envelope result")
    recipes = envelope.get("runtime_recipes")
    if not isinstance(recipes, list) or not recipes:
        return errors + ["runtime_recipes"]
    prefix = ".planning/power/features/specflow-m01/probe/"
    daemon_scope = "host-daemon:/Users/paulosoares/.compozy/daemon.sock"
    for recipe in recipes:
        recipe_id = recipe.get("id", "missing-id")
        if recipe.get("executable") != EXECUTABLE:
            errors.append(f"{recipe_id}: executable")
        argv = recipe.get("argv")
        if (not isinstance(argv, list) or not argv or
                any(not isinstance(arg, str) or not arg or "<" in arg for arg in argv)):
            errors.append(f"{recipe_id}: argv")
        scopes = recipe.get("mutable_scope")
        if not isinstance(scopes, list) or not scopes:
            errors.append(f"{recipe_id}: mutable_scope")
        else:
            for scope in scopes:
                local = isinstance(scope, str) and scope.startswith(prefix)
                traversal = local and ".." in PurePosixPath(scope).parts
                if (not local and scope != daemon_scope) or traversal:
                    errors.append(f"{recipe_id}: unowned scope")
        approval = recipe.get("approved_scope")
        errors.extend(validate_approval(approval))
        if not isinstance(approval, dict) or approval.get("gate_id") != "gate:specflow-m01:runtime-recipe":
            errors.append(f"{recipe_id}: approval")
        if not isinstance(approval, dict) or not approval.get("run_id", "").startswith("power-approval-run:"):
            errors.append(f"{recipe_id}: power namespace")
        if not isinstance(approval, dict) or approval.get("actor_ref") != "human:user":
            errors.append(f"{recipe_id}: actor")
        if recipe.get("result") != "NOT_RUN" or recipe.get("observed") != "NOT_RUN":
            errors.append(f"{recipe_id}: invented result")
        if recipe.get("evidence_refs") != []:
            errors.append(f"{recipe_id}: invented evidence")
    return errors


def validate_approval(approval):
    """Independent pre-Run ApprovalRef validator, including canonical ID inputs."""
    errors = []
    if not isinstance(approval, dict): return ["approval"]
    digest = "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4"
    run_record = f"schema=specflow.power-approval-run.v1\nfeature=specflow-m01\ntask=M01.05\ncheckout_revision=fb146297d681a1a6a77d71b5c30772655802590a\nsnapshot_sha256={digest}\n"
    run_id = "power-approval-run:" + hashlib.sha256(run_record.encode()).hexdigest()
    decision_record = f"schema=specflow.power-approval-decision.v1\nrun_id={run_id}\ngate_id=gate:specflow-m01:runtime-recipe\nactor_ref=human:user\ndecision=approved\ndecided_at=2026-09-13T08:53:00Z\nsnapshot_sha256={digest}\ntechspec_sha256=09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3\ntasks_sha256=1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4\n"
    decision_id = "decision:" + hashlib.sha256(decision_record.encode()).hexdigest()
    if approval.get("run_id") != run_id: errors.append("run_id")
    if approval.get("decision_id") != decision_id: errors.append("decision_id")
    if approval.get("actor_ref") != "human:user": errors.append("actor")
    if approval.get("decided_at") != "2026-09-13T08:53:00Z": errors.append("timestamp")
    expected = ["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3", "power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]
    if approval.get("prerequisites") != expected: errors.append("prerequisites")
    arts = approval.get("artifacts")
    snap = FEATURE / "probe-recipe-approved-snapshot.md"
    if not isinstance(arts, list) or len(arts) != 1: return errors + ["artifacts"]
    a = arts[0]
    if a.get("path") != ".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md": errors.append("artifact path")
    if a.get("sha256") != digest or not snap.is_file() or snap.is_symlink() or hashlib.sha256(snap.read_bytes()).hexdigest() != digest: errors.append("artifact digest")
    return errors


class SpecFlowM01RecipeTests(unittest.TestCase):
    def read_required(self, path):
        self.assertTrue(path.is_file(), f"missing required document: {path.relative_to(ROOT)}")
        return path.read_text(encoding="utf-8")

    def test_concrete_argv_is_documented_but_never_executed_or_approved(self):
        envelope = recipe_envelope(RECIPE.read_text(encoding="utf-8"))
        self.assertEqual(recipe_contract_errors(envelope), [])
        recipes = envelope["runtime_recipes"]
        self.assertGreater(len(recipes), 0)
        for recipe in recipes:
            with self.subTest(recipe=recipe.get("id")):
                self.assertEqual(recipe["executable"], EXECUTABLE)
                self.assertTrue(recipe["argv"])
                self.assertEqual(recipe["cwd"], str(ROOT))
                self.assertEqual(recipe["approved_scope"]["decision"], "approved")
                self.assertEqual(recipe["result"], "NOT_RUN")
                self.assertEqual(recipe["evidence_refs"], [])
                self.assertEqual(recipe["observed"], "NOT_RUN")

    def test_invalid_recipe_mutations_are_structurally_rejected(self):
        valid = recipe_envelope(RECIPE.read_text(encoding="utf-8"))
        cases = []

        traversal = deepcopy(valid)
        traversal["runtime_recipes"][0]["mutable_scope"].append(
            ".planning/power/features/specflow-m01/probe/../../outside"
        )
        cases.append(("traversal", traversal, "unowned scope"))

        empty_argv = deepcopy(valid)
        empty_argv["runtime_recipes"][0]["argv"] = []
        cases.append(("empty argv", empty_argv, "argv"))

        unqualified_argv = deepcopy(valid)
        unqualified_argv["runtime_recipes"][0]["argv"] = ["<unknown>"]
        cases.append(("unqualified argv", unqualified_argv, "argv"))

        foreign_cleanup = deepcopy(valid)
        foreign_cleanup["runtime_recipes"][0]["mutable_scope"].append(
            "foreign:/tmp/not-owned-by-specflow"
        )
        cases.append(("unowned cleanup", foreign_cleanup, "unowned scope"))

        forged_approval = deepcopy(valid)
        forged_approval["runtime_recipes"][0]["approved_scope"] = {
            "decision": "approved", "actor_ref": "fabricated"
        }
        cases.append(("forged approval", forged_approval, "approval"))

        stale_approval = deepcopy(valid)
        stale_approval["approved_scope"] = {"decision": "approved", "stale": True}
        cases.append(("stale approval", stale_approval, "envelope approval"))

        invented_pass = deepcopy(valid)
        invented_pass["runtime_recipes"][0]["result"] = "PASS"
        invented_pass["runtime_recipes"][0]["observed"] = "PASS"
        cases.append(("invented PASS", invented_pass, "invented result"))

        for name, mutation, expected in cases:
            with self.subTest(case=name):
                self.assertTrue(
                    any(expected in error for error in recipe_contract_errors(mutation)),
                    recipe_contract_errors(mutation),
                )

    def test_mutable_scope_and_cleanup_are_exact_and_owned(self):
        document = RECIPE.read_text(encoding="utf-8")
        recipes = recipe_envelope(document)["runtime_recipes"]
        for recipe in recipes:
            with self.subTest(recipe=recipe["id"]):
                self.assertTrue(recipe["mutable_scope"])
                self.assertTrue(any(scope.startswith(".planning/power/features/specflow-m01/probe/")
                                    for scope in recipe["mutable_scope"]))
                self.assertTrue(all(
                    scope.startswith(".planning/power/features/specflow-m01/probe/")
                    or scope == "host-daemon:/Users/paulosoares/.compozy/daemon.sock"
                    for scope in recipe["mutable_scope"]
                ))
        for clause in (
            "cleanup somente de recursos próprios registrados",
            "3 tentativas totais incluindo a primeira",
            "janela de ausência de progresso 2",
            "fan-out 1",
            "Não remover recurso desconhecido",
        ):
            self.assertIn(clause, document)

    def test_stale_or_absent_approval_blocks_every_recipe(self):
        document = RECIPE.read_text(encoding="utf-8")
        envelope = recipe_envelope(document)
        self.assertEqual(envelope["approved_scope"], None)
        self.assertEqual(envelope["status"], "BLOCKED")
        self.assertIn("aprovação stale", document)
        self.assertIn("digest divergente", document)
        self.assertIn("Task 04", document)

    def test_read_only_discovery_does_not_invent_behavioral_pass(self):
        qualification = self.read_required(QUALIFICATION)
        runtime = self.read_required(RUNTIME)
        self.assertIn("compozy 0.3.0-beta.16", qualification)
        self.assertIn("daemon socket", qualification)
        self.assertNotRegex(runtime, r"(?m)^\| (?:CORE|OPT)-\d{3} \|.*\| PASS \|")
        self.assertEqual(len(re.findall(r"(?m)^\| CORE-\d{3} \|.*\| NOT_RUN \|", runtime)), 9)
        self.assertEqual(len(re.findall(r"(?m)^\| OPT-\d{3} \|.*\| NOT_RUN \|", runtime)), 5)

    def test_tasks_reopens_first_gate_with_exact_task_003_scope(self):
        document = TASKS.read_text(encoding="utf-8")
        allowed = set(re.findall(r"(?m)^  - path: `([^`]+)`$", document))
        self.assertEqual(allowed, ALLOWED_PATHS)
        self.assertRegex(document, r"(?m)^\| TASK-003 \|.*\| pending \|")
        for clause in (
            "Primeiro gate: TASKS",
            "gate operacional separado",
            "STATUS: NEEDS_CONTEXT",
            "nenhum comando mutável",
        ):
            self.assertIn(clause, document)


    def test_approval_ids_and_snapshot_are_recomputed_and_addressable(self):
        envelope = recipe_envelope(RECIPE.read_text(encoding="utf-8"))
        snapshot = FEATURE / "probe-recipe-approved-snapshot.md"
        self.assertTrue(snapshot.is_file()); self.assertFalse(snapshot.is_symlink())
        digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
        self.assertEqual(digest, "c606ebbf29d30881e54dd3e66c58d7e273a5f4bf6d49fd60b980e2171240b7c4")
        run = "schema=specflow.power-approval-run.v1\nfeature=specflow-m01\ntask=M01.05\ncheckout_revision=fb146297d681a1a6a77d71b5c30772655802590a\nsnapshot_sha256=" + digest + "\n"
        run_id = "power-approval-run:" + hashlib.sha256(run.encode()).hexdigest()
        decision = "schema=specflow.power-approval-decision.v1\nrun_id=" + run_id + "\ngate_id=gate:specflow-m01:runtime-recipe\nactor_ref=human:user\ndecision=approved\ndecided_at=2026-09-13T08:53:00Z\nsnapshot_sha256=" + digest + "\ntechspec_sha256=09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3\ntasks_sha256=1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4\n"
        decision_id = "decision:" + hashlib.sha256(decision.encode()).hexdigest()
        prereqs = ["power-gate:techspec:09bde614371cb465ea1c135244bd6c4e8cc3f3e62c0c9fdeb3dc065d70ab54f3", "power-gate:tasks:1efe23df5abe7950567a39bc9451adb5672de14f835ec111fed30bb941bd02d4"]
        for recipe in envelope["runtime_recipes"]:
            approval = recipe["approved_scope"]
            self.assertEqual((approval["run_id"], approval["decision_id"]), (run_id, decision_id))
            self.assertEqual(approval["actor_ref"], "human:user"); self.assertEqual(approval["prerequisites"], prereqs)
            self.assertEqual(approval["artifacts"][0]["path"], ".planning/power/features/specflow-m01/probe-recipe-approved-snapshot.md")
            self.assertEqual(approval["artifacts"][0]["sha256"], digest)

    def test_approval_mutations_are_rejected_for_every_recipe(self):
        base = recipe_envelope(RECIPE.read_text(encoding="utf-8"))
        fields = [("run_id", "x"), ("decision_id", "decision:0"), ("artifacts", []), ("prerequisites", []), ("decided_at", "2000-01-01T00:00:00Z"), ("actor_ref", "agent:loop"), ("run_id", "loop-run:future")]
        for field, value in fields:
            for index in range(7):
                mutated = deepcopy(base); mutated["runtime_recipes"][index]["approved_scope"][field] = value
                self.assertTrue(validate_approval(mutated["runtime_recipes"][index]["approved_scope"]), (field, index))
        for index in range(7):
            mutated = deepcopy(base); a = mutated["runtime_recipes"][index]["approved_scope"]
            a["prerequisites"] = list(reversed(a["prerequisites"]))
            self.assertTrue(validate_approval(a), ("reversed prerequisites", index))
            mutated = deepcopy(base); a = mutated["runtime_recipes"][index]["approved_scope"]
            a["artifacts"][0]["sha256"] = "0" * 64
            self.assertTrue(validate_approval(a), ("wrong digest", index))
            mutated = deepcopy(base); a = mutated["runtime_recipes"][index]["approved_scope"]
            a["artifacts"][0]["path"] = ".planning/power/features/specflow-m01/probe-recipe.md"
            self.assertTrue(validate_approval(a), ("stale path", index))

if __name__ == "__main__":
    unittest.main()
