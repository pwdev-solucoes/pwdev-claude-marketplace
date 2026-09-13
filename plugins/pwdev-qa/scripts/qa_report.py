"""Validate, consolidate, and atomically publish PWDEV QA report packages."""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import re
import secrets
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from qa_contract import ValidationError, load_manifest
from qa_evidence import (
    MAX_EVIDENCE_BYTES,
    MAX_TOTAL_EVIDENCE_BYTES,
    EvidenceError,
    _open_evidence,
    _reject_sensitive_path,
    _safe_parts,
    _verify_media,
    inspect_evidence,
)
from qa_html import render_html
from qa_pdf import render_pdf
from qa_verdict import build_report


class PublicationError(ValueError):
    """Raised when the requested output location cannot be used safely."""


_READ_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_DIRECTORY_FLAGS = _READ_FLAGS | getattr(os, "O_DIRECTORY", 0)
_CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_MEDIA_SUFFIX = {
    "text/plain": ".txt",
    "application/json": ".json",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}


def _open_directory(path: Path, label: str) -> Tuple[int, Tuple[int, int]]:
    if not getattr(os, "O_NOFOLLOW", 0) or not getattr(os, "O_DIRECTORY", 0):
        raise PublicationError(f"{label}: secure no-follow operations are unavailable")
    try:
        observed = path.lstat()
    except OSError as error:
        raise PublicationError(f"{label}: directory cannot be inspected") from error
    if stat.S_ISLNK(observed.st_mode):
        raise PublicationError(f"{label}: symlink is refused")
    if not stat.S_ISDIR(observed.st_mode):
        raise PublicationError(f"{label}: expected a directory")
    try:
        descriptor = os.open(str(path), _DIRECTORY_FLAGS)
    except OSError as error:
        raise PublicationError(f"{label}: directory cannot be opened safely") from error
    opened = os.fstat(descriptor)
    identity = (opened.st_dev, opened.st_ino)
    if identity != (observed.st_dev, observed.st_ino):
        os.close(descriptor)
        raise PublicationError(f"{label}: directory changed during safe open")
    return descriptor, identity


def _ensure_directory(parent_fd: int, name: str, label: str) -> Tuple[int, Tuple[int, int]]:
    try:
        observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
        try:
            observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except OSError as error:
            raise PublicationError(f"{label}: directory cannot be created safely") from error
    except OSError as error:
        raise PublicationError(f"{label}: directory cannot be inspected") from error
    if stat.S_ISLNK(observed.st_mode):
        raise PublicationError(f"{label}: symlink is refused")
    if not stat.S_ISDIR(observed.st_mode):
        raise PublicationError(f"{label}: expected a directory")
    try:
        descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent_fd)
    except OSError as error:
        raise PublicationError(f"{label}: directory cannot be opened safely") from error
    opened = os.fstat(descriptor)
    identity = (opened.st_dev, opened.st_ino)
    if identity != (observed.st_dev, observed.st_ino):
        os.close(descriptor)
        raise PublicationError(f"{label}: directory changed during safe open")
    return descriptor, identity


def _open_existing_directory(
    parent_fd: int, name: str, label: str
) -> Tuple[int, Tuple[int, int]]:
    try:
        observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as error:
        raise PublicationError(f"{label}: directory is missing or inaccessible") from error
    if stat.S_ISLNK(observed.st_mode):
        raise PublicationError(f"{label}: symlink is refused")
    if not stat.S_ISDIR(observed.st_mode):
        raise PublicationError(f"{label}: expected a directory")
    try:
        descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent_fd)
    except OSError as error:
        raise PublicationError(f"{label}: directory cannot be opened safely") from error
    opened = os.fstat(descriptor)
    identity = (opened.st_dev, opened.st_ino)
    if identity != (observed.st_dev, observed.st_ino):
        os.close(descriptor)
        raise PublicationError(f"{label}: directory changed during safe open")
    return descriptor, identity


def _reports_root(project_root: Path) -> Tuple[int, Tuple[int, int]]:
    current_fd, _ = _open_directory(project_root, "project root")
    try:
        for name, label in (
            (".planning", "output component .planning"),
            ("pwdev-qa", "output component pwdev-qa"),
            ("reports", "reports root"),
        ):
            next_fd, identity = _ensure_directory(current_fd, name, label)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd, identity
    except Exception:
        os.close(current_fd)
        raise


def _write_exclusive(directory_fd: int, name: str, raw: bytes) -> None:
    descriptor = os.open(name, _CREATE_FLAGS, 0o600, dir_fd=directory_fd)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_regular_at(directory_fd: int, name: str, label: str) -> bytes:
    try:
        descriptor = os.open(name, _READ_FLAGS, dir_fd=directory_fd)
    except OSError as error:
        raise RuntimeError(f"{label} is missing or unsafe") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"{label} is not a regular file")
        chunks: List[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
        raw = b"".join(chunks)
        if (
            (final.st_dev, final.st_ino) != (metadata.st_dev, metadata.st_ino)
            or final.st_size != metadata.st_size
            or len(raw) != final.st_size
        ):
            raise RuntimeError(f"{label} changed during validation")
        return raw
    finally:
        os.close(descriptor)


def _validate_pdf_structure(raw: bytes) -> None:
    """Validate the classic cross-reference structure emitted by ReportLab."""

    if not re.match(rb"%PDF-1\.[0-9](?:\r?\n|\r)", raw):
        raise RuntimeError("report.pdf has an invalid PDF header")
    ending = re.search(rb"startxref\s+([0-9]+)\s+%%EOF\s*\Z", raw)
    if ending is None:
        raise RuntimeError("report.pdf has no valid startxref and EOF")
    xref_offset = int(ending.group(1))
    if xref_offset <= 0 or xref_offset >= ending.start():
        raise RuntimeError("report.pdf startxref is outside the PDF body")
    if not raw.startswith(b"xref", xref_offset):
        raise RuntimeError("report.pdf startxref does not point to xref")

    position = xref_offset + 4
    newline = re.match(rb"(?:\r?\n|\r)", raw[position:])
    if newline is None:
        raise RuntimeError("report.pdf xref header is malformed")
    position += newline.end()
    entries: Dict[int, Tuple[int, int, bytes]] = {}
    while not raw.startswith(b"trailer", position):
        subsection = re.match(rb"([0-9]+) ([0-9]+)(?:\r?\n|\r)", raw[position:])
        if subsection is None:
            raise RuntimeError("report.pdf xref subsection is malformed")
        first = int(subsection.group(1))
        count = int(subsection.group(2))
        if count <= 0:
            raise RuntimeError("report.pdf xref subsection is empty")
        position += subsection.end()
        for index in range(count):
            entry = re.match(
                rb"([0-9]{10}) ([0-9]{5}) ([nf]) ?(?:\r?\n|\r)",
                raw[position:],
            )
            if entry is None:
                raise RuntimeError("report.pdf xref entry is malformed")
            object_id = first + index
            if object_id in entries:
                raise RuntimeError("report.pdf xref contains duplicate object entries")
            entries[object_id] = (
                int(entry.group(1)),
                int(entry.group(2)),
                entry.group(3),
            )
            position += entry.end()

    trailer_match = re.match(
        rb"trailer\s*<<(.*?)>>\s*\Z", raw[position : ending.start()], re.DOTALL
    )
    if trailer_match is None:
        raise RuntimeError("report.pdf trailer is malformed")
    trailer = trailer_match.group(1)
    size_match = re.search(rb"/Size\s+([0-9]+)\b", trailer)
    root_match = re.search(rb"/Root\s+([0-9]+)\s+([0-9]+)\s+R\b", trailer)
    if size_match is None or root_match is None:
        raise RuntimeError("report.pdf trailer has no Size or Root")
    declared_size = int(size_match.group(1))
    root_id = int(root_match.group(1))
    root_generation = int(root_match.group(2))
    if declared_size <= root_id or root_id not in entries:
        raise RuntimeError("report.pdf trailer Root is outside the xref")

    for object_id, (offset, generation, state) in entries.items():
        if state != b"n":
            continue
        marker = f"{object_id} {generation} obj".encode("ascii")
        if offset <= 0 or offset >= xref_offset or not raw.startswith(marker, offset):
            raise RuntimeError("report.pdf xref entry does not point to its object")
    root_offset, generation, state = entries[root_id]
    if state != b"n" or generation != root_generation or root_offset >= xref_offset:
        raise RuntimeError("report.pdf trailer Root is not a live xref object")

    def object_body(object_id: int, object_generation: int, label: str) -> bytes:
        entry = entries.get(object_id)
        if entry is None or entry[1] != object_generation or entry[2] != b"n":
            raise RuntimeError(f"report.pdf {label} reference is not live")
        marker = f"{object_id} {object_generation} obj".encode("ascii")
        start = entry[0] + len(marker)
        end = raw.find(b"endobj", start, xref_offset)
        if end < 0:
            raise RuntimeError(f"report.pdf {label} object is incomplete")
        return raw[start:end].strip()

    def dictionary(body: bytes, label: str) -> bytes:
        if not body.startswith(b"<<") or not body.endswith(b">>"):
            raise RuntimeError(f"report.pdf {label} is not a dictionary")
        return body[2:-2]

    catalog = dictionary(object_body(root_id, root_generation, "Catalog"), "Catalog")
    if re.search(rb"/Type\s*/Catalog\b", catalog) is None:
        raise RuntimeError("report.pdf Root dictionary is not /Type /Catalog")
    pages_match = re.search(rb"/Pages\s+([0-9]+)\s+([0-9]+)\s+R\b", catalog)
    if pages_match is None:
        raise RuntimeError("report.pdf Catalog has no valid /Pages reference")
    pages_id = int(pages_match.group(1))
    pages_generation = int(pages_match.group(2))
    pages = dictionary(
        object_body(pages_id, pages_generation, "Pages"), "Pages"
    )
    if re.search(rb"/Type\s*/Pages\b", pages) is None:
        raise RuntimeError("report.pdf Pages dictionary is not /Type /Pages")
    count_matches = re.findall(rb"/Count\s+(-?[0-9]+)(?![0-9.])", pages)
    kids_matches = re.findall(rb"/Kids\s*\[(.*?)\]", pages, re.DOTALL)
    if len(count_matches) != 1 or int(count_matches[0]) < 0:
        raise RuntimeError("report.pdf Pages /Count is not a non-negative integer")
    if len(kids_matches) != 1:
        raise RuntimeError("report.pdf Pages /Kids is not an array")
    kids = kids_matches[0]
    references = list(re.finditer(rb"([0-9]+)\s+([0-9]+)\s+R\b", kids))
    remainder = re.sub(rb"[0-9]+\s+[0-9]+\s+R\b", b"", kids)
    if remainder.strip():
        raise RuntimeError("report.pdf Pages /Kids contains a malformed reference")
    if int(count_matches[0]) != len(references):
        raise RuntimeError("report.pdf Pages /Count does not match /Kids")
    for reference in references:
        object_body(
            int(reference.group(1)), int(reference.group(2)), "page tree child"
        )


def _publication_snapshot_fd(directory_fd: int, prefix: str = "") -> Dict[str, Any]:
    """Return the deterministic, inode-independent public package snapshot."""

    snapshot: Dict[str, Any] = {}
    for name in sorted(os.listdir(directory_fd)):
        relative = f"{prefix}/{name}" if prefix else name
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        identity = (metadata.st_dev, metadata.st_ino)
        if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            child_fd = os.open(name, _DIRECTORY_FLAGS, dir_fd=directory_fd)
            try:
                opened = os.fstat(child_fd)
                if identity != (opened.st_dev, opened.st_ino):
                    raise RuntimeError(f"published report directory {relative} changed")
                snapshot[relative] = {"kind": "directory"}
                snapshot.update(_publication_snapshot_fd(child_fd, relative))
            finally:
                os.close(child_fd)
        elif stat.S_ISREG(metadata.st_mode):
            raw = _read_regular_at(directory_fd, name, f"published artifact {relative}")
            snapshot[relative] = {
                "kind": "file",
                "size_bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        else:
            raise RuntimeError(f"published artifact {relative} is unsafe")
    return snapshot


def _publication_digest(snapshot: Dict[str, Any]) -> str:
    canonical = json.dumps(
        snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_stage(
    reports_fd: int,
    staging_name: str,
    staging_fd: int,
    report: Dict[str, Any],
    expected_html: bytes,
) -> None:
    """Reopen every public artifact before the one atomic publication step."""

    named_fd = os.open(staging_name, _DIRECTORY_FLAGS, dir_fd=reports_fd)
    try:
        opened = os.fstat(staging_fd)
        named = os.fstat(named_fd)
        if (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino):
            raise RuntimeError("staging directory identity changed")
    finally:
        os.close(named_fd)

    expected_names = {"manifest.json", "report.html", "report.pdf"}
    if report["verified_evidence"]:
        expected_names.add("attachments")
    actual_names = set(os.listdir(staging_fd))
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        unexpected = sorted(actual_names - expected_names)
        raise RuntimeError(
            "staging package inventory mismatch "
            f"(missing={missing}, unexpected={unexpected})"
        )
    if _read_regular_at(staging_fd, "report.html", "report.html") != expected_html:
        raise RuntimeError("report.html content changed during validation")
    public_raw = _read_regular_at(staging_fd, "manifest.json", "manifest.json")
    try:
        if json.loads(public_raw.decode("utf-8")) != report:
            raise RuntimeError("manifest.json does not match the rendered public model")
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("manifest.json is not valid UTF-8 JSON") from error
    pdf = _read_regular_at(staging_fd, "report.pdf", "report.pdf")
    _validate_pdf_structure(pdf)

    if not report["verified_evidence"]:
        return
    attachments_fd, _ = _ensure_directory(
        staging_fd, "attachments", "staging attachments"
    )
    try:
        expected_attachments = {
            Path(item["path"]).name for item in report["verified_evidence"]
        }
        if set(os.listdir(attachments_fd)) != expected_attachments:
            raise RuntimeError("attachment inventory is incomplete or unexpected")
        for item in report["verified_evidence"]:
            name = Path(item["path"]).name
            raw = _read_regular_at(attachments_fd, name, f"attachment {item['id']}")
            if (
                len(raw) != item["size_bytes"]
                or hashlib.sha256(raw).hexdigest() != item["sha256"]
            ):
                raise RuntimeError(f"attachment {item['id']} changed during validation")
            if _verify_media(raw, item["id"], item["media_type"]):
                raise EvidenceError(
                    f"evidence {item['id']!r}: credential-like data detected in staging"
                )
    finally:
        os.close(attachments_fd)


def _remove_tree(parent_fd: int, name: str) -> None:
    """Remove one private staging tree without following any entry."""

    try:
        descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent_fd)
    except FileNotFoundError:
        return
    try:
        for child in os.listdir(descriptor):
            metadata = os.stat(child, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
                _remove_tree(descriptor, child)
            else:
                os.unlink(child, dir_fd=descriptor)
    finally:
        os.close(descriptor)
    os.rmdir(name, dir_fd=parent_fd)


def _exclusive_directory(parent_fd: int, template: str) -> Tuple[str, int]:
    for _ in range(100):
        name = template.format(token=secrets.token_hex(12))
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            continue
        try:
            descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent_fd)
        except Exception:
            os.rmdir(name, dir_fd=parent_fd)
            raise
        return name, descriptor
    raise PublicationError("could not create an exclusive staging directory")


def _blocked_copy(record: Dict[str, Any], message: str) -> Dict[str, Any]:
    return {
        "id": record["id"],
        "target_id": record["target_id"],
        "contract": dict(record["contract"]),
        "status": "BLOCKED",
        "copy_allowed": False,
        "diagnostic": f"evidence {record['id']}: {message}",
    }


def _copy_revalidated(
    project_fd: int,
    staging_fd: int,
    manifest: Dict[str, Any],
    inspections: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Copy verified bytes from their revalidated source descriptors."""

    source_by_id = {item["id"]: item for item in manifest["evidence"]}
    adjusted: List[Dict[str, Any]] = []
    staged_paths: Dict[str, str] = {}
    attachments_fd: Optional[int] = None
    copied_total = 0
    copied_names: List[str] = []
    try:
        for index, inspection in enumerate(inspections, 1):
            if inspection.get("status") != "VERIFIED":
                adjusted.append(inspection)
                continue
            item = source_by_id[inspection["id"]]
            parts = _safe_parts(item["id"], item["path"])
            _reject_sensitive_path(item["id"], parts)
            descriptor, metadata = _open_evidence(project_fd, parts, item["id"])
            if descriptor is None or metadata is None:
                adjusted.append(_blocked_copy(inspection, "missing during copy revalidation"))
                continue
            suffix = _MEDIA_SUFFIX[item["media_type"]]
            destination_name = f"evidence-{index:04d}{suffix}"
            destination_fd: Optional[int] = None
            raw_chunks: List[bytes] = []
            size = 0
            digest = hashlib.sha256()
            try:
                if attachments_fd is None:
                    attachments_fd, _ = _ensure_directory(
                        staging_fd, "attachments", "staging attachments"
                    )
                destination_fd = os.open(
                    destination_name, _CREATE_FLAGS, 0o600, dir_fd=attachments_fd
                )
                copied_names.append(destination_name)
                while True:
                    chunk = os.read(descriptor, 1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_EVIDENCE_BYTES:
                        raise EvidenceError(
                            f"evidence {item['id']!r}: actual evidence exceeds the 10 MiB limit"
                        )
                    copied_total += len(chunk)
                    if copied_total > MAX_TOTAL_EVIDENCE_BYTES:
                        raise EvidenceError("actual evidence exceeds the 100 MiB aggregate limit")
                    raw_chunks.append(chunk)
                    digest.update(chunk)
                    view = memoryview(chunk)
                    while view:
                        written = os.write(destination_fd, view)
                        if written <= 0:
                            raise OSError("short attachment write")
                        view = view[written:]
                final = os.fstat(descriptor)
                raw = b"".join(raw_chunks)
                contains_credential = _verify_media(raw, item["id"], item["media_type"])
                changed = (
                    not stat.S_ISREG(final.st_mode)
                    or (final.st_dev, final.st_ino) != (metadata.st_dev, metadata.st_ino)
                    or final.st_size != metadata.st_size
                    or size != item["size_bytes"]
                    or digest.hexdigest() != item["sha256"]
                )
                if contains_credential:
                    raise EvidenceError(
                        f"evidence {item['id']!r}: credential-like data detected during copy"
                    )
                if changed:
                    adjusted.append(
                        _blocked_copy(inspection, "changed during copy revalidation")
                    )
                    os.close(destination_fd)
                    destination_fd = None
                    os.unlink(destination_name, dir_fd=attachments_fd)
                    copied_names.remove(destination_name)
                    copied_total -= size
                    continue
                os.fsync(destination_fd)
                adjusted.append(inspection)
                staged_paths[item["id"]] = f"attachments/{destination_name}"
            finally:
                os.close(descriptor)
                if destination_fd is not None:
                    os.close(destination_fd)
        if attachments_fd is not None and not copied_names:
            os.close(attachments_fd)
            attachments_fd = None
            os.rmdir("attachments", dir_fd=staging_fd)
        return adjusted, staged_paths
    finally:
        if attachments_fd is not None:
            os.close(attachments_fd)


def _atomic_rename_exclusive(
    parent_fd: int,
    source: str,
    destination: str,
    project_root: Path,
    reports_identity: Tuple[int, int],
    expected_snapshot: Dict[str, Any],
) -> None:
    _assert_nominal_reports_root(project_root, reports_identity)
    staging_fd, _ = _open_existing_directory(
        parent_fd, source, "staging directory"
    )
    try:
        try:
            current_snapshot = _publication_snapshot_fd(staging_fd)
        except (OSError, RuntimeError, EvidenceError) as error:
            raise PublicationError(
                "staging package changed before commit"
            ) from error
        if current_snapshot != expected_snapshot:
            raise PublicationError("staging package changed before commit")
    finally:
        os.close(staging_fd)
    libc = ctypes.CDLL(None, use_errno=True)
    encoded_source = os.fsencode(source)
    encoded_destination = os.fsencode(destination)
    if hasattr(libc, "renameatx_np"):
        rename = libc.renameatx_np
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(
            parent_fd, encoded_source, parent_fd, encoded_destination, 0x00000004
        )
    elif hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(
            parent_fd, encoded_source, parent_fd, encoded_destination, 0x00000001
        )
    else:
        raise PublicationError("atomic no-overwrite directory rename is unavailable")
    if result != 0:
        error_number = ctypes.get_errno()
        if error_number in (errno.EEXIST, errno.ENOTEMPTY):
            raise PublicationError(f"report directory {destination!r} already exists")
        raise PublicationError(
            f"atomic report publication failed: {os.strerror(error_number)}"
        )


def _assert_nominal_reports_root(
    project_root: Path, expected_identity: Tuple[int, int]
) -> None:
    """Reject a reports-root exchange observed before the atomic commit."""

    root_fd, _ = _open_directory(project_root, "project root")
    opened_children: List[int] = []
    try:
        current_fd = root_fd
        for name, label in (
            (".planning", "output component .planning"),
            ("pwdev-qa", "output component pwdev-qa"),
            ("reports", "reports root"),
        ):
            next_fd, identity = _open_existing_directory(current_fd, name, label)
            opened_children.append(next_fd)
            current_fd = next_fd
        if identity != expected_identity:
            raise PublicationError("reports root identity changed before publication commit")
    finally:
        for descriptor in reversed(opened_children):
            os.close(descriptor)
        os.close(root_fd)


def _preserve_partial(
    reports_fd: int, reports_path: Path, run_id: str, result: Dict[str, Any]
) -> Path:
    name, descriptor = _exclusive_directory(reports_fd, f"{run_id}.partial-{{token}}")
    partial_path = reports_path / name
    try:
        result["output_dir"] = str(partial_path)
        raw = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _write_exclusive(descriptor, "diagnostic.json", raw)
        os.fsync(descriptor)
    except Exception:
        os.close(descriptor)
        _remove_tree(reports_fd, name)
        raise
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass
    return partial_path


def generate_report(manifest_path: Path, project_root: Path) -> dict:
    """Generate and atomically publish one complete HTML/PDF report package."""

    manifest = load_manifest(Path(manifest_path))
    root = Path(project_root)
    inspections = inspect_evidence(root, manifest)
    reports_fd, reports_identity = _reports_root(root)
    reports_path = root / ".planning" / "pwdev-qa" / "reports"
    run_id = manifest["run_id"]
    try:
        try:
            os.stat(run_id, dir_fd=reports_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise PublicationError(f"report directory {run_id!r} already exists")

        staging_name, staging_fd = _exclusive_directory(
            reports_fd, f".{run_id}.{{token}}.staging"
        )
        try:
            project_fd, _ = _open_directory(root, "project root")
            try:
                adjusted, staged_paths = _copy_revalidated(
                    project_fd, staging_fd, manifest, inspections
                )
            finally:
                os.close(project_fd)
            report = build_report(manifest, adjusted)
            for item in report["verified_evidence"]:
                item["path"] = staged_paths[item["id"]]

            html = render_html(report).encode("utf-8")
            _write_exclusive(staging_fd, "report.html", html)
            public_raw = (
                json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf-8")
            _write_exclusive(staging_fd, "manifest.json", public_raw)
            render_pdf(report, reports_path / staging_name / "report.pdf")
            _validate_stage(reports_fd, staging_name, staging_fd, report, html)
            os.fsync(staging_fd)
            publication_snapshot = _publication_snapshot_fd(staging_fd)
            publication_digest = _publication_digest(publication_snapshot)
            _atomic_rename_exclusive(
                reports_fd,
                staging_name,
                run_id,
                root,
                reports_identity,
                publication_snapshot,
            )
            staging_name = ""
            return {
                "run_id": run_id,
                "verdict": report["verdict"],
                "export_status": "complete",
                "output_dir": str(reports_path / run_id),
                "diagnostics": list(report["diagnostics"]),
                "publication_digest": publication_digest,
                "publication_snapshot": publication_snapshot,
            }
        except (EvidenceError, ValidationError, PublicationError):
            raise
        except Exception as error:
            diagnostics = list(locals().get("report", {}).get("diagnostics", []))
            diagnostics.append(f"report export incomplete: {error}")
            result = {
                "run_id": run_id,
                "verdict": locals().get("report", {}).get("verdict", "BLOCKED"),
                "export_status": "incomplete",
                "output_dir": "",
                "diagnostics": diagnostics,
                "publication_digest": None,
                "publication_snapshot": {},
            }
            if staging_fd >= 0:
                os.close(staging_fd)
                staging_fd = -1
            if staging_name:
                _remove_tree(reports_fd, staging_name)
                staging_name = ""
            partial_path = _preserve_partial(reports_fd, reports_path, run_id, result)
            result["output_dir"] = str(partial_path)
            return result
        finally:
            if staging_fd >= 0:
                os.close(staging_fd)
            if staging_name:
                _remove_tree(reports_fd, staging_name)
    finally:
        os.close(reports_fd)


def main(argv: Optional[List[str]] = None) -> int:
    """Run the ``report`` CLI and return its automation-oriented exit code."""

    parser = argparse.ArgumentParser(prog="qa_report.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--manifest", required=True, type=Path)
    report_parser.add_argument("--project-root", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        result = generate_report(arguments.manifest, arguments.project_root)
    except (ValidationError, EvidenceError, PublicationError) as error:
        print(json.dumps({"export_status": "refused", "diagnostics": [str(error)]}))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["export_status"] == "complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
