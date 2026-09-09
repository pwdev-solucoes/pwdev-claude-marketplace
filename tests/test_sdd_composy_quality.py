import unittest
import json
import subprocess
from pathlib import Path
import sys, tempfile


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
sys.path.insert(0, str(PLUGIN / "scripts"))
import sdd_execute
import sdd_qa
import sdd_evidence

class EvidenceManifestContractTest(unittest.TestCase):
    def test_evidence_cli_build_verify_export_and_discover(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "run.txt").write_text("ok")
            import sdd_language
            sdd_language.persist_language(root, 'en-US')
            source = root / "input.json"
            source.write_text(json.dumps({"prd_slug":"demo","task_id":"TASK-007","entries":[{"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}]}))
            manifest = root / "manifest.json"; report = root / "report.html"
            script = PLUGIN / "scripts/sdd_evidence.py"
            built = subprocess.run([sys.executable, str(script), "build", str(source), str(root), str(manifest)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr); self.assertIn("generated_at", json.loads(built.stdout))
            verified = subprocess.run([sys.executable, str(script), "verify", str(manifest), str(root)], capture_output=True, text=True)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            exported = subprocess.run([sys.executable, str(script), "export", str(manifest), str(root), str(report)], capture_output=True, text=True)
            self.assertEqual(exported.returncode, 0, exported.stderr); self.assertTrue(report.exists())
            discovered = subprocess.run([sys.executable, str(script), "discover", str(root)], capture_output=True, text=True)
            self.assertEqual(discovered.returncode, 0, discovered.stderr); self.assertIn("run.txt", discovered.stdout)

    def test_manifest_generated_at_is_required_and_rfc3339(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "run.txt").write_text("ok")
            entry={"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}
            built=sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, root, generated_at="2026-01-01T00:00:00Z")
            self.assertEqual(built["generated_at"], "2026-01-01T00:00:00Z")
            self.assertFalse(sdd_evidence.verify({**built, "generated_at":"invalid"}, root)["ok"])
    def test_evidence_skill_and_adapter_route_existing_manifest_and_optional_pdf(self):
        skill = (PLUGIN / "skills/sdd-evidence/SKILL.md").read_text()
        metadata = (PLUGIN / "skills/sdd-evidence/agents/openai.yaml").read_text()
        command = (PLUGIN / "commands/evidence.md").read_text()
        for text in (skill, metadata, command):
            self.assertIn("sdd-evidence", text)
        self.assertIn("existing", skill.lower())
        self.assertIn("PDF", skill)
        self.assertIn("pass through", command)

    def test_evidence_skill_documents_discovery_and_route(self):
        skill = (PLUGIN / "skills/sdd-evidence/SKILL.md").read_text()
        for term in ("discover", "build", "verify", "export", "evidence_required", "review_required", "manifest"):
            self.assertIn(term, skill)

    def test_existing_evidence_can_be_rebuilt_without_mutating_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); source = root / "run.txt"; source.write_text("ok")
            entry = {"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}
            first = sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, root)
            before = source.read_bytes()
            rebuilt = sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, root)
            self.assertEqual(first["entries"][0]["sha256"], rebuilt["entries"][0]["sha256"])
            self.assertEqual(before, source.read_bytes())

    def test_evidence_transition_remains_guarded(self):
        import sdd_tasks
        task = {"id":"TASK-001","title":"x","state":"qa_required","dependencies":[],"acceptance_criteria":["CA-001"],"verification_commands":["true"],"allowed_paths":["src/"],"evidence_required":True}
        data = {"schema_version":"1","prd_slug":"demo","updated_at":"2026-01-01T00:00:00Z","tasks":[task]}
        with self.assertRaises(sdd_tasks.TaskError):
            sdd_tasks.transition(data, "TASK-001", "review_required", now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc))
    def test_confined_hashed_and_html_escaped(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "run.txt").write_text("<script>alert(1)</script>")
            entry = {"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}
            built = sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, root)
            self.assertEqual(len(built["entries"][0]["sha256"]), 64)
            self.assertTrue(sdd_evidence.verify(built, root)["ok"])
            self.assertNotIn("<script>", sdd_evidence.render_html(built))
            for bad in ("../run.txt", "/tmp/run.txt", "link\\run.txt"):
                with self.assertRaises(ValueError): sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[{**entry,"path":bad}]}, root)

    def test_rejects_unknown_enums_missing_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"ok.txt").write_text("ok"); (root/"link.txt").symlink_to(root/"ok.txt")
            base={"prd_slug":"demo","task_id":"TASK-007","entries":[{"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"ok.txt"}]}
            for change in ({"result":"maybe"},{"evidence_type":"video"},{"path":"missing.txt"},{"path":"link.txt"}):
                with self.assertRaises((ValueError,FileNotFoundError)): sdd_evidence.build({**base,"entries":[{**base["entries"][0],**change}]},root)

    def test_verify_detects_hash_missing_and_internal_symlink_and_order_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"real").mkdir(); (root/"real"/"x.txt").write_text("x"); (root/"alias").symlink_to(root/"real", target_is_directory=True)
            e=lambda p, n: {"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":f"CA-{n:03d}","test_id":f"TEST-{n:03d}","result":"passed","evidence_type":"log","path":p}
            data={"prd_slug":"demo","task_id":"TASK-007","entries":[e("real/x.txt",2),e("real/x.txt",1)]}
            built=sdd_evidence.build(data,root)
            self.assertEqual([x["criterion_id"] for x in built["entries"]], ["CA-001","CA-002"])
            built["entries"][0]["sha256"]="0"*64
            self.assertFalse(sdd_evidence.verify(built,root)["ok"])
            built["entries"][0]["path"]="gone.txt"
            self.assertFalse(sdd_evidence.verify(built,root)["ok"])
            with self.assertRaises(ValueError): sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[e("alias/x.txt",1)]},root)

    def test_evidence_root_symlinks_are_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d); real = base / "real"; real.mkdir(); (real / "run.txt").write_text("ok")
            root_link = base / "root-link"; root_link.symlink_to(real, target_is_directory=True)
            nested_link = base / "nested-link"; nested_link.symlink_to(base, target_is_directory=True)
            entry = {"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}
            for supplied in (root_link, nested_link / "real"):
                with self.assertRaises(ValueError):
                    sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, supplied)
                with self.assertRaises(ValueError):
                    sdd_evidence.discover(supplied)

    def test_export_confines_output_and_writes_html(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"run.txt").write_text("ok")
            entry={"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"log","path":"run.txt"}
            manifest=sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]},root)
            import sdd_language
            sdd_language.persist_language(root, 'en-US')
            out=root/"report.html"; self.assertEqual(sdd_evidence.export(manifest,out,root),out); self.assertIn("Evidence report",out.read_text())
            with self.assertRaises(ValueError): sdd_evidence.export(manifest,root.parent/"escape.html",root)

    def test_pdf_request_fails_when_image_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            entry={"requirement_id":"RF-001","story_id":"US-001","scenario_id":"SC-001","criterion_id":"CA-001","test_id":"TEST-001","result":"passed","evidence_type":"screenshot","path":"missing.png"}
            with self.assertRaises(FileNotFoundError): sdd_evidence.build({"prd_slug":"demo","task_id":"TASK-007","entries":[entry]}, Path(d))


class ExecutionContractTest(unittest.TestCase):
    def read(self, relative):
        return (PLUGIN / relative).read_text(encoding="utf-8")

    def test_reference_defines_preflight_tdd_and_scope_contract(self):
        text = self.read("references/execution.md")
        for term in (
            "dependency preflight", "ready", "TDD", "failing test", "allowed_paths",
            "verification_commands", "SHA-256", "qa_required", "blocked", "rejected",
            "user-owned", "cleanup", "approved requirements", "environment ownership",
        ):
            self.assertIn(term, text)

    def test_verification_template_defaults_to_non_terminal_pending_transition(self):
        text = self.read("templates/verdict.md")
        self.assertIn("lifecycle:\n  status: DRAFT", text)
        self.assertIn("human_approval: PENDING", text)
        self.assertIn("transition: verify_required", text)
        self.assertNotIn("human_approval: PENDING\ntransition: complete", text)

    def test_reference_defines_sanitized_evidence_and_commands(self):
        text = self.read("references/execution.md")
        for term in (
            "evidence", "relative", "sanitized", "exit code", "stdout", "stderr",
            "command", "real", "deterministic", "atomic", "trace",
        ):
            self.assertIn(term, text)

    def test_skill_is_portable_and_routes_execution_without_reimplementing_engine(self):
        text = self.read("skills/sdd-execute/SKILL.md")
        for term in (
            "name: sdd-execute", "references/execution.md", "portable", "ready",
            "dependency preflight", "allowed paths", "verification commands",
            "qa_required", "blocked", "rejected", "Do not commit", "Do not read or expose",
        ):
            self.assertIn(term, text)

    def test_runtime_metadata_and_thin_adapter_exist(self):
        metadata = self.read("skills/sdd-execute/agents/openai.yaml")
        command = self.read("commands/execute.md")
        self.assertIn("display_name", metadata)
        self.assertIn("sdd-execute", metadata)
        self.assertIn("$sdd-execute", command)
        self.assertIn("pass through", command)
        self.assertNotIn("python", command.lower())

    def test_execution_contract_records_failures_and_ownership(self):
        text = self.read("references/execution.md")
        for term in (
            "dependency_missing", "tdd_missing", "path_violation", "command_failed",
            "environment_owned", "cleanup_status", "next_action", "human approval",
        ):
            self.assertIn(term, text)

    def task(self, dependencies=(), paths=("src/",)):
        return {"id":"TASK-001", "state":"ready", "dependencies": list(dependencies), "allowed_paths": list(paths)}

    def test_preflight_blocks_dependency_red_and_unknown_environment(self):
        self.assertEqual(sdd_execute.preflight(self.task(({"state":"running"},)), red_evidence=True, human_approved=True)["reason"], "dependency_missing")
        self.assertEqual(sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=False, human_approved=True)["reason"], "tdd_missing")
        self.assertEqual(sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=True, environment="environment_unknown", human_approved=True)["reason"], "environment_unknown")
        self.assertEqual(sdd_execute.preflight({**self.task(), "state":"running"}, human_approved=True)["reason"], "not_ready")
        self.assertEqual(sdd_execute.preflight(self.task(), red_evidence=True)["reason"], "human_approval_missing")

    def test_preflight_rejects_paths_and_success_transitions_to_qa(self):
        result = sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=True, human_approved=True, changed_paths=("secrets.txt",))
        self.assertEqual((result["transition"], result["reason"]), ("rejected", "path_violation"))
        ready = sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=True, human_approved=True, changed_paths=("src/app.py",))
        done = sdd_execute.finish(ready, [{"status":"passed"}], cleanup_status="cleaned")
        self.assertEqual(done["transition"], "qa_required")

    def test_command_evidence_hashes_sanitizes_and_classifies_failure(self):
        class Result:
            returncode = 1; stdout = "token=abc123"; stderr = "boom"
        evidence = sdd_execute.run_command(["fake"], cwd=Path(tempfile.gettempdir()), runner=lambda *a, **k: Result())
        self.assertEqual(evidence["status"], "command_failed")
        self.assertNotIn("abc123", evidence["stdout"])
        self.assertEqual(len(evidence["sha256"]), 64)
        unavailable = sdd_execute.run_command(["missing-command"], cwd=Path(tempfile.gettempdir()), runner=lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
        self.assertEqual(unavailable["status"], "command_unavailable")

    def test_cleanup_failure_blocks_and_rejection_preserves_reason(self):
        ready = sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=True, human_approved=True)
        blocked = sdd_execute.finish(ready, [{"status":"passed"}], cleanup_status="user_owned")
        self.assertEqual((blocked["transition"], blocked["reason"]), ("blocked", "cleanup_failed"))
        self.assertEqual(sdd_execute.finish(ready, [], cleanup_status="cleaned")["reason"], "evidence_missing")
        rejected = sdd_execute.preflight(self.task(({"state":"complete"},)), red_evidence=True, human_approved=True, changed_paths=("outside/file",))
        self.assertEqual(rejected["next_action"], "change only approved paths")

    def test_result_shape_and_evidence_path_confinement(self):
        ready = sdd_execute.preflight(self.task(), red_evidence=True, human_approved=True)
        self.assertTrue({"task_id","changed_paths","environment_ownership","cleanup_status","evidence_manifest","transition","next_action"} <= set(ready))
        with self.assertRaises(ValueError): sdd_execute.run_command(["true"], cwd=Path(tempfile.gettempdir()), evidence_path="../escape.json")
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "real.json"; target.write_text("x")
            link = Path(d) / "link.json"; link.symlink_to(target)
            with self.assertRaises(ValueError): sdd_execute.run_command(["true"], cwd=Path(d), evidence_path=str(link))

    def test_qa_template_covers_traceable_quality_dimensions_and_okf(self):
        text = self.read("templates/qa.md")
        for term in (
            "type: QA_REPORT", "okf_version: \"0.2\"", "CA-", "SC-", "unit",
            "integration", "E2E", "accessibility", "responsiveness", "environment",
            "evidence", "verified", "generated", "lifecycle", "evidence_required",
            "REJECTED",
        ):
            self.assertIn(term, text)

    def test_quality_reference_defines_results_evidence_and_blocker_semantics(self):
        text = self.read("references/quality.md")
        for term in (
            "qa_required", "CA coverage", "unit", "integration", "E2E", "browser",
            "accessibility", "responsiveness", "environment", "evidence inventory",
            "evidence_required", "rejected", "blocker", "regression", "sha256",
            "sanitized", "human approval",
        ):
            self.assertIn(term, text)

    def test_qa_skill_is_portable_and_fails_closed(self):
        text = self.read("skills/sdd-qa/SKILL.md")
        for term in (
            "name: sdd-qa", "references/quality.md", "portable", "qa_required",
            "CA", "unit", "integration", "E2E", "accessibility", "responsiveness",
            "evidence_required", "rejected", "blocker", "Do not commit",
            "Do not read or expose",
        ):
            self.assertIn(term, text)

    def test_qa_metadata_routes_shared_skill(self):
        metadata = self.read("skills/sdd-qa/agents/openai.yaml")
        self.assertIn("display_name", metadata)
        self.assertIn("sdd-qa", metadata)

    def qa_input(self):
        return {
            "state": "qa_required", "human_approved": True,
            "acceptance": [{"id": "CA-001", "story": "SC-001", "tests": ["T-001"]}],
            "results": {name: {"status": "passed", "command": "pytest -q", "environment": "ci", "exit_code": 0, "evidence": "evidence/run.txt"} for name in ("unit", "integration", "e2e")},
            "browser": {"available": True, "name": "Playwright"},
            "accessibility": "passed", "responsiveness": "passed",
            "environment": {"ready": True, "runtime": "python3.9", "versions": {"app": "1"}, "cleanup": "cleaned", "ownership": "run"},
            "regression": {"status": "passed", "evidence": "evidence/run.txt"},
            "evidence": [{"path": "evidence/run.txt", "type": "log", "result": "passed", "summary": "QA output", "source": "unit"}],
        }

    def test_qa_complete_report_transitions_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "evidence").mkdir(); (root / "evidence/run.txt").write_text("ok")
            first = sdd_qa.assess(self.qa_input(), evidence_root=root, generated_by="agent", verified_by="reviewer")
            second = sdd_qa.assess(self.qa_input(), evidence_root=root, generated_by="agent", verified_by="reviewer")
        self.assertEqual(first["transition"], "evidence_required")
        self.assertEqual(first["status"], "APPROVED")
        self.assertEqual(first["evidence"], second["evidence"])
        self.assertEqual(first["coverage"], [{"ca": "CA-001", "story": "SC-001", "tests": ["T-001"]}])

    def test_qa_rejects_each_required_dimension_with_sanitized_reason(self):
        cases = (("acceptance", "coverage_missing"), ("unit", "unit_failed"),
                 ("integration", "integration_failed"), ("e2e", "e2e_failed"),
                 ("browser", "browser_unavailable"), ("accessibility", "accessibility_failed"),
                 ("responsiveness", "responsiveness_failed"), ("environment", "environment_not_ready"),
                 ("cleanup", "cleanup_failed"), ("evidence", "evidence_missing"))
        for field, reason in cases:
            data = self.qa_input()
            if field == "acceptance": data["acceptance"] = []
            elif field == "browser": data["browser"] = {"available": False}
            elif field == "cleanup": data["environment"]["cleanup"] = "user_owned"
            elif field == "evidence": data["evidence"] = []
            elif field == "environment": data["environment"]["ready"] = False
            elif field in ("accessibility", "responsiveness"): data[field] = "failed"
            elif field in ("unit", "integration", "e2e"): data["results"][field]["status"] = "failed"
            result = sdd_qa.assess(data)
            self.assertEqual((result["transition"], result["reason"]), ("rejected", reason))
            self.assertTrue(result["next_action"])
            self.assertNotIn("token=", result["blocker"])

    def test_qa_report_has_okf_lifecycle_and_actor_separation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "evidence").mkdir(); (root / "evidence/run.txt").write_text("ok")
            result = sdd_qa.assess(self.qa_input(), evidence_root=root, generated_by="agent", verified_by="reviewer")
            report = result["report"]
            self.assertEqual((report["type"], report["okf_version"]), ("QA_REPORT", "0.2"))
            self.assertEqual(report["generated"]["by"], "agent")
            self.assertEqual(report["verified"][0]["by"], "reviewer")
            self.assertEqual(report["lifecycle"]["status"], "APPROVED")
            self.assertEqual(report["transition"], "evidence_required")

    def test_qa_persists_complete_report_and_can_reload_it(self):
        with tempfile.TemporaryDirectory() as d:
            __import__('sdd_language').persist_language(d, 'en-US')
            root = Path(d); (root / "evidence").mkdir(); (root / "evidence/run.txt").write_text("ok")
            output = root / "qa.md"
            result = sdd_qa.assess(self.qa_input(), evidence_root=root, report_path=Path("qa.md"), allowed_root=root,
                                   generated_by="agent", verified_by="reviewer", title="Product QA")
            output = root / "qa.md"
            self.assertTrue(output.exists())
            text = output.read_text()
            for term in ("type: QA_REPORT", "okf_version: \"0.2\"", "Product QA", "generated:",
                         "verified:", '"human_approval": "APPROVED"', "regression", "environment",
                         "unit", "integration", "e2e", "evidence_required"):
                self.assertIn(term, text)
            self.assertEqual(sdd_qa.load_report(output)["lifecycle"]["status"], "APPROVED")

    def test_qa_persists_and_reloads_rejection_without_secret_leak(self):
        with tempfile.TemporaryDirectory() as d:
            __import__('sdd_language').persist_language(d, 'en-US')
            output = Path(d) / "qa.md"
            data = self.qa_input(); data["results"]["unit"]["status"] = "failed"
            data["secret"] = "token=private"
            result = sdd_qa.assess(data, report_path=Path("qa.md"), allowed_root=Path(d), generated_by="agent", verified_by="reviewer")
            self.assertEqual(result["transition"], "rejected")
            self.assertTrue(output.exists())
            self.assertEqual(sdd_qa.load_report(output)["lifecycle"]["status"], "REJECTED")
            self.assertNotIn("private", output.read_text())

    def test_rejected_qa_persists_sanitized_origin_context(self):
        with tempfile.TemporaryDirectory() as d:
            __import__('sdd_language').persist_language(d, 'en-US')
            root = Path(d); output = root / "qa.md"
            data = self.qa_input()
            data.update({"task_id": "TASK-007", "source": "tasks/prd-demo/task.md",
                         "result_id": "RESULT-009", "secret": "token=private"})
            data["acceptance"][0].update({"story_id": "US-001", "result_id": "RESULT-001"})
            data["results"]["unit"]["status"] = "failed"
            result = sdd_qa.assess(data, report_path=Path("qa.md"), allowed_root=root,
                                   generated_by="agent", verified_by="reviewer")
            self.assertEqual(result["origin"], {
                "task_id": "TASK-007", "source": "tasks/prd-demo/task.md",
                "result_id": "RESULT-009",
                "coverage": [{"ca": "CA-001", "story": "US-001", "result": "RESULT-001"}],
            })
            persisted = sdd_qa.load_report(output)
            self.assertEqual(persisted["origin"], result["origin"])
            self.assertNotIn("private", output.read_text())

    def test_qa_rejects_symlink_report_path(self):
        with tempfile.TemporaryDirectory() as d:
            __import__('sdd_language').persist_language(d, 'en-US')
            root = Path(d); target = root / "real.md"; target.write_text("keep")
            link = root / "link.md"; link.symlink_to(target)
            with self.assertRaises(ValueError): sdd_qa.assess(self.qa_input(), report_path=link, allowed_root=root)

    def test_review_contract_covers_scope_findings_and_no_silent_fix(self):
        template = self.read("templates/codereview.md")
        for term in (
            "type: CODE_REVIEW", "okf_version: \"0.2\"", "base", "target",
            "diff scope", "approved contracts", "severity", "blocker", "rule",
            "citation", "command", "exit code", "skill conformity", "no-silent-fix",
            "human approval", "verified", "lifecycle", "verify_required", "REJECTED",
        ):
            self.assertIn(term, template)

    def test_review_skill_is_portable_and_preserves_review_authority(self):
        skill = self.read("skills/sdd-review/SKILL.md")
        for term in (
            "name: sdd-review", "portable", "references/quality.md", "base", "target",
            "approved contracts", "task evidence", "severity", "rule citations",
            "commands", "skill conformity", "no-silent-fix", "verify_required",
            "rejected", "Do not silently fix", "Do not commit", "Do not read or expose",
        ):
            self.assertIn(term, skill)

    def test_review_runtime_metadata_and_thin_adapter_exist(self):
        metadata = self.read("skills/sdd-review/agents/openai.yaml")
        command = self.read("commands/review.md")
        self.assertIn("display_name", metadata)
        self.assertIn("sdd-review", metadata)
        self.assertIn("$sdd-review", command)
        self.assertIn("pass through", command)
        self.assertNotIn("python", command.lower())

    def test_review_template_requires_explicit_blockers_and_commands(self):
        text = self.read("templates/codereview.md")
        for term in (
            "diff", "base_ref", "target_ref", "changed_paths", "finding_id",
            "severity", "rule_citation", "commands", "exit_code", "evidence",
            "approved", "contract", "blocker", "next_action", "silent",
        ):
            self.assertIn(term, text)

    def test_verification_template_declares_truth_table_and_verdict_values(self):
        text = self.read("templates/verdict.md")
        for term in (
            "type: VERIFICATION_VERDICT", "okf_version: \"0.2\"", "verify_required",
            "truth table", "fresh", "command", "exit code", "evidence", "sha256",
            "PASS", "FAIL", "STALE", "ENVIRONMENT_FAILURE", "NOT_RUN",
            "COMPLETE", "REJECTED", "generated", "verified", "lifecycle",
        ):
            self.assertIn(term, text)

    def test_verification_reference_requires_independent_fresh_refutation_and_stale_rejection(self):
        text = self.read("references/verification.md")
        for term in (
            "independent", "fresh command", "reproduce", "refute", "stale evidence",
            "environment failure", "truth table", "PASS", "FAIL", "STALE",
            "ENVIRONMENT_FAILURE", "NOT_RUN", "sha256", "sanitized", "complete",
            "rejected", "human approval", "verification actor",
        ):
            self.assertIn(term, text)

    def test_verification_skill_is_portable_and_fails_closed(self):
        text = self.read("skills/sdd-verify/SKILL.md")
        for term in (
            "name: sdd-verify", "references/verification.md", "portable",
            "verify_required", "fresh", "independently", "truth table", "refute",
            "stale", "environment failure", "COMPLETE", "REJECTED", "Do not commit",
            "Do not read or expose", "Do not silently",
        ):
            self.assertIn(term, text)

    def test_verification_runtime_metadata_routes_shared_skill(self):
        metadata = self.read("skills/sdd-verify/agents/openai.yaml")
        for term in ("display_name", "sdd-verify", "default_prompt", "fresh"):
            self.assertIn(term, metadata)

    def test_verification_claude_adapter_is_thin_and_guarded(self):
        text = self.read("commands/verify.md")
        for term in ("$sdd-verify", "pass through", "artifact predicates", "lifecycle transitions"):
            self.assertIn(term, text)
        self.assertNotIn("python", text.lower())


if __name__ == "__main__":
    unittest.main()
