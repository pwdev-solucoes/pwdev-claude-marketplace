"""Remaining sdd-composy defects: map inventory details, dashboard handle, CRLF sync, and PDF export."""

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "sdd-composy"
SCRIPTS = PLUGIN / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sdd_evidence  # noqa: E402
import sdd_language  # noqa: E402
import sdd_map  # noqa: E402
import sdd_sync  # noqa: E402

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


class MapInventoryTests(unittest.TestCase):
    def test_project_scripts_are_run_by_their_entry_point_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text('[project]\nname = "demo"\n[project.scripts]\ndemo-cli = "demo.cli:main"\n')
            commands = sdd_map._manifest_commands("pyproject.toml", path)
            if not commands:
                self.skipTest("tomllib is unavailable on this interpreter")
            self.assertIn({"name": "demo-cli", "command": "demo-cli", "source": "pyproject.toml"}, commands)

    def test_makefile_variable_assignments_are_not_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Makefile"
            path.write_text("CC := gcc\nPREFIX:=/usr\nFLAGS ::= -O2\nOUT ?= bin\nbuild: deps\n\tcc x\ntest:\n\ttrue\n")
            names = [item["name"] for item in sdd_map._manifest_commands("Makefile", path)]
            self.assertEqual(names, ["build", "test"])

    def test_sha256_repositories_have_a_valid_commit(self):
        self.assertTrue(sdd_map._valid_commit("a" * 40))
        self.assertTrue(sdd_map._valid_commit("b" * 64))
        self.assertFalse(sdd_map._valid_commit("c" * 12))

    def test_common_secret_files_are_never_opened(self):
        for relative in ("credentials.json", "config/secrets.yaml", ".npmrc", ".pypirc", ".netrc",
                         "home/.ssh/id_rsa", "id_ed25519", "deploy/service-account.json", ".git-credentials",
                         "keys/client.key", "app/.env.production"):
            with self.subTest(relative=relative):
                self.assertTrue(sdd_map._sensitive(relative))
        for relative in ("src/token_parser.py", "docs/keyboard.md", "README.md"):
            with self.subTest(relative=relative):
                self.assertFalse(sdd_map._sensitive(relative))


class DashboardHandleTests(unittest.TestCase):
    DASHBOARD = SCRIPTS / "fleet" / "dashboard.sh"

    def fleet(self, root):
        members = root / ".planning/sdd-composy/fleet/demo/members"; members.mkdir(parents=True)
        (members / "TASK-001.json").write_text(json.dumps({"id": "TASK-001", "status": "running",
                                                          "worktree_path": str(root / "work/TASK-001")}))
        return members

    def dashboard(self, root, *extra):
        return subprocess.run([str(self.DASHBOARD), "--root", str(root), "--fleet-id", "demo", *extra],
                              capture_output=True, text=True)

    def test_handle_is_validated_before_any_output_and_projected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); self.fleet(root)
            real = root / "handle.json"; real.write_text(json.dumps({"driver": "tmux", "pane_id": "%3", "note": "a\u001bb"}))
            link = root / "link.json"; link.symlink_to(real)
            refused = self.dashboard(root, "--json", "--handle", str(link))
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(refused.stdout, "")
            accepted = self.dashboard(root, "--json", "--handle", str(real))
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            payload = json.loads(accepted.stdout)
            self.assertEqual(payload["ui_handle"]["pane_id"], "%3")
            self.assertEqual(payload["ui_handle"]["note"], "a b")

    def test_absolute_worktree_inside_the_root_is_shown_relative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); self.fleet(root)
            payload = json.loads(self.dashboard(root, "--json").stdout)
            self.assertEqual(payload["members"][0]["worktree"], "work/TASK-001")

    def test_json_mode_reports_malformed_members_as_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); members = self.fleet(root)
            (members / "bad.json").write_text("{broken")
            result = self.dashboard(root, "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["errors"], ["malformed member: bad.json"])


class SyncCrlfTests(unittest.TestCase):
    def test_json_authority_rewrites_a_crlf_task_block_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve(); bundle = repo / "tasks/prd-demo"; bundle.mkdir(parents=True)
            markdown = bundle / "task-001.md"
            markdown.write_bytes(("---\r\ntype: TASK\r\ntask:\r\n  id: TASK-001\r\n  title: One\r\n  state: pending\r\n"
                                  "  dependencies: []\r\n  acceptance_criteria: [CA-001]\r\n---\r\n\r\n# TASK-001\r\n").encode())
            state = repo / ".planning/sdd-composy/tasks/demo.json"; state.parent.mkdir(parents=True)
            state.write_text(json.dumps({"schema_version": "1", "prd_slug": "demo", "updated_at": "2026-01-01T00:00:00Z",
                                         "tasks": [{"id": "TASK-001", "title": "One", "state": "ready", "dependencies": [],
                                                    "acceptance_criteria": ["CA-001"], "verification_commands": ["true"],
                                                    "allowed_paths": ["src"], "evidence_required": True}]}))
            plan = sdd_sync.plan(sdd_sync.inspect(bundle, state))
            result = sdd_sync.apply(bundle, state, plan, authority="json", confirmation_token=plan["confirmation_token"])
            self.assertTrue(result["verified"])
            text = markdown.read_bytes().decode()
            self.assertEqual(text.count("task:"), 1)
            self.assertNotIn("\n", text.replace("\r\n", ""), "line endings must stay CRLF")


class PdfExportTests(unittest.TestCase):
    ENTRY = {"requirement_id": "RF-001", "story_id": "US-001", "scenario_id": "SC-001", "criterion_id": "CA-001",
             "test_id": "TEST-001", "result": "passed", "evidence_type": "screenshot", "path": "shot.png"}

    def workspace(self, tmp, image=PNG):
        workspace = Path(tmp).resolve(); sdd_language.persist_language(workspace, "en-US")
        evidences = workspace / "tasks/prd-demo/evidences"; evidences.mkdir(parents=True)
        (evidences / "shot.png").write_bytes(image)
        manifest = sdd_evidence.build({"prd_slug": "demo", "task_id": "TASK-001", "entries": [self.ENTRY]}, evidences)
        return workspace, evidences, manifest

    def fake_browser(self, tmp):
        browser = Path(tmp) / "browser"
        browser.write_text("#!/usr/bin/env python3\nimport sys\n"
                           "out=[a.split('=',1)[1] for a in sys.argv if a.startswith('--print-to-pdf=')][0]\n"
                           "open(out,'wb').write(b'%PDF-1.7\\n%fake\\n%%EOF\\n')\n")
        browser.chmod(0o755)
        return browser

    def test_html_embeds_screenshots_and_pdf_is_written_beside_it(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_dir:
            _, evidences, manifest = self.workspace(tmp)
            output = evidences.parent / "evidence-report.html"
            env = {**os.environ, "SDD_PDF_BROWSER": str(self.fake_browser(bin_dir))}
            old = os.environ.copy(); os.environ.update(env)
            try:
                sdd_evidence.export(manifest, output, evidences, pdf=True)
            finally:
                os.environ.clear(); os.environ.update(old)
            self.assertIn("data:image/png;base64,", output.read_text())
            self.assertTrue(output.with_suffix(".pdf").read_bytes().startswith(b"%PDF-"))

    def test_a_screenshot_that_is_not_an_image_fails_the_pdf(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_dir:
            _, evidences, manifest = self.workspace(tmp, image=b"not an image")
            os.environ["SDD_PDF_BROWSER"] = str(self.fake_browser(bin_dir))
            try:
                with self.assertRaisesRegex(ValueError, "expected image did not load"):
                    sdd_evidence.export(manifest, evidences.parent / "evidence-report.html", evidences, pdf=True)
            finally:
                os.environ.pop("SDD_PDF_BROWSER")

    def test_without_a_backend_the_pdf_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, evidences, manifest = self.workspace(tmp)
            os.environ["SDD_PDF_BROWSER"] = str(Path(tmp) / "missing-browser")
            try:
                with self.assertRaisesRegex(RuntimeError, "PDF backend"):
                    sdd_evidence.export(manifest, evidences.parent / "evidence-report.html", evidences, pdf=True)
            finally:
                os.environ.pop("SDD_PDF_BROWSER")


if __name__ == "__main__":
    unittest.main()
