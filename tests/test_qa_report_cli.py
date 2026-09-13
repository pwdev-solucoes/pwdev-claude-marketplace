"""Behavioral tests for the atomic PWDEV QA report publisher."""

import builtins
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_qa_contract import valid_manifest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-qa" / "scripts"
SCRIPT = SCRIPTS / "qa_report.py"


def load_module(name="qa_report"):
    if not SCRIPT.is_file():
        raise AssertionError("qa_report.py is missing")
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("qa_report.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def publication_snapshot(path):
    root = Path(path)
    result = {}
    for item in sorted(root.rglob("*")):
        relative = item.relative_to(root).as_posix()
        if item.is_dir():
            result[relative] = {"kind": "directory"}
        else:
            raw = item.read_bytes()
            result[relative] = {
                "kind": "file",
                "size_bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
    return result


def snapshot_digest(snapshot):
    canonical = json.dumps(
        snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class QaReportCliTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "artifacts").mkdir()
        self.raw = b"synthetic QA evidence\n"
        (self.root / "artifacts/result.txt").write_bytes(self.raw)
        self.manifest = valid_manifest()
        self.manifest["run_id"] = "cli-run"
        self.manifest["evidence"][0].update(
            path="artifacts/result.txt",
            sha256=hashlib.sha256(self.raw).hexdigest(),
            size_bytes=len(self.raw),
        )
        self.manifest["x-private"] = {"secret-note": "PRIVATE-ONLY"}
        self.manifest["cases"][0]["command"] = (
            "python3 -c 'open(\"COMMAND-RAN\", \"w\").write(\"bad\")'"
        )
        self.manifest_path = self.root / "input.json"
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def output(self, run_id="cli-run"):
        return self.root / ".planning/pwdev-qa/reports" / run_id

    @staticmethod
    def fake_pdf(_report, destination):
        chunks = [
            b"%PDF-1.4\n",
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
            b"2 0 obj\n<< /Type /Pages /Count 0 /Kids [] >>\nendobj\n",
        ]
        offsets = [0]
        position = len(chunks[0])
        for chunk in chunks[1:]:
            offsets.append(position)
            position += len(chunk)
        xref = position
        chunks.extend(
            [
                b"xref\n0 3\n",
                b"0000000000 65535 f \n",
                f"{offsets[1]:010d} 00000 n \n".encode("ascii"),
                f"{offsets[2]:010d} 00000 n \n".encode("ascii"),
                b"trailer\n<< /Size 3 /Root 1 0 R >>\n",
                f"startxref\n{xref}\n%%EOF\n".encode("ascii"),
            ]
        )
        Path(destination).write_bytes(b"".join(chunks))

    def test_publishes_complete_allowlisted_package_without_executing_command(self):
        publisher = load_module()

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "complete")
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(Path(result["output_dir"]), self.output())
        self.assertEqual(result["publication_snapshot"], publication_snapshot(self.output()))
        self.assertEqual(
            result["publication_digest"], snapshot_digest(result["publication_snapshot"])
        )
        self.assertEqual(
            {item.name for item in self.output().iterdir()},
            {"attachments", "manifest.json", "report.html", "report.pdf"},
        )
        public = json.loads((self.output() / "manifest.json").read_text("utf-8"))
        self.assertNotIn("x-private", public)
        self.assertNotIn("PRIVATE-ONLY", json.dumps(public))
        attachment = self.output() / public["verified_evidence"][0]["path"]
        self.assertEqual(attachment.read_bytes(), self.raw)
        self.assertFalse((self.root / "COMMAND-RAN").exists())
        self.assertIn("Command (inert)", (self.output() / "report.html").read_text("utf-8"))

    def test_collision_and_symlinked_output_component_are_refused(self):
        publisher = load_module("qa_report_collision")
        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf):
            publisher.generate_report(self.manifest_path, self.root)
            with self.assertRaisesRegex(publisher.PublicationError, "already exists"):
                publisher.generate_report(self.manifest_path, self.root)

        other = self.root / "other"
        other.mkdir()
        fresh = self.root / "fresh"
        fresh.mkdir()
        (fresh / ".planning").symlink_to(other, target_is_directory=True)
        fresh_manifest = fresh / "input.json"
        fresh_manifest.write_text(json.dumps(self.manifest), encoding="utf-8")
        with self.assertRaisesRegex(publisher.PublicationError, "symlink"):
            publisher.generate_report(fresh_manifest, fresh)

    def test_changed_after_inspection_is_withheld_and_prevents_pass(self):
        publisher = load_module("qa_report_changed")
        real_inspect = publisher.inspect_evidence

        def inspect_then_change(root, manifest):
            inspected = real_inspect(root, manifest)
            (Path(root) / "artifacts/result.txt").write_bytes(b"changed after inspection\n")
            return inspected

        with mock.patch.object(
            publisher, "inspect_evidence", side_effect=inspect_then_change
        ), mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "complete")
        self.assertEqual(result["verdict"], "BLOCKED")
        public = json.loads((self.output() / "manifest.json").read_text("utf-8"))
        self.assertEqual(public["verified_evidence"], [])
        self.assertFalse((self.output() / "attachments").exists())
        self.assertTrue(any("changed during copy revalidation" in d for d in result["diagnostics"]))

    def test_pdf_failure_preserves_only_exclusive_partial_diagnostic(self):
        publisher = load_module("qa_report_pdf_failure")
        with mock.patch.object(publisher, "render_pdf", side_effect=RuntimeError("PDF unavailable")):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "incomplete")
        self.assertFalse(self.output().exists())
        partial = Path(result["output_dir"])
        self.assertRegex(partial.name, r"^cli-run\.partial-[0-9a-f]+$")
        self.assertEqual({item.name for item in partial.iterdir()}, {"diagnostic.json"})
        diagnostic = json.loads((partial / "diagnostic.json").read_text("utf-8"))
        self.assertEqual(diagnostic["export_status"], "incomplete")
        self.assertIn("PDF unavailable", " ".join(diagnostic["diagnostics"]))

    def test_renderer_returning_without_pdf_cannot_publish_complete_report(self):
        publisher = load_module("qa_report_missing_pdf")
        with mock.patch.object(publisher, "render_pdf", return_value=None):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "incomplete")
        self.assertFalse(self.output().exists())
        self.assertIn("report.pdf", " ".join(result["diagnostics"]))

    def test_superficial_pdf_markers_without_xref_are_rejected(self):
        publisher = load_module("qa_report_malformed_pdf")

        def malformed(_report, destination):
            Path(destination).write_bytes(b"%PDF-1.4\n%%EOF\n")

        with mock.patch.object(publisher, "render_pdf", side_effect=malformed):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "incomplete")
        self.assertFalse(self.output().exists())
        self.assertIn("startxref", " ".join(result["diagnostics"]))

    def test_xref_coherent_pdf_with_garbage_root_is_rejected(self):
        publisher = load_module("qa_report_garbage_root")

        def garbage_root(report, destination):
            self.fake_pdf(report, destination)
            path = Path(destination)
            raw = path.read_bytes()
            valid = b"<< /Type /Catalog /Pages 2 0 R >>"
            raw = raw.replace(valid, b"garbage".ljust(len(valid), b" "))
            path.write_bytes(raw)

        with mock.patch.object(publisher, "render_pdf", side_effect=garbage_root):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "incomplete")
        self.assertFalse(self.output().exists())
        self.assertIn("Catalog", " ".join(result["diagnostics"]))

    def test_semantically_invalid_catalog_pages_graphs_are_rejected(self):
        substitutions = {
            "catalog-type": (b"/Type /Catalog", b"/Type /Garbage"),
            "pages-reference": (b"/Pages 2 0 R", b"/Pages 9 0 R"),
            "pages-type": (b"/Type /Pages", b"/Type /Garba"),
            "negative-count": (b"/Count 0", b"/Count -"),
            "malformed-kids": (b"/Kids []", b"/Kids[x]"),
        }
        for label, (valid, invalid) in substitutions.items():
            with self.subTest(label=label):
                publisher = load_module(f"qa_report_semantic_{label}")

                def corrupt(report, destination, valid=valid, invalid=invalid):
                    self.fake_pdf(report, destination)
                    path = Path(destination)
                    raw = path.read_bytes()
                    self.assertEqual(len(valid), len(invalid))
                    self.assertIn(valid, raw)
                    path.write_bytes(raw.replace(valid, invalid, 1))

                with mock.patch.object(publisher, "render_pdf", side_effect=corrupt):
                    result = publisher.generate_report(self.manifest_path, self.root)
                self.assertEqual(result["export_status"], "incomplete")
                self.assertFalse(self.output().exists())

    def test_source_replaced_by_symlink_after_inspection_refuses_export(self):
        publisher = load_module("qa_report_source_symlink")
        real_inspect = publisher.inspect_evidence
        outside = self.root / "outside.txt"
        outside.write_bytes(self.raw)

        def inspect_then_link(root, manifest):
            inspected = real_inspect(root, manifest)
            source = Path(root) / "artifacts/result.txt"
            source.unlink()
            source.symlink_to(outside)
            return inspected

        with mock.patch.object(publisher, "inspect_evidence", side_effect=inspect_then_link):
            with self.assertRaisesRegex(publisher.EvidenceError, "symlink"):
                publisher.generate_report(self.manifest_path, self.root)
        self.assertFalse(self.output().exists())

    def test_final_collision_won_during_rename_is_never_overwritten(self):
        publisher = load_module("qa_report_collision_race")
        real_rename = publisher._atomic_rename_exclusive

        def attacker_wins(parent_fd, source, destination, *commit_context):
            os.mkdir(destination, dir_fd=parent_fd)
            destination_fd = os.open(
                destination, os.O_RDONLY | os.O_DIRECTORY, dir_fd=parent_fd
            )
            try:
                marker_fd = os.open(
                    "attacker-marker",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=destination_fd,
                )
                os.close(marker_fd)
            finally:
                os.close(destination_fd)
            return real_rename(parent_fd, source, destination, *commit_context)

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf), mock.patch.object(
            publisher, "_atomic_rename_exclusive", side_effect=attacker_wins
        ):
            with self.assertRaisesRegex(publisher.PublicationError, "already exists"):
                publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual({item.name for item in self.output().iterdir()}, {"attacker-marker"})
        self.assertFalse(any("staging" in item.name for item in self.output().parent.iterdir()))

    def test_nominal_reports_root_exchange_is_detected_and_sentinel_is_preserved(self):
        publisher = load_module("qa_report_root_exchange")
        reports = self.output().parent
        preserved = self.root / "preserved-reports"
        real_rename = publisher._atomic_rename_exclusive

        def exchange_root(parent_fd, source, destination, *commit_context):
            reports.rename(preserved)
            reports.mkdir()
            self.output().mkdir()
            (self.output() / "sentinel").write_bytes(b"attacker sentinel")
            return real_rename(parent_fd, source, destination, *commit_context)

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf), mock.patch.object(
            publisher, "_atomic_rename_exclusive", side_effect=exchange_root
        ):
            with self.assertRaisesRegex(publisher.PublicationError, "reports root.*changed"):
                publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual((self.output() / "sentinel").read_bytes(), b"attacker sentinel")
        self.assertFalse((preserved / "cli-run").exists())

    def test_staging_file_exchange_before_commit_is_exporter_failure(self):
        publisher = load_module("qa_report_staging_exchange")
        real_rename = publisher._atomic_rename_exclusive

        def exchange_staging(parent_fd, source, destination, *commit_context):
            staging_fd = os.open(
                source, os.O_RDONLY | os.O_DIRECTORY, dir_fd=parent_fd
            )
            try:
                os.unlink("report.html", dir_fd=staging_fd)
                replacement = os.open(
                    "report.html",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=staging_fd,
                )
                os.write(replacement, b"attacker pre-commit")
                os.close(replacement)
            finally:
                os.close(staging_fd)
            return real_rename(parent_fd, source, destination, *commit_context)

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf), mock.patch.object(
            publisher, "_atomic_rename_exclusive", side_effect=exchange_staging
        ):
            with self.assertRaisesRegex(
                publisher.PublicationError, "staging package changed before commit"
            ):
                publisher.generate_report(self.manifest_path, self.root)

        self.assertFalse(self.output().exists())

    def test_post_commit_pdf_exchange_is_external_and_digest_detects_it(self):
        publisher = load_module("qa_report_pdf_exchange")
        real_rename = publisher._atomic_rename_exclusive

        def exchange_pdf(parent_fd, source, destination, *commit_context):
            result = real_rename(parent_fd, source, destination, *commit_context)
            pdf = self.output() / "report.pdf"
            pdf.unlink()
            pdf.write_bytes(b"ATTACKER-PDF")
            return result

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf), mock.patch.object(
            publisher, "_atomic_rename_exclusive", side_effect=exchange_pdf
        ):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "complete")
        self.assertEqual((self.output() / "report.pdf").read_bytes(), b"ATTACKER-PDF")
        self.assertNotEqual(
            result["publication_digest"], snapshot_digest(publication_snapshot(self.output()))
        )

    def test_post_commit_run_exchange_is_external_and_digest_detects_it(self):
        publisher = load_module("qa_report_run_exchange")
        real_rename = publisher._atomic_rename_exclusive
        displaced = self.root / "displaced-owned-package"

        def exchange_run(parent_fd, source, destination, *commit_context):
            result = real_rename(parent_fd, source, destination, *commit_context)
            self.output().rename(displaced)
            self.output().mkdir()
            (self.output() / "sentinel").write_bytes(b"attacker run")
            return result

        with mock.patch.object(publisher, "render_pdf", side_effect=self.fake_pdf), mock.patch.object(
            publisher, "_atomic_rename_exclusive", side_effect=exchange_run
        ):
            result = publisher.generate_report(self.manifest_path, self.root)

        self.assertEqual(result["export_status"], "complete")
        self.assertEqual((self.output() / "sentinel").read_bytes(), b"attacker run")
        self.assertTrue((displaced / "manifest.json").is_file())
        self.assertNotEqual(
            result["publication_digest"], snapshot_digest(publication_snapshot(self.output()))
        )

    def test_main_exit_codes_distinguish_input_and_export_failures(self):
        publisher = load_module("qa_report_main")
        bad = copy.deepcopy(self.manifest)
        bad["run_id"] = "INVALID"
        self.manifest_path.write_text(json.dumps(bad), encoding="utf-8")
        with mock.patch("builtins.print"):
            self.assertEqual(
                publisher.main(["report", "--manifest", str(self.manifest_path), "--project-root", str(self.root)]),
                2,
            )

        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        real_import = builtins.__import__

        def unavailable(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=unavailable), mock.patch("builtins.print"):
            self.assertEqual(
                publisher.main(["report", "--manifest", str(self.manifest_path), "--project-root", str(self.root)]),
                3,
            )


if __name__ == "__main__":
    unittest.main()
