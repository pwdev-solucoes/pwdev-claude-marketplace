"""Behavioral tests for PWDEV QA evidence admission."""

import base64
import copy
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

from tests.test_qa_contract import load_contract_module, valid_manifest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-qa" / "scripts"
SCRIPT = SCRIPTS / "qa_evidence.py"
MIB = 1024 * 1024


def load_evidence_module():
    if not SCRIPT.is_file():
        raise AssertionError("qa_evidence.py is missing")
    spec = importlib.util.spec_from_file_location("qa_evidence", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("qa_evidence.py cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(SCRIPTS))
    return module


def png_header(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def png_image(width: int, height: int) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    pixels = (b"\x00" + (b"\x00" * width)) * height
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(pixels))
        + png_chunk(b"IEND", b"")
    )


def png_with_pixels(width: int, height: int, pixels: bytes) -> bytes:
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(pixels))
        + png_chunk(b"IEND", b"")
    )


def jpeg_image() -> bytes:
    return base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
        "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh"
        "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAAR"
        "CAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAA"
        "AgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkK"
        "FhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWG"
        "h4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl"
        "5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA"
        "AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYk"
        "NOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOE"
        "hYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk"
        "5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q=="
    )


class QaEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract_module()

    def manifest_for(self, path: str, raw: bytes, media_type: str = "text/plain") -> dict:
        data = valid_manifest()
        data["evidence"][0].update(
            path=path,
            sha256=hashlib.sha256(raw).hexdigest(),
            media_type=media_type,
            size_bytes=len(raw),
        )
        return self.contract.validate_manifest(data)

    def inspect_one(self, root: Path, manifest: dict) -> dict:
        records = load_evidence_module().inspect_evidence(root, manifest)
        self.assertEqual(len(records), 1)
        return records[0]

    def test_verified_file_exposes_only_approved_public_metadata(self) -> None:
        raw = b"synthetic QA evidence\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "result.txt").write_bytes(raw)
            manifest = self.manifest_for("artifacts/result.txt", raw)

            record = self.inspect_one(root, manifest)

        self.assertEqual(
            record,
            {
                "id": "ev-1",
                "target_id": "web-app",
                "contract": {
                    "path": "tasks/prd-pwdev-qa/prd.md",
                    "sha256": "a" * 64,
                },
                "status": "VERIFIED",
                "copy_allowed": True,
                "requires_copy_revalidation": True,
                "path": "artifacts/result.txt",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "media_type": "text/plain",
                "size_bytes": len(raw),
                "diagnostic": None,
            },
        )

    def test_missing_changed_or_target_incompatible_file_is_blocked_without_path(self) -> None:
        cases = ("missing", "size", "hash", "target")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                root.joinpath("artifacts").mkdir()
                raw = b"expected evidence\n"
                manifest = self.manifest_for("artifacts/result.txt", raw)
                if case != "missing":
                    actual = b"different length" if case == "size" else b"changed evidence\n"
                    if case == "target":
                        actual = raw
                        manifest["evidence"][0]["target_id"] = "other-target"
                    root.joinpath("artifacts/result.txt").write_bytes(actual)

                record = self.inspect_one(root, manifest)

                self.assertEqual(record["status"], "BLOCKED")
                self.assertFalse(record["copy_allowed"])
                self.assertNotIn("path", record)
                self.assertNotIn("sha256", record)
                self.assertNotIn("media_type", record)
                self.assertNotIn("size_bytes", record)
                self.assertNotIn(raw.decode().strip(), record["diagnostic"])

    def test_rejects_external_paths_and_symlinks_in_file_or_directory(self) -> None:
        evidence = load_evidence_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            raw = b"safe\n"
            outside.joinpath("result.txt").write_bytes(raw)

            traversal = self.manifest_for("artifacts/result.txt", raw)
            traversal["evidence"][0]["path"] = "../outside/result.txt"
            with self.assertRaisesRegex(evidence.EvidenceError, "confined"):
                evidence.inspect_evidence(root, traversal)

            root.joinpath("file-link.txt").symlink_to(outside / "result.txt")
            file_link = self.manifest_for("file-link.txt", raw)
            with self.assertRaisesRegex(evidence.EvidenceError, "symlink"):
                evidence.inspect_evidence(root, file_link)

            root.joinpath("dir-link").symlink_to(outside, target_is_directory=True)
            directory_link = self.manifest_for("dir-link/result.txt", raw)
            with self.assertRaisesRegex(evidence.EvidenceError, "symlink"):
                evidence.inspect_evidence(root, directory_link)

    def test_refuses_secret_bearing_paths_before_content_inspection(self) -> None:
        evidence = load_evidence_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b"THIS_VALUE_MUST_NOT_BE_READ"
            root.joinpath(".env").write_bytes(raw)
            manifest = self.manifest_for(".env", raw)

            with self.assertRaisesRegex(evidence.EvidenceError, "sensitive path"):
                evidence.inspect_evidence(root, manifest)

    def test_parent_path_swap_cannot_redirect_the_opened_snapshot(self) -> None:
        evidence = load_evidence_module()
        safe = b"synthetic safe evidence\n"
        attacker = b"attacker-controlled bytes\n"
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            outside = base / "outside"
            parent = root / "artifacts"
            attacker_parent = outside / "attacker"
            parent.mkdir(parents=True)
            attacker_parent.mkdir(parents=True)
            parent.joinpath("result.txt").write_bytes(safe)
            attacker_parent.joinpath("result.txt").write_bytes(attacker)
            manifest = self.manifest_for("artifacts/result.txt", safe)
            original_open = evidence.os.open
            swapped = False

            def swap_before_file_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if not swapped and Path(path).name == "result.txt":
                    parent.rename(outside / "original")
                    parent.symlink_to(attacker_parent, target_is_directory=True)
                    swapped = True
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(evidence.os, "open", side_effect=swap_before_file_open):
                try:
                    records = evidence.inspect_evidence(root, manifest)
                    self.assertEqual(len(records), 1)
                    record = records[0]
                except ValueError:
                    self.fail("parent swap redirected or invalidated the descriptor-held snapshot")

        self.assertTrue(swapped)
        self.assertEqual(record["status"], "VERIFIED")
        self.assertTrue(record["requires_copy_revalidation"])
        self.assertNotIn(attacker.decode().strip(), json.dumps(record))

    def test_revalidates_actual_individual_and_aggregate_size_limits(self) -> None:
        evidence = load_evidence_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            oversized = root / "oversized.txt"
            oversized.write_bytes(b"x")
            manifest = self.manifest_for("oversized.txt", b"x")
            oversized.write_bytes(b"x" * (10 * MIB + 1))
            with self.assertRaisesRegex(evidence.EvidenceError, "10 MiB"):
                evidence.inspect_evidence(root, manifest)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = valid_manifest()
            manifest["evidence"] = []
            manifest["cases"][0]["evidence_ids"] = []
            manifest["defects"][0]["evidence_ids"] = []
            for number in range(11):
                path = root / f"ev-{number}.txt"
                path.touch()
                path.write_bytes(b"x" * (10 * MIB - 1))
                item = copy.deepcopy(valid_manifest()["evidence"][0])
                raw_size = path.stat().st_size
                item.update(
                    id=f"ev-{number}",
                    path=path.name,
                    size_bytes=1,
                    sha256="0" * 64,
                )
                manifest["evidence"].append(item)
            manifest = self.contract.validate_manifest(manifest)
            with self.assertRaisesRegex(evidence.EvidenceError, "100 MiB"):
                evidence.inspect_evidence(root, manifest)

    def test_verifies_real_mime_signature_and_image_pixel_limit(self) -> None:
        evidence = load_evidence_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            json_raw = b'{"result": "PASS"}'
            root.joinpath("result.txt").write_bytes(json_raw)
            manifest = self.manifest_for("result.txt", json_raw, "text/plain")
            with self.assertRaisesRegex(evidence.EvidenceError, "media type"):
                evidence.inspect_evidence(root, manifest)

            raw = png_image(1, 1)
            root.joinpath("fake.jpg").write_bytes(raw)
            manifest = self.manifest_for("fake.jpg", raw, "image/jpeg")
            with self.assertRaisesRegex(evidence.EvidenceError, "media type"):
                evidence.inspect_evidence(root, manifest)

            truncated_png = png_header(1, 1)
            root.joinpath("truncated.png").write_bytes(truncated_png)
            manifest = self.manifest_for("truncated.png", truncated_png, "image/png")
            manifest["evidence"][0]["sanitization"]["status"] = "reviewed"
            with self.assertRaisesRegex(evidence.EvidenceError, "PNG|image/png"):
                evidence.inspect_evidence(root, manifest)

            malformed_png = png_with_pixels(1, 1, b"\x00" * 1000)
            root.joinpath("malformed.png").write_bytes(malformed_png)
            manifest = self.manifest_for("malformed.png", malformed_png, "image/png")
            manifest["evidence"][0]["sanitization"]["status"] = "reviewed"
            with self.assertRaisesRegex(evidence.EvidenceError, "PNG"):
                evidence.inspect_evidence(root, manifest)

            truncated_jpeg = jpeg_image()[:-2]
            root.joinpath("truncated.jpg").write_bytes(truncated_jpeg)
            manifest = self.manifest_for("truncated.jpg", truncated_jpeg, "image/jpeg")
            manifest["evidence"][0]["sanitization"]["status"] = "reviewed"
            with self.assertRaisesRegex(evidence.EvidenceError, "JPEG|image/jpeg"):
                evidence.inspect_evidence(root, manifest)

            valid_jpeg = jpeg_image()
            root.joinpath("valid.jpg").write_bytes(valid_jpeg)
            manifest = self.manifest_for("valid.jpg", valid_jpeg, "image/jpeg")
            manifest["evidence"][0]["sanitization"]["status"] = "reviewed"
            self.assertEqual(self.inspect_one(root, manifest)["status"], "VERIFIED")

            huge = png_image(5000, 4001)
            root.joinpath("huge.png").write_bytes(huge)
            manifest = self.manifest_for("huge.png", huge, "image/png")
            manifest["evidence"][0]["sanitization"]["status"] = "reviewed"
            with self.assertRaisesRegex(evidence.EvidenceError, "20 megapixels"):
                evidence.inspect_evidence(root, manifest)

    def test_synthetic_credentials_in_log_and_json_are_never_exposed(self) -> None:
        fixtures = (
            ("result.log", b"Authorization: Bearer synthetic-secret-token\n", "text/plain"),
            ("result.json", json.dumps({"api_key": "synthetic-secret-token"}).encode(), "application/json"),
            (
                "escaped.json",
                b'{"api\\u005fkey":"synthetic-secret-token"}',
                "application/json",
            ),
        )
        for filename, raw, media_type in fixtures:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                root.joinpath(filename).write_bytes(raw)
                manifest = self.manifest_for(filename, raw, media_type)

                record = self.inspect_one(root, manifest)

                serialized = json.dumps(record)
                self.assertEqual(record["status"], "BLOCKED")
                self.assertFalse(record["copy_allowed"])
                self.assertNotIn("path", record)
                self.assertNotIn("synthetic-secret-token", serialized)
                self.assertNotIn("api_key", serialized)
                self.assertIn("credential-like data", record["diagnostic"])

    def test_pending_image_is_blocked_without_public_path_or_bytes(self) -> None:
        raw = png_image(1, 1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("capture.png").write_bytes(raw)
            manifest = self.manifest_for("capture.png", raw, "image/png")
            manifest["evidence"][0]["sanitization"]["status"] = "pending"

            record = self.inspect_one(root, manifest)

        self.assertEqual(record["status"], "BLOCKED")
        self.assertFalse(record["copy_allowed"])
        self.assertNotIn("path", record)
        self.assertNotIn("sha256", record)
        self.assertIn("sanitization review is pending", record["diagnostic"])


if __name__ == "__main__":
    unittest.main()
