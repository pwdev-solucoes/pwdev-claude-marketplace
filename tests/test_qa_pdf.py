"""Behavioral tests for the paginated PWDEV QA PDF renderer."""

import builtins
import copy
import hashlib
import importlib.util
import re
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

try:
    import pdfplumber
    from pypdf import PdfReader
except ImportError as exc:  # verification-only dependencies, as test_qa_scenarios already treats them
    raise unittest.SkipTest(
        "requires the declared PDF verification environment: Python 3.12 with "
        "plugins/pwdev-qa/requirements.txt and requirements-dev.txt"
    ) from exc

from tests.test_qa_contract import load_contract_module, valid_manifest
from tests.test_qa_verdict import inspections


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-qa"
SCRIPTS = PLUGIN / "scripts"
PDF_SCRIPT = SCRIPTS / "qa_pdf.py"
VERDICT_SCRIPT = SCRIPTS / "qa_verdict.py"
REQUIREMENTS = PLUGIN / "requirements.txt"


def png_fixture(width: int = 40, height: int = 24) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    rows = b"".join(
        b"\x00" + bytes((20, 80, 180)) * width for _ in range(height)
    )
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(
        b"IDAT", zlib.compress(rows)
    ) + chunk(b"IEND", b"")


PNG_BYTES = png_fixture()


def load_module(name: str, path: Path):
    if not path.is_file():
        raise AssertionError(f"{path.name} is missing")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"{path.name} cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def build(data: dict) -> dict:
    manifest = load_contract_module().validate_manifest(data)
    verdict = load_module("qa_verdict_for_pdf", VERDICT_SCRIPT)
    return verdict.build_report(manifest, inspections(manifest))


def long_criterion(index: int):
    tokens = []
    word = 0
    while len(" ".join(tokens)) < 2000:
        tokens.append(f"c{index:03d}w{word:04d}á")
        word += 1
    return " ".join(tokens)[:2000], tokens[:-1]


class QaPdfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = load_module("qa_pdf", PDF_SCRIPT)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.destination = Path(self.temporary.name) / "report.pdf"

    def image_report(
        self, relative_path: str, *, digest: str, size: int, media_type: str
    ) -> dict:
        data = valid_manifest()
        data["defects"] = []
        data["evidence"][0].update(
            path=relative_path,
            sha256=digest,
            size_bytes=size,
            media_type=media_type,
        )
        return build(data)

    def test_renders_a4_paginated_complete_public_report_with_textual_statuses(self) -> None:
        report = build(valid_manifest())
        report["project"] = "Qualidade — ação <b>não é markup</b>"
        self.renderer.render_pdf(report, self.destination)

        reader = PdfReader(self.destination)
        self.assertGreaterEqual(len(reader.pages), 2)
        self.assertAlmostEqual(float(reader.pages[0].mediabox.width), 595.2756, places=2)
        self.assertAlmostEqual(float(reader.pages[0].mediabox.height), 841.8898, places=2)
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
        for label in (
            "PWDEV QA report",
            "Contents",
            "Status legend",
            "Summary",
            "Acceptance criteria",
            "Cases and attempts",
            "Defects",
            "Approved evidence",
            "Diagnostics",
            "Verdict",
            "PASS",
            "BLOCKED",
            "NOT_RUN",
            "NOT_APPLICABLE",
            "Page 1 of",
            "Qualidade — ação <b>não é markup</b>",
            "O relatório é exportado.",
            "Dois formatos",
            "python3 -m unittest tests.test_qa_contract",
            "Defeito corrigido",
            "artifacts/qa-output.txt",
        ):
            self.assertIn(label, extracted)

    def test_preserves_all_tokens_in_one_hundred_2000_character_criteria(self) -> None:
        data = valid_manifest()
        base_criterion = data["criteria"][0]
        base_case = data["cases"][0]
        data["criteria"] = []
        data["cases"] = []
        expected_tokens = []
        for index in range(100):
            text, tokens = long_criterion(index)
            expected_tokens.extend(tokens)
            criterion = copy.deepcopy(base_criterion)
            criterion.update(id=f"CA-{index:03d}", text=text, case_ids=[f"case-{index:03d}"])
            case = copy.deepcopy(base_case)
            case.update(
                id=f"attempt-{index:03d}",
                case_id=f"case-{index:03d}",
                criterion_ids=[f"CA-{index:03d}"],
            )
            data["criteria"].append(criterion)
            data["cases"].append(case)
        data["defects"] = []
        report = build(data)

        self.renderer.render_pdf(report, self.destination)

        reader = PdfReader(self.destination)
        self.assertGreater(len(reader.pages), 20)
        pypdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        with pdfplumber.open(self.destination) as document:
            plumber_text = "\n".join(page.extract_text() or "" for page in document.pages)
        token_pattern = re.compile(r"c\d{3}w\d{4}á")
        self.assertCountEqual(token_pattern.findall(pypdf_text), expected_tokens)
        self.assertCountEqual(token_pattern.findall(plumber_text), expected_tokens)

    def test_fails_explicitly_when_reportlab_is_unavailable(self) -> None:
        report = build(valid_manifest())
        real_import = builtins.__import__

        def unavailable(name, *args, **kwargs):
            if name == "reportlab" or name.startswith("reportlab."):
                raise ModuleNotFoundError("No module named 'reportlab'", name="reportlab")
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=unavailable):
            with self.assertRaisesRegex(RuntimeError, "reportlab==4.4.9 is required"):
                self.renderer.render_pdf(report, self.destination)
        self.assertFalse(self.destination.exists())

    def test_embeds_revalidated_verified_image_with_safe_caption(self) -> None:
        relative = "artifacts/captura-á.png"
        staged = self.destination.parent / relative
        staged.parent.mkdir(parents=True)
        staged.write_bytes(PNG_BYTES)
        report = self.image_report(
            relative,
            digest=hashlib.sha256(PNG_BYTES).hexdigest(),
            size=len(PNG_BYTES),
            media_type="image/png",
        )

        self.renderer.render_pdf(report, self.destination)

        reader = PdfReader(self.destination)
        self.assertEqual(sum(len(page.images) for page in reader.pages), 1)
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn("Evidence image: ev-1 — artifacts/captura-á.png", extracted)

    def test_refuses_unsafe_or_changed_staged_images(self) -> None:
        digest = hashlib.sha256(PNG_BYTES).hexdigest()
        scenarios = {
            "missing": ("capture.png", digest, len(PNG_BYTES), "image/png", "missing"),
            "hash": ("capture.png", "0" * 64, len(PNG_BYTES), "image/png", "SHA-256"),
            "mime": ("capture.png", digest, len(PNG_BYTES), "image/jpeg", "MIME"),
            "symlink": ("capture.png", digest, len(PNG_BYTES), "image/png", "symlink"),
        }
        for name, (relative, expected_hash, size, media_type, error) in scenarios.items():
            with self.subTest(name=name):
                parent = Path(self.temporary.name) / name
                parent.mkdir()
                self.destination = parent / "report.pdf"
                staged = parent / relative
                if name == "symlink":
                    target = parent / "target.png"
                    target.write_bytes(PNG_BYTES)
                    staged.symlink_to(target.name)
                elif name != "missing":
                    staged.write_bytes(PNG_BYTES)
                report = self.image_report(
                    relative,
                    digest=expected_hash,
                    size=size,
                    media_type=media_type,
                )

                with self.assertRaisesRegex(RuntimeError, error):
                    self.renderer.render_pdf(report, self.destination)
                self.assertFalse(self.destination.exists())

    def test_refuses_symlink_as_destination_root(self) -> None:
        actual = Path(self.temporary.name) / "actual-root"
        actual.mkdir()
        staged = actual / "capture.png"
        staged.write_bytes(PNG_BYTES)
        linked = Path(self.temporary.name) / "linked-root"
        linked.symlink_to(actual.name, target_is_directory=True)
        self.destination = linked / "report.pdf"
        report = self.image_report(
            "capture.png",
            digest=hashlib.sha256(PNG_BYTES).hexdigest(),
            size=len(PNG_BYTES),
            media_type="image/png",
        )

        with self.assertRaisesRegex(RuntimeError, "destination root.*symlink"):
            self.renderer.render_pdf(report, self.destination)
        self.assertFalse((actual / "report.pdf").exists())

    def test_root_exchange_cannot_redirect_final_publication(self) -> None:
        root = Path(self.temporary.name) / "publication-root"
        root.mkdir()
        staged = root / "capture.png"
        staged.write_bytes(PNG_BYTES)
        preserved = Path(self.temporary.name) / "preserved-root"
        self.destination = root / "report.pdf"
        report = self.image_report(
            "capture.png",
            digest=hashlib.sha256(PNG_BYTES).hexdigest(),
            size=len(PNG_BYTES),
            media_type="image/png",
        )
        original_revalidation = self.renderer._staged_image_bytes
        exchanged = False

        def exchange_after_revalidation(*args, **kwargs):
            nonlocal exchanged
            result = original_revalidation(*args, **kwargs)
            if not exchanged:
                root.rename(preserved)
                root.mkdir()
                (root / "report.pdf").write_bytes(b"attacker-controlled-root")
                exchanged = True
            return result

        with mock.patch.object(
            self.renderer,
            "_staged_image_bytes",
            side_effect=exchange_after_revalidation,
        ):
            with self.assertRaisesRegex(RuntimeError, "destination root.*changed"):
                self.renderer.render_pdf(report, self.destination)

        self.assertEqual(
            (root / "report.pdf").read_bytes(), b"attacker-controlled-root"
        )
        self.assertFalse((preserved / "report.pdf").exists())

    def test_final_file_exchange_is_detected_without_removing_attacker_file(self) -> None:
        staged = self.destination.parent / "capture.png"
        staged.write_bytes(PNG_BYTES)
        report = self.image_report(
            "capture.png",
            digest=hashlib.sha256(PNG_BYTES).hexdigest(),
            size=len(PNG_BYTES),
            media_type="image/png",
        )
        original_replace = self.renderer.os.replace

        def exchange_after_publish(*args, **kwargs):
            result = original_replace(*args, **kwargs)
            self.destination.unlink()
            self.destination.write_bytes(b"attacker-file-after-publication")
            return result

        with mock.patch.object(
            self.renderer.os, "replace", side_effect=exchange_after_publish
        ):
            with self.assertRaisesRegex(RuntimeError, "published PDF.*changed"):
                self.renderer.render_pdf(report, self.destination)

        self.assertEqual(
            self.destination.read_bytes(), b"attacker-file-after-publication"
        )

    def test_lists_only_verified_evidence_as_approved_references(self) -> None:
        data = valid_manifest()
        pending = copy.deepcopy(data["evidence"][0])
        pending_path = self.destination.parent / "artifacts" / "SECRET-unreviewed.png"
        pending_path.parent.mkdir(parents=True)
        pending_path.write_bytes(PNG_BYTES)
        pending.update(
            id="ev-pending",
            path="artifacts/SECRET-unreviewed.png",
            media_type="image/png",
            sha256=hashlib.sha256(PNG_BYTES).hexdigest(),
            size_bytes=len(PNG_BYTES),
        )
        pending["sanitization"]["status"] = "pending"
        data["evidence"].append(pending)
        data["cases"][0]["evidence_ids"].append("ev-pending")
        data["defects"][0]["evidence_ids"].append("ev-pending")
        manifest = load_contract_module().validate_manifest(data)
        verdict = load_module("qa_verdict_filtered_pdf", VERDICT_SCRIPT)
        report = verdict.build_report(manifest, inspections(manifest, "ev-pending"))

        self.renderer.render_pdf(report, self.destination)

        extracted = "\n".join(
            page.extract_text() or "" for page in PdfReader(self.destination).pages
        )
        self.assertNotIn("ev-1, ev-pending", extracted)
        self.assertNotIn("SECRET-unreviewed.png", extracted)
        self.assertIn("Approved evidence IDs\nev-1", extracted)
        self.assertIn("evidence 'ev-pending': unavailable", extracted)
        self.assertEqual(sum(len(page.images) for page in PdfReader(self.destination).pages), 0)

    def test_declares_exact_runtime_and_verification_dependencies(self) -> None:
        runtime_lines = [
            line.strip()
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        dev_lines = [
            line.strip()
            for line in (PLUGIN / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertEqual(runtime_lines, ["reportlab==4.4.9"])
        self.assertEqual(dev_lines, ["pypdf==6.10.0", "pdfplumber==0.11.9"])


if __name__ == "__main__":
    unittest.main()
